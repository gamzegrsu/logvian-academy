#!/usr/bin/env python3
"""
🔮 Bilge Logvian — Siber Güvenlik Botu Test Scripti
HF Inference API, Groq API ve task_data modüllerini test eder.
"""

import os
import time
import json
import requests
from dotenv import load_dotenv
from groq import Groq

# --- Config ---
load_dotenv()


class BilgeLogvianTester:
    def __init__(self):
        self.results = []
        self.start_time = time.time()

        # API Key'leri yükle
        self.hf_token = os.getenv("HF_TOKEN")
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("MODEL_NAME", "llama3-70b-8192")

        # Clients
        self.groq_client = None
        if self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                self.results.append(("Groq Client", "✅ Başarılı", ""))
            except Exception as e:
                self.results.append(("Groq Client", "❌ Hata", str(e)))

    def print_header(self, text):
        print(f"\n{'=' * 60}")
        print(f"🔍 {text}")
        print(f"{'=' * 60}")

    def print_result(self, test_name, status, details=""):
        emoji = "✅" if status == "Başarılı" else "❌"
        print(f"{emoji} {test_name}: {status}")
        if details:
            print(f"   📝 {details}")
        self.results.append((test_name, status, details))

    def test_env_variables(self):
        """Ortam değişkenlerini test et"""
        self.print_header("1. Ortam Değişkenleri Testi")

        variables = {
            "HF_TOKEN": self.hf_token,
            "GROQ_API_KEY": self.groq_api_key,
            "MODEL_NAME": self.model_name
        }

        all_ok = True
        for name, value in variables.items():
            if value:
                self.print_result(f"{name}", "Başarılı", f"Değer: {value[:10]}...")
            else:
                self.print_result(f"{name}", "Eksik", "Ortam değişkeni bulunamadı")
                all_ok = False

        return all_ok

    def test_hf_inference_api(self):
        """Hugging Face Inference API testi"""
        self.print_header("2. Hugging Face Inference API Testi")

        if not self.hf_token:
            self.print_result("HF API Test", "Atlandı", "HF_TOKEN bulunamadı")
            return False

        api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {self.hf_token}"}

        test_prompt = "Merhaba! Sen bir siber güvenlik uzmanısın. SQL Injection nedir?"

        try:
            payload = {
                "inputs": test_prompt,
                "parameters": {
                    "max_new_tokens": 100,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }

            response = requests.post(api_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                generated_text = data[0].get('generated_text', 'No text generated')
                self.print_result("HF API Test", "Başarılı", f"Yanıt: {generated_text[:100]}...")
                return True
            else:
                self.print_result("HF API Test", "Hata", f"Status: {response.status_code}, Mesaj: {response.text}")
                return False

        except Exception as e:
            self.print_result("HF API Test", "Hata", str(e))
            return False

    def test_groq_api(self):
        """Groq API testi"""
        self.print_header("3. Groq API Testi")

        if not self.groq_client:
            self.print_result("Groq API Test", "Atlandı", "Groq client başlatılamadı")
            return False

        test_prompt = "Merhaba! Sen Bilge Logvian'sın. SQL Injection'ı mistik bir üslupla anlat."

        try:
            messages = [
                {
                    "role": "system",
                    "content": "Sen Bilge Logvian'sın. Mistik ve bilge bir siber güvenlik üstadısın."
                },
                {
                    "role": "user",
                    "content": test_prompt
                }
            ]

            start_time = time.time()
            completion = self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=150,
                timeout=30
            )
            end_time = time.time()

            response = completion.choices[0].message.content
            response_time = end_time - start_time

            self.print_result("Groq API Test", "Başarılı",
                              f"Yanıt süresi: {response_time:.2f}s\nYanıt: {response[:100]}...")
            return True

        except Exception as e:
            self.print_result("Groq API Test", "Hata", str(e))
            return False

    def test_task_data(self):
        """Task data modülünü test et"""
        self.print_header("4. Task Data Modülü Testi")

        try:
            # tasks_data.py'yı import et
            from tasks_data import modules, GENERAL_SAFETY

            module_count = len(modules)
            first_module = list(modules.values())[0] if modules else None

            if module_count > 0:
                self.print_result("Task Data Yükleme", "Başarılı",
                                  f"{module_count} modül yüklendi. İlk modül: {first_module['title']}")

                # Modül içeriğini kontrol et
                if 'labs' in first_module and first_module['labs']:
                    lab_count = len(first_module['labs'])
                    self.print_result("Modül Labları", "Başarılı", f"{lab_count} lab mevcut")
                else:
                    self.print_result("Modül Labları", "Uyarı", "Lab bulunamadı")

                return True
            else:
                self.print_result("Task Data", "Hata", "Modül bulunamadı")
                return False

        except ImportError as e:
            self.print_result("Task Data Import", "Hata", f"Import hatası: {e}")
            return False
        except Exception as e:
            self.print_result("Task Data", "Hata", str(e))
            return False

    def test_chat_function(self):
        """Sohbet fonksiyonunu test et"""
        self.print_header("5. Sohbet Fonksiyonu Testi")

        if not self.groq_client:
            self.print_result("Sohbet Testi", "Atlandı", "Groq client yok")
            return False

        test_messages = [
            "SQL Injection nedir?",
            "XSS nasıl önlenir?",
            "Bana siber güvenlik için tavsiye ver"
        ]

        successful_tests = 0

        for i, message in enumerate(test_messages, 1):
            try:
                messages = [
                    {
                        "role": "system",
                        "content": "Kısa ve öz cevap ver. Siber güvenlik uzmanısın."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ]

                completion = self.groq_client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=100,
                    timeout=20
                )

                response = completion.choices[0].message.content
                self.print_result(f"Sohbet Test {i}", "Başarılı", f"Soru: {message}\nYanıt: {response[:50]}...")
                successful_tests += 1

            except Exception as e:
                self.print_result(f"Sohbet Test {i}", "Hata", str(e))

        return successful_tests > 0

    def run_all_tests(self):
        """Tüm testleri çalıştır"""
        print("🔮 Bilge Logvian Test Senaryosu Başlatılıyor...")
        print("⏰ Başlangıç zamanı:", time.strftime("%Y-%m-%d %H:%M:%S"))

        tests = [
            self.test_env_variables,
            self.test_hf_inference_api,
            self.test_groq_api,
            self.test_task_data,
            self.test_chat_function
        ]

        test_results = []
        for test in tests:
            try:
                result = test()
                test_results.append(result)
            except Exception as e:
                self.print_result(test.__name__, "Hata", f"Test hatası: {e}")
                test_results.append(False)

        # Sonuçları özetle
        self.print_header("🎯 TEST SONUÇLARI")

        successful_tests = sum(test_results)
        total_tests = len(test_results)

        print(f"📊 Toplam Test: {total_tests}")
        print(f"✅ Başarılı: {successful_tests}")
        print(f"❌ Başarısız: {total_tests - successful_tests}")
        print(f"⏱️  Toplam Süre: {time.time() - self.start_time:.2f} saniye")

        # Detaylı sonuçlar
        print(f"\n📋 Detaylı Sonuçlar:")
        for test_name, status, details in self.results:
            emoji = "✅" if status == "Başarılı" else "❌"
            print(f"   {emoji} {test_name}: {status}")
            if details:
                print(f"      → {details}")

        # Öneriler
        print(f"\n💡 Öneriler:")
        if not self.hf_token:
            print("   - HF_TOKEN eksik. Hugging Face token eklemeyi düşün")
        if not self.groq_api_key:
            print("   - GROQ_API_KEY eksik. Groq'dan API key al")
        if successful_tests == total_tests:
            print("   - 🎉 Tüm testler başarılı! Sistem hazır.")
        else:
            print("   - ⚠️  Bazı testler başarısız. Logları kontrol et.")

        return all(test_results)


# --- Main ---
if __name__ == "__main__":
    tester = BilgeLogvianTester()
    success = tester.run_all_tests()

    # Çıkış kodu
    exit(0 if success else 1)