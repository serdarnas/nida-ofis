"""Rapor postacısı: sabah özeti, gün sonu raporu ve hata uyarılarını SAHİBİNE e-posta ile gönderir.

Güvenlik kuralları (bilinçli sınırlar):
- Alıcı yalnız RAPOR_ALICI (varsayılan serdarnas@gmail.com). Ajanlar bu modüle alıcı veremez;
  müşteriye/dışarıya mail gönderme ofisin kapsamı DIŞINDA kalmaya devam eder.
- SMTP parolası yalnız ortam değişkeninden (.env / Coolify) okunur; loglanmaz, çıktıya yazılmaz.
- SMTP tanımlı değilse rapor gönderilmez, cikti/rapor/ altına HTML olarak kaydedilir.

Ortam değişkenleri: bkz. .env.example
Komut satırı:
    python3 rapor_mail.py sabah            # kuru çalıştırma: üretir, cikti/rapor/ altına kaydeder
    python3 rapor_mail.py gun-sonu --gonder  # gerçekten gönderir
    python3 rapor_mail.py test --gonder    # kısa bağlantı testi maili
"""
import html
import json
import os
import re
import smtplib
import ssl
import sys
import time
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

import ortak
import otonom_takvim

VARSAYILAN_ALICI = "serdarnas@gmail.com"
ALICI_DESENI = re.compile(r"[^@\s,;<>]+@[^@\s,;<>]+\.[^@\s,;<>]+")
DURUM_DOSYASI = os.path.join(ortak.VERI_DIZINI, "rapor_durum.json")
RAPOR_DIZINI = os.path.join(ortak.CIKTI_DIZINI, "rapor")
BEKLENEN_VERILER = {
    "fiyat-listesi.csv": "ürün maliyeti ve hedef marj",
    "satis.csv": "kanal/ürün bazlı satışlar",
    "musteriler.csv": "müşteri ve B2B lead listesi",
}


# ---------------------------------------------------------------- yapılandırma
def ayar():
    e = os.environ
    try:
        port = int(e.get("SMTP_PORT") or 587)
    except ValueError:
        port = 587
    return {
        "alici": (e.get("RAPOR_ALICI") or VARSAYILAN_ALICI).strip(),
        "host": (e.get("SMTP_HOST") or "").strip(),
        "port": port,
        "kullanici": (e.get("SMTP_USER") or "").strip(),
        "sifre": e.get("SMTP_PASSWORD") or "",
        "gonderen": (e.get("SMTP_FROM") or e.get("SMTP_USER") or "").strip(),
        "sabah": (e.get("RAPOR_SABAH_SAAT") or "08:00").strip(),
        "gun_sonu": (e.get("RAPOR_GUN_SONU_SAAT") or "18:30").strip(),
        "aktif": (e.get("RAPOR_MAIL_AKTIF") or "1").strip().lower() not in ("0", "false", "hayir", "hayır"),
        "gorev_maili": (e.get("RAPOR_GOREV_MAILI") or "0").strip().lower() in ("1", "true", "evet"),
    }


def smtp_hazir(cfg):
    return bool(cfg["host"] and cfg["kullanici"] and cfg["sifre"] and cfg["gonderen"]
                and ALICI_DESENI.fullmatch(cfg["alici"]))


def _saat(metin, varsayilan):
    try:
        s, d = metin.split(":")
        s, d = int(s), int(d)
        if 0 <= s < 24 and 0 <= d < 60:
            return s, d
    except ValueError:
        pass
    return varsayilan


# ---------------------------------------------------------------- veri toplama
def _temiz(metin, sinir=240):
    metin = re.sub(r"[*#`>_]+", "", metin or "")
    metin = re.sub(r"\s+", " ", metin).strip()
    return metin if len(metin) <= sinir else metin[:sinir].rstrip() + "…"


def _gorevler():
    try:
        otonom_takvim.gecmis_kosulari_senkronla()
    except Exception:
        pass
    return otonom_takvim._oku_ham().get("gorevler", [])


def _cikti_yolu(g):
    if g.get("kosu_id") and g.get("ajan"):
        return f"cikti/{g['ajan']}/{g['kosu_id']}.md"
    return ""


def tukenenler():
    yol = os.path.join(ortak.VERI_DIZINI, "urun-fiyat-stok.md")
    sonuc = []
    try:
        with open(yol, encoding="utf-8") as f:
            for satir in f:
                if satir.startswith("|") and "Tükendi" in satir:
                    h = [c.strip().strip("*") for c in satir.strip().strip("|").split("|")]
                    if len(h) >= 4:
                        sonuc.append(f"{h[1]} ({h[2]})")
    except OSError:
        pass
    return sonuc


def token_ozeti(gun):
    yol = os.path.join(ortak.DURUM_DIZINI, f"token-{gun}.json")
    toplam = 0
    try:
        with open(yol, encoding="utf-8") as f:
            veri = json.load(f)
        for ajan in veri.values():
            for kaynak in ajan.values():
                toplam += int(kaynak.get("input_tokens", 0)) + int(kaynak.get("output_tokens", 0))
    except (OSError, ValueError, AttributeError):
        return None
    return toplam


def eksik_veriler():
    return [f"{ad} — {neden}" for ad, neden in BEKLENEN_VERILER.items()
            if not os.path.isfile(os.path.join(ortak.VERI_DIZINI, ad))]


def rapor_verisi(tur):
    simdi = datetime.now()
    bugun = simdi.strftime("%Y-%m-%d")
    yarin = (simdi + timedelta(days=1)).strftime("%Y-%m-%d")
    simdi_str = simdi.strftime("%Y-%m-%d %H:%M")
    gorevler = _gorevler()

    bugun_biten = [g for g in gorevler if g.get("durum") == "yapildi" and str(g.get("bitis_saati", "")).startswith(bugun)]
    bugun_hata = [g for g in gorevler if g.get("durum") == "hata" and str(g.get("bitis_saati", "")).startswith(bugun)]
    calisan = [g for g in gorevler if g.get("durum") == "calisiyor"]
    bugun_bekleyen = [g for g in gorevler if g.get("durum") == "yapilacak" and str(g.get("tarih_saat", "")).startswith(bugun)]
    geciken = [g for g in gorevler if g.get("durum") == "yapilacak" and str(g.get("tarih_saat", "9999")) < simdi_str]
    yarin_plan = sorted((g for g in gorevler if g.get("durum") == "yapilacak" and str(g.get("tarih_saat", "")).startswith(yarin)),
                        key=lambda g: g.get("tarih_saat", ""))
    onay_bekleyen = [g for g in gorevler if g.get("durum") == "yapildi" and not g.get("yayinlandi")
                     and str(g.get("bitis_saati", "")).startswith(bugun)]
    return {
        "tur": tur, "tarih": bugun, "saat": simdi.strftime("%H:%M"),
        "biten": bugun_biten, "hata": bugun_hata, "calisan": calisan,
        "bekleyen": bugun_bekleyen, "geciken": geciken, "yarin": yarin_plan,
        "onay": onay_bekleyen, "tukenen": tukenenler(),
        "token": token_ozeti(bugun), "eksik": eksik_veriler(),
    }


# ---------------------------------------------------------------- biçimlendirme
def _satir_gorev(g, ozet=True):
    saat = str(g.get("bitis_saati") or g.get("tarih_saat") or "")[-5:]
    s = f"{saat} · {g.get('ajan', '?')} · {g.get('baslik', '')}"
    if ozet and g.get("ozet"):
        s += f"\n      → {_temiz(g['ozet'])}"
    yol = _cikti_yolu(g)
    if yol:
        s += f"\n      dosya: {yol}"
    return s


def bolumler(v):
    """[(başlık, [satır...], vurgu)] — hem düz metin hem HTML bu listeden üretilir."""
    b = []
    sayac = (f"Tamamlanan: {len(v['biten'])} · Hata: {len(v['hata'])} · Çalışan: {len(v['calisan'])} · "
             f"Bugün bekleyen: {len(v['bekleyen'])} · Geciken: {len(v['geciken'])}")
    b.append(("Durum", [sayac], None))

    if v["tur"] == "gun-sonu":
        b.append(("Bugün tamamlananlar", [_satir_gorev(g) for g in v["biten"]] or ["Bugün tamamlanan görev yok."], None))
    if v["hata"]:
        b.append(("Hata veren görevler", [_satir_gorev(g) for g in v["hata"]], "uyari"))
    if v["geciken"]:
        b.append(("Gecikmiş görevler (saati geçti, başlamadı)",
                  [_satir_gorev(g, ozet=False) for g in v["geciken"][:12]]
                  + (["…ve %d görev daha" % (len(v["geciken"]) - 12)] if len(v["geciken"]) > 12 else []), "uyari"))
    if v["tur"] == "sabah":
        b.append(("Bugünün planı", [_satir_gorev(g, ozet=False) for g in sorted(v["bekleyen"], key=lambda g: g.get("tarih_saat", ""))]
                  or ["Bugün planlı görev yok."], None))
    if v["tur"] == "gun-sonu" and v["onay"]:
        b.append(("Senin onayını/yayınını bekleyen taslaklar",
                  [f"{g.get('ajan', '?')} · {g.get('baslik', '')} → {_cikti_yolu(g)}" for g in v["onay"]], None))
    if v["tukenen"]:
        b.append((f"Tükenen ürünler ({len(v['tukenen'])})",
                  v["tukenen"][:15] + (["…"] if len(v["tukenen"]) > 15 else []), "uyari"))
    if v["tur"] == "gun-sonu":
        b.append(("Yarın planı", [_satir_gorev(g, ozet=False) for g in v["yarin"]] or ["Yarın için planlı görev yok."], None))
        if v["token"] is not None:
            b.append(("Yapay zekâ kullanımı", [f"Bugünkü toplam token: {v['token']:,}".replace(",", ".")], None))
    if v["eksik"]:
        b.append(("Ajanların çalışması için eksik veri", v["eksik"] + ["Bu dosyalar olmadan marj ve satış analizi yapılamıyor."], "uyari"))
    return b


def baslik(v):
    ad = "Gün sonu raporu" if v["tur"] == "gun-sonu" else "Sabah özeti"
    gun = datetime.strptime(v["tarih"], "%Y-%m-%d").strftime("%d.%m.%Y")
    return ad, gun


def metin_olustur(v):
    ad, gun = baslik(v)
    out = [f"Nida Zeytin Ajan Ofisi — {ad} ({gun}, {v['saat']})", "=" * 50, ""]
    for bas, satirlar, _ in bolumler(v):
        out.append(bas.upper())
        out.extend(f"  - {s}" for s in satirlar)
        out.append("")
    out.append("Bu mesaj ofis sunucusundan otomatik gönderildi. Ofis hiçbir müşteriye mail göndermez; yayın ve ödeme kararları sendedir.")
    return "\n".join(out)


def html_olustur(v):
    ad, gun = baslik(v)
    e = html.escape
    p = [f"<div style='font-family:Segoe UI,Arial,sans-serif;max-width:680px;margin:auto;color:#222'>",
         f"<h2 style='margin:0 0 4px'>Nida Zeytin Ajan Ofisi</h2>",
         f"<div style='color:#666;margin-bottom:16px'>{e(ad)} · {e(gun)} · {e(v['saat'])}</div>"]
    for bas, satirlar, vurgu in bolumler(v):
        renk = "#b3261e" if vurgu == "uyari" else "#33691e"
        p.append(f"<h3 style='margin:18px 0 6px;font-size:15px;color:{renk}'>{e(bas)}</h3><ul style='margin:0;padding-left:20px'>")
        for s in satirlar:
            ilk, *devam = s.split("\n")
            p.append(f"<li style='margin:4px 0'>{e(ilk)}")
            for d in devam:
                p.append(f"<div style='color:#555;font-size:13px'>{e(d.strip())}</div>")
            p.append("</li>")
        p.append("</ul>")
    p.append("<p style='color:#888;font-size:12px;margin-top:24px'>Otomatik rapor. Ofis müşterilere mail göndermez; "
             "yayın, fiyat ve ödeme kararları sana aittir.</p></div>")
    return "".join(p)


# ---------------------------------------------------------------- gönderim
def _smtp_gonder(cfg, msg):
    ctx = ssl.create_default_context()
    if cfg["port"] == 465:
        sunucu = smtplib.SMTP_SSL(cfg["host"], 465, timeout=30, context=ctx)
    else:
        sunucu = smtplib.SMTP(cfg["host"], cfg["port"], timeout=30)
        sunucu.ehlo()
        sunucu.starttls(context=ctx)
        sunucu.ehlo()
    with sunucu:
        sunucu.login(cfg["kullanici"], cfg["sifre"])
        sunucu.send_message(msg)


def _mesaj(cfg, konu, metin, html_govde):
    m = EmailMessage()
    m["From"] = cfg["gonderen"]
    m["To"] = cfg["alici"]
    m["Subject"] = konu.replace("\n", " ")[:200]
    m["Date"] = formatdate(localtime=True)
    m["Message-ID"] = make_msgid(domain="nidazeytin.com")
    m.set_content(metin)
    m.add_alternative(html_govde, subtype="html")
    return m


def _kaydet(ad, html_govde):
    os.makedirs(RAPOR_DIZINI, exist_ok=True)
    yol = os.path.join(RAPOR_DIZINI, ad)
    with open(yol, "w", encoding="utf-8") as f:
        f.write(html_govde)
    return yol


def _olay(**kw):
    try:
        ortak.olay_yaz({"zaman": ortak.simdi_iso(), "tur": "rapor_mail", **kw})
    except Exception:
        pass


def gonder_veya_kaydet(konu, metin, html_govde, dosya_adi, gercekten=True):
    """('gonderildi'|'kaydedildi'|'hata', açıklama)"""
    cfg = ayar()
    yol = _kaydet(dosya_adi, html_govde)
    if not gercekten or not smtp_hazir(cfg):
        neden = "kuru çalıştırma" if not gercekten else "SMTP tanımlı değil (SMTP_HOST/USER/PASSWORD)"
        return "kaydedildi", f"{neden}; rapor şuraya yazıldı: {yol}"
    try:
        _smtp_gonder(cfg, _mesaj(cfg, konu, metin, html_govde))
        return "gonderildi", f"{cfg['alici']} adresine gönderildi"
    except Exception as e:  # parola mesajda geçmez; yine de yalnız tür + mesaj
        return "hata", f"{type(e).__name__}: {e}"


def rapor_gonder(tur, gercekten=True):
    v = rapor_verisi(tur)
    ad, gun = baslik(v)
    ek = ""
    if v["hata"]:
        ek = f" ⚠ {len(v['hata'])} hata"
    elif v["geciken"]:
        ek = f" ⚠ {len(v['geciken'])} gecikmiş"
    konu = f"[Nida Ofis] {ad} — {gun}{ek}"
    return gonder_veya_kaydet(konu, metin_olustur(v), html_olustur(v), f"{v['tarih']}-{tur}.html", gercekten)


def hata_uyarisi(g):
    cfg = ayar()
    metin = (f"Görev hata verdi.\n\nAjan: {g.get('ajan')}\nGörev: {g.get('baslik')}\nSaat: {g.get('bitis_saati', '')}\n"
             f"Çıktı: {_cikti_yolu(g)}\n\nÖzet: {_temiz(g.get('ozet'), 600)}\n\nOfis paneline girip görevi yeniden çalıştırabilirsin.")
    h = f"<div style='font-family:Segoe UI,Arial,sans-serif'><h3 style='color:#b3261e'>Görev hata verdi</h3><pre style='white-space:pre-wrap'>{html.escape(metin)}</pre></div>"
    return gonder_veya_kaydet(f"[Nida Ofis] ⚠ Görev hatası: {g.get('baslik', '')}", metin, h,
                              f"hata-{g.get('id', 'x')}.html", cfg["aktif"])


def gorev_bildirimi(g):
    metin = (f"Görev tamamlandı.\n\nAjan: {g.get('ajan')}\nGörev: {g.get('baslik')}\nBitiş: {g.get('bitis_saati', '')}\n"
             f"Çıktı: {_cikti_yolu(g)}\n\nÖzet: {_temiz(g.get('ozet'), 600)}\n\nTaslak senin onayını bekliyor; yayın/gönderim yapılmadı.")
    h = f"<div style='font-family:Segoe UI,Arial,sans-serif'><h3 style='color:#33691e'>Görev tamamlandı</h3><pre style='white-space:pre-wrap'>{html.escape(metin)}</pre></div>"
    return gonder_veya_kaydet(f"[Nida Ofis] Tamamlandı: {g.get('baslik', '')}", metin, h, f"gorev-{g.get('id', 'x')}.html", True)


# ---------------------------------------------------------------- zamanlama (sunucu döngüsünden çağrılır)
def _durum_oku():
    try:
        with open(DURUM_DOSYASI, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _durum_yaz(d):
    try:
        os.makedirs(os.path.dirname(DURUM_DOSYASI), exist_ok=True)
        gecici = DURUM_DOSYASI + ".tmp"
        with open(gecici, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        os.replace(gecici, DURUM_DOSYASI)
    except OSError:
        pass


def kontrol_et():
    """Saati gelen raporu gün başına en çok bir kez gönderir; hata görevlerini bildirir."""
    cfg = ayar()
    if not cfg["aktif"]:
        return []
    simdi = datetime.now()
    bugun = simdi.strftime("%Y-%m-%d")
    durum = _durum_oku()
    islemler = []

    for tur, anahtar, varsayilan in (("sabah", "sabah", (8, 0)), ("gun-sonu", "gun_sonu", (18, 30))):
        s, d = _saat(cfg[anahtar], varsayilan)
        hedef = simdi.replace(hour=s, minute=d, second=0, microsecond=0)
        if simdi < hedef or simdi > hedef + timedelta(hours=5):
            continue
        k = durum.get(tur, {})
        if k.get("tarih") == bugun:
            if k.get("sonuc") in ("gonderildi", "kaydedildi") or k.get("deneme", 0) >= 3:
                continue
            if time.time() - k.get("son_ts", 0) < 900:
                continue
        sonuc, aciklama = rapor_gonder(tur)
        deneme = (k.get("deneme", 0) + 1) if k.get("tarih") == bugun else 1
        durum[tur] = {"tarih": bugun, "sonuc": sonuc, "deneme": deneme, "son_ts": time.time()}
        _olay(rapor=tur, sonuc=sonuc, aciklama=aciklama[:200])
        if sonuc != "gonderildi":
            sys.stderr.write(f"Rapor mail ({tur}): {sonuc} — {aciklama}\n")
        islemler.append((tur, sonuc))

    # Görev bildirimleri: ilk çalışmada mevcut bitmişleri sessizce işaretle (mail seli olmasın)
    gorevler = _gorevler()
    bitmis = [g for g in gorevler if g.get("durum") in ("yapildi", "hata") and g.get("kosu_id")]
    anahtar = lambda g: f"{g.get('id')}:{g.get('kosu_id')}"
    if "bildirilen" not in durum:
        durum["bildirilen"] = [anahtar(g) for g in bitmis]
    else:
        bildirilen = set(durum["bildirilen"])
        for g in bitmis:
            if anahtar(g) in bildirilen:
                continue
            if g["durum"] == "hata":
                sonuc, aciklama = hata_uyarisi(g)
            elif cfg["gorev_maili"]:
                sonuc, aciklama = gorev_bildirimi(g)
            else:
                sonuc, aciklama = "atlandi", ""
            if sonuc != "hata":  # gönderim hatasında bir sonraki turda tekrar dener
                bildirilen.add(anahtar(g))
                if sonuc != "atlandi":
                    _olay(bildirim=g.get("id"), sonuc=sonuc)
                    islemler.append((g.get("id"), sonuc))
        durum["bildirilen"] = list(bildirilen)[-500:]
    _durum_yaz(durum)
    return islemler


# ---------------------------------------------------------------- komut satırı
def main(argv):
    if len(argv) < 2 or argv[1] not in ("sabah", "gun-sonu", "test"):
        print(__doc__)
        return 2
    gercekten = "--gonder" in argv
    if argv[1] == "test":
        cfg = ayar()
        govde = "Bu bir test mesajıdır. Nida Zeytin Ajan Ofisi rapor maili çalışıyor."
        sonuc, aciklama = gonder_veya_kaydet("[Nida Ofis] Test mesajı", govde, f"<p>{govde}</p>", "test.html", gercekten)
    else:
        sonuc, aciklama = rapor_gonder(argv[1], gercekten)
    print(f"{sonuc}: {aciklama}")
    return 0 if sonuc != "hata" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
