import os
import json
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Transformers import
try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    TF_AVAILABLE = True
except Exception:
    TF_AVAILABLE = False

app = FastAPI(title="LLM Server - Bilge Logvian")

# Config from environment
MODEL_NAME = os.getenv("MODEL_NAME", "microsoft/phi-3-mini-4k-instruct")
MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", "400"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.65"))
TOP_P = float(os.getenv("TOP_P", "0.92"))

LOCAL = {"loaded": False, "tokenizer": None, "model": None, "device": "cpu"}

class ChatRequest(BaseModel):
    message: str
    user_id: str = "anon"
    character: str = "Bilge Logvian"
    verbosity: str = "normal"  # "short" | "normal" | "detailed"

@app.on_event("startup")
def startup():
    if not TF_AVAILABLE:
        print("⚠️ transformers/torch paketleri kurulu değil; LLM çalışmayacak.")
        return

    try:
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"LLM yükleniyor: {MODEL_NAME} (device={device}, dtype={dtype})")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=dtype if device == "cuda" else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )

        if device == "cpu":
            model.to("cpu")

        LOCAL.update({
            "loaded": True,
            "tokenizer": tokenizer,
            "model": model,
            "device": device
        })
        print("✅ LLM yüklendi:", MODEL_NAME)
    except Exception as e:
        print("⚠️ LLM yüklenirken hata:", e)
        LOCAL["loaded"] = False

def build_prompt(character: str, message: str, verbosity: str = "normal") -> str:
    return f"""
Sen "{character}" adında deneyimli bir siber güvenlik öğretmenisin (Bilge Logvian).
Her yanıtta mutlaka şu bölümleri JSON formatında döndür:

{{
  "theory": "Konu özeti (2-4 cümle)",
  "answer": "Kullanıcının sorusuna açıklama ve örneklerle yanıt",
  "homework": ["1. ödev", "2. ödev"],
  "lab": ["adım 1", "adım 2"],
  "notes": "ek notlar"
}}

Kurallar:
- JSON dışında hiçbir şey yazma.
- Alanları boş bırakman gerekirse bile mutlaka bulunsun.
- verbosity = "{verbosity}" → "short" ise kısa cevap ver, "detailed" ise daha kapsamlı yaz.

Kullanıcının sorusu: "{message}"
Şimdi sadece JSON üret.
""".strip()

def try_parse_json(text: str):
    text_stripped = text.strip()
    try:
        return json.loads(text_stripped)
    except Exception:
        pass

    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end+1]
        try:
            return json.loads(candidate)
        except Exception:
            cleaned = re.sub(r",\s*}", "}", candidate)
            cleaned = re.sub(r",\s*]", "]", cleaned)
            try:
                return json.loads(cleaned)
            except Exception:
                return None
    return None

@app.post("/chat")
def chat(req: ChatRequest):
    if not LOCAL["loaded"]:
        raise HTTPException(status_code=503, detail="LLM yüklenmedi veya yükleme başarısız oldu.")

    tokenizer = LOCAL["tokenizer"]
    model = LOCAL["model"]

    prompt = build_prompt(req.character, req.message, req.verbosity)

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
    try:
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
    except Exception:
        inputs = {k: v.to("cpu") for k, v in inputs.items()}

    try:
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            do_sample=True,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.pad_token_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model üretim hatası: {e}")

    raw = tokenizer.decode(outputs[0], skip_special_tokens=True)
    raw_after = raw.split(prompt, 1)[-1].strip() if prompt in raw else raw.strip()

    parsed = try_parse_json(raw_after)
    if parsed:
        def ensure_list(v):
            if v is None:
                return []
            if isinstance(v, list):
                return v
            if isinstance(v, str):
                items = [ln.strip("-• \t") for ln in v.splitlines() if ln.strip()]
                return items if len(items) > 1 else [v.strip()]
            return [str(v)]

        return {
            "theory": str(parsed.get("theory", "")),
            "answer": str(parsed.get("answer", "")),
            "homework": ensure_list(parsed.get("homework", [])),
            "lab": ensure_list(parsed.get("lab", [])),
            "notes": str(parsed.get("notes", "")),
            "raw_model_text": raw_after
        }

    return {
        "theory": "",
        "answer": raw_after,
        "homework": [],
        "lab": [],
        "notes": "⚠️ Model çıktısı JSON parse edilemedi; ham metin 'answer' alanında.",
        "raw_model_text": raw_after
    }
