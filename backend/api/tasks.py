from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from core.tasks_data import TASKS

router = APIRouter()

class AnswerRequest(BaseModel):
    user_id: str
    answer: str

# Basit kullanıcı ilerleme store
USER_PROGRESS = {}

def default_user(user_id: str):
    return {
        "user_id": user_id,
        "xp": 0,
        "coins": 0,
        "completed_tasks": []
    }

def ensure_user(user_id: str):
    if user_id not in USER_PROGRESS:
        USER_PROGRESS[user_id] = default_user(user_id)
    else:
        user = USER_PROGRESS[user_id]
        for key, val in default_user(user_id).items():
            if key not in user:
                user[key] = val
    return USER_PROGRESS[user_id]

@router.get("/tasks")
async def get_tasks(user_id: str = Query("anon")):
    user = ensure_user(user_id)
    tasks_list = []
    for task in TASKS.values():
        tasks_list.append({
            **task,
            "xp": user.get("xp", 0),
            "coins": user.get("coins", 0),
            "completed": task.get("id") in user.get("completed_tasks", [])
        })
    return {"tasks": tasks_list}

@router.post("/tasks/{task_id}/answer")
async def check_answer(task_id: str, req: AnswerRequest):
    user = ensure_user(req.user_id)
    task = TASKS.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if req.answer.strip() == task["flag"]:
        user["xp"] += task.get("xp_reward", 50)
        user["coins"] += task.get("coin_reward", 10)
        if task_id not in user["completed_tasks"]:
            user["completed_tasks"].append(task_id)
        return {"correct": True, "message": "Doğru! Flag bulundu 🚀"}
    else:
        return {"correct": False, "message": "Yanlış flag, tekrar dene."}
