#!/usr/bin/env python3
"""kaynaklar/*.md dosyalarından indekslenebilir statik kılavuz sitesi üretir.

Her bölüm ayrı bir HTML sayfası olur; böylece her bölüm kendi arama terimi
için sıralanabilir. Girdiler yapısal olarak ayrıştırılır — hem sayfa hem de
arama indeksi (arama.json) aynı kaynaktan üretilir. Çıktı site/ dizinine yazılır.

Kullanım:  python3 araclar/site-uret.py
"""

import html
import json
import pathlib
import re
import sys

import markdown

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from bicim import girdi_ayristir  # noqa: E402

KOK = pathlib.Path(__file__).resolve().parent.parent
KAYNAK_DIZIN = KOK / "kaynaklar"
CIKTI = KOK / "site"

TABAN_URL = "https://fevziegeyurtsevenler.github.io/awesome-ai-security-tr"
REPO_URL = "https://github.com/fevziegeyurtsevenler/awesome-ai-security-tr"
YAZAR = "Fevzi Ege Yurtsevenler"
SON_GUNCELLEME = "2026-08-03"

SITE_ADI = "Yapay Zeka Güvenliği Kaynakları"
SITE_ACIKLAMA = (
    "Türkçe açıklamalı, küratörlü ve CI ile doğrulanan yapay zeka güvenliği "
    "kaynak kılavuzu: prompt injection, jailbreak, red teaming, guardrail, "
    "ajan/MCP güvenliği, RAG güvenliği ve model tedarik zinciri."
)

# Bölüm dosyası -> (kısa ad, arama odaklı meta açıklama)
META = {
    "01-prompt-injection": (
        "Prompt Injection",
        "Prompt injection nedir, nasıl çalışır ve nasıl savunulur — Türkçe "
        "açıklamalı kaynaklar: temel okumalar, akademik makaleler, gerçek "
        "dünya vakaları ve tespit araçları.",
    ),
    "02-jailbreak-red-teaming": (
        "Jailbreak ve Red Teaming",
        "LLM jailbreak ve yapay zeka red teaming kaynakları: saldırı "
        "yöntemleri, garak ve PyRIT gibi otomasyon araçları, saldırı veri "
        "setleri ve açık arenalar.",
    ),
    "03-guardrail-savunma": (
        "Guardrail ve Savunma",
        "LLM guardrail ve savunma kaynakları: NeMo Guardrails, Llama Guard, "
        "PII maskeleme ve guardrail'lerin gerçekte ne kadar çalıştığını "
        "gösteren ölçümler.",
    ),
    "04-degerlendirme-standartlar": (
        "Değerlendirme ve Standartlar",
        "Yapay zeka güvenliği standartları ve değerlendirme çerçeveleri: "
        "OWASP LLM Top 10, MITRE ATLAS, NIST AI RMF, AISVS ve ölçüt araçları.",
    ),
    "05-model-tedarik-zinciri": (
        "Model ve Tedarik Zinciri Güvenliği",
        "Model dosyası ve yapay zeka tedarik zinciri güvenliği: pickle "
        "riskleri, safetensors, veri zehirlenmesi, model imzalama ve ML-BOM.",
    ),
    "06-agent-mcp-guvenligi": (
        "Ajan, Araç ve MCP Güvenliği",
        "Yapay zeka ajanı ve MCP güvenliği kaynakları: tool poisoning, "
        "ölümcül üçlü, yetki sınırlama, ajan eklentisi denetim araçları.",
    ),
    "07-rag-uygulama-guvenligi": (
        "RAG ve Uygulama Güvenliği",
        "RAG güvenliği ve LLM uygulama güvenliği: bilgi tabanı zehirlenmesi, "
        "vektör veritabanı riskleri, eğitim verisi sızıntısı ve API katmanı.",
    ),
    "08-turkce-kaynaklar-veri-setleri": (
        "Türkçe Kaynaklar ve Veri Setleri",
        "Türkçe yapay zeka güvenliği kaynakları ve veri setleri: Türkçeye "
        "özgü ölçülmüş guardrail kör noktaları, KVKK, USOM ve Türkçe "
        "rehber serisi.",
    ),
    "09-egitim-lab-ctf": (
        "Eğitim, Lab ve CTF",
        "Yapay zeka güvenliği eğitimi, laboratuvarları ve CTF'leri: Gandalf, "
        "PortSwigger LLM lab'ları, HackAPrompt, ücretsiz kurslar ve bug "
        "bounty platformları.",
    ),
}

FONT_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=IBM+Plex+Mono:wght@400;500&"
    "family=IBM+Plex+Sans:wght@400;450;500;600&"
    "family=IBM+Plex+Serif:wght@600;700&display=swap"
)

# --- stil -------------------------------------------------------------------
# Palet, veriyi kodlar: kızıl = atlatılan/başarısız ölçüm, zeytin = tutulan.
# Süs için ikinci bir renk yok.
CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
  --kagit:#FCFBF8; --kagit-2:#F4F2EC; --murekkep:#16181D; --kursun:#5A6069;
  --cizgi:#E3E1DA; --kizil:#B03A2E; --zeytin:#3E6B4F; --vurgu-zemin:#F7EDEB;
  --olcu:68rem; --yazi:17px;
  --ff-serif:"IBM Plex Serif",Georgia,"Times New Roman",serif;
  --ff-sans:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --ff-mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
  color-scheme:light;
}
:root[data-tema="koyu"]{
  --kagit:#131519; --kagit-2:#1B1E24; --murekkep:#E9E7E1; --kursun:#9AA0A9;
  --cizgi:#282C33; --kizil:#E4776A; --zeytin:#79B994; --vurgu-zemin:#241C1B;
  color-scheme:dark;
}
@media (prefers-color-scheme:dark){
  :root:not([data-tema="acik"]){
    --kagit:#131519; --kagit-2:#1B1E24; --murekkep:#E9E7E1; --kursun:#9AA0A9;
    --cizgi:#282C33; --kizil:#E4776A; --zeytin:#79B994; --vurgu-zemin:#241C1B;
    color-scheme:dark;
  }
}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *,*::before,*::after{animation-duration:.001ms!important;animation-delay:0ms!important;transition-duration:.001ms!important}
}
body{
  margin:0;background:var(--kagit);color:var(--murekkep);
  font-family:var(--ff-sans);font-size:var(--yazi);line-height:1.65;
  font-feature-settings:"kern","liga";-webkit-font-smoothing:antialiased;
}
.kabuk{max-width:var(--olcu);margin:0 auto;padding:0 clamp(1.1rem,4vw,2.5rem)}
a{color:inherit;text-decoration-color:color-mix(in srgb,var(--kizil) 45%,transparent);text-underline-offset:3px}
a:hover{text-decoration-color:var(--kizil)}
:focus-visible{outline:2px solid var(--kizil);outline-offset:3px;border-radius:2px}

/* ---------- üst çubuk ---------- */
.ust{position:sticky;top:0;z-index:40;background:color-mix(in srgb,var(--kagit) 88%,transparent);
     backdrop-filter:saturate(1.6) blur(10px);border-bottom:1px solid var(--cizgi)}
.ust .kabuk{display:flex;align-items:center;gap:1rem;min-height:56px}
.marka{font-family:var(--ff-mono);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;
       text-decoration:none;color:var(--murekkep);white-space:nowrap;font-weight:500;
       min-width:0;overflow:hidden;text-overflow:ellipsis}
.marka b{color:var(--kizil);font-weight:500}
.ust nav{margin-inline-start:auto;display:flex;align-items:center;gap:.35rem;flex:none}
.ust nav a{font-size:.85rem;color:var(--kursun);text-decoration:none;padding:.35rem .55rem;border-radius:4px}
.ust nav a:hover{color:var(--murekkep);background:var(--kagit-2)}
.dugme{display:inline-flex;align-items:center;gap:.4rem;border:1px solid var(--cizgi);background:var(--kagit);
       color:var(--kursun);border-radius:5px;padding:.34rem .6rem;font:inherit;font-size:.82rem;cursor:pointer}
.dugme:hover{color:var(--murekkep);border-color:var(--kursun)}
.dugme kbd{font-family:var(--ff-mono);font-size:.7rem;border:1px solid var(--cizgi);border-radius:3px;
           padding:0 .25rem;color:var(--kursun);background:var(--kagit-2)}
@media (max-width:640px){
  .ust nav a.gizle-dar{display:none}
  .marka{font-size:.68rem;letter-spacing:.05em}
  .ust .kabuk{gap:.6rem}
  .dugme#ara-kisayol kbd{display:none}
}

/* ---------- hero: tez ---------- */
.tez{padding:clamp(3rem,9vw,6rem) 0 clamp(2rem,5vw,3.5rem);border-bottom:1px solid var(--cizgi)}
.tez-etiket{font-family:var(--ff-mono);font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;
            color:var(--kursun);margin:0 0 1.6rem}
.kanit{font-family:var(--ff-mono);font-size:clamp(1.05rem,3.4vw,1.7rem);line-height:1.9;
       display:flex;flex-wrap:wrap;align-items:center;gap:.5rem .85rem;margin:0 0 1.1rem}
.kanit span{display:inline-block}
.kanit .kod{background:var(--kagit-2);padding:.16em .5em;border-radius:4px;border:1px solid var(--cizgi)}
.kanit .nokta{color:var(--kizil);font-weight:500}
.kanit .ok{color:var(--kursun)}
.kanit .esitsiz{color:var(--kizil);font-size:1.25em;font-weight:500}
.kanit-sonuc{display:inline-flex;align-items:center;gap:.5rem;font-family:var(--ff-mono);font-size:.8rem;
             letter-spacing:.06em;text-transform:uppercase;color:var(--kizil);
             background:var(--vurgu-zemin);border:1px solid color-mix(in srgb,var(--kizil) 30%,transparent);
             padding:.3rem .65rem;border-radius:99px}
.tez h1{font-family:var(--ff-serif);font-weight:700;font-size:clamp(2.1rem,6.4vw,3.9rem);
        line-height:1.06;letter-spacing:-.022em;margin:2.4rem 0 0;max-width:16ch}
.tez-alt{font-size:clamp(1rem,2.2vw,1.2rem);color:var(--kursun);margin:1rem 0 0;max-width:56ch}
.tez-alt b{color:var(--murekkep);font-weight:500}
.kunye{display:flex;flex-wrap:wrap;gap:.5rem 1.4rem;margin:1.8rem 0 0;font-family:var(--ff-mono);
       font-size:.76rem;letter-spacing:.04em;color:var(--kursun)}
.kunye b{color:var(--murekkep);font-weight:500}
@media (prefers-reduced-motion:no-preference){
  .can{opacity:0;animation:yuksel .62s cubic-bezier(.22,.68,.36,1) forwards}
  .can-1{animation-delay:.05s}.can-2{animation-delay:.16s}.can-3{animation-delay:.27s}
  .can-4{animation-delay:.40s}.can-5{animation-delay:.54s}.can-6{animation-delay:.66s}
  @keyframes yuksel{from{opacity:0;transform:translateY(9px)}to{opacity:1;transform:none}}
}

/* ---------- arama ---------- */
.ara-alan{padding:2.4rem 0;border-bottom:1px solid var(--cizgi)}
.ara-kutu{display:flex;align-items:center;gap:.8rem;border:1px solid var(--cizgi);background:var(--kagit-2);
          border-radius:8px;padding:.85rem 1.1rem;transition:border-color .15s,background .15s}
.ara-kutu:focus-within{border-color:var(--kizil);background:var(--kagit)}
.ara-kutu svg{flex:none;color:var(--kursun)}
.ara-kutu input{flex:1;border:0;background:none;font:inherit;font-size:1.02rem;color:var(--murekkep);outline:none;min-width:0}
.ara-kutu input::placeholder{color:var(--kursun)}
.ara-sayac{font-family:var(--ff-mono);font-size:.75rem;color:var(--kursun);white-space:nowrap}
.ara-sonuc{margin:1.4rem 0 0;display:none}
.ara-sonuc.acik{display:block}
.ara-bos{color:var(--kursun);font-size:.94rem;margin:1rem 0 0}

/* ---------- dizin ---------- */
.blok{padding:clamp(2.6rem,6vw,4rem) 0;border-bottom:1px solid var(--cizgi)}
.blok:last-of-type{border-bottom:0}
.blok-basi{font-family:var(--ff-mono);font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;
           color:var(--kursun);margin:0 0 1.6rem;display:flex;align-items:baseline;gap:.8rem}
.blok-basi::after{content:"";flex:1;height:1px;background:var(--cizgi)}
.dizin{list-style:none;padding:0;margin:0}
.dizin li{border-top:1px solid var(--cizgi)}
.dizin li:last-child{border-bottom:1px solid var(--cizgi)}
.dizin a{display:flex;align-items:baseline;gap:.9rem;padding:.95rem .25rem;text-decoration:none;
         transition:background .14s,padding-inline-start .14s}
.dizin a:hover{background:var(--kagit-2);padding-inline-start:.7rem}
.dizin .no{font-family:var(--ff-mono);font-size:.8rem;color:var(--kizil);flex:none;width:2ch}
.dizin .ad{font-size:1.06rem;font-weight:500;flex:none}
.dizin .ozet{color:var(--kursun);font-size:.9rem;flex:1 1 auto;overflow:hidden;text-overflow:ellipsis;
             white-space:nowrap;min-width:0}
.dizin .lider{flex:1 1 2rem;border-bottom:1px dotted var(--cizgi);transform:translateY(-.3em);min-width:1.5rem}
.dizin .sayi{font-family:var(--ff-mono);font-size:.82rem;color:var(--kursun);flex:none}
@media (max-width:720px){.dizin .ozet{display:none}}

/* ---------- yol kartları ---------- */
.yollar{display:grid;gap:.9rem;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));list-style:none;padding:0;margin:0}
.yol{border:1px solid var(--cizgi);border-radius:8px;padding:1.15rem 1.25rem;background:var(--kagit-2);
     display:flex;flex-direction:column;gap:.5rem}
.yol h3{margin:0;font-size:.98rem;font-weight:600;line-height:1.35}
.yol p{margin:0;font-size:.88rem;color:var(--kursun);line-height:1.55}
.yol .git{margin-top:auto;padding-top:.6rem;font-family:var(--ff-mono);font-size:.78rem;color:var(--kizil);text-decoration:none;white-space:nowrap}
.yol .git:hover{text-decoration:underline}

/* ---------- ölçüm tablosu ---------- */
.olcumler{display:grid;gap:1px;background:var(--cizgi);border:1px solid var(--cizgi);border-radius:8px;overflow:hidden}
.olcum{background:var(--kagit);padding:1.35rem 1.4rem;display:grid;gap:.55rem}
.olcum .rakam{font-family:var(--ff-serif);font-size:clamp(2rem,5.5vw,2.7rem);line-height:1;color:var(--kizil);
              font-weight:700;letter-spacing:-.02em}
.olcum .ne{font-size:.94rem;color:var(--murekkep);line-height:1.5}
.olcum .kaynak{font-family:var(--ff-mono);font-size:.74rem}
.olcum .kaynak a{color:var(--kursun)}
@media (min-width:820px){.olcumler{grid-template-columns:repeat(3,1fr)}}
.not{color:var(--kursun);font-size:.92rem;margin:1.2rem 0 0;max-width:64ch}

/* ---------- bölüm sayfası ---------- */
.sayfa{display:grid;gap:clamp(1.5rem,4vw,3.5rem);padding:clamp(2rem,5vw,3.2rem) 0 4rem}
@media (min-width:960px){.sayfa{grid-template-columns:14rem minmax(0,1fr)}}
.yan{align-self:start}
@media (min-width:960px){.yan{position:sticky;top:76px}}
.yan-basi{font-family:var(--ff-mono);font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;
          color:var(--kursun);margin:0 0 .8rem}
.yan ol{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:.1rem}
.yan a{display:flex;justify-content:space-between;gap:.6rem;text-decoration:none;font-size:.88rem;
       color:var(--kursun);padding:.36rem .5rem;border-radius:5px;border-inline-start:2px solid transparent}
.yan a:hover{color:var(--murekkep);background:var(--kagit-2)}
.yan a.etkin{color:var(--murekkep);border-inline-start-color:var(--kizil);background:var(--kagit-2)}
.yan a span{font-family:var(--ff-mono);font-size:.74rem;color:var(--kursun);flex:none}
@media (max-width:959px){
  .yan{border:1px solid var(--cizgi);border-radius:8px;padding:1rem}
  .yan ol{flex-direction:row;flex-wrap:wrap;gap:.4rem}
  .yan a{border:1px solid var(--cizgi);border-radius:99px;padding:.3rem .7rem;border-inline-start-width:1px}
  .yan a.etkin{border-color:var(--kizil)}
}
.bolum-no{font-family:var(--ff-mono);font-size:.8rem;letter-spacing:.12em;color:var(--kizil);margin:0 0 .5rem}
.icerik h1{font-family:var(--ff-serif);font-weight:700;font-size:clamp(1.9rem,5vw,2.9rem);line-height:1.1;
           letter-spacing:-.02em;margin:0 0 1rem}
.giris{font-size:1.1rem;color:var(--kursun);line-height:1.6;margin:0 0 1.8rem;max-width:60ch;
       border-inline-start:2px solid var(--kizil);padding-inline-start:1.1rem}
.icerik h2{font-family:var(--ff-sans);font-size:1.18rem;font-weight:600;letter-spacing:-.01em;
           margin:3rem 0 1.2rem;padding-bottom:.6rem;border-bottom:1px solid var(--cizgi);
           display:flex;align-items:baseline;gap:.7rem;scroll-margin-top:76px}
.icerik h2 .adet{font-family:var(--ff-mono);font-size:.74rem;font-weight:400;color:var(--kursun);margin-inline-start:auto}
.icerik > p{max-width:66ch;color:var(--kursun)}
.icerik code{font-family:var(--ff-mono);font-size:.87em;background:var(--kagit-2);border:1px solid var(--cizgi);
             padding:.08em .35em;border-radius:4px}

/* ---------- girdi ---------- */
.girdiler{list-style:none;padding:0;margin:0;display:flex;flex-direction:column}
.girdi{padding:1.05rem 0 1.05rem 1.05rem;border-top:1px solid var(--cizgi);
       border-inline-start:2px solid transparent;transition:border-color .16s,background .16s}
.girdi:last-child{border-bottom:1px solid var(--cizgi)}
.girdi:hover{border-inline-start-color:var(--kizil);background:var(--kagit-2)}
.girdi-ad{font-size:1.01rem;font-weight:500;line-height:1.4;text-decoration:none;
          text-decoration-color:transparent;display:inline-block}
.girdi:hover .girdi-ad{text-decoration:underline;text-decoration-color:var(--kizil)}
.girdi-ac{margin:.4rem 0 0;color:var(--kursun);font-size:.94rem;line-height:1.6;max-width:74ch}
.girdi-ac code{font-size:.85em}
.girdi-meta{display:flex;flex-wrap:wrap;align-items:center;gap:.45rem;margin:.6rem 0 0;
            font-family:var(--ff-mono);font-size:.7rem;letter-spacing:.05em}
.etiket{border:1px solid var(--cizgi);border-radius:99px;padding:.13rem .5rem;color:var(--kursun);text-transform:lowercase}
.etiket.tr{color:var(--zeytin);border-color:color-mix(in srgb,var(--zeytin) 40%,transparent)}
.etiket.altaysec{color:var(--kizil);border-color:color-mix(in srgb,var(--kizil) 35%,transparent);text-transform:none}
.etiket.bakimsiz{color:var(--kursun);border-style:dashed}
.girdi-host{color:var(--kursun);opacity:.75;margin-inline-start:auto;text-transform:none;letter-spacing:0}
@media (max-width:600px){.girdi-host{display:none}}

/* ---------- sayfa geçişi ---------- */
.gecis{display:grid;gap:.8rem;margin:3.5rem 0 0;padding-top:1.6rem;border-top:1px solid var(--cizgi)}
@media (min-width:640px){.gecis{grid-template-columns:1fr 1fr}}
.gecis a{border:1px solid var(--cizgi);border-radius:8px;padding:.95rem 1.1rem;text-decoration:none;
         display:grid;gap:.25rem;transition:border-color .15s,background .15s}
.gecis a:hover{border-color:var(--kizil);background:var(--kagit-2)}
.gecis .yon{font-family:var(--ff-mono);font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--kursun)}
.gecis .hedef{font-weight:500}
.gecis .sag{text-align:end}

/* ---------- alt bilgi ---------- */
.alt{border-top:1px solid var(--cizgi);background:var(--kagit-2);padding:2.4rem 0;margin-top:auto}
.alt .kabuk{display:flex;flex-wrap:wrap;gap:1rem 2rem;justify-content:space-between;
            font-size:.85rem;color:var(--kursun)}
.alt a{color:var(--kursun)}
.alt a:hover{color:var(--murekkep)}
body{display:flex;flex-direction:column;min-height:100vh}
main{flex:1}
"""

JS = r"""
(function(){
  // --- tema ---
  var kok=document.documentElement, anahtar='aisec-tema';
  try{var kayit=localStorage.getItem(anahtar); if(kayit) kok.setAttribute('data-tema',kayit);}catch(e){}
  var dgm=document.getElementById('tema-dugme');
  if(dgm) dgm.addEventListener('click',function(){
    var koyuMu = kok.getAttribute('data-tema')==='koyu' ||
      (!kok.getAttribute('data-tema') && matchMedia('(prefers-color-scheme:dark)').matches);
    var yeni = koyuMu ? 'acik' : 'koyu';
    kok.setAttribute('data-tema',yeni);
    try{localStorage.setItem(anahtar,yeni);}catch(e){}
    dgm.setAttribute('aria-label', yeni==='koyu' ? 'Açık temaya geç' : 'Koyu temaya geç');
  });

  // --- arama ---
  var girdi=document.getElementById('ara'), kutu=document.getElementById('ara-sonuc'),
      sayac=document.getElementById('ara-sayac'), veri=null, yukleniyor=false;
  if(!girdi) return;
  var kok_yol = girdi.getAttribute('data-kok') || '';

  function normalize(s){
    return (s||'').toLocaleLowerCase('tr')
      .replace(/[ıİ]/g,'i').replace(/[şŞ]/g,'s').replace(/[ğĞ]/g,'g')
      .replace(/[üÜ]/g,'u').replace(/[öÖ]/g,'o').replace(/[çÇ]/g,'c');
  }
  function yukle(){
    if(veri||yukleniyor) return Promise.resolve(veri);
    yukleniyor=true;
    return fetch(kok_yol+'arama.json').then(function(r){return r.json();})
      .then(function(j){veri=j;yukleniyor=false;return j;})
      .catch(function(){yukleniyor=false;return null;});
  }
  function kacir(s){return s.replace(/[&<>"]/g,function(c){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}

  function ciz(sonuclar,terim){
    if(!terim){kutu.classList.remove('acik');kutu.innerHTML='';sayac.textContent='';return;}
    kutu.classList.add('acik');
    sayac.textContent = sonuclar.length + ' sonuç';
    if(!sonuclar.length){
      kutu.innerHTML='<p class="ara-bos">“'+kacir(terim)+'” için kayıt yok. Farklı bir terim deneyin — '+
        'ya da <a href="'+kok_yol+'#katki">eksik kaynağı önerin</a>.</p>';
      return;
    }
    var h='<ul class="girdiler">';
    sonuclar.slice(0,40).forEach(function(k){
      h+='<li class="girdi"><a class="girdi-ad" href="'+kacir(k.u)+'">'+kacir(k.a)+'</a>'+
         '<p class="girdi-ac">'+kacir(k.d)+'</p><div class="girdi-meta">'+
         '<span class="etiket">'+kacir(k.t)+'</span>'+
         (k.l==='TR'?'<span class="etiket tr">türkçe</span>':'')+
         (k.s?'<span class="etiket altaysec">AltaySec</span>':'')+
         '<span class="etiket" style="border-style:dashed">'+kacir(k.b)+'</span></div></li>';
    });
    h+='</ul>';
    if(sonuclar.length>40) h+='<p class="ara-bos">İlk 40 sonuç gösteriliyor.</p>';
    kutu.innerHTML=h;
  }

  var zaman;
  girdi.addEventListener('input',function(){
    clearTimeout(zaman);
    zaman=setTimeout(function(){
      var terim=girdi.value.trim();
      if(!terim){ciz([],'');return;}
      yukle().then(function(j){
        if(!j){sayac.textContent='';return;}
        var n=normalize(terim), kelimeler=n.split(/\s+/).filter(Boolean);
        var bulunan=j.filter(function(k){
          var hedef=k._n||(k._n=normalize(k.a+' '+k.d+' '+k.t+' '+k.b));
          return kelimeler.every(function(w){return hedef.indexOf(w)>-1;});
        });
        bulunan.sort(function(x,y){
          var xa=normalize(x.a).indexOf(n), ya=normalize(y.a).indexOf(n);
          if(xa>-1&&ya<0) return -1; if(ya>-1&&xa<0) return 1; return 0;
        });
        ciz(bulunan,terim);
      });
    },110);
  });
  girdi.addEventListener('focus',yukle);

  document.addEventListener('keydown',function(e){
    if(e.key==='/'&&document.activeElement!==girdi&&!/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)){
      e.preventDefault();girdi.focus();
    }
    if(e.key==='Escape'&&document.activeElement===girdi){girdi.value='';ciz([],'');girdi.blur();}
  });
  var kisayol=document.getElementById('ara-kisayol');
  if(kisayol) kisayol.addEventListener('click',function(){girdi.focus();girdi.scrollIntoView({block:'center'});});

  // --- yan menüde aktif başlık ---
  var baglar=[].slice.call(document.querySelectorAll('.yan a[href^="#"]'));
  if(baglar.length&&'IntersectionObserver' in window){
    var hedefler=baglar.map(function(a){return document.querySelector(a.getAttribute('href'));}).filter(Boolean);
    var izleyici=new IntersectionObserver(function(girisler){
      girisler.forEach(function(g){
        if(!g.isIntersecting) return;
        baglar.forEach(function(a){a.classList.toggle('etkin',a.getAttribute('href')==='#'+g.target.id);});
      });
    },{rootMargin:'-76px 0px -70% 0px'});
    hedefler.forEach(function(h){izleyici.observe(h);});
  }
})();
"""


# --- ayrıştırma -------------------------------------------------------------

# Girdi sözleşmesi araclar/bicim.py'de tanımlı (tek kaynak).
# Biçim denetleyicisi de aynı yerden okur.


def satir_ici(metin: str) -> str:
    """Girdi açıklamasındaki `kod` ve **kalın** işaretlerini HTML'e çevirir."""
    p = html.escape(metin)
    p = re.sub(r"`([^`]+)`", r"<code>\1</code>", p)
    p = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", p)
    return p


def host(url: str) -> str:
    m = re.match(r"https?://(?:www\.)?([^/]+)", url)
    return m.group(1) if m else ""


def bolum_ayristir(yol: pathlib.Path):
    ham = yol.read_text(encoding="utf-8")
    baslik = re.search(r"^# (.+)$", ham, re.M).group(1).strip()
    m = re.search(r"^> (.+)$", ham, re.M)
    ozet = m.group(1).strip() if m else ""

    govde = ham.split("\n---\n", 1)[-1]
    parcalar = re.split(r"(?m)^## (.+)$", govde)
    kisimlar = []
    for i in range(1, len(parcalar), 2):
        ad = parcalar[i].strip()
        icerik = parcalar[i + 1]
        girdiler, nesir = [], []
        for satir in icerik.split("\n"):
            g = girdi_ayristir(satir)
            if g:
                girdiler.append(g)
            elif satir.strip() and not satir.startswith("- ["):
                nesir.append(satir)
        kisimlar.append({"ad": ad, "kimlik": kimlik(ad), "girdiler": girdiler,
                         "nesir": "\n".join(nesir).strip()})
    return baslik, ozet, kisimlar


def kimlik(metin: str) -> str:
    tr = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosucgiosu")
    s = metin.translate(tr).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "bolum"


def bolum_verisi():
    veriler = []
    for yol in sorted(KAYNAK_DIZIN.glob("*.md")):
        anahtar = yol.stem
        if anahtar not in META:
            print(f"uyarı: {anahtar} için meta tanımı yok, atlanıyor", file=sys.stderr)
            continue
        baslik, ozet, kisimlar = bolum_ayristir(yol)
        kisa_ad, meta_aciklama = META[anahtar]
        sayi = sum(len(k["girdiler"]) for k in kisimlar)
        veriler.append({
            "anahtar": anahtar, "no": anahtar[:2], "ad": kisa_ad, "baslik": baslik,
            "meta": meta_aciklama, "ozet": ozet, "sayi": sayi, "kisimlar": kisimlar,
            "cikti": f"bolum/{anahtar}.html",
        })
    return veriler


# --- şablon -----------------------------------------------------------------

def govde_ust(kok: str, aktif: str = "") -> str:
    return f"""<header class="ust"><div class="kabuk">
  <a class="marka" href="{kok}index.html">Yapay Zeka Güvenliği <b>Kaynakları</b></a>
  <nav>
    <a href="{kok}bolumler.html"{' aria-current="page"' if aktif == 'bolumler' else ''}>Bölümler</a>
    <a class="gizle-dar" href="{REPO_URL}/blob/main/CONTRIBUTING.md">Katkı</a>
    <a class="gizle-dar" href="{REPO_URL}">GitHub</a>
    <button class="dugme" id="ara-kisayol" type="button">Ara <kbd>/</kbd></button>
    <button class="dugme" id="tema-dugme" type="button" aria-label="Temayı değiştir" title="Temayı değiştir">◐</button>
  </nav>
</div></header>"""


def govde_alt(kok: str) -> str:
    return f"""<footer class="alt"><div class="kabuk">
  <span>CC BY 4.0 · Küratör <a href="https://github.com/fevziegeyurtsevenler">{YAZAR}</a> · <a href="https://altaysec.com.tr">AltaySec</a></span>
  <span>Son güncelleme {SON_GUNCELLEME} · <a href="{REPO_URL}">Kaynak repo</a> · <a href="{REPO_URL}/blob/main/CONTRIBUTING.md">Katkı ver</a></span>
</div></footer>"""


def ara_alani(kok: str, yer_tutucu: str) -> str:
    return f"""<section class="ara-alan"><div class="kabuk">
  <label class="ara-kutu" for="ara">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
    <input id="ara" type="search" autocomplete="off" data-kok="{kok}" placeholder="{yer_tutucu}" aria-label="Kaynaklarda ara">
    <span class="ara-sayac" id="ara-sayac"></span>
  </label>
  <div class="ara-sonuc" id="ara-sonuc" role="region" aria-live="polite"></div>
</div></section>"""


def sayfa(*, baslik, aciklama, govde, yol, jsonld):
    kanonik = f"{TABAN_URL}/{yol}" if yol else f"{TABAN_URL}/"
    tam_baslik = baslik if baslik == SITE_ADI else f"{baslik} — {SITE_ADI}"
    kok = "../" if "/" in yol else ""
    return f"""<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(tam_baslik)}</title>
<meta name="description" content="{html.escape(aciklama)}">
<link rel="canonical" href="{kanonik}">
<meta name="author" content="{YAZAR}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#FCFBF8" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#131519" media="(prefers-color-scheme:dark)">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{html.escape(SITE_ADI)}">
<meta property="og:locale" content="tr_TR">
<meta property="og:title" content="{html.escape(tam_baslik)}">
<meta property="og:description" content="{html.escape(aciklama)}">
<meta property="og:url" content="{kanonik}">
<meta property="og:image" content="{TABAN_URL}/afis.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(tam_baslik)}">
<meta name="twitter:description" content="{html.escape(aciklama)}">
<meta name="twitter:image" content="{TABAN_URL}/afis.svg">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='88'>🛡️</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONT_URL}">
<style>{CSS}</style>
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False, indent=1)}</script>
</head>
<body>
{govde_ust(kok, 'bolumler' if yol == 'bolumler.html' else '')}
<main>
{govde}
</main>
{govde_alt(kok)}
<script>{JS}</script>
</body>
</html>
"""


def girdi_html(g, kok=""):
    et = [f'<span class="etiket">{html.escape(g["tur"])}</span>']
    if g["dil"] == "TR":
        et.append('<span class="etiket tr">türkçe</span>')
    if g["altaysec"]:
        et.append('<span class="etiket altaysec">AltaySec</span>')
    if g["bakimsiz"]:
        et.append('<span class="etiket bakimsiz">bakımsız</span>')
    et.append(f'<span class="girdi-host">{html.escape(host(g["url"]))}</span>')
    return (
        f'<li class="girdi">'
        f'<a class="girdi-ad" href="{html.escape(g["url"])}" rel="noopener">{html.escape(g["ad"])}</a>'
        f'<p class="girdi-ac">{satir_ici(g["aciklama"])}</p>'
        f'<div class="girdi-meta">{"".join(et)}</div></li>'
    )


# --- üretim -----------------------------------------------------------------

def uret():
    bolumler = bolum_verisi()
    if not bolumler:
        print("hata: hiç bölüm bulunamadı", file=sys.stderr)
        return 1

    toplam = sum(b["sayi"] for b in bolumler)
    CIKTI.mkdir(parents=True, exist_ok=True)
    (CIKTI / "bolum").mkdir(exist_ok=True)
    (CIKTI / "afis.svg").write_text(
        (KOK / "varlik" / "afis-koyu.svg").read_text(encoding="utf-8"), encoding="utf-8"
    )

    # --- arama indeksi ---
    indeks = []
    for b in bolumler:
        for k in b["kisimlar"]:
            for g in k["girdiler"]:
                indeks.append({
                    "a": g["ad"], "u": g["url"], "d": g["aciklama"], "t": g["tur"],
                    "l": g["dil"], "s": g["altaysec"], "b": b["ad"],
                })
    (CIKTI / "arama.json").write_text(json.dumps(indeks, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    # --- ana sayfa ---
    dizin = "\n".join(
        f'<li><a href="{b["cikti"]}"><span class="no">{b["no"]}</span>'
        f'<span class="ad">{html.escape(b["ad"])}</span>'
        f'<span class="ozet">{html.escape(b["ozet"])}</span>'
        f'<span class="lider"></span><span class="sayi">{b["sayi"]}</span></a></li>'
        for b in bolumler
    )

    YOLLAR = [
        ("Alana yeni giriyorum", "Prompt injection'ın ne olduğunu okuyun, sonra Gandalf'ta ilk sistem prompt'unu sızdırın.",
         "bolum/01-prompt-injection.html", "Prompt Injection"),
        ("Uygulamamı güvene almam lazım", "Önce hangi riske bakacağınızı standartlardan öğrenin, sonra guardrail seçin.",
         "bolum/04-degerlendirme-standartlar.html", "Standartlar"),
        ("Ajan veya MCP sistemi kuruyorum", "Ölümcül üçlüyü kontrol edin: özel veri, güvenilmeyen girdi, dışarı iletişim.",
         "bolum/06-agent-mcp-guvenligi.html", "Ajan güvenliği"),
        ("Türkçede ne değişiyor?", "İngilizce için ölçülmüş hiçbir guardrail sonucu Türkçeye doğrudan taşınmıyor.",
         "bolum/08-turkce-kaynaklar-veri-setleri.html", "Türkçe bulgular"),
    ]
    yollar = "\n".join(
        f'<li class="yol"><h3>{html.escape(a)}</h3><p>{html.escape(p)}</p>'
        f'<a class="git" href="{u}">{html.escape(t)} →</a></li>'
        for a, p, u, t in YOLLAR
    )

    OLCUMLER = [
        ("%94,6", "Türkçe büyük İ küçültüldüğünde naif kelime filtreleri atlatılıyor.",
         "turkish-casefold-evasion", "https://github.com/fevziegeyurtsevenler/turkish-casefold-evasion"),
        ("%59", "Bir guard modeli zararsız Türkçe istekleri reddediyor — aynı setin İngilizcesinde bu oran %0,8.",
         "turkish-over-refusal-set", "https://github.com/fevziegeyurtsevenler/turkish-over-refusal-set"),
        ("%83", "Popüler bir jailbreak sınıflandırıcısı Türkçe saldırıları kaçırıyor.",
         "guardrail-arena", "https://github.com/fevziegeyurtsevenler/guardrail-arena"),
    ]
    olcumler = "\n".join(
        f'<div class="olcum"><div class="rakam">{r}</div><p class="ne">{html.escape(n)}</p>'
        f'<p class="kaynak"><a href="{u}" rel="noopener">{html.escape(k)} ↗</a></p></div>'
        for r, n, k, u in OLCUMLER
    )

    ana_govde = f"""<section class="tez"><div class="kabuk">
  <p class="tez-etiket can can-1">Bu liste neden Türkçe</p>
  <div class="kanit">
    <span class="kod can can-1">"<span class="nokta">İ</span>GNORE".lower()</span>
    <span class="ok can can-2">→</span>
    <span class="kod can can-3">"i̇gnore"</span>
    <span class="esitsiz can can-4">≠</span>
    <span class="kod can can-5">"ignore"</span>
  </div>
  <p class="can can-6"><span class="kanit-sonuc">filtre atlandı · %94,6</span></p>
  <h1 class="can can-2">Yapay zeka güvenliği kaynakları</h1>
  <p class="tez-alt can can-3">Türkçe noktalı İ küçültüldüğünde İngilizce <code>ignore</code> ile eşleşmiyor;
     kelime listesine dayanan filtre saldırıyı göremiyor. <b>İngilizce için ölçülmüş hiçbir güvenlik sonucu
     Türkçeye doğrudan taşınmıyor</b> — bu kılavuz o boşluğu kapatmak için var.</p>
  <p class="kunye can can-4">
    <span><b>{toplam}</b> kaynak</span>
    <span><b>{len(bolumler)}</b> bölüm</span>
    <span>her biri <b>açılıp okundu</b></span>
    <span>ölü linkler <b>haftalık</b> taranıyor</span>
  </p>
</div></section>

{ara_alani('', 'Kaynaklarda ara — “prompt injection”, “guardrail”, “MCP”, “dataset”…')}

<section class="blok"><div class="kabuk">
  <h2 class="blok-basi">Nereden başlamalı</h2>
  <ul class="yollar">{yollar}</ul>
</div></section>

<section class="blok"><div class="kabuk">
  <h2 class="blok-basi">Bölümler</h2>
  <ul class="dizin">{dizin}</ul>
</div></section>

<section class="blok"><div class="kabuk">
  <h2 class="blok-basi">Ölçülmüş bulgular</h2>
  <div class="olcumler">{olcumler}</div>
  <p class="not">Bunlar tahmin değil; her biri açık veri seti ve tekrar üretilebilir yöntemle
     birlikte yayımlandı. Bir guardrail'in İngilizcede iyi olması, Türkçede iyi olduğu anlamına gelmiyor.</p>
</div></section>

<section class="blok" id="katki"><div class="kabuk">
  <h2 class="blok-basi">Katkı</h2>
  <p class="not" style="max-width:64ch;font-size:1rem;color:var(--murekkep)">
     Bölüm sahibi, atama veya sıra yok — istediğiniz bölüme PR açabilirsiniz. Tek kural: her kaynağın
     yanında neden listelendiğini anlatan 1-2 cümlelik Türkçe açıklama olacak ve eklediğiniz kaynağı
     açıp okumuş olacaksınız. Zayıf bulduğunuz bir girdinin çıkarılmasını önermek de katkıdır; bu liste
     eklendikçe değil, elendikçe değer kazanıyor.</p>
  <p class="not"><a href="{REPO_URL}/blob/main/CONTRIBUTING.md">Katkı rehberi ↗</a> ·
     <a href="{REPO_URL}">Depo ↗</a></p>
</div></section>"""

    ana_jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "WebSite", "@id": f"{TABAN_URL}/#website", "name": SITE_ADI,
             "url": f"{TABAN_URL}/", "description": SITE_ACIKLAMA, "inLanguage": "tr-TR",
             "author": {"@type": "Person", "name": YAZAR}},
            {"@type": "CollectionPage", "@id": f"{TABAN_URL}/#collection", "name": SITE_ADI,
             "url": f"{TABAN_URL}/", "description": SITE_ACIKLAMA, "inLanguage": "tr-TR",
             "dateModified": SON_GUNCELLEME, "isPartOf": {"@id": f"{TABAN_URL}/#website"},
             "hasPart": [{"@type": "WebPage", "name": b["ad"],
                          "url": f"{TABAN_URL}/{b['cikti']}", "description": b["meta"]}
                         for b in bolumler]},
        ],
    }
    (CIKTI / "index.html").write_text(
        sayfa(baslik=SITE_ADI, aciklama=SITE_ACIKLAMA, govde=ana_govde, yol="", jsonld=ana_jsonld),
        encoding="utf-8")

    # --- bölüm listesi ---
    liste_govde = f"""<section class="blok" style="border-bottom:0"><div class="kabuk">
  <p class="bolum-no">Dizin</p>
  <h1 style="font-family:var(--ff-serif);font-weight:700;font-size:clamp(1.9rem,5vw,2.8rem);line-height:1.1;letter-spacing:-.02em;margin:0 0 .8rem">Bölümler</h1>
  <p class="not" style="margin:0 0 2rem">{len(bolumler)} bölüm, toplam {toplam} küratörlü kaynak.</p>
  <ul class="dizin">{dizin.replace('href="bolum/', 'href="bolum/')}</ul>
</div></section>
{ara_alani('', 'Tüm bölümlerde ara…')}"""
    (CIKTI / "bolumler.html").write_text(
        sayfa(baslik="Bölümler", aciklama=f"Yapay zeka güvenliği kılavuzunun {len(bolumler)} bölümü: "
              + ", ".join(b["ad"] for b in bolumler) + ".",
              govde=liste_govde, yol="bolumler.html",
              jsonld={"@context": "https://schema.org", "@type": "ItemList", "name": "Bölümler",
                      "numberOfItems": len(bolumler),
                      "itemListElement": [{"@type": "ListItem", "position": i, "name": b["ad"],
                                           "url": f"{TABAN_URL}/{b['cikti']}"}
                                          for i, b in enumerate(bolumler, 1)]}),
        encoding="utf-8")

    # --- bölüm sayfaları ---
    for i, b in enumerate(bolumler):
        yan = "\n".join(
            f'<li><a href="#{k["kimlik"]}">{html.escape(k["ad"])}<span>{len(k["girdiler"])}</span></a></li>'
            for k in b["kisimlar"] if k["girdiler"] or k["nesir"]
        )
        kisimlar_html = []
        for k in b["kisimlar"]:
            parca = [f'<h2 id="{k["kimlik"]}">{html.escape(k["ad"])}'
                     + (f'<span class="adet">{len(k["girdiler"])} kaynak</span>' if k["girdiler"] else "")
                     + "</h2>"]
            if k["nesir"]:
                parca.append(markdown.markdown(k["nesir"], extensions=["tables"]))
            if k["girdiler"]:
                parca.append('<ul class="girdiler">' + "".join(girdi_html(g, "../") for g in k["girdiler"]) + "</ul>")
            kisimlar_html.append("\n".join(parca))

        onceki = bolumler[i - 1] if i > 0 else None
        sonraki = bolumler[i + 1] if i < len(bolumler) - 1 else None
        gecis = []
        if onceki:
            gecis.append(f'<a href="{onceki["anahtar"]}.html"><span class="yon">← Önceki bölüm</span>'
                         f'<span class="hedef">{html.escape(onceki["ad"])}</span></a>')
        else:
            gecis.append('<span></span>')
        if sonraki:
            gecis.append(f'<a class="sag" href="{sonraki["anahtar"]}.html"><span class="yon">Sonraki bölüm →</span>'
                         f'<span class="hedef">{html.escape(sonraki["ad"])}</span></a>')

        govde = f"""{ara_alani('../', 'Tüm kaynaklarda ara…')}
<div class="kabuk"><div class="sayfa">
  <aside class="yan"><p class="yan-basi">Bu bölümde</p><ol>{yan}</ol></aside>
  <article class="icerik">
    <p class="bolum-no">Bölüm {b["no"]} · {b["sayi"]} kaynak</p>
    <h1>{html.escape(b["baslik"])}</h1>
    <p class="giris">{html.escape(b["ozet"])}</p>
    {"".join(kisimlar_html)}
    <nav class="gecis">{"".join(gecis)}</nav>
  </article>
</div></div>"""

        jsonld = {
            "@context": "https://schema.org", "@type": "Article",
            "headline": f"{b['ad']} — Türkçe kaynaklar", "description": b["meta"],
            "inLanguage": "tr-TR", "url": f"{TABAN_URL}/{b['cikti']}",
            "dateModified": SON_GUNCELLEME, "author": {"@type": "Person", "name": YAZAR},
            "isPartOf": {"@id": f"{TABAN_URL}/#website"},
            "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": SITE_ADI, "item": f"{TABAN_URL}/"},
                {"@type": "ListItem", "position": 2, "name": b["ad"], "item": f"{TABAN_URL}/{b['cikti']}"}]},
        }
        (CIKTI / b["cikti"]).write_text(
            sayfa(baslik=b["ad"], aciklama=b["meta"], govde=govde, yol=b["cikti"], jsonld=jsonld),
            encoding="utf-8")

    # --- sitemap + robots ---
    yollar_x = ["", "bolumler.html"] + [b["cikti"] for b in bolumler]
    girisler = "\n".join(
        f"  <url><loc>{TABAN_URL}/{y}</loc><lastmod>{SON_GUNCELLEME}</lastmod>"
        f"<changefreq>weekly</changefreq><priority>{'1.0' if y == '' else '0.8'}</priority></url>"
        for y in yollar_x)
    (CIKTI / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{girisler}\n</urlset>\n", encoding="utf-8")
    (CIKTI / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {TABAN_URL}/sitemap.xml\n", encoding="utf-8")
    (CIKTI / ".nojekyll").write_text("", encoding="utf-8")

    print(f"site üretildi: {len(bolumler)} bölüm, {toplam} kaynak, "
          f"{len(yollar_x)} sayfa, {len(indeks)} arama kaydı")
    return 0


if __name__ == "__main__":
    sys.exit(uret())
