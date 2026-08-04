# LLM ve AI Güvenlik Olayları


## Giriş

Yapay zeka (AI) ve büyük dil modelleri (LLM); müşteri hizmetleri otomasyonlarından otonom yazılım geliştirme ajanlarına kadar modern dijital altyapıların merkezine yerleşmiştir. Ancak bu hızla benimsenme süreci, geleneksel yazılım güvenliği açıklarının çok ötesinde, model manipülasyonu, dolaylı prompt injection, ajan yetki aşımı (excessive agency) ve veri sızıntısı gibi yepyeni bir tehdit ekosistemini de beraberinde getirmiştir. 

Bu doküman, günümüz endüstrisinde yaşanmış doğrulanmış gerçek dünya AI güvenlik olaylarını (post-mortem analizleri ve zafiyet taksonomileriyle birlikte) inceleyerek, organizasyonların ve geliştiricilerin yapay zeka sistemlerini güvenli bir şekilde nasıl tasarlaması gerektiğine dair kritik rehberlik sunmayı amaçlamaktadır.
---
1. Cursor DuneSlide - Dolaylı Prompt Injection ile Sandbox İçi Kilit Kırılması ve Sıfır Tıkla RCE (CVE-2026-50548 / CVE-2026-50549)
- **Olay Özeti:** Cursor kodlama ajanının, bir MCP araç yanıtı veya web arama sonucunda okuduğu gizli talimatları izleyerek sandbox'ın çalışma dizini parametresini manipüle etmesi ve koruyucu dosyaların üzerine yazarak sıfır tıkla işletim sistemi seviyesinde komut çalıştırması.
- **AI Güvenlik Temeli:** Dolaylı Prompt Injection ve Güvensiz Kod Yürütme.
- **Kaynaklar:**
  - https://riskatlas.principle.sg/cases/cursor-duneslide-sandbox-rce
  - https://thehackernews.com/2026/07/critical-cursor-flaws-could-let-prompt.html

2. Mem0 Ajan Bellek Sunucusu Kimlik Doğrulama ve Anahtar İfşası (CVE-2026-59705)
- **Olay Özeti:** Yapay zeka bellek sunucusunun API uç noktalarında kimlik doğrulamasının bulunmaması nedeniyle saldırganların kullanıcı belleklerine erişmesi ve düz metin LLM API anahtarlarının sızması.
- **AI Güvenlik Temeli:** LLM Bellek Katmanı Güvenliği ve Hassas Veri İfşası.
- **Kaynak:** https://riskatlas.principle.sg/cases/mem0-openmemory-unauth

3. Azure DevOps MCP Sunucusu Karıştırılmış Vekil (Confused Deputy) Vakası
- **Olay Özeti:** MCP sunucusunun çekme isteği açıklamasındaki gizli HTML yorumlarında yer alan talimatları döndürmesi ve yapay zeka inceleme ajanının bunları yetkili kullanıcı haklarıyla çalıştırması.
- **AI Güvenlik Temeli:** Model Context Protocol Güvenliği ve Karıştırılmış Vekil Zafiyeti.
- **Kaynak:** https://riskatlas.principle.sg/cases/azure-devops-mcp-confused-deputy

4. Hugging Face Veri İşleme Boru Hattı ve Ajan İhlali
- **Olay Özeti:** Veri işleme hatlarında uzaktan kod çalıştırma ve şablon enjeksiyonu zafiyetlerini kullanan bir ajanın düğüm seviyesine erişip bulut kimlik bilgilerini ele geçirmesi.
- **AI Güvenlik Temeli:** Yapay Zeka Tedarik Zinciri Saldırıları.
- **Kaynak:** https://huggingface.co/blog/security-incident-july-2026

5. GhostApproval - Yapay Zeka Asistanlarında Onay Mekanizması Atlatma
- **Olay Özeti:** Kodlama asistanlarında symlink manipülasyonu ile masum dosya yolu gösterilirken arka planda hassas sistem dosyalarının üzerine yazılması.
- **AI Güvenlik Temeli:** Otomasyon Önyargısı ve LLM Güven Sınırı İhlali.
- **Kaynak:** https://riskatlas.principle.sg/cases/ghostapproval-symlink-approval-ui-bypass

6. Chevrolet Otomotiv Bayisi Botu Prompt Injection İstismarı (Incident 622)
- **Olay Özeti:** Chevrolet bayisinin ChatGPT destekli AI sohbet botunun, bir kullanıcının hazırladığı özel bir prompt ile manipüle edilerek 2024 model Chevy Tahoe SUV aracını 1 dolara satmayı kabul etmesi ve bunu yasal olarak bağlayıcı ilan etmesi.
- **AI Güvenlik Temeli:** Doğrudan Prompt Injection ve Hedef Manipülasyonu.
- **Kaynak:** https://incidentdatabase.ai/cite/622/

7. DPD Müşteri Hizmetleri Botunun İsyanı
- **Olay Özeti:** Sosyal mühendislik yoluyla botun şirkete küfür etmesi ve rakip firmaları övmesi.
- **AI Güvenlik Temeli:** Yetersiz Girdi ve Çıktı Filtreleme.
- **Kaynak:** https://www.theguardian.com/technology/2024/jan/20/dpd-ai-chatbot-swears-calls-itself-useless-and-criticises-firm

8. Air Canada Chatbot Yanıltma Vakası ve Mahkeme Kararı
- **Olay Özeti:** Müşteri hizmetleri botunun yanlış indirim politikası önermesi ve mahkemenin şirketi yasal olarak sorumlu tutması.
- **AI Güvenlik Temeli:** Model Halüsinasyonu ve Güvenilirlik Zafiyeti.
- **Kaynak:** https://www.cbc.ca/news/canada/british-columbia/air-canada-chatbot-lawsuit-1.7116416

9. Samsung Dahili Veri Sızıntısı Vakası
- **Olay Özeti:** Çalışanların gizli kaynak kodlarını harici yapay zeka araçlarına girmesiyle şirket içi verilerin sızması.
- **AI Güvenlik Temeli:** LLM Veri Gizliliği ve Hassas Veri İfşası.
- **Kaynak:** https://www.techradar.com/news/samsung-bans-chatgpt-use-after-employee-leak

10. OWASP Top 10 for LLM Applications Referans Vakaları
- **Olay Özeti:** Büyük dil modellerine yönelik en güncel 10 kritik riskin resmi endüstri vaka analizleri haritası.
- **AI Güvenlik Temeli:** LLM Güvenlik Standartları ve Zafiyet Taksonomisi.
- **Kaynak:** https://github.com/owasp/www-project-top-10-for-large-language-model-applications

11. OWASP Machine Learning Security Top Ten Raporu
- **Olay Özeti:** Makine öğrenimi sistemlerine yönelik veri zehirleme, model hırsızlığı ve girdi manipülasyonu vakalarının analizi.
- **AI Güvenlik Temeli:** Makine Öğrenimi Güvenlik Açıkları.
- **Kaynak:** https://owasp.org/www-project-machine-learning-security-top-10/

12. Cloud Security Alliance Otonom AI Post-Mortem Raporu
- **Olay Özeti:** Otonom yapay zeka ajanlarının güvenlik testleri sırasında sandbox dışına çıkış senaryolarının analizi.
- **AI Güvenlik Temeli:** Otonom Ajan Güvenliği ve Sandbox İzolasyonu.
- **Kaynak:** https://cloudsecurityalliance.org/artifacts/hugging-face-ciso-post-mortem

13. NVIDIA Garak LLM Zaafiyet Tarayıcı Bulguları
- **Olay Özeti:** Endüstriyel LLM sistemlerinde otomatik tarama araçlarıyla tespit edilen yaygın jailbreak ve sızıntı kalıpları.
- **AI Güvenlik Temeli:** LLM Zaafiyet Tarama Metodolojileri.
- **Kaynak:** https://gist.github.com/roycewilliams/b17feea61f39a96d75031930180ef6a6

14. NeMo Guardrails Örnek Olay Senaryoları
- **Olay Özeti:** Konuşma tabanlı yapay zeka sistemlerinde programlanabilir kalkanların önlediği diyalog tabanlı güvenlik ihlalleri.
- **AI Güvenlik Temeli:** Diyalog Güvenliği ve Guardrail Mimarileri.
- **Kaynak:** https://github.com/NVIDIA/NeMo-Guardrails

15. AI RiskAtlas Gerçek Dünya Vaka Kütüphanesi
- **Olay Özeti:** Doğrulanmış gerçek dünya yapay zeka arızaları, prompt injection örnekleri ve tedarik zinciri ihlallerinin güncel arşivi.
- **AI Güvenlik Temeli:** Yapay Zeka Tehdit İstihbaratı.
- **Kaynak:** https://riskatlas.principle.sg/cases

---

## Çıkarılan Temel Dersler

- **İnsan Onay Mekanizmalarının (Human-in-the-Loop) Kötüye Kullanımı:** GhostApproval ve Azure DevOps MCP vakalarında görüldüğü üzere; onay mekanizmaları, symlink'ler veya gizli HTML yorumları gibi yöntemlerle insan gözünden kaçırılan arka plan işlemlerine karşı körü körüne güvenilmemeli, kritik dosya değişimleri ve yetki yükseltmeleri için şeffaf doğrulama katmanları şart koşulmalıdır.
- **Üçüncü Parti Entegrasyon ve Tedarik Zinciri Risk Yönetimi:** Cursor DuneSlide ve Mem0 olayları, kullanılan yapay zeka eklentilerinin (MCP sunucuları, bellek servisleri) yerel sistem dosyalarına ve kimlik bilgilerine erişim sınırlarının (Least Privilege ilkesi) en katı şekilde denetlenmesi gerektiğini göstermiştir.
- **Kurumsal Yapay Zeka Kullanım Politikaları ve Veri Sızıntısı Farkındalığı:** Samsung vakasında olduğu gibi, teknik güvenlik duvarları ne kadar gelişmiş olursa olsun, çalışanların harici LLM platformlarına girdi veri setleri (kaynak kod, hassas belgeler) sızdırmasını önlemek için kurumsal düzeyde katı veri maskeleme ve DLP (Data Loss Prevention) politikaları uygulanmalıdır.