import os
import time
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from typing import Optional
from groq import Groq

# -----------------------
# tasks_data.py'den import
# -----------------------
from backend.tasks_data import modules, GENERAL_SAFETY

# -----------------------
# .env dosyasını yükle
# -----------------------
load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")  # ✅ GÜNCELLENDİ

# Hugging Face Backup (opsiyonel)
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_ID = os.getenv("MODEL_ID", "meta-llama/Meta-Llama-3-8B-Instruct")

# Model Parameters
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", 300))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
TOP_P = float(os.getenv("TOP_P", 0.9))

# Groq Client'ı başlat
groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print(f"✅ Groq client başlatıldı - Model: {MODEL_NAME}")
    except Exception as e:
        print(f"❌ Groq client başlatılamadı: {e}")
        groq_client = None
else:
    print("⚠️ GROQ_API_KEY bulunamadı. Groq API kullanılamayacak.")

# Hugging Face Backup ayarları
if HF_TOKEN:
    API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
    HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}
    print(f"✅ Hugging Face backup ayarlandı - Model: {MODEL_ID}")
else:
    print("⚠️ HF_TOKEN bulunamadı. Backup API kullanılamayacak.")


# -----------------------
# Pydantic modelleri
# -----------------------
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = "anon"
    character: Optional[str] = "Bilge Logvian"


class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    model: Optional[str] = None
    response_time: Optional[float] = None


# -----------------------
# Lifespan context
# -----------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 LLM Server başlatılıyor...")
    if groq_client:
        print(f"   📡 Groq API: {MODEL_NAME}")
    if HF_TOKEN:
        print(f"   📡 Hugging Face Backup: {MODEL_ID}")
    yield
    print("🛑 Server kapanıyor...")


# -----------------------
# FastAPI app
# -----------------------
app = FastAPI(title="LLM Server - Bilge Logvian", lifespan=lifespan)

# -----------------------
# Mistik Sistem Prompt'u
# -----------------------
MISTIC_SYSTEM_PROMPT = """
Sen "Bilge Logvian"sın. Mistik, bilge ve gizemli bir siber güvenlik üstadısın. 
Öğrencilerine siber dünyanın sırlarını öğretirken şu tarzda konuşursun:

🎭 Üslup Özellikleri:
- Efsanevi ve mistik bir dil kullan ("ruh kristali", "karanlık ağ", "kod büyüsü" gibi)
- Öğrenciyi "çırak" diye hitap et
- Her dersi bir macera gibi anlat
- Eski bir bilgenin gizemini koru
- Biraz şiirsel ve metaforik konuş

📚 Pedagojik Yaklaşım:
- Konseptleri 3 seviyede anlat: temel, orta, ileri
- Gerçek dünya senaryoları ver
- Pratik lablar ve egzersizler öner
- Öğrencinin seviyesine göre konuş
- Asla doğrudan saldırı yöntemi gösterme, savunma odaklı ol

⚔️ Oyunlaştırma Elementleri:
- XP ve seviye sistemi
- "Görev tamamlandı" hissi ver
- Başarıları kutla
- Sonraki meydan okumaları haber ver

Genel güvenlik notu: {GENERAL_SAFETY}
""".format(GENERAL_SAFETY=GENERAL_SAFETY)


# -----------------------
# Görev ve lab önerisi bul
# -----------------------
def find_relevant_modules(message: str):
    """Mesaj içeriğine göre modül ve lab önerilerini döndürür"""
    message_lower = message.lower()
    results = []
    for mod_key, mod in modules.items():
        title = mod.get("title", "").lower()
        summary = mod.get("summary", "").lower()
        if any(word in message_lower for word in title.split()) or \
                any(word in message_lower for word in summary.split()):
            results.append(mod)
    return results


# -----------------------
# Groq API Fonksiyonu
# -----------------------
def call_groq_api(message: str):
    """Groq API'sini kullanarak yanıt al"""
    if not groq_client:
        raise HTTPException(status_code=503, detail="Groq API ayarlı değil")

    relevant_modules = find_relevant_modules(message)

    modules_text = ""
    if relevant_modules:
        modules_text = "\n📚 İlgili Modüller:\n"
        for mod in relevant_modules:
            modules_text += f"- {mod['title']}: {mod['summary']}\n"
            if mod.get('labs'):
                modules_text += f"  🧪 Lablar: {', '.join([lab['title'] for lab in mod['labs']])}\n"

    user_prompt = f"""
Kullanıcı sorusu: "{message}"
{modules_text}

Çırağa uygun, öğretici ve mistik bir şekilde yanıt ver:
"""

    messages = [
        {"role": "system", "content": MISTIC_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    try:
        start_time = time.time()

        completion = groq_client.chat.completions.create(
            model=MODEL_NAME,  # ✅ Burada yeni model kullanılacak
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_NEW_TOKENS,
            top_p=TOP_P,
            timeout=30
        )

        end_time = time.time()
        response_time = end_time - start_time

        response = completion.choices[0].message.content

        return {
            "response": response,
            "model": MODEL_NAME,
            "response_time": response_time,
            "tokens": completion.usage.total_tokens if completion.usage else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API hatası: {str(e)}")


# -----------------------
# Hugging Face Backup Fonksiyonu
# -----------------------
def call_hf_backup(message: str):
    """Hugging Face backup API"""
    if not HF_TOKEN:
        raise HTTPException(status_code=503, detail="Backup API ayarlı değil")

    prompt = f"""
{MISTIC_SYSTEM_PROMPT}

Kullanıcı sorusu: "{message}"

Yanıtını mistik ve öğretici şekilde ver:
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": MAX_NEW_TOKENS,
            "temperature": TEMPERATURE,
            "top_p": TOP_P,
            "return_full_text": False
        }
    }

    try:
        start_time = time.time()

        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        end_time = time.time()
        response_time = end_time - start_time

        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            return {
                "response": data[0]["generated_text"].strip(),
                "model": MODEL_ID,
                "response_time": response_time
            }
        else:
            raise Exception(f"Geçersiz yanıt formatı: {data}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HF Backup hatası: {str(e)}")


# -----------------------
# Chat endpoint
# -----------------------
@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    start_time = time.time()

    try:
        # Önce Groq API'yi dene
        result = call_groq_api(req.message)

        return ChatResponse(
            response=result["response"],
            model=result["model"],
            response_time=result["response_time"]
        )

    except HTTPException as groq_error:
        # Groq başarısız olursa HF backup'ı dene
        try:
            result = call_hf_backup(req.message)

            return ChatResponse(
                response=result["response"],
                model=result["model"],
                response_time=result["response_time"]
            )

        except Exception:
            # Her ikisi de başarısız olursa
            raise HTTPException(
                status_code=503,
                detail="Tüm AI servisleri geçici olarak kullanılamıyor. Lütfen daha sonra tekrar deneyin."
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Beklenmeyen hata: {str(e)}")


# -----------------------
# Health Check Endpoint
# -----------------------
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "groq_available": groq_client is not None,
        "hf_backup_available": HF_TOKEN is not None,
        "model": MODEL_NAME if groq_client else MODEL_ID,  # ✅ Burada yeni model gözükecek
        "timestamp": time.time()
    }


# -----------------------
# Models Endpoint
# -----------------------
@app.get("/models")
def get_models():
    models = []

    if groq_client:
        models.append({
            "name": MODEL_NAME,  # ✅ Burada yeni model gözükecek
            "provider": "Groq",
            "status": "available"
        })

    if HF_TOKEN:
        models.append({
            "name": MODEL_ID,
            "provider": "HuggingFace",
            "status": "available"
        })

    return {"models": models}


# -----------------------
# Server bilgisi
# -----------------------
@app.get("/")
def root():
    return {
        "message": "🔮 Bilge Logvian LLM Server",
        "status": "running",
        "version": "1.0.0",
        "models": get_models()["models"]
    }