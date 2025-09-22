from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.lab_manager import start_lab_container, stop_lab_container, list_running_labs

router = APIRouter()

# --- Request modelleri ---
class StartLabRequest(BaseModel):
    user_id: str

class StopLabRequest(BaseModel):
    container_name: str

# --- Lab Başlat ---
@router.post("/lab/{task_id}/start")
async def start_lab(task_id: str, req: StartLabRequest):
    try:
        # task_id string olarak geliyor, lab_manager’da da string bekliyoruz
        result = start_lab_container(task_id, req.user_id)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Lab Durdur ---
@router.post("/lab/stop")
async def stop_lab(req: StopLabRequest):
    try:
        stopped = stop_lab_container(req.container_name)
        if not stopped:
            raise HTTPException(status_code=404, detail="Container bulunamadı")
        return {"stopped": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Çalışan Labları Listele ---
@router.get("/lab/running")
async def running_labs():
    try:
        return {"running": list_running_labs()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
