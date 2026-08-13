#!/usr/bin/env python3
"""Biçim denetleyicisi — CI'ın bloklayıcı kapısı.

Girdi sözleşmesini araclar/bicim.py'den okur; yani burada geçen her satır
site üreteci tarafından da ayrıştırılır. Sessizce sitede kaybolan girdi olmaz.

Kullanım:  python3 araclar/bicim-denetle.py
Çıkış:     0 = temiz, 1 = en az bir hata
"""

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bicim import (  # noqa: E402
    ACIKLAMA_UYARI_SINIRI, BOLUM_ALT_SINIR, BOLUM_UST_SINIR, GIRDI_ADAYI_RE,
    HAM_URL_RE, girdi_ayristir, neden_ayrismadi,
)

KOK = pathlib.Path(__file__).resolve().parent.parent
KAYNAK_DIZIN = KOK / "kaynaklar"
URETEC = KOK / "araclar" / "site-uret.py"

hatalar = []
uyarilar = []


def hata(dosya, satir_no, mesaj):
    yer = f"{dosya}:{satir_no}" if satir_no else str(dosya)
    hatalar.append((dosya, satir_no, mesaj))
    konum = f" file={dosya},line={satir_no}" if satir_no else f" file={dosya}"
    print(f"::error{konum}::{mesaj}")


def uyari(dosya, mesaj):
    uyarilar.append((dosya, mesaj))
    print(f"::warning file={dosya}::{mesaj}")


def denetle():
    dosyalar = sorted(KAYNAK_DIZIN.glob("*.md"))
    if not dosyalar:
        print("::error::kaynaklar/ altında hiç bölüm dosyası yok")
        return 1

    uretec_metni = URETEC.read_text(encoding="utf-8")
    toplam_girdi = 0

    for f in dosyalar:
        goreli = f.relative_to(KOK)
        satirlar = f.read_text(encoding="utf-8").split("\n")
        girdi_sayisi = 0

        for i, satir in enumerate(satirlar, 1):
            # 1) Girdi adayı sözleşmeye uyuyor mu?
            if GIRDI_ADAYI_RE.match(satir):
                g = girdi_ayristir(satir)
                if g:
                    girdi_sayisi += 1
                    n = len(g["aciklama"])
                    if n > ACIKLAMA_UYARI_SINIRI:
                        uyari(goreli, f"satır {i}: açıklama {n} karakter "
                                      f"(uyarı sınırı {ACIKLAMA_UYARI_SINIRI}, liste medyanı ~300). "
                                      "Dizin girdisi taranabilir kalmalı — en karar-verdirici "
                                      "sayıyı tutup gerisini kısaltın.")
                else:
                    hata(goreli, i, f"Girdi sözleşmesine uymuyor — {neden_ayrismadi(satir)}. "
                                    "Bu satır sitede ve aramada görünmez.")
                continue

            # 2) Çıplak/ham URL
            if HAM_URL_RE.match(satir):
                hata(goreli, i, "Ham URL. Kaynaklar '- [Ad](url) — açıklama "
                                "*(tür: …, dil: …)*' biçiminde olmalı.")

        # 3) Bölüm site üretecine kayıtlı mı?
        if f'"{f.stem}"' not in uretec_metni:
            hata(goreli, None,
                 f"'{f.stem}' araclar/site-uret.py içindeki META sözlüğünde yok — "
                 "bu bölüm sitede yayımlanmaz. META anahtarı dosya adıyla "
                 "(uzantısız) BİREBİR aynı olmalı.")

        # 4) Bölüm boyutu
        if girdi_sayisi > BOLUM_UST_SINIR:
            hata(goreli, None, f"{girdi_sayisi} kaynak — üst sınır {BOLUM_UST_SINIR}; "
                               "bölünmeli veya zayıf girdiler elenmeli.")
        elif girdi_sayisi < BOLUM_ALT_SINIR:
            uyari(goreli, f"{girdi_sayisi} kaynak (hedef en az {BOLUM_ALT_SINIR}) — "
                          "doldurulmayı bekliyor.")

        toplam_girdi += girdi_sayisi
        print(f"  {goreli}: {girdi_sayisi} girdi")

    # 5) META'da olup dosyası olmayan bölüm (ters yön)
    mevcut = {f.stem for f in dosyalar}
    for anahtar in re.findall(r'^\s*"([0-9]{2}-[a-z0-9-]+)":', uretec_metni, re.M):
        if anahtar not in mevcut:
            hata("araclar/site-uret.py", None,
                 f"META'da '{anahtar}' kayıtlı ama kaynaklar/{anahtar}.md yok.")

    print(f"\nToplam: {len(dosyalar)} bölüm, {toplam_girdi} girdi")
    if uyarilar:
        print(f"{len(uyarilar)} uyarı (bloklamaz)")
    if hatalar:
        print(f"\n{len(hatalar)} HATA — düzeltilmeden birleştirilemez")
        return 1
    print("Biçim denetimi temiz.")
    return 0


if __name__ == "__main__":
    sys.exit(denetle())
