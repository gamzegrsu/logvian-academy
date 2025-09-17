import requests

res = requests.post("http://127.0.0.1:8001/chat", json={"message": "Wizard, bana phishing nedir anlat."})
print(res.json())
