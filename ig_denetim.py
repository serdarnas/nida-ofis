"""Instagram ajan çıktısı için yerel, deterministik ön denetim (ağ yok, bağımlılık yok).

`instagram-agent-skill` (MIT, Jake Schincariol) fikirlerinden Türkçeye uyarlandı: kanca puanı,
senaryo süre/beat kontrolü, altyazı linti, kalıp ifade temizliği. Üzerine Nida'ya özel iki kontrol
eklendi: katalog dışı fiyat ve belgesiz sağlık iddiası.

DÜRÜSTLÜK NOTU: Bunlar yerel sezgisel kurallardır; izlenme tahmini DEĞİLDİR ve Türkçe için
istatistiksel olarak doğrulanmamıştır. Kötü kancayı (selamlama, somutluk yok, çok uzun) yakalar;
iki iyi kancadan hangisinin yayılacağını söyleyemez.

Kullanım:
    python3 ig_denetim.py cikti/instagram/<koşu>.md
    python3 ig_denetim.py --metin "Bir litre yağ 380 TL"   # yalnız genel kontroller
Ajan çıktısı <KANCA>, <SENARYO>, <EKRAN_METNI>, <ALTYAZI>, <ILK_YORUM> etiketlerini kullanır.
"""
import os
import re
import sys
import unicodedata

KOK = os.path.dirname(os.path.abspath(__file__))
VERI = os.path.join(os.environ.get("OFIS_DATA_DIR") or KOK, "veri")

SOZ = re.compile(r"[0-9A-Za-zÇĞİÖŞÜçğıöşü$%₺'’-]+")
ETIKET = re.compile(r"<(KANCA|SENARYO|EKRAN_METNI|ALTYAZI|ILK_YORUM)>(.*?)</\1>", re.S)
HASHTAG = re.compile(r"#[\wÇĞİÖŞÜçğıöşü]+")
EMOJI = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")
GORUNMEZ = re.compile(r"[​-‏⁠⁦-⁩﻿­  ]")
LINK = re.compile(r"https?://|www\.|\b[\w-]+\.(?:com|net|org|tr|co)\b", re.I)
YER_TUTUCU = re.compile(r"\{\{.*?\}\}")

JENERIK_ETIKET = {"#viral", "#fyp", "#foryou", "#kesfet", "#keşfet", "#explore", "#explorepage", "#reels",
                  "#reel", "#instagram", "#instagood", "#trend", "#takip", "#like4like", "#follow"}
GIRIS = re.compile(r"^\W*(merhaba|selam|herkese|arkadaşlar|günaydın|hoş\s?geldin|bu videoda|bugün sizlere|"
                   r"bugün size|sevgili|değerli|ben\s+\w+,)", re.I)
SAGLIK = re.compile(r"\b(tedavi|önler|önleyici|iyileştir|şifa|kanser|diyabet|şeker hastal|kolesterol(ü)? düş|"
                    r"tansiyon|kalp hastal|bağışıklığ?ı? (güçlend|artır)|hastalık|ağrı kes|kan şekeri)", re.I)
KALIP = ["eşsiz", "benzersiz", "lezzet şöleni", "kaçırmayın", "kaçırma sakın", "sağlığınıza sağlık", "hemen takip et",
         "etiketle", "algoritma", "bu videoda", "merhaba arkadaşlar", "keşfedin", "damak çatlatan", "mükemmel",
         "inanılmaz", "harika bir", "vazgeçilmez", "olmazsa olmaz", "hepsi bu kadar değil", "yeni bir boyut",
         "kaçırılmayacak", "dünyasına hoş", "yolculuğuna çık", "ayrıcalıklı bir deneyim", "doğanın armağanı",
         "bambaşka", "tadına doyum olmayan", "görmeniz gereken", "durdurucu", "hemen tıkla", "tüm detaylar"]
CAGRI = {
    "yorum": re.compile(r"yorum(a|lara)?\b.{0,25}\b(yaz|bırak)|\byaz\b.{0,15}\byorum", re.I),
    "kaydet": re.compile(r"\bkaydet", re.I),
    "takip": re.compile(r"takip\s?et", re.I),
    "dm/whatsapp": re.compile(r"\bdm\b|mesaj\s(at|gönder)|whatsapp|\bd\.?m\.?\b", re.I),
    "paylaş": re.compile(r"\bpaylaş", re.I),
    "etiketle": re.compile(r"etiketle", re.I),
    "sipariş/link": re.compile(r"sipariş\s?ver|biyografi|bio(daki)?\s?link|linke? tıkla", re.I),
}
RAKAM_KELIME = {"sıfır", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on", "yirmi", "otuz", "kırk",
                "elli", "yüz", "bin", "milyon", "yarım", "çeyrek", "iki katı"}
BIRIM = re.compile(r"\d[\d.,]*\s?(tl|₺|kg|kilo|litre|lt|l\b|ml|gün|saat|dakika|dk|sn|saniye|yıl|ay|hafta|ağaç|"
                   r"teneke|şişe|%)", re.I)
SOMUT_KELIME = {"edremit", "kazdağı", "kazdağları", "ayvalık", "havran", "zeytinyağı", "zeytin", "teneke", "şişe",
                "sızma", "çizik", "sele", "kırma", "hasat", "sıkım", "ağaç", "tank", "kalibre", "kova", "koli",
                "nida", "ege", "balıkesir", "kolonya", "sabun"}
KITLE = {"sen", "senin", "seni", "sana", "siz", "sizin", "sizi", "size", "bak", "dur", "dikkat", "sakın", "eğer",
         "kimse", "kimsenin", "herkes", "yanlış", "hata", "pahalı", "kaybet", "kaybettim", "para", "gerek",
         "durdur", "bırak", "yapma", "bilmeyen", "biliyor", "biliyorsan"}


def tr_kucuk(s):
    return s.replace("İ", "i").replace("I", "ı").lower()


def kelimeler(s):
    return SOZ.findall(s)


def blok_ayir(metin):
    bloklar = {}
    for ad, icerik in ETIKET.findall(metin):
        bloklar.setdefault(ad, []).append(icerik.strip())
    return bloklar


# ------------------------------------------------------------------ kanca
def kanca_puani(satir):
    """(puan, [not]) — her kontrol 0-100; 0.6*ortalama + 0.4*en zayıf."""
    k = tr_kucuk(satir)
    sozler = kelimeler(k)
    n = len(sozler)
    notlar = []
    saniye = n / 2.7  # ~160 kelime/dk
    sure = 100 if saniye <= 3 else 70 if saniye <= 4 else 40 if saniye <= 5 else 15
    if sure < 100:
        notlar.append(f"{n} kelime ≈ {saniye:.1f} sn (hedef ≤3 sn, ≈8 kelime)")
    sayisal = bool(BIRIM.search(k)) or any(c.isdigit() for c in k) or bool(RAKAM_KELIME & set(sozler))
    yer_urun = bool(SOMUT_KELIME & set(sozler))
    somut = 100 if sayisal else 70 if yer_urun else 30
    if somut < 100:
        notlar.append("rakam yok" if yer_urun else "ne rakam ne ürün/yer var, kanca genel kalıyor")
    giris = 0 if GIRIS.search(satir) else 100
    if not giris:
        notlar.append("selamlama/giriş cümlesiyle başlıyor")
    kitle = 100 if (KITLE & set(sozler)) else 60 if re.search(r"\b(ben|biz|bizim|benim)\b|\bm[ıiuü]ş\b|\bd[ıiuü]m\b", k) else 30
    if kitle < 100:
        notlar.append("izleyiciye seslenme/risk yok")
    on = sozler[:5]
    yuk = 100 if (any(c.isdigit() for c in " ".join(on)) or (SOMUT_KELIME & set(on))) else 60 if (sayisal or yer_urun) else 30
    if yuk < 100:
        notlar.append("somut öğe ilk 5 kelimede değil")
    puanlar = [sure, somut, giris, kitle, yuk]
    puan = round(0.6 * sum(puanlar) / len(puanlar) + 0.4 * min(puanlar))
    return puan, notlar


def karar(p):
    return "GÜÇLÜ" if p >= 75 else "İDARE" if p >= 55 else "ZAYIF"


# ------------------------------------------------------------------ senaryo
def senaryo_kontrol(metin, wpm=160):
    satirlar = []
    for s in metin.splitlines():
        s = re.sub(r"^\s*(\d+[:.]\d+\s*[-–]\s*\d+[:.]\d+|\[?\d+\s?sn\]?|[-*•]|\d+[.)])\s*", "", s).strip()
        s = re.sub(r"^(kanca|hook|neden|gövde|vaat|çağrı|döngü)\s*[:：]\s*", "", s, flags=re.I)
        if s:
            satirlar.append(s)
    out = []
    if not satirlar:
        return [("WARN", "senaryo: boş")]
    hiz = wpm / 60.0
    sureler = [len(kelimeler(s)) / hiz + 0.3 for s in satirlar]
    toplam = sum(sureler)
    out.append(("INFO", f"senaryo: {len(satirlar)} beat, ≈{toplam:.0f} sn ({wpm} kelime/dk varsayımıyla)"))
    if sureler[0] > 3.0:
        out.append(("WARN", f"senaryo: kanca satırı ≈{sureler[0]:.1f} sn; ilk 3 saniyeye sığmalı"))
    uzun = [i + 1 for i, d in enumerate(sureler) if i > 0 and d > 4.0]
    if uzun:
        out.append(("WARN", f"senaryo: {len(uzun)} beat 4 sn'den uzun (beat {', '.join(map(str, uzun[:6]))}); kare değişimi için böl"))
    if toplam < 15:
        out.append(("WARN", f"senaryo: ≈{toplam:.0f} sn; 15-45 sn aralığının altında"))
    elif toplam > 45:
        out.append(("WARN", f"senaryo: ≈{toplam:.0f} sn; 45 sn'yi aşıyor, tek fikre indir"))
    ilk = {w for w in kelimeler(tr_kucuk(satirlar[0])) if len(w) >= 4}
    son = {w for w in kelimeler(tr_kucuk(satirlar[-1])) if len(w) >= 4}
    if len(satirlar) > 2 and not (ilk & son):
        out.append(("WARN", "senaryo: son satır kancadan bir kelime tekrar etmiyor (döngü yok)"))
    if GIRIS.search(satirlar[0]):
        out.append(("FAIL", "senaryo: selamlama/giriş cümlesiyle başlıyor; videoyu 6. saniyedeki cümleyle başlat"))
    return out


def ekran_kontrol(metin):
    out = []
    for s in [x.strip() for x in metin.splitlines() if x.strip()]:
        govde = re.sub(r"^\s*(\d+[:.]\d+\s*[-–]?\s*\d*[:.]?\d*|[-*•]|\d+[.)])\s*[:\-–]?\s*", "", s)
        if len(kelimeler(govde)) > 6:
            out.append(("WARN", f"ekran metni 6 kelimeyi aşıyor: “{govde[:50]}”"))
    return out or [("OK", "ekran metni: kartlar ≤6 kelime")]


# ------------------------------------------------------------------ altyazı
def altyazi_kontrol(metin):
    out = []
    t = metin.strip()
    onizleme = " ".join(t.split())[:125]
    out.append(("INFO", f"altyazı önizleme (125 karakter): “{onizleme}{'…' if len(' '.join(t.split())) > 125 else ''}”"))
    if len(t) > 2200:
        out.append(("FAIL", f"altyazı {len(t)} karakter; sınır 2200"))
    if t and (EMOJI.match(t[0]) or t[0] == "#" or GIRIS.search(t)):
        out.append(("WARN", "altyazı emoji/hashtag/selamla başlıyor; ilk 125 karakter boşa gidiyor"))
    et = HASHTAG.findall(t)
    if len(et) > 5:
        out.append(("FAIL", f"{len(et)} hashtag; Instagram 18 Aralık 2025'ten beri en çok 5'e izin veriyor"))
    jen = [h for h in et if tr_kucuk(h) in JENERIK_ETIKET]
    if jen:
        out.append(("FAIL", f"jenerik hashtag hiçbir şey anlatmıyor: {' '.join(jen)}"))
    if LINK.search(t):
        out.append(("FAIL", "altyazıda link/alan adı var; tıklanmaz. İlk yoruma veya biyografiye taşı"))
    bulunan = [ad for ad, desen in CAGRI.items() if desen.search(t)]
    if len(bulunan) > 1:
        out.append(("WARN", f"{len(bulunan)} farklı çağrı ({', '.join(bulunan)}); tek çağrı bırak"))
    elif not bulunan:
        out.append(("WARN", "çağrı yok; tek bir eylem iste (yorumla YAĞ / kaydet / DM)"))
    em = len(EMOJI.findall(t))
    if em > 2 or (t and em * 100 / len(t) > 4):
        out.append(("WARN", f"{em} emoji; altyazıda en çok 2 kullan"))
    return out


# ------------------------------------------------------------------ genel (tüm metin)
def _fiyat_oku(s):
    s = s.replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    elif "." in s and len(s.split(".")[-1]) == 3:
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def katalog_oku():
    fiyatlar, tukenen = set(), []
    try:
        with open(os.path.join(VERI, "urun-fiyat-stok.md"), encoding="utf-8") as f:
            for satir in f:
                if not satir.startswith("|"):
                    continue
                m = re.search(r"\*\*([\d.,]+)\s*TL\*\*", satir)
                if m:
                    p = _fiyat_oku(m.group(1))
                    if p is not None:
                        fiyatlar.add(round(p, 2))
                if "Tükendi" in satir:
                    h = [c.strip() for c in satir.strip().strip("|").split("|")]
                    if len(h) > 1:
                        tukenen.append(h[1])
    except OSError:
        pass
    return fiyatlar, tukenen


def genel_kontrol(metin):
    out = []
    fiyatlar, tukenen = katalog_oku()
    gorulen = []
    for m in re.finditer(r"(\d[\d.,]*)\s?(?:TL|₺)", metin, re.I):
        p = _fiyat_oku(m.group(1))
        if p is None or p in gorulen:
            continue
        gorulen.append(p)
        if fiyatlar and not any(abs(p - x) < 0.51 for x in fiyatlar):
            out.append(("WARN", f"{m.group(0).strip()} katalogdaki fiyatlarla eşleşmiyor; kampanya fiyatıysa doğrula"))
    k = tr_kucuk(metin)
    for ad in tukenen:
        cekirdek = re.sub(r"\(.*?\)|\b\d+([.,]\d+)?\s?(gr|g|kg|ml|lt|litre|l)\b|\bdoğal\b|\bkutulu\b", " ", tr_kucuk(ad))
        cekirdek = " ".join(cekirdek.split())
        if len(cekirdek) >= 8 and (cekirdek in k or tr_kucuk(ad) in k):
            out.append(("FAIL", f"tükenen ürün öne çıkarılıyor: {ad}"))
    sag = SAGLIK.findall(metin)
    if sag:
        out.append(("FAIL", "belgesiz sağlık iddiası olabilir (tedavi/önleme/hastalık dili); kullanım anlatımına çevir"))
    kalip = [p for p in KALIP if p in k]
    if kalip:
        out.append(("WARN", f"kalıp/AI izi ifadeler ({len(kalip)}): {', '.join(kalip[:5])}"))
    if "—" in metin or "–" in metin:
        out.append(("WARN", "uzun/orta çizgi var; virgül veya nokta kullan"))
    if GORUNMEZ.search(metin):
        out.append(("WARN", "görünmez karakter bulundu (sıfır genişlikli boşluk vb.); metni düz metin olarak yeniden yapıştır"))
    yt = YER_TUTUCU.findall(metin)
    if yt:
        out.append(("INFO", f"doldurulacak yer tutucu: {len(yt)} ({', '.join(sorted(set(yt))[:4])})"))
    return out


# ------------------------------------------------------------------ birleştir
def denetle(metin, wpm=None):
    wpm = wpm or int(os.environ.get("IG_WPM") or 160)
    bloklar = blok_ayir(metin)
    sonuc = []
    kancalar = []
    for b in bloklar.get("KANCA", []):
        kancalar += [re.sub(r"^\s*(\d+[.)]|[-*•])\s*", "", s).strip() for s in b.splitlines() if s.strip()]
    if kancalar:
        puanli = sorted(((kanca_puani(s), s) for s in kancalar), key=lambda x: -x[0][0])
        for (p, notlar), s in puanli:
            sonuc.append(("INFO", f"kanca {p:3d} {karar(p):5s} “{s[:80]}”" + (f" — {'; '.join(notlar[:2])}" if notlar else "")))
        if puanli[0][0][0] < 50:
            sonuc.append(("FAIL", "en iyi kanca bile 50'nin altında; düzenleme değil yeni fikir/kanca gerekir"))
    else:
        sonuc.append(("WARN", "<KANCA> etiketi yok; kanca puanlanamadı"))
    for b in bloklar.get("SENARYO", []):
        sonuc += senaryo_kontrol(b, wpm)
    for b in bloklar.get("EKRAN_METNI", []):
        sonuc += ekran_kontrol(b)
    for b in bloklar.get("ALTYAZI", []):
        sonuc += altyazi_kontrol(b)
    if not bloklar:
        sonuc.append(("WARN", "hiç etiket bulunamadı; yalnız genel kontroller yapıldı"))
    sonuc += genel_kontrol(metin)

    fail = sum(1 for s, _ in sonuc if s == "FAIL")
    warn = sum(1 for s, _ in sonuc if s == "WARN")
    sira = {"FAIL": 0, "WARN": 1, "INFO": 2, "OK": 3}
    sonuc.sort(key=lambda x: sira[x[0]])
    durum = "DÜZELT" if fail else "İNCELE" if warn else "HAZIR"
    satirlar = ["---", "## OTOMATİK DENETİM (ig_denetim.py)", ""]
    satirlar += [f"- [{s}] {m}" for s, m in sonuc]
    satirlar += ["", f"**SONUÇ: {durum}** · {fail} FAIL · {warn} WARN",
                 "_Yerel sezgisel kontrol: izlenme tahmini değildir, Türkçe için doğrulanmamıştır. Yayın kararı ve son okuma sende._"]
    return "\n".join(satirlar)


def main(argv):
    if len(argv) >= 3 and argv[1] == "--metin":
        print(denetle(argv[2]))
        return 0
    if len(argv) != 2:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        print(denetle(f.read()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
