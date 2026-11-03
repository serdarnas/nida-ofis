# Nida Zeytin — Yeni Müşteri ve Satış Büyüme Planı

**Hazırlanma tarihi:** 3 Kasım 2026 · **Plan dönemi:** Kasım 2026 – Ocak 2027 (90 gün)
**Kapsam:** `nida-ofis` ajan ofisi + nidazeytin.com + pazaryerleri. Bu belge bir plandır; canlı mağaza, fiyat, reklam ve mail kararları her zaman senin onayındadır.

---

## 1. Tek bakışta

1. **Ürün ve altyapı hazır, satış motoru eksik.** 10 departman ajanı, 12 görevlik takvim, canlı katalog var; ama 3 Kasım itibarıyla yalnızca 2 gerçek çıktı üretilmiş ve bunlar ya boş iskelet ya genel metin.
2. **En büyük fırsat B2B/HORECA ve kurumsal hediye.** Katalogda zaten kalibre bazlı 8–10 kg zeytin kovaları, 5 L tenekeler ve "Kiralık Zeytin Ağacı" (4.585 TL) var; bunlar için ne bir toptan sayfası ne bir lead listesi ne de takip sistemi var.
3. **Mevsim şimdi:** Erken hasat sezonu, 11.11, Efsane Kasım / Black Friday (27 Kasım), yılbaşı kurumsal hediye ve Ocak sonunda Ramazan hazırlığı. İlk 4 hafta kaçırılırsa en güçlü satış penceresi geçer.
4. **Ajanlar kör çalışıyor:** maliyet, satış ve müşteri verisi yok; web erişimleri yok. Bu yüzden fiyat/marj ve kampanya önerileri üretemiyorlar.
5. **Önce temel, sonra reklam:** sitede güven unsuru (yorum, analiz raporu), kargo mesajı ve sosyal bağlantılar yok; sepet ve şifre linkleri hatalı. Reklam bütçesi bu açık sepete dökülmemeli.

---

## 2. Mevcut durum — bulgular

### 2.1 Ajan ofisi (proje klasörü)

| Bulgu | Kanıt | Sonuç |
|---|---|---|
| Sadece 2 gerçek çalışma var (1 Kasım) | `kosular/`, `cikti/` | Planlı iş akışı fiilen başlamadı |
| `pazaryeri-butik` çıktısı boş iskelet | "XML okunamadı — sayı uydurmayacağım" | Fiyat/marj matrisi hâlâ yok |
| `pazaryeri-tr` çıktısı iyi ama tek | 2 ürün için başlık + madde | 53 ürünün 51'i için yok |
| Takvimde 10 görev "yapılacak", 2 Kasım görevleri hâlâ tamamlanmamış | `veri/takvim.json` | Otonom zamanlayıcı çalışmıyor olabilir (sunucu/Docker kapalı?) |
| `hafiza/` boş (sadece 1 satırlık dosya) | `hafiza/pazaryeri-tr.md` | Ajanlar öğrenmiyor, her seferinde sıfırdan başlıyor |
| `veri/dahili-fiyat-listesi.md` bozuk: sadece ID sütunu dolu, diğer sütunlar boş | dosya içeriği | Maliyet/taban fiyat verisi fiilen yok |
| `veri/fiyat-listesi.csv` yok (sadece `.example.csv`) | `marka-profili.md` bu dosyaya atıf yapıyor | Marj hesabı yapılamaz |
| Excel 80 ürün, XML 53 ürün | `docs/*.xlsx` vs `urun-fiyat-stok.md` | Hangi 27 ürün sitede/pazaryerinde yok belirsiz |
| Satış, sipariş, müşteri, lead verisi hiç yok | klasörde yok | Hangi ürün/kanal kazandırıyor bilinmiyor |

### 2.2 Katalog ve fiyat (53 ürün, XML 2 Kasım)

- **En az 10 ürün "Tükendi":** 8 süngerli sabun, Aloe Vera sabunu, 10 kg Edremit Çizik Yeşil (1.400 TL). Bunlar pazaryerinde "tedarik edilemedi" cezası ve reklam israfı riski.
- **Fiyat merdiveni tutarsız görünüyor:** "Soğuk Sıkım Naturel Sızma 1 L" 537,10 TL iken "Erken Hasat 1 L Cam" 380 TL ve "Naturel Sızma 1 L Pet" 326,67 TL. Küsuratlı fiyatlar (326,67 / 537,10 / 97,16) otomatik dönüşümden gelmiş gibi duruyor. Müşteri neden 537 TL'nin 380 TL'den pahalı olduğunu göremez.
- **İki marka aynı sitede:** "Kocaseyit Köklü" kalibreli 10 kg zeytinler ve "Nida" ürünleri karışık; sitede "Havran Zeytini" adı da geçiyor. Marka hikâyesi netleşmeli (bkz. 4.4).
- **Kalibreli 10 kg kovalar (2XS–2XL, yeşil/pembe/siyah sele) güçlü bir B2B varlığı** ama perakende ürün sayfası gibi duruyor, toptan fiyat kademesi yok.
- **Kiralık Zeytin Ağacı + kişisel etiketli yağ (4.585 TL)** hediye ve kurumsal için ayrıcalıklı bir ürün; hediye kampanyalarında öne çıkmıyor.
- 8 ürün 55 TL'lik sabun; sabunlar sepet ortalamasını büyütmek için çapraz satış ürünü olarak kullanılabilir (tükenenler hariç).

### 2.3 nidazeytin.com (3 Kasım ana sayfa incelemesi)

- **Eksik:** görünür H1/değer önerisi, yorum/sertifika/analiz raporu, kargo/ücretsiz kargo mesajı, ödeme logoları, özel toptan sayfası (sadece "Bayilik Başvurusu"), sosyal medya linkleri.
- **Hatalar:** "Şifremi Unuttum" kayıt sayfasına gidiyor, "Sepetim" ana sayfaya gidiyor, dil seçeneğinde "Engilish", meta açıklamada yazım hataları, her üründe "Yeni Ürün" rozeti, bazı başlıklar kesik.
- **Güçlü yan:** WhatsApp butonu, e-bülten kaydı, ETBİS rozeti, zeytin hasat/yağ verimi hesaplayıcıları (iyi bir lead mıknatısı olabilir), Pazaryerleri sayfası.

### 2.4 Kanal portföyü

9 pazaryeri + site + Facebook + LinkedIn tanımlı. Instagram sadece bir görev açıklamasında geçiyor, `marka-profili.md` kanal listesinde yok. Google tarafı (Merchant Center, Shopping, Business Profile, Search Console) hiçbir yerde tanımlı değil. Küçük bir ekip için 9 pazaryeri dağınık; hangi kanalın para kazandırdığını bilmeden hepsini beslemek enerji kaybı.

---

## 3. Eksikler — öncelik sırasıyla

### P0 — Önce bunlar (Hafta 1–2, satışı doğrudan engelliyor)
1. **Maliyet ve taban fiyat dosyası** (`veri/fiyat-listesi.csv`): ürün bazlı maliyet (zeytin/yağ, ambalaj, etiket, koli, kargo) + hedef marj. Bu olmadan hiçbir kampanya "kârlı mı" diye ölçülemez.
2. **Sitedeki kırık akışlar:** sepet linki, şifre sıfırlama, "Engilish", meta yazım hataları, "Yeni Ürün" rozetini temizleme.
3. **Güven katmanı:** laboratuvar/asit analiz raporu görselleri (hasat yılı bazlı), üretim hikâyesi, yorum bloğu, kargo koruma garantisi, ödeme logoları, sosyal bağlantılar.
4. **Stok doğruluğu:** tükenen ürünleri pazaryerlerinde kapat/“geri bildirim” moduna al; kritik stoklar için güvenlik stoğu eşiği tanımla.
5. **Zamanlayıcıyı doğrula:** Docker/Coolify'daki ofis sunucusu çalışıyor mu, `otonom_aktif` gerçekten tetikliyor mu? Gecikmiş 2 Kasım görevleri koşulmalı. **Bulunan neden adayı:** Docker imajında saat dilimi yoktu (UTC); "08:30" görevleri İstanbul'da 11:30'da tetiklenirdi. `TZ=Europe/Istanbul` eklendi, yeniden deploy gerekli.

### P1 — Yeni müşteri kazandıran kurulumlar (Hafta 2–4)
6. **B2B/HORECA sayfası + teklif formu:** minimum sipariş, kademeli fiyat, numune talebi, 5 L / 8–10 kg ürünler, kalibre tablosu, fatura/vade koşulları, WhatsApp'a tek tık.
7. **Lead listesi ve basit CRM** (`veri/musteriler.csv` veya Google Sheet): kişi, kurum, segment, kaynak, durum, son temas, sonraki adım. Başlangıç için 150–300 hedef kurum.
8. **Google görünürlüğü:** Merchant Center ürün akışı (zaten SoftTR XML var), Google Business Profile (Edremit), Search Console, Shopping + marka dışı arama kampanyası.
9. **Sosyal kanal tamamlama:** Instagram hesabı resmi kanal olarak profile eklensin; Facebook/Instagram Reels düzeni haftalık çalışsın; yorum ve UGC toplama.
10. **Yorum ve itibar sistemi:** kutu içi teşekkür kartı + QR (yorum bırak), WhatsApp'tan sipariş sonrası mesaj, pazaryeri soru-cevap SLA.
11. **Satış verisi akışı:** SoftTR sipariş export'u ve pazaryeri raporlarını haftalık `veri/satis.csv`'ye çekmek.

### P2 — Büyütme ve farklılaşma (Ocak sonrası)
12. **Abonelik / yıllık yağ planı** ("her ay 1 L" veya "sezonluk 5 L") ve **kurumsal yıllık anlaşma**.
13. **Kiralık zeytin ağacını marka vitrinine çıkarma** (hediye, düğün, şirket CSR); fotoğraf/video, sertifika, ağaç sahibi sayfası.
14. **Private label / ihracat hattı:** B2B ihracat sayfası (EN), tek sayfalık ürün föyü, numune politikası.
15. **Amazon pilotu** (tek ürün, tek ülke); Ozon ve Temu pilotu marj netleşmeden başlatılmamalı.
16. **Blog / SEO kümeleri** (hakiki zeytinyağı nasıl anlaşılır, erken hasat farkı, çizik zeytin nasıl tüketilir, 5 L kaç kişilik yeter) + FAQ şeması.

---

## 4. Hedef kitle ve kanal stratejisi

### 4.1 Segmentler

| Segment | Neden | Ana ürün | Ana kanal |
|---|---|---|---|
| Kahvaltı salonu, otel, restoran, catering (HORECA) | Tekrarlı ve büyük sipariş | 5 L teneke, 8–10 kg kova zeytin | Telefon/WhatsApp, LinkedIn, yerel saha, Google Haritalar |
| Şarküteri, gurme market, bakkal zinciri, bayi | Dağıtım ve sürekli sipariş | 1 L cam, 250/500 ml, kolonya + sabun seti | Bayilik başvurusu, katalog PDF, numune kiti |
| Kurumsal hediye (yılbaşı, bayram, müşteri hediyesi) | Yüksek sepet, planlı alım | Hediye seti, Kiralık Ağaç, özel etiket | LinkedIn, e-posta, kurumsal teklif PDF |
| Bireysel tüketici (kahvaltı/ev) | Hacim ve marka bilinirliği | 1 L erken hasat, 5 L teneke, çizik zeytin | Site, Google Shopping, Meta, Trendyol/HB |
| Pazaryeri alıcısı | Keşif ve ilk satın alma | Tanışma paketi, 5 L | Trendyol, Hepsiburada, N11 |
| Yurt dışı (ithalatçı / private label) | Uzun vadeli | Kutulu zeytin, teneke yağ | LinkedIn, B2B fuar listeleri, olive@ maili |

### 4.2 Teklif (paketler)
Maliyet verisi gelmeden fiyat vermiyorum; aşağıdaki öneriler paket kurgusudur, fiyat marj hesabından sonra sabitlenir.
- **Tanışma Paketi:** 1 L Erken Hasat Cam + 1 kg Edremit Çizik Yeşil + 1 kg Siyah Sele (liste fiyat toplamı 720 TL; paket indirimi marj kontrolüyle).
- **Sofra Paketi (aile):** 5 L Erken Hasat Teneke + 1 kg çizik + 1 kg kırma zeytin.
- **Hediye Seti:** 500 ml Erken Hasat + kolonya 150 ml + 2 sabun, kutulu ve kart notlu.
- **Kurumsal Set:** hediye seti + logolu kart, 20/50/100 adet kademeli.
- **HORECA Başlangıç:** 5 L teneke ×3 + 10 kg kova zeytin ×1 + numune kiti.
- **Kiralık Zeytin Ağacı:** hediye sertifikası + kişisel etiketli yağ; kurumsal "ağaç hediye et" varyantı.

### 4.3 Kanal öncelikleri
1. **Odak (aktif büyüt):** nidazeytin.com, Trendyol, Hepsiburada, N11, Google Shopping, Meta, LinkedIn, WhatsApp B2B.
2. **Bakım (düşük efor):** PttAVM (ağır ürün kargo avantajı), Pazarama, Akıllı Esnaf. Fiyat matrisi gelince yalnız kârlı SKU'lar.
3. **Pilot (kanıtlanana kadar bekle):** Amazon (tek ürün), Ozon, Temu. Ozon için ödeme/lojistik uygunluğu ve marj ayrıca doğrulanmalı; Temu'da yağ ve zeytin için fiyat baskısı yüksek olabilir.

### 4.4 Marka netleştirme
- Nida Zeytin = Edremit körfezi, erken hasat soğuk sıkım yağ + günlük tüketim.
- Kocaseyit Köklü = kalibreli, işlenmiş sofralık zeytin (B2B odaklı). Sitede ayrı bir koleksiyon/hikâye olarak sunulmalı, "Havran Zeytini" ifadesi tek isimde birleşmeli.
- Karar sende: iki marka mı, "Nida × Kocaseyit Köklü" birlikte mi?

---

## 5. 90 günlük uygulama takvimi

| Dönem | Ana hedef | İşler |
|---|---|---|
| **Hafta 1** (3–9 Kas) | Temeli onar | Site hataları; `fiyat-listesi.csv`; stok kapatma; Google Merchant/Business Profile kurulumu; ofis sunucusunu doğrula; `pazaryeri-butik` ve `web-seo` görevlerini yeniden koştur |
| **Hafta 2** (10–16 Kas) | 11.11 + B2B hazırlık | 11.11 pazaryeri kampanyası (kupon + tanışma paketi); B2B sayfası + teklif formu; ilk 100 lead; Instagram hesabı ve haftalık içerik; yorum kartı basımı |
| **Hafta 3–4** (17–30 Kas) | Efsane Kasım / Black Friday (27 Kas) | Site ve pazaryeri paket kampanyası; Meta retargeting + Google Shopping başlangıcı; LinkedIn ve WhatsApp B2B dalga 1 (ilk 50–100 kurum); kurumsal hediye kataloğu |
| **Aralık** | Hediye + B2B ilk anlaşmalar | Yılbaşı hediye ve Kiralık Ağaç kampanyası; B2B dalga 2 + numune kitleri; e-posta/WhatsApp müşteri listesi kampanyası; haftalık KPI toplantısı |
| **Ocak 2027** | Ölç ve ölçekle | Kanal bazlı kâr analizi; kazanmayan pazaryerlerini ve SKU'ları çıkar; abonelik pilotu; Ramazan (Şubat) paket ve stok planı; Amazon pilot kararı |

### Haftalık ritim (önerilen)
- **Pazartesi:** stok + KPI özeti (tedarik-stok, finans-kontrol)
- **Salı–Çarşamba:** B2B outreach ve LinkedIn (linkedin-b2b)
- **Perşembe:** pazaryeri kampanya güncelleme (pazaryeri-tr, pazaryeri-butik)
- **Cuma:** içerik ve reklam performansı, haftalık özet

---

## 6. Ofis sistemi (ajanlar) için geliştirmeler

| # | Geliştirme | Neden |
|---|---|---|
| 1 | **Veri katmanı:** `fiyat-listesi.csv`, `satis.csv`, `musteriler.csv`, `leadler.csv`; bozuk Excel işleyiciyi (`dahili-fiyat-listesi.md`) düzelt | Ajanlar veriden çalışsın, tahmin etmesin |
| 2 | **Ajan başlamadan veri enjeksiyonu:** `veri_senkron.py` zaten XML çekiyor; sonucu görev promptuna otomatik ekle | `pazaryeri-butik` XML okuyamadı; çözüm erişim değil, veriyi önceden vermek |
| 3 | **Yeni ajan: `b2b-lead`** (HORECA/otel/şarküteri araştırması, kişiselleştirilmiş WhatsApp/e-posta/LinkedIn taslakları, takip hatırlatmaları) | En büyük yeni müşteri kaynağı bu |
| 4 | **Yeni ajan: `crm-sadakat`** (sipariş sonrası mesaj, yorum isteği, yeniden satın alma, abonelik) | Mevcut müşteriden tekrar satış en ucuz satış |
| 5 | **Haftalık "CEO raporu"**: satış, marj, stok, lead, reklam harcaması tek sayfa | Kararı sende hızlandırır |
| 6 | **Onay kuyruğu → yayın:** taslakları tek tıkla Meta/LinkedIn'e (API anahtarları `.env`'de var) veya panelden kopyala-yapıştır akışı | Taslaklar birikip uygulanmıyor |
| 7 | **Hafıza kullanımı:** her koşudan sonra "ne işe yaradı/yaramadı" satırı | `hafiza/` boş |
| 8 | **Başarı ölçümü:** her görev çıktısına "uygulandı mı / sonuç ne" alanı | Hangi ajan değer üretiyor ölçülebilir |
| 9 | **Rapor ve bildirim maili (eklendi, bkz. Bölüm 11):** sabah özeti, gün sonu raporu, hata uyarısı → `serdarnas@gmail.com` | Ofis kapalı kutu olmaktan çıkar; ne olduğunu panele girmeden görürsün |
| 10 | **Güvenlik:** IBAN ve Meta/LinkedIn Client ID repoda; `origin` deposunun özel (private) olduğunu doğrula | Kamuya açıksa kaldırılmalı |

---

## 7. Ölçüm (KPI)

**İlk iş:** Bugünkü baz çizgisini çıkar. Aşağıdaki hedefler varsayıma dayalı tahmindir; baz veri gelince revize edilecek.

| Alan | Metrik | Başlangıç hedef önerisi (90 gün) |
|---|---|---|
| B2B | Ulaşılan kurum → yanıt → numune/teklif → müşteri | 300 → 60 → 20 → 5–8 düzenli müşteri (varsayım: %20 yanıt, %10 kapanış) |
| Site | Dönüşüm oranı, sepet ortalaması, terk oranı | Baz + dönüşümde artış, sepet ort. +%15 (paketlerle) |
| Pazaryeri | Satış, mağaza puanı, BuyBox oranı | Odak 3 pazaryerinde puan ≥ 4,7 (mevcut puan bilinmiyor) |
| Reklam | ROAS (Meta, Google), CPA | Önce test; hedef ROAS maliyet verisinden hesaplanır |
| Müşteri | Tekrar sipariş oranı, yorum sayısı | 90 günde ≥ 100 doğrulanmış yorum |
| Operasyon | Stok-out sayısı, kargo hasar oranı | Stok-out 0, hasar < %1 |
| Finans | Kanal başına net marj | Zararlı SKU'ların tespiti ve çıkarılması |

---

## 8. Uyum ve riskler
- **Sağlık/içerik iddiaları:** "polifenol", "sağlığa faydası", "düşük asit", "coğrafi işaretli", "analiz garantili" gibi ifadeler yalnız belgeli (analiz raporu, tescil) olduğunda reklam/ürün sayfasında kullanılmalı. LinkedIn rehberindeki "%0,3 asit" gibi örnek rakamlar gerçek analiz değilse yayınlanmamalı.
- **Etiket ve KVKK:** B2B listelerde kişisel veri kullanımı ve toplu mesajlarda onay/çıkış seçeneği (İYS) kuralları.
- **Fiyat ve kampanya:** pazaryeri komisyon ve kargo oranları sözleşmeden doğrulanmadan fiyat değiştirilmemeli.
- **Operasyon:** satış artınca stok, dolum ve kargo hasar riski artar; erken hasat stok miktarı doğrulanmalı.
- **Kanal dağılması:** 9 pazaryerini aynı anda büyütmek mümkün değil, odak listesi şart.

---

## 9. Senin vermen gereken kararlar / sağlaman gereken veriler

1. Ürün bazlı **maliyet** ve hedef net marj (kanal başına).
2. **Stok miktarları** (özellikle erken hasat 1 L, 5 L ve 10 kg kova zeytinler) ve dolum kapasitesi.
3. **Geçmiş satış** (son 6–12 ay, kanal ve ürün bazlı) ve mevcut müşteri listesi (WhatsApp/e-posta, izin durumu).
4. **B2B koşulları:** minimum sipariş, vade, kargo/nakliye, numune politikası.
5. **Marka kararı:** Nida ve Kocaseyit Köklü ayrı mı birlikte mi sunulacak?
6. **Aylık reklam bütçesi** üst sınırı (Meta + Google) — onay senin.
7. **Analiz raporları ve sertifikalar** (asit, peroksit, polifenol, coğrafi işaret) hangileri elinde?
8. Zamanlayıcı/sunucu: ofis şu an hangi makinede çalışıyor (yerel mi Coolify mi)?

---

## 10. Hemen yapılacak ilk 10 adım (bu hafta)

1. `fiyat-listesi.csv` doldur (maliyet + hedef marj).
2. Site hatalarını düzelt (sepet, şifre, "Engilish", rozet, meta metinler).
3. Tükenen ürünleri pazaryerlerinde kapat.
4. Ofis sunucusunu doğrula ve gecikmiş görevleri koştur.
5. `pazaryeri-butik` fiyat/marj matrisini katalog + maliyetle yeniden iste.
6. Google Merchant Center ve Business Profile başvurularını aç.
7. B2B sayfası metnini ve teklif formunu yazdır (taslağı `linkedin-b2b` + `web-seo`).
8. İlk 100 kurumluk lead listesi (otel, kahvaltı salonu, restoran, şarküteri; Balıkesir, Çanakkale, İzmir, İstanbul, Bursa).
9. Instagram hesabını `marka-profili.md` kanallarına ekle; haftalık içerik takvimini yayına çıkar.
10. 11.11 ve Black Friday için tanışma paketi + hediye seti kurgusunu onayla.

---

## 11. Rapor ve bildirim sistemi (`rapor_mail.py`)

Ofis sunucusu artık sahibine (**serdarnas@gmail.com**) şu mailleri gönderir:

| Mail | Ne zaman | İçerik |
|---|---|---|
| **Sabah özeti** | Her gün 08:00 | Bugünün planı, gecikmiş görevler, tükenen ürünler, eksik veri uyarısı |
| **Gün sonu raporu** | Her gün 18:30 | Tamamlanan görevler ve ajan özetleri, hatalar, onayını bekleyen taslaklar, yarının planı, tükenen ürünler, token kullanımı, eksik veri |
| **Hata uyarısı** | Bir görev hata verdiğinde | Ajan, görev, çıktı dosyası, hata özeti |
| Görev bitti maili (isteğe bağlı) | `RAPOR_GOREV_MAILI=1` ise | Her biten görev için kısa bildirim (varsayılan kapalı, mail seli olmasın) |

**Kurallar:** Alıcı sabittir, ajanlar mail gönderemez ve alıcı veremez; müşteriye hiçbir mail gitmez. Parola yalnız ortam değişkenindedir (`.env` / Coolify), loglanmaz. SMTP tanımlı değilse rapor gönderilmez; `cikti/rapor/` altına HTML olarak kaydedilir ve olay günlüğüne yazılır. Aynı rapor gün başına bir kez gider; gönderim başarısız olursa 15 dakika arayla en çok 3 kez denenir. İlk çalışmada mevcut bitmiş görevler için geriye dönük mail atılmaz.

**Devreye almak için senin yapacakların (parolayı ben yazmadım, yazmayacağım):**
1. Gönderen hesabı seç: `olive@nidazeytin.com` (hosting panelindeki SMTP bilgileri) **veya** Gmail uygulama şifresi (2 adımlı doğrulama açık olmalı).
2. `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` değerlerini Coolify ortam değişkenlerine (yerelde `.env`) gir. Örnek: `.env.example`.
3. Yeniden deploy et (saat dilimi düzeltmesi de bununla devreye girer).
4. Test: `python3 rapor_mail.py test --gonder` → Gmail'e test maili düşmeli. Sonra `python3 rapor_mail.py gun-sonu --gonder` ile gerçek rapor örneği.

**Sınırlar:** Rapor, `takvim.json` ve `cikti/` içindeki gerçek kayıtlardan üretilir; satış, ciro ve reklam harcaması henüz yoktur çünkü bu veri ofise bağlı değildir (bkz. Bölüm 6, madde 1). Gün sonu raporuna satış/marj bölümü, `satis.csv` ve `fiyat-listesi.csv` geldiğinde eklenecek.

---

## 12. Instagram ajanı (`instagram`)

`Jakeschincariol/instagram-agent-skill` (MIT) Nida Zeytin ofisine uyarlandı. Kaynak notu: `departmanlar/instagram/KAYNAK.md`.

**Ne yapar:** 3 farklı formülden puanlı Reel kancası + satır satır senaryo + ekran metni + altyazı; carousel; story akışı; haftalık plan; yorum/DM yanıt taslağı; HORECA/şarküteri Instagram DM taslağı (tek mesaj + tek takip); profil denetimi. **Yayınlamaz**, otomatik beğeni/takip/toplu DM yok.

**Orijinalden farklar:**
- Repodaki Python araçları ofis ajanlarında çalışamaz (ajan tek seferlik LLM çağrısı, kabuk yok). Bu yüzden `ig_denetim.py` olarak Türkçeye uyarlanıp **sunucu tarafında** koşu bitince çıktının sonuna eklenir (kanca puanı, senaryo süresi/beat, altyazı linti, kalıp ifade).
- Nida'ya özel iki kontrol eklendi: **katalog dışı fiyat / tükenen ürün** ve **belgesiz sağlık iddiası** (FAIL).
- Hashtag üst sınırı 5 (Instagram'ın Aralık 2025 değişikliği, haber kaynaklarıyla doğrulandı).
- `sosyal-medya` ajanı artık yalnız Facebook; Instagram tek yerde.

**Takvim:** Pzt 10:30 haftalık Instagram planı · Sal 15:00 Reel senaryosu · Per 16:00 yorum/DM taslakları.

**Sınırlar:** Kanca puanları İngilizce veride ölçülmüş yaklaşımın Türkçe uyarlamasıdır, doğrulanmamıştır. Gerçek LLM ile uçtan uca koşu henüz denenmedi; ilk çıktıyı birlikte okuyup `CLAUDE.md`'yi ayarlamak gerekir.

**Devreye almak için:** (1) `marka-profili.md` ve `departmanlar/instagram/CLAUDE.md` içindeki `{{@kullanici_adi}}` alanını doldur; (2) yeniden deploy et; (3) sunucudaki takvime yeni 3 görevi panelden ekle (volume'daki mevcut `takvim.json` otomatik güncellenmez).
