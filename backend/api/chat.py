# backend/api/chat.py
import os
import time
import json
import re
import asyncio
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from groq import Groq
import httpx

# --- Load environment variables ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")
HF_TOKEN = os.getenv("HF_TOKEN")  # Backup için

# Groq client'ını başlat
groq_client = None
if GROQ_API_KEY:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("✅ Groq client başarıyla başlatıldı")
    except Exception as e:
        print(f"❌ Groq client başlatılamadı: {e}")
        groq_client = None
else:
    print("⚠️ GROQ_API_KEY bulunamadı. Groq API kullanılamayacak.")

# HF API backup için
API_URL = os.getenv("API_URL")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

router = APIRouter()

# --- Mistik Sistem Prompt'u ---
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

Şimdi çırağının sorusuna yanıt ver:
"""

# --- Hızlı Cevaplar ---
QUICK_MAP = {
    "sql injection": "🔮 SQL Injection: Veritabanı ruhunun sızması... Kullanıcı girdisini sorguya direkt eklemekle oluşur. ' OR '1'='1 gibi büyülerle koruma kalkanlarını aşabilirsin.",
    "xss": "🔮 XSS: Ayna illüzyonu... Tarayıcıda script çalıştırmaya izin veren açıklık. <script>alert('X')</script> gibi büyülerle aynalara sızılır.",
    "hash": "🔮 Hash Kırma: Runik şifre çözme... Kadim hashleri wordlist ile çözmek. password gibi zayıf büyüler kolay kırılır.",
    "nasılsın": "🔮 İyiyim çırak! 🤗 Mistik dünyada siber sırları öğretmekle meşgulüm. Sen nasılsın?",
    "merhaba": "🔮 Selamlar çırak! 🧙‍♂️ Siber dünyanın derinliklerinde kaybolmaya hazır mısın?",
    "teşekkür": "🔮 Rica ederim çırak! 🎯 Yolun açık, büyün güçlü olsun!",
    "yardım": "🔮 Yardım elime uzanıyor çırak! 🪄 SQL Injection, XSS, Hash Cracking gibi konularda rehberlik isteyebilirsin."
}


def quick_answer(message: str) -> Optional[str]:
    low = message.lower()
    for k, v in QUICK_MAP.items():
        if k in low:
            return v
    return None


# --- Groq API Fonksiyonu ---
async def call_groq_api(user_message: str, chat_history: list = None) -> Dict[str, Any]:
    """Groq API'sini kullanarak yanıt al"""

    if not groq_client:
        raise HTTPException(status_code=503, detail="Groq API ayarlı değil. GROQ_API_KEY eksik.")

    messages = [{"role": "system", "content": MISTIC_SYSTEM_PROMPT}]

    # Sohbet geçmişini ekle
    if chat_history:
        for msg in chat_history[-6:]:  # Son 3 diyaloğu al
            if msg["role"] == "user":
                messages.append({"role": "user", "content": msg["content"]})
            else:
                messages.append({"role": "assistant", "content": msg["content"]})

    messages.append({"role": "user", "content": user_message})

    try:
        start_time = time.time()

        completion = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
            timeout=30
        )

        end_time = time.time()
        response_time = end_time - start_time

        response = completion.choices[0].message.content

        return {
            "response": response,
            "meta": {
                "model": MODEL_NAME,
                "response_time": f"{response_time:.2f}s",
                "tokens": completion.usage.total_tokens if completion.usage else None
            }
        }

    except Exception as e:
        print(f"❌ Groq API hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Groq API hatası: {str(e)}")


# --- HF Backup API (Groq olmazsa) ---
async def call_hf_api_backup(prompt: str) -> Dict[str, Any]:
    """Groq çalışmazsa Hugging Face backup"""

    if not HF_TOKEN or not API_URL:
        raise HTTPException(status_code=503, detail="Backup API de ayarlı değil.")

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(API_URL, headers=HEADERS, json=payload)
            response.raise_for_status()
            data = response.json()

            raw_text = ""
            if isinstance(data, list) and data and isinstance(data[0], dict):
                raw_text = data[0].get("generated_text", "")
            elif isinstance(data, dict):
                raw_text = data.get("generated_text", "")

            return {"response": raw_text, "meta": {"source": "hf_backup"}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HF Backup hatası: {str(e)}")


# --- Pydantic Modeller ---
class ChatRequest(BaseModel):
    user_id: Optional[str] = "anon"
    message: str
    chat_history: Optional[list] = []


class ChatResponse(BaseModel):
    response: str
    meta: Dict[str, Any]
    user_id: str


# --- Ana Chat Endpoint'i ---
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    🔮 Bilge Logvian ile sohbet et

    Args:
        req: ChatRequest with user message and optional history

    Returns:
        Mistik siber güvenlik yanıtı
    """

    # Hızlı cevap kontrolü
    qa = quick_answer(req.message)
    if qa:
        return ChatResponse(
            response=qa,
            meta={"source": "quick", "model": "quick_map"},
            user_id=req.user_id
        )

    # Özel komutlar
    low_msg = req.message.lower()
    if low_msg.startswith(("/yardım", "/help")):
        help_text = """
        🔮 **Bilge Logvian Komutları:**
        /yardım - Bu yardım mesajını göster
        /konular - Öğrenebileceğin siber güvenlik konuları
        /seviye - Mevcut seviyeni ve XP'ni göster
        /görevler - Aktif görevleri listele

        💡 **Örnek Sorular:**
        - SQL Injection nedir?
        - XSS nasıl önlenir?
        - Hash cracking nasıl çalışır?
        - Bana siber güvenlik temellerini öğret
        """
        return ChatResponse(
            response=help_text,
            meta={"source": "command", "command": "help"},
            user_id=req.user_id
        )

    elif low_msg.startswith(("/konular", "/topics")):
        topics_text = """
        📚 **Öğrenebileceğin Konular:**

        🛡️ **Temel Seviye:**
        - SQL Injection (Ruh Kristali Çatlatma)
        - XSS (Ayna İllüzyonu)
        - CSRF (İzinlerin Fısıltısı)

        ⚔️ **Orta Seviye:**
        - Hash Cracking (Runik Şifre Çözme)
        - Directory Traversal (Yolun Ötesine Bak)
        - Command Injection (Büyülü Komutlar)

        🧙‍♂️ **İleri Seviye:**
        - Network Security (Ağ Büyüsü)
        - Cryptography (Kadim Şifreleme)
        - Reverse Engineering (Büyünün Anatomisi)
        """
        return ChatResponse(
            response=topics_text,
            meta={"source": "command", "command": "topics"},
            user_id=req.user_id
        )

    try:
        # Önce Groq API'yi dene
        result = await call_groq_api(req.message, req.chat_history)

        return ChatResponse(
            response=result["response"],
            meta=result["meta"],
            user_id=req.user_id
        )

    except HTTPException as groq_error:
        # Groq başarısız olursa HF backup'ı dene
        try:
            prompt = f"""
            Sen 'Bilge Logvian'sın. Mistik bir siber güvenlik öğretmenisin.
            Kullanıcıya şu soruya yanıt ver: "{req.message}"

            Yanıtın:
            - Mistik ve efsanevi bir üslupta olsun
            - Öğretici ve pedagojik olsun
            - Türkçe yanıt ver
            - Kısa ve öz olsun (max 200 kelime)
            """

            backup_result = await call_hf_api_backup(prompt)

            return ChatResponse(
                response=backup_result["response"],
                meta={**backup_result["meta"], "fallback": True},
                user_id=req.user_id
            )

        except Exception:
            # Her ikisi de başarısız olursa
            raise HTTPException(
                status_code=503,
                detail="Tüm AI servisleri geçici olarak kullanılamıyor. Lütfen daha sonra tekrar deneyin."
            )

    except Exception as e:
        print(f"❌ Beklenmeyen chat hatası: {e}")
        raise HTTPException(status_code=500, detail=f"Beklenmeyen hata: {str(e)}")


# --- Health Check Endpoint ---
@router.get("/health")
async def health_check():
    """API sağlık durumunu kontrol et"""

    status = {
        "groq_ready": groq_client is not None,
        "hf_backup_ready": bool(HF_TOKEN and API_URL),
        "model": MODEL_NAME,
        "timestamp": time.time(),
        "status": "healthy" if groq_client or HF_TOKEN else "degraded"
    }

    return status


# --- Models Endpoint ---
@router.get("/models")
async def available_models():
    """Mevcut modelleri listele"""

    models = []

    if groq_client:
        models.append({
            "name": MODEL_NAME,
            "provider": "Groq",
            "status": "available"
        })

    if HF_TOKEN and API_URL:
        models.append({
            "name": "HuggingFace",
            "provider": "HuggingFace",
            "status": "available"
        })

    return {"models": models}