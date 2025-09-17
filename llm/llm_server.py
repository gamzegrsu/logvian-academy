from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI()

# Modeli CPU'da yükle
model_path = "./"  # indirilen model buradaysa
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float32,  # CPU için float32
    device_map=None  # GPU yoksa auto yerine None
).to("cpu")


# Karşılama endpointi
@app.get("/")
def home():
    return {"message": "LLM API çalışıyor! POST /chat ile mesaj gönder."}


# Chat endpointi
class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(request: ChatRequest):
    inputs = tokenizer(request.message, return_tensors="pt").to("cpu")
    outputs = model.generate(**inputs, max_new_tokens=200)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"reply": response}
