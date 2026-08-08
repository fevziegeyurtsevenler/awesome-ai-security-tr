#!/usr/bin/env python3
"""Girdi biçiminin TEK kaynağı.

Hem site üreteci (site-uret.py) hem biçim denetleyicisi (bicim-denetle.py)
buradan okur. Böylece "CI'dan geçti ama sitede görünmedi" durumu oluşamaz:
denetleyicinin kabul ettiği her satır, üretecin de ayrıştırdığı satırdır.
"""

import re

# Girdi sözleşmesi:
#   - [Ad](url) — açıklama. *(tür: X, dil: TR|EN)*
# Ayırıcı, normal tire (-) değil EM DASH (—) olmalı; üreteç bunu bekliyor.
GIRDI_RE = re.compile(
    r"^- \[(?P<ad>.+?)\]\((?P<url>[^)]+)\) — (?P<aciklama>.+?) "
    r"\*\(tür: (?P<tur>[^,]+), dil: (?P<dil>TR|EN)\)\*\s*$"
)

# Girdi olmaya çalışan ama sözleşmeye uymayan satırları yakalamak için:
# madde işaretiyle başlayıp markdown linki içeren her satır bir girdi adayıdır.
GIRDI_ADAYI_RE = re.compile(r"^\s*[-*] \[[^\]]+\]\([^)]+\)")

# Markdown linki olmadan doğrudan yazılmış URL (çıplak link).
HAM_URL_RE = re.compile(r"^\s*[-*]?\s*(\*\*[^*]+\*\*:?)?\s*https?://")

BOLUM_ALT_SINIR = 15
BOLUM_UST_SINIR = 40


def girdi_ayristir(satir: str):
    """Satır sözleşmeye uyuyorsa alanları döndürür, uymuyorsa None."""
    m = GIRDI_RE.match(satir)
    if not m:
        return None
    d = m.groupdict()
    ac = d["aciklama"].strip()
    altaysec = "🔧 AltaySec" in ac
    bakimsiz = "⚠️ bakımsız" in ac
    ac = ac.replace("🔧 AltaySec", "").replace("⚠️ bakımsız", "").strip()
    return {
        "ad": d["ad"].strip(), "url": d["url"].strip(), "aciklama": ac,
        "tur": d["tur"].strip(), "dil": d["dil"],
        "altaysec": altaysec, "bakimsiz": bakimsiz,
    }


def neden_ayrismadi(satir: str) -> str:
    """Girdi adayı neden sözleşmeye uymuyor — katkıcıya somut sebep ver."""
    if " — " not in satir:
        if re.search(r"\)\s+-\s+", satir):
            return ("ayırıcı normal tire (-) kullanılmış; EM DASH (—) olmalı. "
                    "Kopyalanacak karakter: —")
        return "açıklamadan önce ' — ' ayırıcısı yok"
    if not re.search(r"\*\(tür: [^,]+, dil: (TR|EN)\)\*\s*$", satir):
        if "tür:" not in satir:
            return "sonda *(tür: …, dil: TR|EN)* etiketi yok"
        return ("etiket biçimi bozuk; tam olarak şöyle olmalı: "
                "*(tür: makale, dil: EN)*")
    if not satir.startswith("- ["):
        return "satır '- [' ile başlamıyor (girinti veya * kullanılmış olabilir)"
    return "sözleşmeye uymuyor (ad/url/açıklama sırasını kontrol edin)"
