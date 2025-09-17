from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tasks_data import tasks
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Tigin – Mistik Siber Güvenlik Chatbotu")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # development için her yerden izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Answer(BaseModel):
    answer: str

# Görevleri listele
@app.get("/tasks")
def get_tasks():
    return list(tasks.values())

# Tek görev getir
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Görev bulunamadı.")
    return tasks[task_id]

# Cevap kontrol et
@app.post("/tasks/{task_id}/answer")
def check_answer(task_id: int, user_answer: Answer):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Görev bulunamadı.")

    task = tasks[task_id]
    normalized_answer = user_answer.answer.lower().replace(" ", "").replace('"', "'")

    # Doğru mu kontrol et
    for dogru in task["dogru_cevaplar"]:
        if dogru.lower().replace(" ", "").replace('"', "'") in normalized_answer:
            return {
                "sonuc": "✅ Doğru",
                "feedback": task["feedback_dogru"],
                "sonraki_gorev": task["sonraki_gorev"]
            }

    # Yanlışsa ipucu döndür
    return {
        "sonuc": "❌ Yanlış",
        "feedback": task["feedback_yanlis"][0]
    }
