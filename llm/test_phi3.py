from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_path = "./"  # modeli indirdiğin klasör (llm içinde çalışıyorsun zaten)

print("Tokenizer yükleniyor...")
tokenizer = AutoTokenizer.from_pretrained(model_path)

print("Model yükleniyor...")
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    device_map="auto",   # CPU’da çalışacak
    torch_dtype=torch.float32
)

# Kullanıcıdan prompt al
prompt = "Merhaba, ben bir siber güvenlik öğrencisiyim. Bana phishing saldırısını anlatır mısın?"

inputs = tokenizer(prompt, return_tensors="pt")

print("Cevap üretiliyor...")
outputs = model.generate(**inputs, max_new_tokens=200)

print("\n--- Modelin Cevabı ---")
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
