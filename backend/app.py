from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Modeli yükle (Phi-3-mini)
model_path = "../llm"  # modeli nereye indirdiysen ona göre ayarla
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float32,
    device_map="cpu"  # sadece CPU kullanıyoruz
)

# FastAPI uygulaması
app = FastAPI()

# Kullanıcı mesaj formatı
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    prompt = f"Sen Bilge Wizard'sın. Kullanıcıya siber güvenlik öğretmeni gibi davran. Açıkla, örnek ver ve gerekirse ödev ver.\n\nKullanıcı: {req.message}\nWizard:"

    inputs = tokenizer(prompt, return_tensors="pt").to("cpu")
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.7,
        top_p=0.9
    )

    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Prompt'un başını kesip sadece cevabı alalım
    if "Wizard:" in reply:
        reply = reply.split("Wizard:")[-1].strip()

    return {"reply": reply}
