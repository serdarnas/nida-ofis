"""Nida Zeytin (nidazeytin.com) — Ürün Kataloğu ve Excel SEO Güncelleyici.

Bu modül:
1. 'docs/Ürünler_1793508054_orijinal.xlsx' kaynağından okur (orijinal dosya hiç bozulmaz).
2. 81 ürünün tamamının SEO metinlerini Google SEO ve E-E-A-T standartlarına göre günceller:
   - title_tr (Temiz, profesyonel ürün adı)
   - keywords_tr (Google Meta Title - CTR artırıcı 50-60 karakter başlık)
   - description_tr (Google Meta Description - 130-160 karakter arası eylem çağrılı özet)
   - detail_tr (Zengin HTML formatında ürün hikayesi, özellikler, besin/üretim detayları, saklama tavsiyesi)
   - etiket (Arama hacmi yüksek LSI anahtar kelimeler)
3. SoftTR e-ticaret paneline doğrudan yüklenebilir 'docs/Ürünler_1793508054.xlsx' ve 'docs/Urunler_SEO_Guncel.xlsx' dosyalarını üretir.
"""
import os
import shutil
import openpyxl
import ortak

KOK = ortak.KOK
DOCS_DIZINI = ortak.DOCS_DIZINI
EXCEL_YOLU = os.path.join(DOCS_DIZINI, "Ürünler_1793508054.xlsx")
YEDEK_YOLU = os.path.join(DOCS_DIZINI, "Ürünler_1793508054_orijinal.xlsx")
GUNCEL_YOLU = os.path.join(DOCS_DIZINI, "Urunler_SEO_Guncel.xlsx")


def seo_metinlerini_uret(code, title):
    """Ürün türüne göre yüksek dönüşümlü ve teknik SEO standartlarına uygun metinler üretir."""
    c_lower = code.replace("İ", "i").replace("I", "ı").lower()
    t_lower = title.replace("İ", "i").replace("I", "ı").lower()

    # 1. ERKEN HASAT ZEYTİNYAĞLARI
    if "erken hasat" in t_lower or "erken" in c_lower or code == "1814":
        hacim = "5 Litre Teneke" if "5lt" in c_lower or "5lt" in t_lower or "5 litre" in t_lower else \
                "1 Litre Cam Galon" if "galon" in t_lower or code == "1814" else \
                "1 Litre Cam Şişe" if "cam" in t_lower and "1" in t_lower else \
                "1 Litre Teneke" if "teneke" in t_lower and "1" in t_lower else \
                "500 ml Cam Şişe" if "500" in t_lower else "1 Litre"

        yeni_baslik = f"Erken Hasat Natürel Sızma Zeytinyağı {hacim} - Soğuk Sıkım"
        meta_title = f"Erken Hasat Soğuk Sıkım Zeytinyağı {hacim} | Nida Zeytin"
        meta_desc = f"Edremit Körfezi 2026 yeni sezon erken hasat soğuk sıkım natürel sızma zeytinyağı {hacim}. Düşük asit, yüksek polifenol garantisiyle güvenle sipariş verin."
        detail_html = f"""<h3>Nida Zeytin — Erken Hasat Natürel Sızma Zeytinyağı ({hacim})</h3>
<p><strong>Edremit Körfezi</strong>'nin verimli zeytinliklerinden, zeytin taneleri henüz dalında yeşilken ve polifenol değerleri en üst seviyedeyken özenle hasat edilmiştir. Hasattan sonra saatler içinde <strong>27°C altında soğuk sıkım (cold press)</strong> yapılarak saf lezzeti ve antioksidan zenginliği korunmuştur.</p>

<h4>Öne Çıkan Ürün Özellikleri:</h4>
<ul>
  <li><strong>Menşei:</strong> Edremit Körfezi / Balıkesir (Coğrafi İşaret Tescilli Bölge)</li>
  <li><strong>Üretim Biçimi:</strong> 27°C Altında Soğuk Sıkım (Cold Pressed), Kontinü Sistem</li>
  <li><strong>Asit Değeri:</strong> En çok %0.4 (Oleik Asit Cinsinden — Üstün Gurme Seviye)</li>
  <li><strong>Aroma Profili:</strong> Çağla badem, enginar, taze biçilmiş çimen kokusu ve genizde meyvemsi yakıcılık</li>
  <li><strong>Filtre Durumu:</strong> Dinlendirilmiş, berrak ve saf zeytinyağı</li>
  <li><strong>Kullanım Tavsiyesi:</strong> Çiğ tüketim, kahvaltılık soslar, gurme salatalar ve şifa amaçlı günlük kullanım için idealdir.</li>
</ul>

<h4>Saklama ve Muhafaza Koşulları:</h4>
<p>Zeytinyağınızı doğrudan güneş ışığından, rutubetten ve ısı kaynaklarından uzak, serin bir yerde (15-20°C) ağzı kapalı olarak muhafaza ediniz. Soğuk havada donması doğallığının ve katkısız yapısının kanıtıdır; oda sıcaklığında çözünür.</p>"""
        etiketler = "erken hasat zeytinyağı, soğuk sıkım zeytinyağı, edremit zeytinyağı, natürel sızma zeytinyağı, düşük asit zeytinyağı, polifenol zeytinyağı, nida zeytin, hakiki zeytinyağı"

    # 2. SOĞUK SIKIM NATÜREL SIZMA ZEYTİNYAĞLARI (Genel Sezon Serisi)
    elif "sizma" in t_lower or "sızma" in t_lower or "zeytinyag" in t_lower or "zeytinyağ" in t_lower or "zeytinyag" in c_lower or "overseas" in c_lower:
        ambalaj = "18 Litre Teneke" if "18" in t_lower or "18litre" in c_lower else \
                  "5 Litre Teneke" if "5lt" in t_lower or "5 litre" in t_lower or "5litre" in c_lower else \
                  "3 Litre Teneke" if "3" in t_lower or "3litre" in c_lower else \
                  "2 Litre Teneke" if "teneke" in t_lower and ("2" in t_lower or "2litre" in c_lower) else \
                  "2 Litre Pet" if "pet" in t_lower and ("2" in t_lower or "2litre" in c_lower) else \
                  "1 Litre Cam Şişe" if "cam" in t_lower and ("1" in t_lower or "1litre" in c_lower or "1lt" in c_lower) else \
                  "1 Litre Teneke" if "teneke" in t_lower and ("1" in t_lower or "1litre" in c_lower) else \
                  "1 Litre Pet Şişe" if "pet" in t_lower and ("1" in t_lower or "1litre" in c_lower) else \
                  "750 ml Cam Şişe" if "750" in t_lower or "750ml" in c_lower else \
                  "500 ml Cam Şişe" if ("500" in t_lower or "500ml" in c_lower) and "cam" in (t_lower + c_lower) else \
                  "500 ml Pet Şişe" if ("500" in t_lower or "500ml" in c_lower) and "pet" in (t_lower + c_lower) else \
                  "250 ml Cam Şişe" if ("250" in t_lower or "250ml" in c_lower) and "cam" in (t_lower + c_lower) else \
                  "250 ml Pet Şişe" if ("250" in t_lower or "250ml" in c_lower) and "pet" in (t_lower + c_lower) else \
                  "1 Litre"

        yeni_baslik = f"Natürel Sızma Zeytinyağı {ambalaj} - Edremit Soğuk Sıkım"
        meta_title = f"Natürel Sızma Zeytinyağı {ambalaj} | Nida Zeytin"
        meta_desc = f"Edremit Körfezi soğuk sıkım natürel sızma zeytinyağı {ambalaj}. Yemeklerde ve salatalarda eşsiz lezzet. Doğal, katkısız, hızlı kargo ile Nida Zeytin'de."
        detail_html = f"""<h3>Nida Zeytin — Natürel Sızma Zeytinyağı ({ambalaj})</h3>
<p><strong>Olive Edremit Zeytincilik</strong> bahçelerinden toplanan geleneksel Edremit tipi zeytinlerden elde edilen <strong>Natürel Sızma Zeytinyağı</strong>, zengin lezzeti ve berrak yapısıyla hem sıcak tencere yemeklerinizde hem de salatalarınızda sofralarınıza sağlık katar.</p>

<h4>Ürün Özellikleri:</h4>
<ul>
  <li><strong>Menşei:</strong> Balıkesir / Edremit Körfezi</li>
  <li><strong>Üretim Biçimi:</strong> Soğuk Sıkım Yöntemi (Maksimum 27°C)</li>
  <li><strong>Asit Değeri:</strong> En çok %0.8 oleik asit (Natürel Sızma Standardı)</li>
  <li><strong>Tadım Notu:</strong> Hafif meyvemsi aroma, yumuşak ve dengeli boğaz geçişi</li>
  <li><strong>Ambalaj:</strong> Işık ve hava geçirmeyen hijyenik {ambalaj}</li>
  <li><strong>Saflık Güvencesi:</strong> %100 katkısız, renklendirici ve koruyucu içermez.</li>
</ul>

<h4>Kullanım Önerileri:</h4>
<p>Tüm zeytinyağlı yemeklerde, balık ve et marinasyonlarında, çorbalarda ve kahvaltılık soslarda mükemmel uyum sağlar. Serin, kuru ve ışık almayan ortamda muhafaza ediniz.</p>"""
        etiketler = "natürel sızma zeytinyağı, edremit zeytinyağı, soğuk sıkım zeytinyağı, yemeklik zeytinyağı, hakiki sızma zeytinyağı, teneke zeytinyağı, nida zeytin"

    # 3. KIRMA YEŞİL ZEYTİN
    elif "kırma" in t_lower or "kirma" in t_lower or "neykz" in c_lower:
        yeni_baslik = "Edremit Yeşil Kırma Zeytin 1 kg - Doğal Fermente"
        meta_title = "Edremit Yeşil Kırma Zeytin 1 kg | Nida Zeytin"
        meta_desc = "Edremit Körfezi taze hasat yeşil kırma zeytin 1 kg. Geleneksel taş kırma yöntemi, katkısız kaya tuzuyla doğal fermente. Hemen Nida Zeytin'den sipariş verin."
        detail_html = """<h3>Nida Zeytin — Edremit Yeşil Kırma Zeytin (1 kg)</h3>
<p>Edremit Körfezi bahçelerimizden erken dönemde toplanan etli yeşil zeytin taneleri, geleneksel yöntemle çekirdeği zedelenmeden kırılarak tatlandırılmıştır. Doğal fermantasyon süreciyle acılığı giderilen zeytinlerimiz taptaze ve diri kıvamıyla kahvaltı sofralarının vazgeçilmezidir.</p>

<h4>Ürün Özellikleri:</h4>
<ul>
  <li><strong>Menşei:</strong> Edremit Körfezi / Balıkesir</li>
  <li><strong>Yöntem:</strong> Taş Kırma, Doğal Kaya Tuzu Salamurası</li>
  <li><strong>Katkı Durumu:</strong> Koruyucu, renklendirici ve kostik içermez; %100 doğaldır.</li>
  <li><strong>Lezzet Profili:</strong> Kendine has hafif meyvemsi ve taze yeşil zeytin rayihası</li>
</ul>"""
        etiketler = "yeşil kırma zeytin, edremit kırma zeytin, taş kırma zeytin, doğal kırma zeytin 1 kg, taze yeşil zeytin, nida zeytin"

    # 4. ÇİZİK YEŞİL ZEYTİNLER
    elif "çizik" in t_lower or "cizik" in t_lower or "kocaseyit" in c_lower:
        agirlik = "1 Kg Kavanoz" if "1 kg" in t_lower or "1kg" in c_lower else \
                  "10 Kg Kova (Kalibre L / 230-260)" if "230-260" in t_lower or "230-260" in c_lower else \
                  "10 Kg Kova (Kalibre M / 260-290)" if "260-290" in t_lower or "260-290" in c_lower else \
                  "10 Kg Kova (Kalibre 2XL / 181-200)" if "181-200" in c_lower else \
                  "10 Kg Kova (Kalibre XL / 201-230)" if "201-230" in c_lower else \
                  "10 Kg Kova (Kalibre S / 291-320)" if "291-320" in c_lower else \
                  "10 Kg Kova (Kalibre 2XS / 351-380)" if "351-380" in c_lower else "10 Kg Kova"

        varyant_ad = "Kocaseyit Köklü Pembe Çizik Zeytin" if "pembe" in t_lower or "pembe" in c_lower else \
                     "Kocaseyit Köklü Yeşil Çizik Zeytin" if "kocaseyit" in t_lower or "kocaseyit" in c_lower else \
                     "Edremit Çizik Yeşil Zeytin"

        yeni_baslik = f"{varyant_ad} {agirlik} - Doğal Fermente"
        meta_title = f"{varyant_ad} {agirlik} | Nida Zeytin"
        meta_desc = f"Edremit Körfezi coğrafi işaretli doğal fermente yeşil çizik zeytin {agirlik}. Katkısız kaya tuzu ve kaynak suyuyla olgunlaştırılmış çıtır zeytin lezzeti."
        detail_html = f"""<h3>Nida Zeytin — {varyant_ad} ({agirlik})</h3>
<p><strong>Edremit Körfezi Coğrafi İşaretli</strong> Edremit tipi etli ve çekirdeğinden kolay ayrılan yeşil zeytinler, hasat edildikten hemen sonra özenle çizilerek yalnızca <strong>kaynak suyu ve kaya tuzu</strong> ile doğal salamura havuzlarında tatlandırılmıştır.</p>

<h4>Ürün Özellikleri:</h4>
<ul>
  <li><strong>Menşei:</strong> Edremit Körfezi / Balıkesir (Coğrafi İşaret Tescilli)</li>
  <li><strong>İşleme Yöntemi:</strong> Geleneksel Doğal Fermantasyon (Kostik ve kimyasal hızlandırıcı içermez)</li>
  <li><strong>Doku ve Lezzet:</strong> Diri, etli, çıtır dokulu, hafif ekşimsi doğal fermente Edremit aroması</li>
  <li><strong>Ambalaj:</strong> Gıdaya uygun kilitli {agirlik}</li>
  <li><strong>Tüketim Tavsiyesi:</strong> Sofraya alırken üzerine Nida Erken Hasat Zeytinyağı, kekik, pul biber ve limon dilimleri ekleyerek servis yapınız.</li>
</ul>

<h4>Saklama Tavsiyesi:</h4>
<p>Kendi salamura suyu içerisinde, serin ve doğrudan güneş almayan yerde muhafaza ediniz. Zeytinlerin suyun üzerinde kalmamasına özen gösteriniz.</p>"""
        etiketler = "edremit çizik zeytin, yeşil çizik zeytin, doğal fermente zeytin, sofralık yeşil zeytin, coğrafi işaretli zeytin, kocaseyit zeytin, kova zeytin, nida zeytin"

    # 5. DİLİMLİ SİYAH ZEYTİN
    elif "dilimli" in t_lower or "dilimli" in c_lower:
        yeni_baslik = "Dilimli Siyah Zeytin 8 kg Teneke Ambalaj"
        meta_title = "Dilimli Siyah Zeytin 8 kg Teneke | Nida Zeytin"
        meta_desc = "Pizza, salata, sandviç ve hamur işleri için birinci kalite dilimli siyah zeytin 8 kg teneke ambalaj. Horeca ve toplu tüketime uygun hijyenik üretim."
        detail_html = """<h3>Nida Zeytin — Dilimli Siyah Zeytin (8 kg Teneke)</h3>
<p>Tam olgunlaşmış etli siyah sofralık zeytinlerin çekirdekleri hijyenik koşullarda çıkarılarak eşit dilimlenmiştir. Peynirli salatalar, gurme pizzalar, poğaça ve sandviçler için kullanıma hazır pratik lezzettir.</p>
<h4>Öne Çıkan Özellikler:</h4>
<ul>
  <li><strong>Net Ağırlık:</strong> 8 kg Teneke Ambalaj</li>
  <li><strong>Kullanım Alanı:</strong> Restoran, kafe, otel (HORECA), unlu mamul işletmeleri ve ev kullanımı</li>
  <li><strong>Form:</strong> Çekirdeksiz, muntazam halka dilimli</li>
</ul>"""
        etiketler = "dilimli siyah zeytin, pizza zeytini, salata zeytini, 8 kg teneke zeytin, horeca zeytin, çekirdeksiz zeytin dilimi, nida zeytin"

    # 6. KURU SELE SİYAH ZEYTİN
    elif "kuru sele" in t_lower or "edremitsele" in c_lower:
        yeni_baslik = "Kuru Sele Siyah Zeytin 1 kg - Katkısız Doğal Çuval Sele"
        meta_title = "Kuru Sele Siyah Zeytin 1 kg (Az Tuzlu) | Nida Zeytin"
        meta_desc = "Geleneksel bez çuvallarda kaya tuzuyla 60 gün dinlendirilen katkısız kuru sele siyah zeytin 1 kg. İnce kabuklu, az tuzlu, yoğun lezzet Nida Zeytin'de."
        detail_html = """<h3>Nida Zeytin — Kuru Sele Siyah Zeytin (1 kg)</h3>
<p>Edremit Körfezi'nin dalında kararmış olgun zeytinleri, geleneksel bez çuvallarda yalnızca kaya tuzu serpiştirilerek günaşırı çevrilmek suretiyle 60 gün dinlendirilir. Kendi suyunu salarak olgunlaşan kuru sele zeytini, buruşuk ince kabuğu ve etli çekirdeğiyle zeytinin en saf halidir.</p>

<h4>Ürün Özellikleri:</h4>
<ul>
  <li><strong>Üretim Şekli:</strong> Geleneksel Kuru Çuval Sele Yöntemi</li>
  <li><strong>Tuz Oranı:</strong> Düşük / Az Tuzlu (Tuz hassasiyeti olanlar için ideal)</li>
  <li><strong>Doku:</strong> İnce kabuklu, yoğun zeytin aromalı, kolay ayrılan çekirdek</li>
  <li><strong>Katkısızlık:</strong> Kimyasal karartıcı, boya veya koruyucu kesinlikle kullanılmaz.</li>
</ul>"""
        etiketler = "kuru sele zeytin, çuval sele siyah zeytin, az tuzlu siyah zeytin, edremit kuru sele 1 kg, katkısız siyah zeytin, nida zeytin"

    # 7. YAĞLI SELE SİYAH ZEYTİN
    elif "sele" in t_lower or "sele" in c_lower:
        agirlik_str = "10 kg Kova (Lüks Kalibre 321-370)" if "10" in t_lower or "10 kg" in c_lower else "1 kg"
        yeni_baslik = f"Gemlik Yağlı Sele Siyah Zeytin {agirlik_str}"
        meta_title = f"Gemlik Yağlı Sele Siyah Zeytin {agirlik_str} | Nida Zeytin"
        meta_desc = f"Doğal fermente etli ve lezzetli Gemlik tipi yağlı sele siyah zeytin {agirlik_str}. Küçük çekirdekli, bol etli sofralık gurme zeytin Nida Zeytin'de."
        detail_html = f"""<h3>Nida Zeytin — Gemlik Yağlı Sele Siyah Zeytin ({agirlik_str})</h3>
<p>Geleneksel havuzlarda doğal fermantasyon ile olgunlaştırılan yağlı sele zeytinimiz, ince kabuğu, zengin et dokusu ve parlak rengiyle sofralarınızın baş tacıdır.</p>
<h4>Öne Çıkan Özellikler:</h4>
<ul>
  <li><strong>Tür:</strong> Yağlı Sele Siyah Sofralık Zeytin</li>
  <li><strong>Ambalaj:</strong> {agirlik_str}</li>
  <li><strong>Karakter:</strong> Yumuşak etli, küçük çekirdekli ve dengeli tuz oranlı</li>
</ul>"""
        etiketler = "yağlı sele zeytin, gemlik siyah zeytin, sofralık siyah zeytin, sele zeytini 1 kg, etli siyah zeytin, nida zeytin"

    # 8. DOĞAL SABUNLAR
    elif "sabun" in t_lower or "sabun" in c_lower:
        tur = "Aloe Vera" if "aloe" in c_lower or "aloe" in t_lower else \
              "Bıttım (Menengiç)" if "bittim" in c_lower or "bıttım" in t_lower or "bittim" in t_lower else \
              "Gül" if "gul" in c_lower or "gül" in c_lower or "gül" in t_lower or "gul" in t_lower else \
              "Kükürt" if "kukurt" in c_lower or "kükürt" in c_lower or "kükürt" in t_lower or "kukurt" in t_lower else \
              "Lavanta" if "lavanta" in c_lower or "lavanta" in t_lower else \
              "Nar Çekirdeği" if "nar" in c_lower or "nar" in t_lower else \
              "Salyangoz Özlü" if "salyangoz" in c_lower or "salyangoz" in t_lower else \
              "Ardıç Katranı" if "ardic" in c_lower or "ardıç" in t_lower or "ardic" in t_lower else \
              "Eşek Sütü" if "esek" in c_lower or "eşek" in t_lower or "esek" in t_lower else \
              "Kolajen" if "kolojen" in c_lower or "kolajen" in t_lower or "kolojen" in t_lower else \
              "Okyanus Ferahlığı" if "okyanus" in c_lower or "okyanus" in t_lower else \
              "Geleneksel Türk Hamamı" if "turk" in c_lower or "hamam" in t_lower else \
              "Keçi Sütü" if "keci" in c_lower or "keçi" in t_lower or "keci" in t_lower else "Zeytinyağlı"

        sungerli = "sungerli" in c_lower or "süngerli" in t_lower or "sungerli" in t_lower
        form_ad = f"Doğal Süngerli {tur} Sabunu 100 gr" if sungerli else f"Doğal {tur} Sabunu 100 gr Kutulu"

        yeni_baslik = form_ad
        meta_title = f"{form_ad} (El Yapımı & Bitkisel) | Nida Zeytin"
        meta_desc = f"{form_ad}. Edremit saf zeytinyağı ve bitkisel özlerle üretilmiş el yapımı banyo ve cilt sabunu. Doğal temizlik ve arındırıcı bakım Nida Zeytin'de."

        fayda_metni = "Cildi derinlemesine nemlendirir, güneş sonrası yatıştırıcı bakım sağlar." if "Aloe" in tur else \
                      "Saç köklerini besler, kepek ve dökülme karşıtı geleneksel saç ve saç derisi bakımı sunar." if "Bıttım" in tur else \
                      "Gözenekleri arındırır, cilde doğal tonik etkisi ve canlı pembe ışıltı kazandırır." if "Gül" in tur else \
                      "Fazla sebumu dengeler, yağlı ve sivilceye eğilimli ciltlerde siyah nokta görünümünü azaltır." if "Kükürt" in tur else \
                      "Aromaterapik kokusuyla cildi ve ruhu dinlendirir, rahatlatıcı banyo keyfi sunar." if "Lavanta" in tur else \
                      "Yüksek antioksidan ve C vitamini içeriğiyle cildi canlandırır, elastikiyeti destekler." if "Nar" in tur else \
                      "Allantoin içeriğiyle cilt yenilenmesini ve pürüzsüz görünümü destekler, leke bakımına yardımcı olur." if "Salyangoz" in tur else \
                      "Zengin protein ve kalsiyumla cildi kurutmadan besler, ipeksi yumuşaklık verir." if "Eşek" in tur or "Keçi" in tur else \
                      "Ardıç katranı antiseptik özelliğiyle problemli cilt ve kepekli saç derisini arındırır." if "Ardıç" in tur else \
                      "Cildin sıkılaşmasını, dolgun ve genç görünüm kazanmasını destekler." if "Kolajen" in tur else \
                      "Geleneksel Türk hamamı ferahlığını saf zeytinyağı bereketiyle teninize taşır."

        detail_html = f"""<h3>Nida Zeytin — {form_ad}</h3>
<p><strong>Edremit zeytinyağı</strong> ve zengin bitkisel özlerin harmanlanmasıyla geleneksel yöntemlerle üretilen sabunumuz, cildinizi kurutmadan nazikçe arındırır ve doğal nem dengesini korur.</p>

<h4>Öne Çıkan Faydaları:</h4>
<ul>
  <li><strong>İçerik:</strong> Saf Edremit zeytinyağı, {tur} özü ve doğal gliserin</li>
  <li><strong>Etki:</strong> {fayda_metni}</li>
  <li><strong>Kullanım:</strong> Yüz, vücut ve saç temizliğinde günlük kullanıma uygundur.</li>
  <li><strong>Temiz Formül:</strong> Paraben, SLS, hayvansal yağ ve sentetik sertleştiriciler içermez.</li>
</ul>"""
        etiketler = f"{tur.lower()} sabunu, doğal sabun, el yapımı sabun, zeytinyağlı sabun, bitkisel sabun, nida zeytin, banyo sabunu"

    # 9. ZEYTİN ÇİÇEĞİ KOLONYALARI
    elif "kolonya" in t_lower or "kolonya" in c_lower:
        hacim = "400 ml" if "400" in t_lower else "250 ml Cam Şişe" if "250" in t_lower else "150 ml"
        yeni_baslik = f"Zeytin Çiçeği Kolonyası {hacim} (80°)"
        meta_title = f"Zeytin Çiçeği Kolonyası {hacim} (80 Derece) | Nida Zeytin"
        meta_desc = f"Kaz Dağları ve Edremit Körfezi esintili 80° ferahlatıcı zeytin çiçeği kolonyası {hacim}. Kalıcı kokusu ve hijyenik formülüyle hemen sipariş verin."
        detail_html = f"""<h3>Nida Zeytin — Zeytin Çiçeği Kolonyası ({hacim} — 80°)</h3>
<p>Kaz Dağları'nın oksijen dolu esintisiyle yeşeren Edremit zeytin bahçelerinin bahar aylarında açan büyüleyici çiçeklerinden ilham alan kolonyamız, 80 derece alkol oranıyla yüksek hijyen ve gün boyu süren ferahlık sağlar.</p>
<h4>Ürün Özellikleri:</h4>
<ul>
  <li><strong>Alkol Derecesi:</strong> 80° (Yüksek Hijyenik Koruma)</li>
  <li><strong>Koku Profili:</strong> Taze zeytin çiçeği, narenciye ve beyaz çiçek esintileri</li>
  <li><strong>Ambalaj:</strong> {hacim} ergonomik tasarım</li>
  <li><strong>Kalıcılık:</strong> Ciltte kuruluk yapmayan ferahlatıcı ve kalıcı koku</li>
</ul>"""
        etiketler = "zeytin çiçeği kolonyası, 80 derece kolonya, kaz dağları kolonyası, edremit kolonyası, hediyelik kolonya, nida zeytin"

    # 10. KİRALIK ZEYTİN AĞACI
    elif "kiralik" in c_lower or "kiralık" in t_lower:
        yeni_baslik = "Kiralık Zeytin Ağacı ve Kişisel Etiketli Natürel Sızma Zeytinyağı"
        meta_title = "Kiralık Zeytin Ağacı & Adınıza Özel Zeytinyağı | Nida Zeytin"
        meta_desc = "Edremit Körfezi'nde bir zeytin ağacınız olsun. Hasat edilen zeytinler adınıza özel etiketli soğuk sıkım sızma zeytinyağı olarak adresinize gelsin."
        detail_html = """<h3>Nida Zeytin — Kiralık Zeytin Ağacı Projesi</h3>
<p>Edremit Körfezi'ndeki asırlık zeytinliğimizde sizin veya sevdiklerinizin adına bir zeytin ağacı tahsis edilir. Ağacınız yıl boyunca uzman ziraatçilerimiz tarafından özenle bakılır, hasat zamanı ürünleri soğuk sıkım natürel sızma zeytinyağına dönüştürülerek <strong>adınıza özel hazırlanan etiketlerle</strong> teneke ambalajlarda kapınıza kadar gönderilir.</p>"""
        etiketler = "kiralık zeytin ağacı, kişiye özel zeytinyağı, ağaç evlat edinme, kurumsal gurme hediye, edremit zeytinliği, nida zeytin"

    else:
        yeni_baslik = title
        meta_title = f"{title} | Nida Zeytin"
        meta_desc = f"{title} en taze ve doğal haliyle Nida Zeytin'de. Edremit Körfezi'nden sofranıza güvenilir ve hızlı kargo ile hemen sipariş verin."
        detail_html = f"<h3>{title}</h3>\n<p>{title}, Nida Zeytin güvencesiyle Edremit Körfezi'nin doğal zenginliğini sofralarınıza taşır.</p>"
        etiketler = "nida zeytin, edremit zeytincilik, doğal ürünler, edremit körfezi"

    return {
        "title_tr": yeni_baslik,
        "keywords_tr": meta_title,
        "description_tr": meta_desc,
        "detail_tr": detail_html,
        "etiket": etiketler,
    }


def excel_seo_guncelle():
    """docs/Ürünler_1793508054_orijinal.xlsx dosyasını okuyup docs/Ürünler_1793508054.xlsx ve docs/Urunler_SEO_Guncel.xlsx yazar."""
    kaynak = YEDEK_YOLU if os.path.exists(YEDEK_YOLU) else EXCEL_YOLU
    if not os.path.exists(kaynak):
        raise FileNotFoundError(f"Kaynak Excel bulunamadı: {kaynak}")

    if not os.path.exists(YEDEK_YOLU):
        shutil.copyfile(EXCEL_YOLU, YEDEK_YOLU)
        print(f"Orijinal Excel yedeklendi: {YEDEK_YOLU}")

    wb = openpyxl.load_workbook(kaynak)
    ws = wb.active

    headers = [cell.value for cell in ws[1]]
    col_idx = {}
    for i, h in enumerate(headers, 1):
        if not h:
            continue
        hs = str(h)
        for field in ("id", "code", "title_tr", "keywords_tr", "description_tr", "detail_tr", "etiket"):
            if f"|{field}|" in hs or hs.strip().lower() == field:
                col_idx[field] = i

    print("Tespit edilen sütunlar:", col_idx)

    guncellenen = 0
    for row_num in range(2, ws.max_row + 1):
        urun_id = ws.cell(row=row_num, column=col_idx.get("id", 1)).value
        if not urun_id:
            continue

        code = str(ws.cell(row=row_num, column=col_idx.get("code", 2)).value or "")
        title = str(ws.cell(row=row_num, column=col_idx.get("title_tr", 5)).value or "")

        if code.lower() == "test":
            continue

        seo = seo_metinlerini_uret(code, title)

        if "title_tr" in col_idx:
            ws.cell(row=row_num, column=col_idx["title_tr"], value=seo["title_tr"])
        if "keywords_tr" in col_idx:
            ws.cell(row=row_num, column=col_idx["keywords_tr"], value=seo["keywords_tr"])
        if "description_tr" in col_idx:
            ws.cell(row=row_num, column=col_idx["description_tr"], value=seo["description_tr"])
        if "detail_tr" in col_idx:
            ws.cell(row=row_num, column=col_idx["detail_tr"], value=seo["detail_tr"])
        if "etiket" in col_idx:
            ws.cell(row=row_num, column=col_idx["etiket"], value=seo["etiket"])

        guncellenen += 1

    wb.save(EXCEL_YOLU)
    wb.save(GUNCEL_YOLU)
    print(f"Toplam {guncellenen} ürünün SEO metinleri başarıyla güncellendi.")
    print(f"1. Doğrudan SoftTR paneline yüklenecek dosya: {EXCEL_YOLU}")
    print(f"2. Yedek güncel kopya: {GUNCEL_YOLU}")

    return guncellenen


if __name__ == "__main__":
    excel_seo_guncelle()
