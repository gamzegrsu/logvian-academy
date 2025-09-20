# main.py
import os, json, time, threading, uuid
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# Docker SDK (works when /var/run/docker.sock is mounted)
try:
    import docker
    DOCKER_AVAILABLE = True
    docker_client = docker.from_env()
except Exception:
    DOCKER_AVAILABLE = False
    docker_client = None

# load tasks_data
from backend import tasks_data
TASKS_MODULE = tasks_data.modules
ID_MAP = tasks_data.id_map

app = FastAPI(title="Cyberbot Backend - Final")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROGRESS_FILE = DATA_DIR / "progress.json"
LAB_MAP_FILE = DATA_DIR / "running_labs.json"

_state_lock = threading.Lock()
USER_PROGRESS = {}
RUNNING_LABS = {}

if PROGRESS_FILE.exists():
    try:
        with PROGRESS_FILE.open("r", encoding="utf8") as f:
            USER_PROGRESS = json.load(f)
    except: USER_PROGRESS = {}

if LAB_MAP_FILE.exists():
    try:
        with LAB_MAP_FILE.open("r", encoding="utf8") as f:
            RUNNING_LABS = json.load(f)
    except: RUNNING_LABS = {}

def save_progress():
    with _state_lock:
        try:
            with PROGRESS_FILE.open("w", encoding="utf8") as f:
                json.dump(USER_PROGRESS, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("⚠️ save_progress:", e)

def save_lab_map():
    with _state_lock:
        try:
            with LAB_MAP_FILE.open("w", encoding="utf8") as f:
                json.dump(RUNNING_LABS, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("⚠️ save_lab_map:", e)

def default_progress(user_id: str):
    return {"user_id": user_id, "completed_tasks": [], "xp": 0, "coins": 100, "hints": [], "chat_history": []}

def ensure_user(user_id: str):
    if user_id not in USER_PROGRESS:
        USER_PROGRESS[user_id] = default_progress(user_id)
    return USER_PROGRESS[user_id]

# Docker helpers (build on demand)
LABS_DIR = Path("./labs")

def build_image_if_needed(lab_name: str):
    if not DOCKER_AVAILABLE:
        raise RuntimeError("Docker not available")
    image_tag = f"cyberbot_lab_{lab_name}:latest"
    try:
        docker_client.images.get(image_tag)
        return image_tag
    except docker.errors.ImageNotFound:
        lab_path = LABS_DIR / lab_name
        if not lab_path.exists():
            raise RuntimeError(f"Lab folder not found: {lab_path}")
        print(f"🔨 Building {image_tag} ...")
        docker_client.images.build(path=str(lab_path), tag=image_tag, rm=True)
        return image_tag

def start_lab_container(lab_name: str, user_id: str):
    if not DOCKER_AVAILABLE:
        raise RuntimeError("Docker not available")
    image = build_image_if_needed(lab_name)
    cname = f"lab_{lab_name}_{user_id}_{str(uuid.uuid4())[:8]}"
    container = docker_client.containers.run(image, detach=True, name=cname, ports={"5000/tcp": None}, restart_policy={"Name":"no"})
    container.reload()
    host_port = container.attrs["NetworkSettings"]["Ports"]["5000/tcp"][0]["HostPort"]
    host = os.getenv("LAB_HOST", "localhost")
    url = f"http://{host}:{host_port}"
    RUNNING_LABS[cname] = {"container_id": container.id, "lab": lab_name, "user_id": user_id, "url": url, "started_at": time.time()}
    save_lab_map()
    return cname, url

def stop_lab_container(cname: str):
    if not DOCKER_AVAILABLE:
        raise RuntimeError("Docker not available")
    info = RUNNING_LABS.get(cname)
    if not info:
        raise RuntimeError("Not found")
    try:
        cont = docker_client.containers.get(cname)
        cont.stop(timeout=3)
        cont.remove()
    except Exception as e:
        print("⚠️ stop error:", e)
    RUNNING_LABS.pop(cname, None)
    save_lab_map()
    return True

# Chat: proxy to LLM server if set, otherwise fallback to tasks_data + rule-based
LLM_SERVER_URL = os.getenv("LLM_SERVER_URL")  # e.g. http://llm:8000
class ChatReq(BaseModel):
    message: str
    user_id: Optional[str] = "anon"
    character: Optional[str] = "Bilge Logvian"
    verbosity: Optional[str] = "normal"

@app.post("/api/chat")
def chat(req: ChatReq):
    user = ensure_user(req.user_id or "anon")
    user["chat_history"].append({"from":"user","msg":req.message,"time":time.time()})
    save_progress()

    # If LLM server available, proxy and include contextual info
    if LLM_SERVER_URL:
        try:
            payload = {"message": req.message, "user_id": req.user_id, "character": req.character, "verbosity": req.verbosity}
            resp = requests.post(LLM_SERVER_URL.rstrip("/") + "/chat", json=payload, timeout=30)
            resp.raise_for_status()
            j = resp.json()
            # LLM server returns structured {"theory","answer","homework","lab","notes"}
            reply_text = j.get("answer") or j.get("response") or json.dumps(j)
            # store bot message
            user["chat_history"].append({"from":"bot","msg":reply_text,"time":time.time()})
            save_progress()
            return {"response": reply_text, "meta": j}
        except Exception as e:
            print("⚠️ LLM proxy failed:", e)

    # Fallback: use tasks_data to answer concisely
    msg = req.message.lower()
    # try to detect topic key
    detected = None
    for key, mod in TASKS_MODULE.items():
        if key in msg or any(w in msg for w in [mod.get("id",""), mod.get("title","").lower().split()[0]]):
            detected = mod
            break
    if not detected:
        # default to sql injection starter
        detected = TASKS_MODULE.get("sql_injection")

    # Build a pedagogical reply
    theory = "\n".join(detected.get("theory", [])[:2]) if isinstance(detected.get("theory", []), list) else detected.get("theory","")
    steps = detected.get("labs", [])[0].get("steps", []) if detected.get("labs") else []
    hint = detected.get("labs", [])[0].get("hints", [""])[0] if detected.get("labs") else ""
    reply = f"🔮 Bilge Logvian — Öğretici:\n\nTeori: {theory}\n\nÖrnek adımlar:\n- " + "\n- ".join(steps[:3]) + f"\n\nİpucu: {hint}\n\nLab'ı başlatmak için sol panelden 'Lab Başlat' butonuna tıkla."
    user["chat_history"].append({"from":"bot","msg":reply,"time":time.time()})
    save_progress()
    return {"response": reply, "meta": {"source":"fallback","task": detected.get("id")} }

# Tasks endpoints
@app.get("/api/tasks")
def api_tasks(user_id: Optional[str] = "anon"):
    user = ensure_user(user_id)
    out = []
    for key, mod in TASKS_MODULE.items():
        tid = mod.get("id")
        locked = False
        req_id = mod.get("labs",[{}])[0].get("requires") if False else None
        # simpler: use numeric prerequisites in module if provided (here not needed)
        completed = tid in user["completed_tasks"]
        out.append({
            "id": tid,
            "title": mod.get("title"),
            "description": mod.get("summary") or mod.get("description",""),
            "difficulty": mod.get("difficulty","medium"),
            "estimated_time": mod.get("estimated_minutes") or mod.get("estimated_time", 15),
            "reward": {"xp": 50, "coins": 10},
            "locked": locked,
            "completed": completed
        })
    return {"tasks": out}

@app.get("/api/tasks/{task_id}")
def api_task(task_id: str, user_id: Optional[str] = "anon"):
    # map numeric id to module key
    key = ID_MAP.get(int(task_id)) if str(task_id).isdigit() else task_id
    if isinstance(key, str) and key in TASKS_MODULE:
        mod = TASKS_MODULE[key]
    else:
        # try direct lookup by id
        mod = None
        for k, m in TASKS_MODULE.items():
            if str(m.get("id")) == str(task_id) or k == task_id:
                mod = m; break
    if not mod:
        raise HTTPException(status_code=404, detail="Task not found")
    user = ensure_user(user_id)
    copy = dict(mod)
    copy.pop("flag", None)  # never send flag
    return {"task": copy}

class AnswerReq(BaseModel):
    user_id: str
    answer: str

@app.post("/api/tasks/{task_id}/answer")
def api_answer(task_id: str, payload: AnswerReq):
    # find module
    mod = None
    for k,m in TASKS_MODULE.items():
        if str(m.get("id")) == str(task_id) or k==task_id:
            mod = m; break
    if not mod:
        raise HTTPException(status_code=404, detail="Task not found")
    user = ensure_user(payload.user_id)
    correct_flag = str(mod.get("flag","")).strip()
    if payload.answer.strip() == correct_flag and correct_flag != "":
        if mod.get("id") not in user["completed_tasks"]:
            user["completed_tasks"].append(mod.get("id"))
            # award example
            user["xp"] += 50
            user["coins"] += 20
            save_progress()
        return {"correct": True, "message": "Tebrikler! Görev tamamlandı.", "user_progress": user, "rewards": {"xp":50,"coins":20}}
    else:
        return {"correct": False, "message": "Yanlış flag.", "user_progress": user}

class HintReq(BaseModel):
    user_id: str
    task_id: str

@app.post("/api/hint")
def api_hint(req: HintReq):
    user = ensure_user(req.user_id)
    # find module
    mod = None
    for k,m in TASKS_MODULE.items():
        if str(m.get("id")) == str(req.task_id) or k==req.task_id:
            mod = m; break
    if not mod:
        raise HTTPException(status_code=404, detail="Task not found")
    cost = 10
    if user["coins"] < cost:
        raise HTTPException(status_code=400, detail="Not enough coins")
    user["coins"] -= cost
    # return first hint if exists
    first_hint = ""
    labs = mod.get("labs", [])
    if labs and isinstance(labs, list):
        first_hint = labs[0].get("hints", [""])[0]
    save_progress()
    return {"hint": first_hint, "coins_left": user["coins"]}

# Leaderboard
@app.get("/api/leaderboard")
def api_leaderboard():
    arr = []
    for uid,u in USER_PROGRESS.items():
        arr.append({"user_id": uid, "xp": u.get("xp",0), "coins": u.get("coins",0), "completed": len(u.get("completed_tasks",[]))})
    arr.sort(key=lambda x: x["xp"], reverse=True)
    return {"leaderboard": arr[:10]}

# Labs control
class LabStartReq(BaseModel):
    user_id: str

class LabStopReq(BaseModel):
    container_name: str

@app.post("/api/lab/{task_id}/start")
def api_lab_start(task_id: str, req: LabStartReq, background_tasks: BackgroundTasks):
    # find module key to get lab folder
    mod = None
    for k,m in TASKS_MODULE.items():
        if str(m.get("id")) == str(task_id) or k==task_id:
            mod = m; break
    if not mod:
        raise HTTPException(status_code=404, detail="Task not found")
    lab_name = mod.get("lab")
    if not DOCKER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Docker not available")
    try:
        cname, url = start_lab_container(lab_name, req.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lab start failed: {e}")

    # schedule stop
    def auto_stop(name, after=15*60):
        time.sleep(after)
        try:
            stop_lab_container(name)
            print("Auto-stopped", name)
        except Exception as e:
            print("Auto-stop error:", e)
    background_tasks.add_task(auto_stop, cname, 15*60)
    return {"container_name": cname, "lab_url": url, "task_id": task_id}

@app.post("/api/lab/stop")
def api_lab_stop(req: LabStopReq):
    if not DOCKER_AVAILABLE:
        raise HTTPException(status_code=503, detail="Docker not available")
    try:
        stop_lab_container(req.container_name)
        return {"stopped": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/lab/running")
def api_lab_running():
    return {"running": RUNNING_LABS}

@app.on_event("shutdown")
def shutdown():
    save_progress()
    save_lab_map()
