"""Nida Zeytin — Veri ve Fiyat Senkronizasyonu.

1. SoftTR XML Feed (https://www.nidazeytin.com/xmlexport/export.php?id=7&source=softtr)
   üzerinden tüm canlı ürün, fiyat, stok ve kategori bilgilerini çeker.
2. 'veri/urun-fiyat-stok.md' ve 'veri/urunler.json' dosyalarını üretir.
3. 'docs/' veya 'veri/' klasöründeki Excel (.xlsx) veya CSV fiyat listesini okuyup
   ajanların anlayacağı markdown tablosuna ('veri/dahili-fiyat-listesi.md') çevirir.
"""
import csv
import glob
import json
import os
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime

import ortak

KOK = ortak.KOK
VERI_DIZINI = ortak.VERI_DIZINI
DOCS_DIZINI = ortak.DOCS_DIZINI
XML_URL = os.environ.get(
    "NIDA_XML_URL",
    "https://www.nidazeytin.com/xmlexport/export.php?id=7&source=softtr"
)

G_NS = "{http://base.google.com/ns/1.0}"


def temizle(metin):
    if not metin:
        return ""
    temiz = re.sub(r"<[^>]+>", " ", str(metin))
    temiz = re.sub(r"\s+", " ", temiz).strip()
    return temiz


def xml_urunleri_getir(url=XML_URL, zaman_asimi=15):
    """SoftTR Google Merchant XML akışından ürünleri çeker ve ayrıştırır."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "NidaZeytin-AjanOfisi/2.0 (VeriSenkron)"}
    )
    with urllib.request.urlopen(req, timeout=zaman_asimi) as response:
        raw_data = response.read()

    root = ET.fromstring(raw_data)
    urunler = []

    for item in root.findall(".//item"):
        id_val = item.findtext(f"{G_NS}id") or item.findtext("id") or ""
        title = temizle(item.findtext("title"))
        link = item.findtext("link") or ""
        desc = temizle(item.findtext("description"))
        price = item.findtext(f"{G_NS}price") or ""
        availability = item.findtext(f"{G_NS}availability") or ""
        brand = item.findtext(f"{G_NS}brand") or "Nida Zeytin"
        category = item.findtext(f"{G_NS}google_product_category") or ""
        mpn = item.findtext(f"{G_NS}mpn") or ""
        image_link = item.findtext(f"{G_NS}image_link") or ""

        stok_tr = "Stokta Var" if "in stock" in availability.lower() else "Tükendi"

        urunler.append({
            "id": id_val,
            "baslik": title,
            "fiyat": price,
            "stok": stok_tr,
            "stok_raw": availability,
            "link": link,
            "aciklama": desc[:300],
            "marka": brand,
            "kategori": category,
            "kod": mpn,
            "resim": image_link,
        })

    return urunler


def xml_kaydet(urunler):
    """Ürünleri veri/ klasörüne JSON ve Markdown formatında yazar."""
    os.makedirs(VERI_DIZINI, exist_ok=True)
    simdi = datetime.now().strftime("%Y-%m-%d %H:%M")

    json_yolu = os.path.join(VERI_DIZINI, "urunler.json")
    with open(json_yolu, "w", encoding="utf-8") as f:
        json.dump({
            "guncelleme": simdi,
            "kaynak": XML_URL,
            "toplam_urun": len(urunler),
            "urunler": urunler
        }, f, ensure_ascii=False, indent=2)

    md_yolu = os.path.join(VERI_DIZINI, "urun-fiyat-stok.md")
    with open(md_yolu, "w", encoding="utf-8") as f:
        f.write("# Nida Zeytin — Canlı Ürün, Fiyat ve Stok Kataloğu (SoftTR XML)\n\n")
        f.write(f"> **Son Güncelleme:** {simdi}\n")
        f.write(f"> **Kaynak:** SoftTR XML Export (`{XML_URL}`)\n")
        f.write(f"> **Toplam Ürün:** {len(urunler)}\n\n")
        f.write("| ID | Ürün Adı | Fiyat | Stok Durumu | Kod / SKU | Ürün Linki |\n")
        f.write("|---|---|---|---|---|---|\n")
        for u in urunler:
            f.write(f"| {u['id']} | {u['baslik']} | **{u['fiyat']}** | {u['stok']} | `{u['kod']}` | [İncele]({u['link']}) |\n")

    return json_yolu, md_yolu


def _xlsx_satirlari_oku(dosya_yolu):
    """Saf Python standart kütüphanesiyle .xlsx dosyasını okur (openpyxl gerekmez)."""
    with zipfile.ZipFile(dosya_yolu) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            sroot = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in sroot.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
                shared.append("".join([node.text for node in si.iter() if node.text]))

        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
        rows = []
        for row in sheet.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
            vals = []
            for c in row.findall("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
                t = c.get("t")
                v = c.findtext("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
                if t == "s" and v is not None:
                    idx = int(v)
                    vals.append(shared[idx] if idx < len(shared) else "")
                else:
                    vals.append(v or "")
            if any(vals):
                rows.append(vals)
        return rows


def excel_veya_csv_isle():
    """veri/ veya docs/ altındaki Excel veya CSV fiyat listesini markdown'a dönüştürür."""
    # Aday dosyaları kontrol et
    adaylar = []
    # 1. veri/ altındaki dosyalar
    for ad in ("fiyat-listesi.xlsx", "fiyat-listesi.csv", "urunler.xlsx"):
        p = os.path.join(VERI_DIZINI, ad)
        if os.path.isfile(p):
            adaylar.append(p)
    # 2. docs/ altındaki xlsx dosyaları
    for p in glob.glob(os.path.join(DOCS_DIZINI, "*.xlsx")):
        adaylar.append(p)
    for p in glob.glob(os.path.join(VERI_DIZINI, "*.xlsx")):
        if p not in adaylar:
            adaylar.append(p)

    if not adaylar:
        return None

    hedef_dosya = adaylar[0]
    simdi = datetime.now().strftime("%Y-%m-%d %H:%M")
    md_yolu = os.path.join(VERI_DIZINI, "dahili-fiyat-listesi.md")

    if hedef_dosya.endswith(".xlsx"):
        rows = _xlsx_satirlari_oku(hedef_dosya)
        if not rows:
            return None
        headers = rows[0]
        onemli = {
            "title_tr": "Ürün Adı",
            "code": "Ürün Kodu",
            "stok": "Stok",
            "purchase_price": "Maliyet/Alış",
            "unit_price": "Site Fiyatı",
            "td_direct_price": "Trendyol Fiyatı",
            "hb_direct_price": "Hepsiburada Fiyatı",
            "n11_direct_price": "N11 Fiyatı",
            "pazarama_direct_price": "Pazarama Fiyatı",
            "kdv": "KDV",
            "desi": "Desi"
        }
        idx_map = {}
        for i, h in enumerate(headers):
            for k in onemli:
                if f"|{k}|" in h or h.strip().lower() == k:
                    idx_map[k] = i

        with open(md_yolu, "w", encoding="utf-8") as f:
            f.write("# Dahili Ürün Fiyat, Maliyet ve Pazaryeri Listesi (Excel)\n\n")
            f.write(f"> **Kaynak Dosya:** `{os.path.basename(hedef_dosya)}`\n")
            f.write(f"> **İşlenme Tarihi:** {simdi}\n")
            f.write(f"> **Toplam Ürün:** {len(rows) - 1}\n\n")

            if "title_tr" in idx_map:
                f.write("| Kod | Ürün Adı | Stok | Maliyet | Site Satış | Trendyol | Hepsiburada | N11 | Pazarama | KDV | Desi |\n")
                f.write("|---|---|---|---|---|---|---|---|---|---|---|\n")
                for r in rows[1:]:
                    def get_c(key):
                        idx = idx_map.get(key)
                        return temizle(r[idx]) if idx is not None and idx < len(r) else "-"
                    f.write(f"| `{get_c('code')}` | {get_c('title_tr')} | {get_c('stok')} | {get_c('purchase_price')} TL | "
                            f"{get_c('unit_price')} TL | {get_c('td_direct_price')} TL | {get_c('hb_direct_price')} TL | "
                            f"{get_c('n11_direct_price')} TL | {get_c('pazarama_direct_price')} TL | %{get_c('kdv')} | {get_c('desi')} |\n")
            else:
                # Standart tablo olarak bas
                f.write("| " + " | ".join(headers[:10]) + " |\n")
                f.write("| " + " | ".join(["---"] * min(len(headers), 10)) + " |\n")
                for r in rows[1:]:
                    f.write("| " + " | ".join([temizle(x) for x in r[:10]]) + " |\n")

        return md_yolu

    elif hedef_dosya.endswith(".csv"):
        try:
            with open(hedef_dosya, mode="r", encoding="utf-8-sig") as f:
                satirlar = list(csv.reader(f))
        except UnicodeDecodeError:
            with open(hedef_dosya, mode="r", encoding="windows-1254") as f:
                satirlar = list(csv.reader(f))

        if not satirlar:
            return None

        with open(md_yolu, "w", encoding="utf-8") as f:
            f.write("# Dahili / Özel Fiyat ve Maliyet Listesi\n\n")
            f.write(f"> **Kaynak:** `{os.path.basename(hedef_dosya)}`\n")
            f.write(f"> **İşlenme Tarihi:** {simdi}\n\n")
            basliklar = satirlar[0]
            f.write("| " + " | ".join(basliklar) + " |\n")
            f.write("| " + " | ".join(["---"] * len(basliklar)) + " |\n")
            for satir in satirlar[1:]:
                if any(huc.strip() for huc in satir):
                    f.write("| " + " | ".join(satir) + " |\n")

        return md_yolu

    return None


def senkronize_et():
    """Tam senkronizasyon çalıştırır."""
    sonuc = {}
    try:
        urunler = xml_urunleri_getir()
        json_y, md_y = xml_kaydet(urunler)
        sonuc["xml"] = {"durum": "basarili", "toplam": len(urunler), "dosya": md_y}
    except Exception as e:
        sonuc["xml"] = {"durum": "hata", "mesaj": str(e)}

    fiyat_md = excel_veya_csv_isle()
    if fiyat_md:
        sonuc["excel_fiyat"] = {"durum": "basarili", "dosya": fiyat_md}
    else:
        sonuc["excel_fiyat"] = {"durum": "yok", "not": "Excel veya CSV dosyası bulunamadı"}

    return sonuc


if __name__ == "__main__":
    print("Veri senkronizasyonu başlatılıyor...")
    res = senkronize_et()
    print("Sonuç:", json.dumps(res, ensure_ascii=False, indent=2))
