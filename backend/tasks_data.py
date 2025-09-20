# backend/tasks_data.py
# Bilge Logvian - Pedagojik, çok adımlı siber güvenlik modülleri
# Dil: Türkçe (öğretici + hafif oyunlaştırılmış Bilge Logvian üslubu)
# NOT: Tüm lab'lar SADECE izole eğitim/CTF ortamlarında çalıştırılmalıdır.
#       İzinsiz test yasa dışıdır.

modules = {
    "sql_injection": {
        "id": "sql_injection",
        "lab": "sql_injection",
        "flag": "FLAG{SQLI_MASTER}",
        "title": "SQL Injection — Ruh Kristali Çatlatma",
        "summary": "Veritabanı sorgularına kötü amaçlı veri enjekte ederek yetkisiz erişim/çıktı elde etme teknikleri.",
        "difficulty": "easy",
        "estimated_minutes": 25,
        "learning_objectives": [
            "SQL sorgularının temel yapısını anlamak",
            "Union/Error/Blind SQLi türlerini ayırt etmek",
            "Basit authentication bypass gerçekleştirmek (simülasyon)",
            "Parametrized queries ile korunmayı uygulamak"
        ],
        "theory": [
            "SQL Injection, uygulamanın kullanıcı girdisini sorgu metnine doğrudan eklediği durumlarda ortaya çıkar.",
            "Hazır ifadeler (prepared statements) ve parametrized queries saldırıyı önlemek için temel savunmadır.",
            "Union, error ve blind teknikleri farklı senaryolarda veri sızdırmak için kullanılır."
        ],
        "mechanisms": {
            "union_based": "Sorgu sonucunu genişletmek için UNION kullanma; ek kolonlar çekme.",
            "error_based": "Hata mesajlarından bilgi sızdırma (ör. syntax hatasıyla veri çıkarımı).",
            "blind_sqli": "Doğrudan çıktı yoksa boolean/time-based testlerle veri çıkarma."
        },
        "detection_and_monitoring": [
            "Anormal uzun/malform edilmiş sorgu parametreleri",
            "DB hata mesajlarının uygulama loglarında görünmesi",
            "Tekrarlayan benzer payload biçimleri ve WAF tetiklemeleri",
            "Zaman tabanlı saldırılarda uygulama gecikmeleri"
        ],
        "prevention": [
            "Prepared statements / parametrized queries",
            "ORM güvenli kullanım (SQL string birleştirmeyi engelle)",
            "Input validation + allowlist",
            "Minimum DB izinleri ve hataların kullanıcıya gösterilmemesi"
        ],
        "labs": [
            {
                "id": "sqli-1-auth-bypass",
                "title": "Login Bypass (Temel)",
                "difficulty": "easy",
                "estimated_minutes": 10,
                "goal": "Basit login formunda authentication bypass simülasyonu ile flag al.",
                "environment": "İzole Flask uygulaması (login endpoint).",
                "steps": [
                    "1) Lab sayfasını aç (login formu).",
                    "2) Username alanına şu payload'u gir: ' OR '1'='1 -- (numerik/işaretleme laboratuvara uyarlanmış).",
                    "3) Parola bölümüne rastgele bir şey gir ve gönder.",
                    "4) Eğer uygulama doğrudan string birleştirme yapıyorsa giriş başarılı olur ve flag gösterilir."
                ],
                "hints": [
                    "Kısa payloadlar deneyin: `' OR '1'='1`",
                    "Yorum işaretleri (`--`, `#`) ile sorgunun kalanını iptal etmeyi deneyin.",
                    "Formun POST payload yapısını tarayıcı geliştirici araçlarında inceleyin."
                ],
                "expected_result": "Authentication bypass — 'welcome admin' veya flag içeren sayfa görünür.",
                "solution_explanation": (
                    "Çoğu tehlikeli kod şu şekildedir:\n"
                    "  sql = \"SELECT * FROM users WHERE username='\" + username + \"' AND password='\" + password + \"'\"\n"
                    "Payload `admin' OR '1'='1` sorguyu `WHERE username='admin' OR '1'='1' AND password='...'` yapar ve doğrulama true döner."
                ),
                "safety_note": "Bu lab izole bir simülasyondur. Gerçek uygulama testleri için mutlaka izin alın."
            },
            {
                "id": "sqli-2-blind-boolean",
                "title": "Blind SQLi — Boolean-based",
                "difficulty": "medium",
                "estimated_minutes": 25,
                "goal": "Çıktı alamıyorsak boolean testleriyle bilgi çıkarımını öğren.",
                "environment": "Parametre alan bir endpoint (ör. /product?id=10) — çıktı yok ama davranış değişiyor.",
                "steps": [
                    "1) `id=10 AND 1=1` ve `id=10 AND 1=2` gibi varyasyonları dene; sayfa davranışını karşılaştır.",
                    "2) `id=10 AND SUBSTRING((SELECT database()),1,1)='a'` gibi testlerle karakterleri parça parça test et.",
                    "3) Time-based: `id=10 AND IF(condition, SLEEP(3), 0)` ile gecikmeye bak."
                ],
                "hints": [
                    "Sayfa çıktısının uzunluğunu, error veya redirect’i dikkatle izle.",
                    "Time-based blind için zaman farkını ölç."
                ],
                "expected_result": "Doğru karakterlerde sayfa davranışı veya gecikme değişir; veritabanı bilgisi parça parça çıkarılabilir.",
                "solution_explanation": "Boolean/time based testlerle veriyi tek tek doğrulayarak çıkarma yapılır.",
                "safety_note": "Blind teknikler gerçek sistemlerde yüksek risklidir; eğitimde izolasyonu kullanın."
            },
            {
                "id": "sqli-3-union-data-extract",
                "title": "Union-based Data Extraction (Advanced)",
                "difficulty": "hard",
                "estimated_minutes": 45,
                "goal": "UNION SELECT kullanarak tablo/kolon isimlerini ve veriyi çıkarmak.",
                "environment": "CONCAT/NULL testleriyle kolon sayısı belirlenebilen endpoint.",
                "steps": [
                    "1) İlk olarak ORDER BY veya UNION SELECT NULL,... ile kaç kolon döndüğünü öğren.",
                    "2) Doğru kolon sayısını bulduktan sonra `UNION SELECT column1,column2 FROM users` deneyin.",
                    "3) Kolon tiplerini (string/int) ayarlayarak çıktıyı görün."
                ],
                "hints": [
                    "ORDER BY ile sayıyı test etmek: `ORDER BY 1..n`",
                    "NULL testleri ile hangi kolonlar string bekliyor kontrol edilir."
                ],
                "expected_result": "Kullanıcı tablolarından veri çıkışı alınır.",
                "solution_explanation": "Union yöntemleri ile hedef veri ekrana getirilebilir.",
                "safety_note": "İleri seviye teknikler sadece laboratuvar ortamında uygulanmalıdır."
            }
        ],
        "quizzes": [
            {"q":"SQL Injection nedir?","a":"Kullanıcı girdilerini sorguya ekleyerek sorgunun yapısını değiştirme tekniğidir.","explanation":"Parametreleri sorgudan ayrı tutmamak asıl nedendir."},
            {"q":"Prepared statement nasıl korur?","a":"Parametreleri sorgudan ayrı tutar; payload sorgu yapısını değiştiremez.","explanation":"Placeholder kullanımı ve prepared statement örnekleri gösterilir."}
        ],
        "resources": [
            {"title":"OWASP SQL Injection","url":"https://owasp.org/www-community/attacks/SQL_Injection"},
            {"title":"SQLMap (araç)","url":"https://sqlmap.org"}
        ],
        "notes": "Lab'ları yalnızca izole ortamda çalıştırın; izinsiz test yasaktır."
    },

    "xss_stored": {
        "id": "xss_stored",
        "lab": "xss_stored",
        "flag": "FLAG{XSS_HERO}",
        "title": "Cross-Site Scripting — Ayna İllüzyonu (Stored)",
        "summary": "Kötü amaçlı JavaScript kodunun kurban tarayıcıda çalıştırılması (stored XSS).",
        "difficulty": "easy",
        "estimated_minutes": 20,
        "learning_objectives": [
            "XSS türlerini ayırt etmek (stored, reflected, DOM-based)",
            "Payload mantığını anlamak (contextual escaping)",
            "Output-escaping ve Content Security Policy ile korunma"
        ],
        "theory": [
            "Stored XSS, veritabanına kaydedilen kötü içeriklerin başka kullanıcıların tarayıcısında çalıştırılmasıdır.",
            "Korunma: output encoding, CSP, input validation değil; output-side sanitization en kritik adımdır."
        ],
        "mechanisms": {
            "stored": "Kötü kod sunucuya kaydedilir ve başka kullanıcılar görüntülediğinde çalışır.",
            "reflected": "Kötü içerik doğrudan isteğe yansıtılır (URL param vs).",
            "dom_based": "Tüm atama tarayıcıda JavaScript ile yapılır."
        },
        "detection_and_monitoring": [
            "Kullanıcı tarafından sağlanan içeriklerin HTML/JS çıktılarında beklenmedik script etiketleri",
            "WAF loglarında sıkça script veya on* event pattern'ları"
        ],
        "prevention": [
            "Output escaping/encoding (HTML encode, JS encode, attribute encode)",
            "Content Security Policy (CSP) ile inline scriptleri engelle",
            "Input allowlist ve uzunluk limitleri"
        ],
        "labs": [
            {
                "id":"xss-1-stored-basic",
                "title":"Stored XSS - Basit",
                "difficulty":"easy",
                "estimated_minutes":15,
                "goal":"Yorum alanına basit script ekleyerek payload çalıştır ve flag al.",
                "environment":"İzole Flask yorum uygulaması (yorumlar veritabanında tutulur).",
                "steps":[
                    "1) Yorum formunu aç.",
                    "2) Yorum alanına `<script>alert('X')</script>` gibi basit payload ekle.",
                    "3) Sayfayı başka bir kullanıcı / yeni sekmede aç ve payload'un çalıştığını gözlemle.",
                    "4) Payload çalışınca flag görünür."
                ],
                "hints":[
                    "Script taglerini doğrudan deneyin: `<script>alert(1)</script>`",
                    "Bazı uygulamalar script etiketlerini filtreler; farklı kontekstlerde (img onerror) deneyin."
                ],
                "expected_result":"Sayfa yüklendiğinde payload çalışır ve flag gösterilir.",
                "solution_explanation":"Uygulama yorumları HTML-escape etmediği için tarayıcı scriptleri çalıştırır.",
                "safety_note":"XSS payloadları gerçek sitelerde veri çalma/oturum çalma gibi tehlikeli sonuçlar doğurur; sadece izole lab kullanın."
            },
            {
                "id":"xss-2-advanced-persistence",
                "title":"Stored XSS — Persistence & Escaping",
                "difficulty":"medium",
                "estimated_minutes":30,
                "goal":"Filtreleri atlatıp payload'u kalıcı hale getirmek; output escaping farklarını gözlemek.",
                "steps":[
                    "1) İlk yorum denemesinde filtrelenme varsa HTML entity encode davranışını gözlemle.",
                    "2) Farklı kontekstlere payload yerleştir (attribute, URL, script).",
                    "3) Çalışan payload ile flag çıkar."
                ],
                "hints":[
                    "Event handler kullanımı (`onerror`) img tag ile denenebilir.",
                    "URL context'inde `javascript:` protokolü kontrol edilmelidir."
                ],
                "expected_result":"Kalıcı payload ile başka sayfa ziyaretlerinde script tetiklenir.",
                "solution_explanation":"Farklı kontekstlerde farklı kaçış/filtreleme davranışları vardır; doğru kontekste payload bulunursa çalışır.",
                "safety_note":"Gerçek kullanıcı verileriyle kesinlikle test etmeyin."
            }
        ],
        "quizzes":[
            {"q":"Stored XSS ile ne tehlike oluşur?","a":"Başka kullanıcıların tarayıcısında kötü JS çalıştırılabilir; çerez/oturum çalınabilir."},
            {"q":"XSS'ten korunmak için en etkili yöntem nedir?","a":"Output-side encoding (contextual escaping) ve CSP kombinasyonu."}
        ],
        "resources":[
            {"title":"OWASP XSS","url":"https://owasp.org/www-community/attacks/xss/"},
            {"title":"CSP Guide","url":"https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP"}
        ],
        "notes":"XSS lab'ları tarayıcı tabanlıdır; lab'ı izole edin ve gerçek kullanıcı verileri kullanmayın."
    },

    "hash_cracking": {
        "id": "hash_cracking",
        "lab": "hash_crack",
        "flag": "FLAG{HASH_BREAKER}",
        "title": "Hash Cracking — Runik Parçaları Çözme",
        "summary": "Hash fonksiyonları, kırılabilirlikleri ve sözlük saldırıları ile pratik yapılır.",
        "difficulty": "medium",
        "estimated_minutes": 30,
        "learning_objectives": [
            "Hash fonksiyonlarının özelliklerini anlamak (tek yönlü, çakışma vs.)",
            "Sözlük ve brute-force saldırıları arasındaki farkı öğrenmek",
            "Hashcat/john gibi araçların temel kullanımını görmek"
        ],
        "theory": [
            "Hash fonksiyonları tek yönlüdür fakat zayıf parolalar sözlük saldırıları ile kırılabilir.",
            "Salt kullanımı, hashing iterasyonları ve güçlü algoritmalar korunma yöntemlerindendir."
        ],
        "mechanisms": {
            "dictionary_attack": "Hazır kelime listesi ile hash'leri karşılaştırma.",
            "brute_force": "Tüm olası kombinasyonları deneme (zaman alır).",
            "rainbow_tables": "Önceden hesaplanmış hash-tablosu kullanma (modern korumalar salt ile bunu etkisizleştirir)."
        },
        "detection_and_monitoring": [
            "Tekrarlayan başarısız giriş denemeleri (rate limit koyun).",
            "Anormal hash çözme trafiği veya parola deneme hızları."
        ],
        "prevention": [
            "Salt + güçlü hashing (bcrypt/argon2) kullanımı",
            "Rate limiting ve account lockout politikaları",
            "Kullanıcı eğitimleri ile güçlü parola gereksinimleri"
        ],
        "labs": [
            {
                "id":"hash-1-basic",
                "title":"Hash Crack — Basit Sözlük",
                "difficulty":"easy",
                "estimated_minutes":15,
                "goal":"Verilen SHA1 hash'in plaintext'ini bulun ve flag alın.",
                "environment":"Basit API: /hash döner -> hash; /submit ile parola testi yapılır.",
                "steps":[
                    "1) /hash endpoint'ini çağır ve hash değerini al.",
                    "2) Küçük bir wordlist kullanarak hash'i doğrula (online veya lokal araç).",
                    "3) Doğru parola ile /submit çağrısında flag dönecek."
                ],
                "hints":[
                    "Hash: 5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8 (örnek) — common listleri dene.",
                    "Online hash-cracker kısa sürede yardımcı olabilir."
                ],
                "expected_result":"Doğru parola ile flag dönülür.",
                "solution_explanation":"Veri setindeki parola basit olduğu için sözlük ile eşleşir.",
                "safety_note":"Gerçek kullanıcı hash'leriyle deney yapmayın; sadece lab içindeki örnekleri kullanın."
            },
            {
                "id":"hash-2-advanced",
                "title":"Hash Crack — Salting & Iteration",
                "difficulty":"medium",
                "estimated_minutes":35,
                "goal":"Salt ve iteration uygulanan hashlerin kırılmasının zorlaştırılmasını öğren.",
                "steps":[
                    "1) Salt kullanılmış hash örneklerini gözlemle.",
                    "2) Salt'ın kırma süresine etkisini not et.",
                    "3) Güçlü hashing stratejilerini uygulayın (argon2/bcrypt)."
                ],
                "hints":["Salt, aynı parolanın farklı hashler üretmesini sağlar."],
                "expected_result":"Salt ve iteration uygulandığında sözlük saldırısının başarısız olacağını gözlemleyeceksiniz.",
                "solution_explanation":"Salt+iteration modern korumalardır; parola politikalarıyla birlikte kullanın.",
                "safety_note":"Gerçek kullanıcı verisini asla kullanmayın."
            }
        ],
        "quizzes":[
            {"q":"Salt ne işe yarar?","a":"Aynı parolaya farklı hash değeri verir; rainbow table etkisini azaltır."},
            {"q":"Argon2 neden tercih edilir?","a":"Memory-hard olması sayesinde brute-force maliyetini artırır."}
        ],
        "resources":[
            {"title":"Hashcat Docs","url":"https://hashcat.net/hashcat/"},
            {"title":"OWASP Password Storage Cheat Sheet","url":"https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html"}
        ],
        "notes":"Hash kırma lab'ları CPU/GPU gerektirebilir; basit örnekler ile demo yapın."
    },

    "csrf": {
        "id": "csrf",
        "lab": "csrf_demo",
        "flag": "FLAG{CSRF_GUARDIAN}",
        "title": "CSRF — İzinlerin Fısıltısı",
        "summary": "Cross-Site Request Forgery: kurbanın tarayıcısını kullanarak yetkili işlemler gerçekleştirme.",
        "difficulty": "medium",
        "estimated_minutes": 20,
        "learning_objectives": [
            "CSRF attack mekanizmasını anlamak",
            "State-changing request'lerde CSRF token kullanmanın önemini öğrenmek",
            "SameSite cookie politikası ve header bazlı önlemleri öğrenmek"
        ],
        "theory": [
            "CSRF saldırısı, kullanıcının oturumu açıkken başka bir siteden yetki gerektiren isteğin tetiklenmesiyle çalışır.",
            "Korunma: CSRF token'ları, SameSite cookie ve header kontrolleri."
        ],
        "labs":[
            {
                "id":"csrf-1-simple",
                "title":"CSRF — Basit Form",
                "difficulty":"easy",
                "estimated_minutes":15,
                "goal":"Küçük bir POST formu aracılığıyla target uygulamada istenmeyen işlem tetiklenip flag alınır (izole lab).",
                "steps":[
                    "1) Target uygulamada profile update formunu incele.",
                    "2) CSRF koruması yoksa, crafted form ile POST isteği gönderin.",
                    "3) Eğer istek çalıştıysa flag görünür."
                ],
                "hints":["Formun POST parametrelerini tarayıcı geliştirici araçlarında inceleyin."],
                "expected_result":"Başarılı CSRF ile target uygulama beklenen değişikliği yapar ve flag gösterir.",
                "solution_explanation":"Target uygulama CSRF token kontrolü yapmıyor, o yüzden tarayıcı aracılığıyla istek yapılabiliyor.",
                "safety_note":"Gerçek kullanıcı oturumlarına zarar vermeyin; sadece izole lab kullanın."
            }
        ],
        "quizzes":[
            {"q":"CSRF nasıl engellenir?","a":"CSRF token, SameSite cookie, header kontrolü (Origin/Referer) ile."}
        ],
        "resources":[
            {"title":"OWASP CSRF","url":"https://owasp.org/www-community/attacks/csrf"}
        ],
        "notes":"CSRF lab'ları tarayıcı ve form temelli örneklerdir."
    },

    "dir_traversal": {
        "id": "dir_traversal",
        "lab": "dir_traversal",
        "flag": "FLAG{PATH_EXPLORER}",
        "title": "Directory Traversal — Yolun Ötesine Bak",
        "summary": "Dosya yolu manipülasyonu ile sunucuda yetkisiz dosya okuma teknikleri.",
        "difficulty": "medium",
        "estimated_minutes": 25,
        "learning_objectives": [
            "Path canonicalization ve güvenli dosya erişimi mantığını öğrenmek",
            "Relative path / absolute path farklarını kavramak",
            "Input sanitization ve whitelisting ile korunmayı anlamak"
        ],
        "theory": [
            "Directory Traversal, kullanıcı kontrollü path parametreleriyle `../` gibi dizin atlamaları yaparak dosya okunmasına sebep olur.",
            "Korunma: canonicalization, allowlist, root chroot veya path normalization."
        ],
        "labs":[
            {
                "id":"dt-1-basic",
                "title":"Directory Traversal — Basit Okuma",
                "difficulty":"easy",
                "estimated_minutes":15,
                "goal":"`/read?file=` parametresi üzerinden sunucuda flag içeren dosyayı okumak.",
                "steps":[
                    "1) `/read?file=` endpoint'ini keşfet.",
                    "2) `../` dizin atlamaları ile `/etc/passwd` gibi sistem dosyalarını değil ama lab içindeki /flag.txt dosyasını hedefleyin.",
                    "3) Flag'i okuyun."
                ],
                "hints":["`../` pattern'lerini deneyin; uygulama path normalization yapıyor mu gözlemleyin."],
                "expected_result":"Doğru path ile flag içeriği döner.",
                "solution_explanation":"Uygulama input validation yapmıyorsa path atlama ile dosyalar okunabilir.",
                "safety_note":"Gerçek sistem dosyalarına kesinlikle erişmeye çalışmayın."
            }
        ],
        "quizzes":[
            {"q":"Directory traversal nasıl önlenir?","a":"Path normalization + allowlist + kullanıcı girdisini dosya adı kabul etmeme."}
        ],
        "resources":[
            {"title":"OWASP Directory Traversal","url":"https://owasp.org/www-community/attacks/Path_Traversal"}
        ]
    },

    # Ek modüller eklenecek: command_injection, file_upload_rce vb. (isteğe göre)
}

# Helper: map numeric id -> module key (kolay entegrasyon için)
id_map = {}
for key, m in modules.items():
    try:
        id_map[int(m.get("id"))] = key
    except Exception:
        pass

# Güvenlik/etik genel notu (her yerde gösterilecek)
GENERAL_SAFETY = (
    "UYARI: Bu modüller sadece izole eğitim/CTF ortamlarında kullanılmak üzere hazırlanmıştır. "
    "Gerçek sistemlerde izinsiz güvenlik testleri yasa dışıdır ve etik dışıdır. "
    "Her zaman hedef sistem sahibi tarafından açık izin alın."
)

