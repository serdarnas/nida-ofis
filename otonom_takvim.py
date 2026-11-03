#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nida Zeytin Ajan Ofisi — Otonom Çalışma & Takvim Merkezi Motoru.

Geçmiş (Yapıldı) ve Gelecek (Yapılacak) tüm görevleri kanal etiketleriyle (#Instagram, #Facebook,
#Trendyol, #Hepsiburada, #SEO vb.) yönetir, geçmiş raporlarla senkronize eder ve zamanı gelen
görevleri otonom olarak tetikler.
"""
import json
import os
import re
import secrets
import threading
import time
from datetime import datetime, timedelta

import ortak

TAKVIM_DOSYASI = ortak.TAKVIM_DOSYASI
TAKVIM_KILIDI = threading.Lock()

# Kanal / Platform etiket tanımları ve renk kategorileri
KANAL_ETIKETLERI = [
    "#Instagram",
    "#Facebook",
    "#Reels",
    "#LinkedIn",
    "#B2B",
    "#MetaAds",
    "#Trendyol",
    "#Hepsiburada",
    "#N11",
    "#Pazarama",
    "#PttAVM",
    "#Amazon",
    "#Ozon",
    "#Temu",
    "#SEO",
    "#nidazeytin.com",
    "#Blog",
    "#Finans",
    "#Stok",
    "#Webmail",
    "#Otonom",
]

AJAN_VARSAYILAN_ETIKET = {
    "pazaryeri-tr": ["#Trendyol", "#Hepsiburada"],
    "pazaryeri-butik": ["#N11", "#Pazarama", "#PttAVM"],
    "global-ihracat": ["#Amazon", "#Ozon", "#Temu"],
    "sosyal-medya": ["#Facebook"],
    "instagram": ["#Instagram", "#Reels"],
    "linkedin-b2b": ["#LinkedIn", "#B2B"],
    "reklam-ppc": ["#MetaAds", "#Instagram", "#Facebook"],
    "web-seo": ["#SEO", "#nidazeytin.com"],
    "iletisim-destek": ["#Webmail"],
    "finans-kontrol": ["#Finans", "#Trendyol"],
    "tedarik-stok": ["#Stok", "#nidazeytin.com"],
    "ceo": ["#Otonom"],
}


def etiketleri_cikar(ajan_id, baslik="", prompt="", mevcut=None):
    """Ajan ID, başlık ve prompt içeriğine göre uygun kanal etiketlerini otomatik çıkarır."""
    bulunan = []
    if isinstance(mevcut, list):
        for e in mevcut:
            e_str = str(e).strip()
            if e_str:
                if not e_str.startswith("#"):
                    e_str = "#" + e_str
                if e_str not in bulunan:
                    bulunan.append(e_str)

    metin = f"{baslik} {prompt}".lower()
    eslesmeler = [
        ("instagram", "#Instagram"),
        ("ig ", "#Instagram"),
        ("reels", "#Reels"),
        ("facebook", "#Facebook"),
        (" fb", "#Facebook"),
        ("linkedin", "#LinkedIn"),
        ("b2b", "#B2B"),
        ("horeca", "#B2B"),
        ("meta ads", "#MetaAds"),
        ("roas", "#MetaAds"),
        ("reklam", "#MetaAds"),
        ("trendyol", "#Trendyol"),
        ("hepsiburada", "#Hepsiburada"),
        ("hb ", "#Hepsiburada"),
        ("n11", "#N11"),
        ("pazarama", "#Pazarama"),
        ("pttavm", "#PttAVM"),
        ("akıllı esnaf", "#PttAVM"),
        ("amazon", "#Amazon"),
        ("ozon", "#Ozon"),
        ("temu", "#Temu"),
        ("seo", "#SEO"),
        ("json-ld", "#SEO"),
        ("blog", "#Blog"),
        ("makale", "#Blog"),
        ("nidazeytin.com", "#nidazeytin.com"),
        ("hakediş", "#Finans"),
        ("garanti bbva", "#Finans"),
        ("mutabakat", "#Finans"),
        ("komisyon", "#Finans"),
        ("stok", "#Stok"),
        ("tedarik", "#Stok"),
        ("dolum", "#Stok"),
        ("teneke", "#Stok"),
        ("mail", "#Webmail"),
        ("soru-cevap", "#Webmail"),
    ]
    for anahtar, etiket in eslesmeler:
        if anahtar in metin and etiket not in bulunan:
            bulunan.append(etiket)

    for v_etiket in AJAN_VARSAYILAN_ETIKET.get(ajan_id, []):
        if v_etiket not in bulunan:
            bulunan.append(v_etiket)

    return bulunan[:6]


def _sonraki_hafta_gunu(hedef_weekday, saat_str, simdi=None):
    """0=Pazartesi ... 6=Pazar için gelecekteki ilk tarih/saat ISO metnini döner."""
    simdi = simdi or datetime.now()
    saat, dakika = [int(x) for x in saat_str.split(":")]
    fark = (hedef_weekday - simdi.weekday()) % 7
    aday = simdi.replace(hour=saat, minute=dakika, second=0, microsecond=0) + timedelta(days=fark)
    if aday <= simdi:
        aday += timedelta(days=7)
    return aday.strftime("%Y-%m-%d %H:%M")


def _sonraki_gunluk(saat_str, simdi=None):
    simdi = simdi or datetime.now()
    saat, dakika = [int(x) for x in saat_str.split(":")]
    aday = simdi.replace(hour=saat, minute=dakika, second=0, microsecond=0)
    if aday <= simdi:
        aday += timedelta(days=1)
    return aday.strftime("%Y-%m-%d %H:%M")


def varsayilan_plan_olustur():
    """Nida Zeytin için varsayılan otonom görev takvimini oluşturur."""
    simdi = datetime.now()
    sablonlar = [
        {
            "baslik": "Günlük SoftTR XML Stok & Kritik Ürün Kontrolü",
            "ajan": "tedarik-stok",
            "tarih_saat": _sonraki_gunluk("08:30", simdi),
            "tekrar": "gunluk",
            "saat": "08:30",
            "etiketler": ["#Stok", "#nidazeytin.com", "#Trendyol", "#Otonom"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. Güncel ürün kataloğundaki stok miktarlarını incele, stoğu azalan veya kritik olan ürünleri tespit et ve 9 pazaryeri için günlük stok güvenlik planını çıkar.",
        },
        {
            "baslik": "Web & Pazaryeri SEO Ürün Metinleri Kontrolü",
            "ajan": "web-seo",
            "tarih_saat": _sonraki_gunluk("09:30", simdi),
            "tekrar": "gunluk",
            "saat": "09:30",
            "etiketler": ["#SEO", "#nidazeytin.com", "#Otonom"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. nidazeytin.com ürün kataloğundaki zeytinyağı, zeytin ve doğal sabun ürünlerinin arama motoru görünürlüğünü artıracak günlük teknik SEO ve meta açıklama iyileştirme önerilerini hazırla.",
        },
        {
            "baslik": "Haftalık Facebook Sayfası Paylaşım Takvimi",
            "ajan": "sosyal-medya",
            "tarih_saat": _sonraki_hafta_gunu(0, "10:00", simdi),  # Pazartesi
            "tekrar": "haftalik",
            "gun": 0,
            "saat": "10:00",
            "etiketler": ["#Facebook", "#Otonom"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. Nida Zeytin Facebook sayfası için 1/3 kuralına uygun (Ürün, Tarif/Sağlık, Edremit Bahçe Hikayesi) 7 günlük paylaşım metinlerini ve CTA'ları hazırla.",
        },
        {
            "baslik": "Haftalık Instagram İçerik Planı (Reel + Carousel + Story)",
            "ajan": "instagram",
            "tarih_saat": _sonraki_hafta_gunu(0, "10:30", simdi),  # Pazartesi
            "tekrar": "haftalik",
            "gun": 0,
            "saat": "10:30",
            "etiketler": ["#Instagram", "#Reels", "#Otonom"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. Bu hafta için 4-5 gönderilik Instagram planı hazırla (en az 3 Reel): gün, format, direk, açı, çağrı, çekim notu; ayrıca 5 günlük story akışı. Stokta olmayan ürünleri kullanma.",
        },
        {
            "baslik": "Instagram Reel Senaryosu (3 kanca, puanlı)",
            "ajan": "instagram",
            "tarih_saat": _sonraki_hafta_gunu(1, "15:00", simdi),  # Salı
            "tekrar": "haftalik",
            "gun": 1,
            "saat": "15:00",
            "etiketler": ["#Instagram", "#Reels", "#Otonom"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. Katalogda stokta olan bir ürün için tek fikirli bir Reel hazırla: 3 farklı formülden 3 kanca, seçilen kancayla satır satır senaryo, ekran metni ve altyazı. Çıktı etiketlerini kullan.",
        },
        {
            "baslik": "Instagram Yorum & DM Yanıt Taslakları",
            "ajan": "instagram",
            "tarih_saat": _sonraki_hafta_gunu(3, "16:00", simdi),  # Perşembe
            "tekrar": "haftalik",
            "gun": 3,
            "saat": "16:00",
            "etiketler": ["#Instagram", "#Webmail", "#Otonom"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. Instagram'da sık gelen 6 soru (fiyat, kargo, tazelik, toptan, hediye, sipariş) için sıcak ve kısa yorum/DM yanıt taslağı hazırla. Fiyat yalnız katalogdan; sipariş WhatsApp hattına yönlenir.",
        },
        {
            "baslik": "Trendyol & Hepsiburada Haftalık Kampanya ve Kupon Kurgusu",
            "ajan": "pazaryeri-tr",
            "tarih_saat": _sonraki_hafta_gunu(0, "11:00", simdi),  # Pazartesi
            "tekrar": "haftalik",
            "gun": 0,
            "saat": "11:00",
            "etiketler": ["#Trendyol", "#Hepsiburada", "#Otonom"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. Nida Zeytin'in Trendyol ve Hepsiburada mağazaları için sepet ortalamasını artıracak haftalık kampanya, kupon ve 3'lü tanışma paketi kurgusunu hazırla.",
        },
        {
            "baslik": "LinkedIn Kurumsal Post & HORECA Toptan Satış Mesajı",
            "ajan": "linkedin-b2b",
            "tarih_saat": _sonraki_hafta_gunu(1, "10:00", simdi),  # Salı
            "tekrar": "haftalik",
            "gun": 1,
            "saat": "10:00",
            "etiketler": ["#LinkedIn", "#B2B", "#Otonom"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. Olive Edremit Zeytincilik LinkedIn sayfası için Edremit Körfezi üretim kalitemizi anlatan kurumsal paylaşım ve HORECA/toptan satın almacılara yönelik haftalık B2B teklif mesajı hazırla.",
        },
        {
            "baslik": "N11, Pazarama ve PttAVM Fiyat & Marj Matrisi Güncelleme",
            "ajan": "pazaryeri-butik",
            "tarih_saat": _sonraki_hafta_gunu(1, "14:00", simdi),  # Salı
            "tekrar": "haftalik",
            "gun": 1,
            "saat": "14:00",
            "etiketler": ["#N11", "#Pazarama", "#PttAVM", "#Finans"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. N11 (olive-edremit), Pazarama, PttAVM ve PTT Akıllı Esnaf kanalları için güncel maliyet, komisyon ve PTT kargo baremlerine göre haftalık fiyatlandırma ve net marj tablosunu oluştur.",
        },
        {
            "baslik": "nidazeytin.com Haftalık SEO Blog Makalesi Taslağı",
            "ajan": "web-seo",
            "tarih_saat": _sonraki_hafta_gunu(2, "10:00", simdi),  # Çarşamba
            "tekrar": "haftalik",
            "gun": 2,
            "saat": "10:00",
            "etiketler": ["#SEO", "#Blog", "#nidazeytin.com"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. nidazeytin.com blogu için 'Gerçek Erken Hasat Soğuk Sıkım Edremit Zeytinyağı Nasıl Anlaşılır?' ve zeytinyağının sağlık faydaları odaklı, ürünlere iç link veren kapsamlı bir SEO makalesi yaz.",
        },
        {
            "baslik": "Amazon, Ozon & Temu Global Listeleme ve Paket Kontrolü",
            "ajan": "global-ihracat",
            "tarih_saat": _sonraki_hafta_gunu(3, "10:00", simdi),  # Perşembe
            "tekrar": "haftalik",
            "gun": 3,
            "saat": "10:00",
            "etiketler": ["#Amazon", "#Ozon", "#Temu"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. Amazon Seller Central, Ozon Global ve Temu mağazalarımız için çok dilli ürün açıklamalarını ve sınır ötesi kargoya uygun paket/fiyat stratejisini hazırla.",
        },
        {
            "baslik": "Meta Ads (IG/FB) & Pazaryeri ROAS Reklam Optimizasyonu",
            "ajan": "reklam-ppc",
            "tarih_saat": _sonraki_hafta_gunu(3, "14:00", simdi),  # Perşembe
            "tekrar": "haftalik",
            "gun": 3,
            "saat": "14:00",
            "etiketler": ["#MetaAds", "#Instagram", "#Facebook"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. nidazeytin.com ve pazaryeri mağazalarımıza trafik ve satış çekecek Soğuk (TOF), Ilık (MOF) ve Sıcak (Retargeting) Meta Ads reklam seti kurgusunu ve reklam metinlerini hazırla.",
        },
        {
            "baslik": "Haftalık 9 Pazaryeri Hakediş & Garanti BBVA Mutabakat Kontrolü",
            "ajan": "finans-kontrol",
            "tarih_saat": _sonraki_hafta_gunu(4, "16:00", simdi),  # Cuma
            "tekrar": "haftalik",
            "gun": 4,
            "saat": "16:00",
            "etiketler": ["#Finans", "#Trendyol", "#Amazon", "#Hepsiburada"],
            "prompt": "../../marka-profili.md ve CLAUDE.md dosyalarını oku. Olive Edremit Zeytincilik San. ve Tic. Ltd. Şti.'nin pazaryeri satışlarından Garanti BBVA hesabına yatan hakedişleri, komisyon ve kargo kesintilerini denetlemek için haftalık mutabakat tablosu oluştur.",
        },
    ]

    gorevler = []
    for s in sablonlar:
        gorevler.append({
            "id": f"tkv-{secrets.token_hex(4)}",
            "baslik": s["baslik"],
            "ajan": s["ajan"],
            "tarih_saat": s["tarih_saat"],
            "tekrar": s.get("tekrar", "tek_sefer"),
            "gun": s.get("gun"),
            "saat": s.get("saat", "10:00"),
            "durum": "yapilacak",
            "etiketler": s["etiketler"],
            "prompt": s["prompt"],
            "kosu_id": None,
            "yayinlandi": False,
            "olusturma": simdi.strftime("%Y-%m-%d %H:%M"),
        })

    return {
        "ayarlar": {
            "otonom_aktif": True,
            "xml_tetik_aktif": True,
            "son_kontrol": simdi.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "gorevler": gorevler,
    }


def _oku_ham():
    os.makedirs(os.path.dirname(TAKVIM_DOSYASI), exist_ok=True)
    if not os.path.isfile(TAKVIM_DOSYASI):
        veri = varsayilan_plan_olustur()
        _yaz_ham(veri)
        return veri
    try:
        with open(TAKVIM_DOSYASI, "r", encoding="utf-8") as f:
            veri = json.load(f)
        if not isinstance(veri, dict) or "gorevler" not in veri:
            veri = varsayilan_plan_olustur()
            _yaz_ham(veri)
        return veri
    except Exception:
        veri = varsayilan_plan_olustur()
        _yaz_ham(veri)
        return veri


def _yaz_ham(veri):
    os.makedirs(os.path.dirname(TAKVIM_DOSYASI), exist_ok=True)
    gecici = TAKVIM_DOSYASI + ".tmp"
    with open(gecici, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)
    os.replace(gecici, TAKVIM_DOSYASI)


def _sonraki_tekrar_tarihi(gorev):
    """Periyodik görevin bir sonraki çalışma zamanını hesaplar."""
    tekrar = gorev.get("tekrar") or "tek_sefer"
    saat_str = gorev.get("saat") or "10:00"
    if ":" not in saat_str:
        saat_str = "10:00"
    simdi = datetime.now()
    if tekrar == "gunluk":
        return _sonraki_gunluk(saat_str, simdi + timedelta(minutes=2))
    if tekrar == "haftalik":
        gun = gorev.get("gun")
        if gun is None:
            try:
                eski_dt = datetime.strptime(gorev.get("tarih_saat", ""), "%Y-%m-%d %H:%M")
                gun = eski_dt.weekday()
            except Exception:
                gun = 0
        return _sonraki_hafta_gunu(int(gun), saat_str, simdi + timedelta(minutes=2))
    return None


def gecmis_kosulari_senkronla():
    """cikti/ içindeki tamamlanmış raporları ve durum/ dosyalarını takvimle senkronize eder."""
    with TAKVIM_KILIDI:
        veri = _oku_ham()
        gorevler = veri.get("gorevler", [])
        mevcut_kosu_idleri = {g.get("kosu_id") for g in gorevler if g.get("kosu_id")}
        degisti = False

        # 1. Durumu 'calisiyor' olan takvim görevlerini kontrol et
        for g in list(gorevler):
            if g.get("durum") == "calisiyor" and g.get("kosu_id"):
                kid = g["kosu_id"]
                ajan_id = g["ajan"]
                cikti_yolu = os.path.join(ortak.CIKTI_DIZINI, ajan_id, f"{kid}.md")
                durum_bilgi = ortak.durum_oku(ajan_id) or {}
                if os.path.isfile(cikti_yolu) and not ortak.ajan_mesgul(ajan_id):
                    try:
                        with open(cikti_yolu, "r", encoding="utf-8") as cf:
                            icerik = cf.read().strip()
                    except Exception:
                        icerik = ""
                    if durum_bilgi.get("kosu_id") == kid and durum_bilgi.get("durum") == "hata":
                        g["durum"] = "hata"
                    else:
                        g["durum"] = "yapildi"
                    g["ozet"] = icerik[:260]
                    g["bitis_saati"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    degisti = True

                    # Periyodik görevse bir sonraki gelecek görevi oluştur
                    sonraki_dt = _sonraki_tekrar_tarihi(g)
                    if sonraki_dt and not any(
                        x.get("baslik") == g.get("baslik")
                        and x.get("ajan") == g.get("ajan")
                        and x.get("durum") == "yapilacak"
                        for x in gorevler
                    ):
                        yeni_g = {
                            "id": f"tkv-{secrets.token_hex(4)}",
                            "baslik": g["baslik"],
                            "ajan": g["ajan"],
                            "tarih_saat": sonraki_dt,
                            "tekrar": g.get("tekrar", "tek_sefer"),
                            "gun": g.get("gun"),
                            "saat": g.get("saat", "10:00"),
                            "durum": "yapilacak",
                            "etiketler": g.get("etiketler", []),
                            "prompt": g.get("prompt", ""),
                            "kosu_id": None,
                            "yayinlandi": False,
                            "olusturma": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                        gorevler.append(yeni_g)

        # 2. cikti/<ajan>/<kosu_id>.md dosyalarını tarayıp takvimde olmayan geçmiş işleri ekle
        if os.path.isdir(ortak.CIKTI_DIZINI):
            for ajan_ad in sorted(os.listdir(ortak.CIKTI_DIZINI)):
                ajan_klasor = os.path.join(ortak.CIKTI_DIZINI, ajan_ad)
                if not os.path.isdir(ajan_klasor):
                    continue
                for md_ad in sorted(os.listdir(ajan_klasor)):
                    if not md_ad.endswith(".md"):
                        continue
                    kosu_id = md_ad[:-3]
                    if kosu_id in mevcut_kosu_idleri:
                        continue
                    tam_yol = os.path.join(ajan_klasor, md_ad)
                    try:
                        st = os.stat(tam_yol)
                        with open(tam_yol, "r", encoding="utf-8") as f:
                            metin = f.read().strip()
                    except Exception:
                        continue

                    arg_yolu = os.path.join(ortak.KOSU_DIZINI, f"{kosu_id}.arg.json")
                    etiket_baslik = ""
                    prompt = ""
                    kaynak = "buton"
                    if os.path.isfile(arg_yolu):
                        try:
                            with open(arg_yolu, "r", encoding="utf-8") as af:
                                arg_veri = json.load(af)
                                etiket_baslik = arg_veri.get("etiket") or ""
                                prompt = arg_veri.get("prompt") or ""
                                kaynak = arg_veri.get("kaynak") or "buton"
                        except Exception:
                            pass

                    if not etiket_baslik:
                        # Prompt'tan anlamlı kısa başlık çıkar
                        temiz_p = re.sub(r"\.\./\.\./marka-profili\.md.*?oku\.\s*", "", prompt, flags=re.I).strip()
                        etiket_baslik = (temiz_p[:68] + "…") if len(temiz_p) > 68 else (temiz_p or f"{ajan_ad} Görevi")

                    tarih_str = datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
                    etiketler = etiketleri_cikar(ajan_ad, etiket_baslik, prompt)
                    if kaynak == "otonom" and "#Otonom" not in etiketler:
                        etiketler.append("#Otonom")

                    gorevler.append({
                        "id": f"tkv-{secrets.token_hex(4)}",
                        "baslik": etiket_baslik,
                        "ajan": ajan_ad,
                        "tarih_saat": tarih_str,
                        "tekrar": "tek_sefer",
                        "saat": tarih_str.split(" ")[1] if " " in tarih_str else "10:00",
                        "durum": "yapildi",
                        "etiketler": etiketler,
                        "prompt": prompt,
                        "ozet": metin[:260],
                        "kosu_id": kosu_id,
                        "kaynak": kaynak,
                        "yayinlandi": False,
                        "olusturma": tarih_str,
                        "bitis_saati": tarih_str,
                    })
                    mevcut_kosu_idleri.add(kosu_id)
                    degisti = True

        if degisti:
            veri["gorevler"] = gorevler
            _yaz_ham(veri)
        return veri


def takvim_yaniti(durum_filtre=None, etiket_filtre=None, ajan_filtre=None):
    """Takvim sekmesi için geçmiş (yapildi) ve gelecek (yapilacak) görevleri döndürür."""
    veri = gecmis_kosulari_senkronla()
    gorevler = list(veri.get("gorevler", []))

    # Etiket sayılarını hesapla
    etiket_sayac = {}
    for g in gorevler:
        for e in g.get("etiketler", []):
            etiket_sayac[e] = etiket_sayac.get(e, 0) + 1

    # Filtreleme
    if durum_filtre and durum_filtre != "tumu":
        gorevler = [g for g in gorevler if g.get("durum") == durum_filtre]
    if etiket_filtre and etiket_filtre != "tumu":
        aranan = etiket_filtre if etiket_filtre.startswith("#") else f"#{etiket_filtre}"
        gorevler = [g for g in gorevler if aranan.lower() in [x.lower() for x in g.get("etiketler", [])]]
    if ajan_filtre and ajan_filtre != "tumu":
        gorevler = [g for g in gorevler if g.get("ajan") == ajan_filtre]

    # Sıralama: yapılacaklar en yakın tarihten ileriye, yapılanlar en yeniden eskiye
    yapilacaklar = sorted(
        [g for g in gorevler if g.get("durum") in ("yapilacak", "calisiyor", "bekliyor")],
        key=lambda x: x.get("tarih_saat", "9999"),
    )
    yapilanlar = sorted(
        [g for g in gorevler if g.get("durum") in ("yapildi", "hata")],
        key=lambda x: x.get("tarih_saat", ""),
        reverse=True,
    )

    tum_gorevler = veri.get("gorevler", [])
    istatistik = {
        "toplam": len(tum_gorevler),
        "yapilacak": sum(1 for x in tum_gorevler if x.get("durum") == "yapilacak"),
        "calisiyor": sum(1 for x in tum_gorevler if x.get("durum") == "calisiyor"),
        "yapildi": sum(1 for x in tum_gorevler if x.get("durum") == "yapildi"),
        "yayinlandi": sum(1 for x in tum_gorevler if x.get("yayinlandi")),
    }

    return {
        "ayarlar": veri.get("ayarlar", {"otonom_aktif": True, "xml_tetik_aktif": True}),
        "istatistik": istatistik,
        "etiketler": etiket_sayac,
        "kanal_listesi": KANAL_ETIKETLERI,
        "yapilacaklar": yapilacaklar,
        "yapilanlar": yapilanlar,
        "gorevler": yapilacaklar + yapilanlar,
    }


def gorev_ekle(baslik, ajan, tarih_saat, tekrar="tek_sefer", etiketler=None, prompt=""):
    if not baslik or not str(baslik).strip():
        raise ValueError("Görev başlığı gerekli")
    if not ajan or not ortak.AJAN_ID_DESENI.match(str(ajan)):
        raise ValueError("Geçersiz ajan seçimi")
    tarih_saat = str(tarih_saat or "").strip().replace("T", " ")
    if not tarih_saat:
        tarih_saat = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")

    saat_parca = tarih_saat.split(" ")[1][:5] if " " in tarih_saat else "10:00"
    gun_no = None
    try:
        dt = datetime.strptime(tarih_saat[:16], "%Y-%m-%d %H:%M")
        gun_no = dt.weekday()
        tarih_saat = dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        pass

    if isinstance(etiketler, str):
        etiket_liste = [x.strip() for x in re.split(r"[,;\s]+", etiketler) if x.strip()]
    elif isinstance(etiketler, list):
        etiket_liste = etiketler
    else:
        etiket_liste = []

    son_etiketler = etiketleri_cikar(ajan, baslik, prompt, mevcut=etiket_liste)
    if not prompt or not str(prompt).strip():
        prompt = f"../../marka-profili.md ve CLAUDE.md dosyalarını oku. '{baslik}' görevi için doğrudan uygulanabilir detaylı tablo/içerik/plan hazırla."

    yeni = {
        "id": f"tkv-{secrets.token_hex(4)}",
        "baslik": str(baslik).strip()[:140],
        "ajan": ajan,
        "tarih_saat": tarih_saat,
        "tekrar": tekrar if tekrar in ("tek_sefer", "gunluk", "haftalik") else "tek_sefer",
        "gun": gun_no,
        "saat": saat_parca,
        "durum": "yapilacak",
        "etiketler": son_etiketler,
        "prompt": str(prompt).strip()[:4000],
        "kosu_id": None,
        "yayinlandi": False,
        "olusturma": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    with TAKVIM_KILIDI:
        veri = _oku_ham()
        veri["gorevler"].append(yeni)
        _yaz_ham(veri)
    return yeni


def gorev_guncelle(gorev_id, **alanlar):
    with TAKVIM_KILIDI:
        veri = _oku_ham()
        bulunan = None
        for g in veri.get("gorevler", []):
            if g.get("id") == gorev_id:
                bulunan = g
                break
        if not bulunan:
            raise ValueError("Görev bulunamadı")

        for k in ("baslik", "ajan", "tarih_saat", "tekrar", "durum", "prompt", "yayinlandi", "kosu_id"):
            if k in alanlar and alanlar[k] is not None:
                if k == "tarih_saat":
                    bulunan[k] = str(alanlar[k]).replace("T", " ")[:16]
                else:
                    bulunan[k] = alanlar[k]

        if "etiketler" in alanlar and alanlar["etiketler"] is not None:
            et = alanlar["etiketler"]
            if isinstance(et, str):
                et = [x.strip() for x in re.split(r"[,;\s]+", et) if x.strip()]
            bulunan["etiketler"] = [x if x.startswith("#") else f"#{x}" for x in et if x]

        _yaz_ham(veri)
    return bulunan


def gorev_sil(gorev_id):
    with TAKVIM_KILIDI:
        veri = _oku_ham()
        eski_uzunluk = len(veri.get("gorevler", []))
        veri["gorevler"] = [g for g in veri.get("gorevler", []) if g.get("id") != gorev_id]
        if len(veri["gorevler"]) == eski_uzunluk:
            return False
        _yaz_ham(veri)
    return True


def otonom_ayar_guncelle(otonom_aktif=None, xml_tetik_aktif=None):
    with TAKVIM_KILIDI:
        veri = _oku_ham()
        ayarlar = veri.setdefault("ayarlar", {"otonom_aktif": True, "xml_tetik_aktif": True})
        if otonom_aktif is not None:
            ayarlar["otonom_aktif"] = bool(otonom_aktif)
        if xml_tetik_aktif is not None:
            ayarlar["xml_tetik_aktif"] = bool(xml_tetik_aktif)
        ayarlar["son_kontrol"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _yaz_ham(veri)
    return ayarlar


def gorev_simdi_tetikle(gorev_id, gorev_baslat_fn):
    """Takvimdeki bir görevi saatini beklemeden hemen başlatır."""
    with TAKVIM_KILIDI:
        veri = _oku_ham()
        hedef = None
        for g in veri.get("gorevler", []):
            if g.get("id") == gorev_id:
                hedef = g
                break
        if not hedef:
            raise ValueError("Görev bulunamadı")
        ajan_id = hedef["ajan"]
        prompt = hedef.get("prompt") or hedef["baslik"]
        baslik = hedef["baslik"]

    sonuc = gorev_baslat_fn(ajan_id, etiket=baslik, prompt=prompt, kaynak="takvim")
    kosu_id = sonuc.get("kosu_id")

    with TAKVIM_KILIDI:
        veri = _oku_ham()
        for g in veri.get("gorevler", []):
            if g.get("id") == gorev_id:
                g["durum"] = "calisiyor"
                g["kosu_id"] = kosu_id
                g["baslangic_saati"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                break
        _yaz_ham(veri)
    return sonuc


def zamani_gelenleri_kontrol_et(gorev_baslat_fn):
    """Arka plan zamanlayıcısı tarafından çağrılır; saati gelen 'yapilacak' görevleri başlatır."""
    gecmis_kosulari_senkronla()
    simdi_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    with TAKVIM_KILIDI:
        veri = _oku_ham()
        ayarlar = veri.get("ayarlar", {})
        ayarlar["son_kontrol"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not ayarlar.get("otonom_aktif", True):
            _yaz_ham(veri)
            return []

        adaylar = [
            g for g in veri.get("gorevler", [])
            if g.get("durum") == "yapilacak" and g.get("tarih_saat", "9999") <= simdi_str
        ]
        _yaz_ham(veri)

    baslatilanlar = []
    for aday in adaylar:
        ajan_id = aday.get("ajan")
        if not ajan_id or ortak.ajan_mesgul(ajan_id):
            continue
        try:
            sonuc = gorev_simdi_tetikle(aday["id"], gorev_baslat_fn)
            baslatilanlar.append({"gorev_id": aday["id"], "ajan": ajan_id, "kosu_id": sonuc.get("kosu_id")})
            time.sleep(1.0)
        except Exception:
            continue
    return baslatilanlar
