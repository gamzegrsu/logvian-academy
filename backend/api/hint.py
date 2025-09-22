from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Frontend'in gönderdiği body
class HintRequest(BaseModel):
    user_id: str
    task_id: int

# Basit örnek ipuçları (gerçekte DB'den ya da tasks_data'dan çekebilirsin)
TASK_HINTS = {
    1: "SQL Injection için giriş formuna özel karakter denemeyi unutma.",
    2: "Stored XSS'te payload'ı kalıcı olarak saklanabilecek bir alana enjekte et.",
    3: "Hash cracking için önce hash algoritmasını tanı, sonra wordlist dene."
}

@router.post("/hint")g
async def get_hint(req: HintRequest):
    if req.task_id not in TASK_HINTS:
        raise HTTPException(status_code=404, detail="Bu görev için ipucu bulunamadı")

    # Normalde coin düşümü gibi bir mekanizma olur.
    # Şimdilik sabit değer dönelim:
    coins_left = 90

    return {
        "hint": TASK_HINTS[req.task_id],
        "coins_left": coins_left
    }
