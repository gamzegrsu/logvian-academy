# 🔮 Logvian Akademi - Siber Güvenlik Eğitim Platformu

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Hackathon](https://img.shields.io/badge/Hackathon-Winner-blue)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![Docker](https://img.shields.io/badge/Docker-Enabled-blue)

**Mistik bir üslupla siber güvenlik öğreten interaktif AI eğitmen platformu**

---

## 🏆 Hackathon Proje

**Logvian Akademi**, siber güvenlik eğitimini eğlenceli ve etkileşimli hale getiren, yapay zeka destekli bir öğrenme platformudur. Gerçek dünya senaryoları, canlı lablar ve mistik bir AI eğitmenle siber güvenlik becerilerinizi geliştirin. Logvian Akademi evreninde gerçek bir mentör Bilge Logvian , sana tüm detayları öğretecektir.

## ✨ Öne Çıkan Özellikler

- 🤖 **Bilge Logvian** - Mistik AI eğitmenle interaktif öğrenme
- 🧪 **Canlı Lablar** - Gerçek siber güvenlik ortamları
- 🎮 **Oyunlaştırılmış Eğitim** - XP, seviye ve ödül sistemi
- 🔐 **Gerçek Dünya Senaryoları** - Pratik odaklı eğitim içerikleri
- 🚀 **Tek Tıkla Lab Kurulumu** - Docker tabanlı hızlı dağıtım

## 🛠️ Teknoloji Stack'i

### Backend
- **Python 3.9+** - Temel programlama dili
- **FastAPI** - Yüksek performanslı web framework
- **Groq API** - Llama 3.3 70B açık kaynak AI modeli
- **Docker SDK** - Konteyner yönetimi
- **Uvicorn** - ASGI sunucusu

### Frontend
- **React.js** - Modern kullanıcı arayüzü
- **CSS3 & Animations** - Mistik arayüz tasarımı
- **WebSocket** - Gerçek zamanlı güncellemeler

### Lab Ortamları
- **Docker** - Konteynerizasyon
- **DVWA** (Damn Vulnerable Web App) - SQL Injection labı
- **Juice Shop** - XSS ve Web Güvenliği labı
- **Özel Hash Lab** - Hash kırma çalışmaları

## 🚀 Hızlı Kurulum

### Ön Koşullar
```bash
# Docker Desktop kurulu olmalı
# Python 3.9+ kurulu olmalı

git clone https://github.com/yourusername/logvian-academy.git
cd logvian-academy

python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# veya
.\.venv\Scripts\activate  # Windows

pip install -r requirements.txt

cp .env.example .env
# .env dosyasını düzenle:
# GROQ_API_KEY=your_groq_api_key_here
# MODEL_NAME=llama-3.3-70b-versatile


# Tüm labları docker-compose ile başlat
docker-compose up -d

# Veya tek tek başlat:
docker pull vulnerables/web-dvwa
docker pull bkimminich/juice-shop

cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

cd view
npm install
npm start
