# main.py - Bilge Logvian Siber Güvenlik Platformu (Docker'sız Lab Simülasyonu)

import os
import time
import json
import random
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

# --- Ortam değişkenlerini yükle ---
load_dotenv()

# --- Groq API Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY bulunamadı. Lütfen .env dosyasında ayarla.")

# Groq client'ını başlat
try:
    client = Groq(api_key=GROQ_API_KEY)
    print("✅ Groq client başarıyla başlatıldı")
except Exception as e:
    print(f"⚠️ Groq client başlatılamadı: {e}")
    client = None

# --- FastAPI setup ---
app = FastAPI(
    title="Bilge Logvian — Siber Güvenlik Akademisi",
    description="Mistik bir üslupla siber güvenlik öğreten interaktif AI eğitmen",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --- Data Models ---
class ChatRequest(BaseModel):
    user_id: Optional[str] = "anon"
    message: str


class LabStartRequest(BaseModel):
    user_id: str
    lab_name: str


class LabStopRequest(BaseModel):
    user_id: str
    lab_name: str


class HintRequest(BaseModel):
    user_id: str
    task_id: str


class AnswerRequest(BaseModel):
    user_id: str
    answer: str


# --- Lab Simülasyon Konfigürasyonu ---
LAB_SIMULATIONS = {
    "sql_injection": {
        "friendly_name": "SQL Enjeksiyon Simülasyonu",
        "description": "SQL enjeksiyon saldırılarını öğren ve pratik yap",
        "url": "http://localhost:8081",
        "challenges": [
            {
                "id": 1,
                "title": "Temel SQL Injection",
                "description": "' OR '1'='1 payload'unu kullanarak giriş yap",
                "target": "admin",
                "hint": "Kullanıcı adı kısmına ' OR '1'='1 yazmayı dene",
                "solution": "admin' OR '1'='1' --"
            },
            {
                "id": 2,
                "title": "Union Based SQL Injection",
                "description": "UNION SELECT kullanarak veritabanından veri çek",
                "hint": "UNION SELECT 1,2,3 -- kullan",
                "solution": "' UNION SELECT 1,username,password FROM users --"
            }
        ]
    },
    "xss": {
        "friendly_name": "XSS Simülasyonu",
        "description": "XSS payload'larını deneyimle ve korunma yöntemlerini öğren",
        "url": "http://localhost:8082",
        "challenges": [
            {
                "id": 1,
                "title": "Temel XSS",
                "description": "<script>alert('XSS')</script> payload'unu çalıştır",
                "hint": "Yorum kısmına script tag'i ekle",
                "solution": "<script>alert('XSS')</script>"
            },
            {
                "id": 2,
                "title": "Stored XSS",
                "description": "XSS payload'unu kalıcı hale getir",
                "hint": "Profil bilgilerine XSS ekle",
                "solution": "<img src=x onerror=alert('XSS')>"
            }
        ]
    },
    "hash_cracking": {
        "friendly_name": "Hash Kırma Simülasyonu",
        "description": "Hash fonksiyonlarını çözümle ve kırma tekniklerini öğren",
        "url": "http://localhost:8083",
        "challenges": [
            {
                "id": 1,
                "title": "MD5 Hash Kırma",
                "description": "5f4dcc3b5aa765d61d8327deb882cf99 hash'ini kır",
                "hint": "Bu 'password' şifresinin MD5 hash'i",
                "solution": "password"
            },
            {
                "id": 2,
                "title": "SHA1 Hash Kırma",
                "description": "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8 hash'ini kır",
                "hint": "Bu çok yaygın bir şifre",
                "solution": "password"
            }
        ]
    }
}

# --- Simülasyon Durumları ---
SIMULATION_STATES = {
    "sql_injection": {
        "current_challenge": 0,
        "completed": False,
        "user_inputs": []
    },
    "xss": {
        "current_challenge": 0,
        "completed": False,
        "user_inputs": []
    },
    "hash_cracking": {
        "current_challenge": 0,
        "completed": False,
        "user_inputs": []
    }
}

# --- Veri Depolama ---
USER_PROGRESS: Dict[str, Dict[str, Any]] = {}
ACTIVE_LABS: Dict[str, Dict[str, Any]] = {}


# --- Yardımcı Fonksiyonlar ---
def ensure_user(user_id: str) -> Dict[str, Any]:
    if user_id not in USER_PROGRESS:
        USER_PROGRESS[user_id] = {
            "xp": 0,
            "coins": 100,
            "level": 1,
            "completed_modules": [],
            "chat_history": [],
            "current_quest": None,
            "inventory": ["Başlangıç Tılsımı"],
            "skills": {
                "SQL Injection": 0,
                "XSS": 0,
                "Hash Cracking": 0,
                "Cryptography": 0
            },
            "active_labs": {},
            "simulation_states": SIMULATION_STATES.copy(),
            "created_at": time.time()
        }
    return USER_PROGRESS[user_id]


# --- Lab Simülasyon Fonksiyonları ---
def start_lab_simulation(user_id: str, lab_name: str) -> Dict[str, Any]:
    """Kullanıcı için bir lab simülasyonu başlat"""

    if lab_name not in LAB_SIMULATIONS:
        raise HTTPException(status_code=404, detail="Lab simülasyonu bulunamadı")

    lab_config = LAB_SIMULATIONS[lab_name]

    # Lab bilgilerini hazırla
    lab_info = {
        "container_id": f"simulation_{lab_name}",
        "host_port": lab_config["url"].split(":")[-1],
        "status": "running",
        "url": lab_config["url"],
        "start_time": time.time(),
        "friendly_name": lab_config["friendly_name"],
        "description": lab_config["description"],
        "type": "simulation"
    }

    # Kullanıcı verilerine kaydet
    user_data = ensure_user(user_id)
    if "active_labs" not in user_data:
        user_data["active_labs"] = {}
    user_data["active_labs"][lab_name] = lab_info

    if user_id not in ACTIVE_LABS:
        ACTIVE_LABS[user_id] = {}
    ACTIVE_LABS[user_id][lab_name] = lab_info

    # Simülasyon durumunu sıfırla
    user_data["simulation_states"][lab_name]["current_challenge"] = 0
    user_data["simulation_states"][lab_name]["completed"] = False
    user_data["simulation_states"][lab_name]["user_inputs"] = []

    print(f"✅ Lab simülasyonu başlatıldı: {lab_name} for {user_id}")
    return lab_info


def check_simulation_answer(lab_name: str, challenge_id: int, user_answer: str) -> bool:
    """Simülasyon cevabını kontrol et"""
    if lab_name not in LAB_SIMULATIONS:
        return False

    challenges = LAB_SIMULATIONS[lab_name]["challenges"]
    if challenge_id < 0 or challenge_id >= len(challenges):
        return False

    challenge = challenges[challenge_id]
    return user_answer.strip().lower() == challenge["solution"].lower()


def get_current_challenge(user_id: str, lab_name: str) -> Dict[str, Any]:
    """Mevcut challenge'ı getir"""
    user_data = ensure_user(user_id)
    state = user_data["simulation_states"][lab_name]
    challenges = LAB_SIMULATIONS[lab_name]["challenges"]

    if state["current_challenge"] < len(challenges):
        return challenges[state["current_challenge"]]
    return None


# --- Mistik Öğretici Prompt ---
MISTIC_SYSTEM_PROMPT = """
Sen "Bilge Logvian"sın. Mistik, bilge ve gizemli bir siber güvenlik üstadısın. Karanlık ağların sırlarını bilen, kod büyüsünün ustası bir mentorsun.

🎭 Üslup Özellikleri:
- Efsanevi ve mistik bir dil kullan ("kristal ağ", "şifreler alemi", "kod büyüsü")
- Öğrenciyi "çırak" diye hitap et
- Her dersi bir macera gibi anlat ama çok uzun değil tane tane öğrendiğinden emin olarak anlat.
- Anlayamadığı yerlerde örnekler, ipucular ver
- Gerçek dünya senaryoları ve lablar öner
- Savunma odaklı siber güvenlik öğret
- KISA ve ÖZ cevaplar ver (maksimum 3-4 cümle)
- Her derse başlamadan önce ilk kullanıcıya konu hakkında neler bildiğini sor
- Bildiği bilgiler üzerine gerekiyorsa ekleme yap eksik varsa düzelt ve yeni bilgileri öğret.
- Çok uzun cevaplar verme akılda kalıcı mistik tarz örnekler, öğretici, mentör bir Bilge Logvian tarzı davran.
- Öğrencinin sohbetine karşılık ver ama yine derse dönmeyi unutma
"""


def ask_bilge_logvian(user_message: str, chat_history: list = None) -> str:
    """Bilge Logvian'a soru sor"""
    if not client:
        return "🔮 Bilge Logvian şu anda derin meditasyonda... (API bağlantı hatası)"

    messages = [{"role": "system", "content": MISTIC_SYSTEM_PROMPT}]

    if chat_history:
        for msg in chat_history[-6:]:
            if msg["from"] == "user":
                messages.append({"role": "user", "content": msg["msg"]})
            else:
                messages.append({"role": "assistant", "content": msg["msg"]})

    messages.append({"role": "user", "content": user_message})

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            timeout=30
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"🔮 Bilge Logvian derin düşüncelere daldı... (Hata: {str(e)})"


# --- API ENDPOINT'LERİ ---

@app.get("/")
async def root():
    return {
        "message": "🔮 Bilge Logvian'ın Siber Güvenlik Akademisine Hoş Geldiniz",
        "status": "active",
        "version": "3.0.0 (Simülasyon Modu)",
        "active_users": len(USER_PROGRESS),
        "active_labs": sum(len(labs) for labs in ACTIVE_LABS.values())
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "groq_connected": client is not None,
        "simulation_mode": True
    }


# --- Lab Simülasyon Endpoint'leri ---

@app.post("/api/lab/start")
async def start_lab(req: LabStartRequest):
    """Yeni bir lab simülasyonu başlat"""
    lab_info = start_lab_simulation(req.user_id, req.lab_name)
    return {
        "success": True,
        "lab": lab_info,
        "message": f"🔮 {lab_info['friendly_name']} başlatıldı!",
        "simulation_mode": True
    }


@app.post("/api/lab/stop")
async def stop_lab(req: LabStopRequest):
    """Aktif bir lab simülasyonu durdur"""
    user_data = ensure_user(req.user_id)

    if req.user_id in ACTIVE_LABS and req.lab_name in ACTIVE_LABS[req.user_id]:
        del ACTIVE_LABS[req.user_id][req.lab_name]

    if req.lab_name in user_data.get("active_labs", {}):
        del user_data["active_labs"][req.lab_name]

    return {
        "success": True,
        "message": f"🔮 Lab simülasyonu durduruldu: {req.lab_name}"
    }


@app.get("/api/lab/active/{user_id}")
async def get_active_labs(user_id: str):
    """Kullanıcının aktif lablarını listele"""
    user_data = ensure_user(user_id)
    return {
        "active_labs": user_data.get("active_labs", {}),
        "available_labs": LAB_SIMULATIONS
    }


# --- Simülasyon Challenge Endpoint'leri ---

@app.get("/api/simulation/{lab_name}/challenge")
async def get_current_challenge_endpoint(user_id: str, lab_name: str):
    """Mevcut challenge'ı getir"""
    if lab_name not in LAB_SIMULATIONS:
        raise HTTPException(status_code=404, detail="Lab bulunamadı")

    challenge = get_current_challenge(user_id, lab_name)
    if not challenge:
        return {"completed": True, "message": "Tüm challenge'lar tamamlandı!"}

    return {
        "challenge": {
            "id": challenge["id"],
            "title": challenge["title"],
            "description": challenge["description"],
            "hint_available": True
        },
        "progress": {
            "current": challenge["id"],
            "total": len(LAB_SIMULATIONS[lab_name]["challenges"])
        }
    }


@app.post("/api/simulation/{lab_name}/submit")
async def submit_simulation_answer(user_id: str, lab_name: str, answer: str):
    """Simülasyon cevabını gönder"""
    if lab_name not in LAB_SIMULATIONS:
        raise HTTPException(status_code=404, detail="Lab bulunamadı")

    user_data = ensure_user(user_id)
    state = user_data["simulation_states"][lab_name]

    if state["completed"]:
        return {"correct": True, "completed": True, "message": "Bu lab zaten tamamlandı!"}

    current_challenge = state["current_challenge"]
    is_correct = check_simulation_answer(lab_name, current_challenge, answer)

    if is_correct:
        state["current_challenge"] += 1
        state["user_inputs"].append({"challenge": current_challenge, "answer": answer, "correct": True})

        # Son challenge mı kontrol et
        if state["current_challenge"] >= len(LAB_SIMULATIONS[lab_name]["challenges"]):
            state["completed"] = True

            # Ödül ver
            rewards = {
                "sql_injection": {"xp": 25, "coins": 15},
                "xss": {"xp": 30, "coins": 20},
                "hash_cracking": {"xp": 35, "coins": 25}
            }

            reward = rewards.get(lab_name, {"xp": 0, "coins": 0})
            user_data["xp"] += reward["xp"]
            user_data["coins"] += reward["coins"]
            user_data["completed_modules"].append(lab_name)

            # Skill geliştir
            skill_name = lab_name.replace("_", " ").title()
            user_data["skills"][skill_name] += 1

            return {
                "correct": True,
                "completed": True,
                "message": f"🎉 Tebrikler! {LAB_SIMULATIONS[lab_name]['friendly_name']} tamamlandı!",
                "rewards": reward,
                "level_up": user_data["xp"] >= user_data["level"] * 100
            }
        else:
            return {
                "correct": True,
                "completed": False,
                "message": "Doğru cevap! Sonraki challenge'a geçiliyor...",
                "next_challenge": state["current_challenge"] + 1
            }
    else:
        state["user_inputs"].append({"challenge": current_challenge, "answer": answer, "correct": False})
        return {
            "correct": False,
            "message": "Cevap yanlış. Tekrar deneyin veya ipucu alın."
        }


# --- Frontend için uyumlu endpoint'ler ---

@app.get("/api/tasks")
async def get_tasks(user_id: str):
    """Mevcut görevleri getir"""
    user = ensure_user(user_id)

    tasks = [
        {
            "id": "sql_injection",
            "title": "SQL Injection",
            "description": "SQL enjeksiyon saldırılarını öğren",
            "reward": {"xp": 25, "coins": 15},
            "completed": "sql_injection" in user["completed_modules"],
            "locked": False,
            "type": "simulation"
        },
        {
            "id": "xss",
            "title": "XSS - Stored",
            "description": "XSS payload'larını deneyimle",
            "reward": {"xp": 30, "coins": 20},
            "completed": "xss" in user["completed_modules"],
            "locked": user["xp"] < 25,
            "type": "simulation"
        },
        {
            "id": "hash_cracking",
            "title": "Hash Cracking",
            "description": "Hash fonksiyonlarını çözümle",
            "reward": {"xp": 35, "coins": 25},
            "completed": "hash_cracking" in user["completed_modules"],
            "locked": user["xp"] < 50,
            "type": "simulation"
        }
    ]

    return {"tasks": tasks}


@app.post("/api/lab/{task_id}/start")
async def start_lab_by_task(task_id: str, user_id: str):
    """Görev ID'sine göre lab başlat"""
    if task_id not in LAB_SIMULATIONS:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")

    lab_info = start_lab_simulation(user_id, task_id)
    return {
        "container_name": lab_info["container_id"],
        "lab_url": lab_info["url"],
        "lab": lab_info["friendly_name"],
        "simulation_mode": True
    }


@app.post("/api/hint")
async def get_hint(req: HintRequest):
    """Görev için ipucu ver"""
    user = ensure_user(req.user_id)

    if user["coins"] < 10:
        raise HTTPException(status_code=400, detail="Yeterli jetonunuz yok")

    user["coins"] -= 10

    lab_hints = {
        "sql_injection": "SQL Injection için: ' OR '1'='1 gibi temel payload'ları dene",
        "xss": "XSS için: <script>alert('XSS')</script> temel payload ile başla",
        "hash_cracking": "Hash cracking için: 'password' gibi basit şifreleri dene"
    }

    hint = lab_hints.get(req.task_id, "Bu görev için ipucu bulunmuyor")

    return {
        "hint": hint,
        "coins_left": user["coins"]
    }


# --- Diğer endpoint'ler ---

@app.post("/api/chat")
async def chat_with_bilge(req: ChatRequest):
    """Bilge Logvian ile sohbet et"""
    user = ensure_user(req.user_id)

    user_msg_entry = {
        "from": "user",
        "msg": req.message,
        "time": time.time()
    }
    user["chat_history"].append(user_msg_entry)

    bot_response = ask_bilge_logvian(req.message, user["chat_history"])

    bot_msg_entry = {
        "from": "bot",
        "msg": bot_response,
        "time": time.time()
    }
    user["chat_history"].append(bot_msg_entry)

    return {
        "response": bot_response,
        "user_id": req.user_id,
        "timestamp": time.time()
    }


@app.get("/api/user/{user_id}/progress")
async def get_user_progress(user_id: str):
    """Kullanıcı ilerlemesini getir"""
    user = ensure_user(user_id)
    return {
        "progress": {
            "level": user["level"],
            "total_xp": user["xp"],
            "total_coins": user["coins"],
            "next_level_xp": user["level"] * 100,
            "completed_tasks": user["completed_modules"],
            "skills": user["skills"]
        }
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Bilge Logvian Siber Güvenlik Akademisi (Simülasyon Modu) başlatılıyor...")
    print(f"🧠 Groq AI Durumu: {'✅ Bağlı' if client else '❌ Bağlı Değil'}")
    print("🔧 Docker'sız simülasyon modu aktif!")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
