# Katkı Rehberi

Bu liste **kapsamlı olmaya değil, seçici olmaya** çalışır. Değer eklenen linkten değil, elenen linkten gelir.

Katkı için GitHub hesabı ve bir PR yeterli. Konu uzmanı olmak şart değil; **eklediğin kaynağı okumuş olmak** şart.

---

## 1. Kalite çıtası

### Çıplak link kabul edilmez

Her girdi 1-2 cümlelik Türkçe açıklama içerir ve "neden burada" sorusuna cevap verir. Bu kural CI'da otomatik denetlenir.

```markdown
- [Kaynak Adı](https://url) — Ne olduğu ve neden değerli olduğu. *(tür: makale | araç | lab | dataset | standart, dil: TR | EN)*
```

**İyi:**
```markdown
- [garak](https://github.com/NVIDIA/garak) — LLM'lere karşı otomatik zafiyet taraması yapan tarayıcı; probe/detector mimarisi sayesinde kendi saldırı sınıfınızı eklemek kolay, alanın fiili `nmap`'i. *(tür: araç, dil: EN)*
```

**Reddedilir:**
```markdown
- [garak](https://github.com/NVIDIA/garak) — LLM güvenlik aracı.
- [garak](https://github.com/NVIDIA/garak)
```

Fark şu: iyi açıklama okuyucunun **tıklayıp tıklamayacağına karar vermesini** sağlar. "LLM güvenlik aracı" hiçbir karar verdirmez.

### Kaynağı okumuş ol

Eklediğin her kaynağı açıp inceledin mi? Bu listenin tek gerçek değeri bu. Bir dil modeline liste doldurtmak, listeyi diğer yüz listeden ayırt edilemez hâle getirir — ve bu repo tam da o listelerden farklı olmak için var.

### Bölüm başına 15-40 kaynak

Alt sınır ciddiyet, üst sınır seçicilik içindir. Bir bölüm 40'ı geçiyorsa ya bölünmeli ya da zayıf girdiler elenmeli.

### Ölü ve bakımsız kaynaklar

- 12+ aydır güncellenmemiş araç/proje: `⚠️ bakımsız` işareti alır veya listeden çıkarılır
- Erişilemeyen link: CI yakalar, düzeltilir veya çıkarılır
- Bu kural listenin kendisine de uygulanır

### AltaySec kaynakları işaretlenir

Bu listeyi yürüten ekibin ürettiği kaynaklar `🔧 AltaySec` rozetiyle gösterilir. Kendi araçlarımızı listelemek meşru; gizlemek değil. Rozet olmadan eklenen AltaySec kaynağı PR'da düzeltilir.

## 2. Neyi listelemeyiz

- Genel "yapay zekaya giriş" içerikleri — bu bir **güvenlik** listesi
- Ödeme duvarı arkasındaki içerik (erişilebilir bir özeti yoksa)
- Kendi iddiasını doğrulamayan tanıtım yazıları
- Bir insanın okumadığı, toplu üretilmiş girdiler

## 3. Bölümler

Bölüm sahibi veya atama yok. İstediğin bölüme katkı verebilirsin.

| Dosya | Bölüm |
|---|---|
| `kaynaklar/01-prompt-injection.md` | Prompt Injection |
| `kaynaklar/02-jailbreak-red-teaming.md` | Jailbreak ve Red Teaming |
| `kaynaklar/03-guardrail-savunma.md` | Guardrail ve Savunma |
| `kaynaklar/04-degerlendirme-standartlar.md` | Değerlendirme ve Standartlar |
| `kaynaklar/05-model-tedarik-zinciri.md` | Model ve Tedarik Zinciri |
| `kaynaklar/06-agent-mcp-guvenligi.md` | Ajan, Araç ve MCP Güvenliği |
| `kaynaklar/07-rag-uygulama-guvenligi.md` | RAG ve Uygulama Güvenliği |
| `kaynaklar/08-turkce-kaynaklar-veri-setleri.md` | Türkçe Kaynaklar ve Veri Setleri |
| `kaynaklar/09-egitim-lab-ctf.md` | Eğitim, Lab ve CTF |

Bir bölüm 15 kaynağın altındaysa orası doldurulmayı bekliyor demektir — en kolay başlangıç noktası.

## 4. PR süreci

1. **Fork'la, ekle, PR aç.** Ön izin, issue veya atama gerekmiyor.
2. Küçük ve sık PR at. 40 linklik tek dev PR yerine 8'erli parçalar hem daha hızlı incelenir hem daha iyi incelenir.
3. **CI yeşil olmalı.** Beş kontrol çalışır: açıklamasız markdown linki, ham URL, tür/dil etiketi, bölümün site üretecine kayıtlı olması ve ölü link taraması.
4. PR'lar geldikçe küratör tarafından incelenir; uygun olanlar merge edilir.

## 5. Yerelde kontrol

PR açmadan önce CI'ın çalıştırdığı biçim kontrollerini kendin koşturabilirsin. Dördü de sessiz kalırsa temizsin:

```bash
# 1) Açıklamasız markdown linki
grep -rnE '^\s*[-*] \[[^]]+\]\([^)]+\)\s*$' kaynaklar/

# 2) Ham URL — kaynaklar her zaman [Ad](url) biçiminde olmalı
grep -rnE '^\s*[-*]?\s*(\*\*[^*]+\*\*:?)?\s*https?://' kaynaklar/

# 3) Eksik veya bozuk tür/dil etiketi
grep -rn '^- \[' kaynaklar/ | grep -vE '\*\(tür: [^,]+, dil: (TR|EN)\)\*\s*$'

# 4) Bölüm site üretecine kayıtlı mı
for f in kaynaklar/*.md; do a=$(basename "$f" .md); \
  grep -q "\"$a\"" araclar/site-uret.py || echo "META'da yok: $a"; done
```

## 6. Yeni bölüm önerisi

Mevcut dokuz bölüme sığmayan bir konu varsa önce issue aç. Yeni bölüm en az 15 nitelikli kaynak gerektirir — daha azı mevcut bir bölümün alt başlığı olarak durmalı.

Yeni bölüm eklerken **iki dosyaya dokunman gerekir**:

1. `kaynaklar/NN-kisa-ad.md` — bölümün kendisi (H1 başlık, `>` ile bir cümlelik özet, sonra `##` alt başlıklar)
2. `araclar/site-uret.py` içindeki `META` sözlüğü — bölümün kısa adı ve arama odaklı meta açıklaması

İkincisini atlarsan bölüm sitede **hiç yayımlanmaz**; üreteç onu sessizce atlar. CI bu durumu yakalar ve PR'ı kırmızıya çevirir.
