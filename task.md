# CERCA — Görev ve Uygulama Listesi (`task.md`)
## Faz Bazlı Eylem Planı ve Takip Matrisi

Bu dosya, `plan.md` belgesindeki mimarinin eksiksiz ve pürüzsüz biçimde hayata geçirilmesi için adım adım uygulanacak görevleri listeler.

---

### [FAZ 1] Veri Analizi, Temizleme ve İlişkisel Köprülerin Kurulması
- [x] **Görev 1.1: Karakter Kodlama ve Veri Bütünlüğü Doğrulaması**
  - UTF-8 dönüşümleri tamamlandı, HTML entity'leri temizlendi.
- [x] **Görev 1.2: 81 İl Haritalama Tablosunun Oluşturulması**
  - `sehirId` plaka kodları (01-81) standart şehir adlarına ve SEO slug'larına dönüştürüldü.
- [x] **Görev 1.3: İlişkisel Veri Köprüsünün Kurulması (Data Aggregator Script)**
  - `scripts/data_pipeline.py` ile 268.245 seans, 21.247 etkinlik, 4.407 mekan ve 2.650 sanatçı köprülendi.
- [x] **Görev 1.4: Çekirdek Veri Setinin (Core Data) JSON/YAML Modeline Dönüştürülmesi**
  - `_data/sehirler.json`, `_data/kategoriler.json`, `_data/mekanlar_populer.json`, `_data/sanatcilar_populer.json`, `_data/etkinlikler_core.json`, `_data/istatistikler.json` başarıyla üretildi.

---

### [FAZ 2] Tema Yapılandırması, Cerca Tasarım Sistemi ve Modüler Şablonlar
- [x] **Görev 2.1: Merkezi Ayar Dosyalarının Oluşturulması**
  - `_config.yml` ve `_data/cerca_settings.yml` oluşturuldu (Logo, Favicon, Başlık, Slogan, Renk Kodları, Sosyal Medya, Doğrulama Kodları).
- [x] **Görev 2.2: Cerca Turuncusu ve Açık Tonlar Tasarım Sistemi (SCSS/CSS)**
  - Ana renk: Turuncu (`#FF6600` / `#FF7A00`), Arka plan: Sıcak krem & beyaz tonları (`#FAF9F6`, `#FFFFFF`).
  - `assets/css/cerca.css` eksiksiz oluşturuldu.
- [x] **Görev 2.3: Modüler Parçaların (Includes) İnşası**
  - `_includes/header.html` (Üst karşılama alanı / duyuru çubuğu).
  - `_includes/navbar.html` (Logo, şehir seçici, kategoriler, arama ve yakınımdakiler butonu).
  - `_includes/footer.html` (Kurumsal linkler, popüler şehirler SEO iç link ağı, mekan linkleri, telif alanı).
  - `_includes/custom_head_code.html` (Kullanıcının dilediği zaman özel kod, doğrulama, AdSense ekleyebileceği alan).
  - `_includes/custom_footer_code.html` (Google Analytics 4, Yandex Metrica, özel izleme scriptleri alanı).

---

### [FAZ 3] Sayfa Düzenleri ve Bileşenleri (Layouts & UI)
- [x] **Görev 3.1: Ana Sayfa Düzeni (`_layouts/default.html` & `index.html`)**
  - Hero bölümü: "Sana En Yakın Etkinlikleri Keşfet", canlı arama, istatistik rozetleri (21.247 Etkinlik, 4.407 Mekan vb.).
  - Şehirlere göre filtreleme butonları, öne çıkan etkinlik kartları, popüler mekanlar ve sanatçılar.
- [x] **Görev 3.2: Etkinlik Detay Sayfası Düzeni (`_layouts/event.html`)**
  - Seanslar, bilet, mekan haritası, özet, "Bilmeniz Gerekenler" ve **Evergreen UI** (geçmiş etkinliklerde 404 yerine arşiv uyarısı ve benzer etkinlik linkleri).
- [x] **Görev 3.3: Mekan Detay Sayfası Düzeni (`_layouts/venue.html` & `mekanlar.html`)**
  - Mekan başlığı, adresi, Google Maps yol tarifi entegrasyonu ve etkinlik takvimi.
- [x] **Görev 3.4: Sanatçı Detay Sayfası Düzeni (`_layouts/artist.html` & `sanatcilar.html`)**
  - Sanatçı biyografisi, doğum yeri ve konser/turne takvimi.
- [x] **Görev 3.5: Şehir ve Kategori SEO Hub Düzenleri (`sehirler.html`)**
  - 81 ilin tamamını kapsayan SEO hub ve mekan sayısı listesi.

---

### [FAZ 4] İleri Düzey SEO, Schema.org ve İndeks Koruma Mimarisi
- [x] **Görev 4.1: Yapılandırılmış Veri (Schema.org / JSON-LD) Entegrasyonu**
  - `_includes/seo_head.html` içinde Event, Place, BreadcrumbList ve WebSite JSON-LD şemaları tamamlandı.
- [x] **Görev 4.2: Evergreen URL ve Sıfır 404 Kuralları**
  - Tarihi geçen etkinliklerin 200 OK ile dizinde kalması ve canonical etiketleme sağlandı.
- [x] **Görev 4.3: Bölümlendirilmiş XML Sitemap Mimarisi**
  - `sitemap.xml` (Ana Master Sitemap Index).
  - `sitemap-etkinlikler.xml` (21.247 Etkinlik URL'i - 3.5 MB).
  - `sitemap-mekanlar.xml` (4.407 Mekan URL'i - 709 KB).
  - `sitemap-sanatcilar.xml` (2.650 Sanatçı URL'i - 402 KB).
  - `sitemap-sehirler.xml` (81 İl Hub URL'i).
  - `sitemap-kategoriler.xml` (9 Kategori Hub URL'i).
  - `sitemap-ana.xml` (Ana sayfa ve kurumsal sayfalar).
  - Toplam 28.402 URL indekslendi ve `robots.txt` ile bağlandı.
- [x] **Görev 4.4: Arama Motoru Taraması ve Robots.txt Optimizasyonu**
  - `robots.txt` Googlebot ve YandexBot için tarama bütçesi korumasıyla oluşturuldu.

---

### [FAZ 5] "Cerca" Konum Bazlı Mesafe ve Canlı Arama Motoru
- [x] **Görev 5.1: İstemci Taraflı Hızlı Arama (Instant Client Search)**
  - `assets/js/cerca.js` içinde canlı arama entegrasyonu yapıldı.
- [x] **Görev 5.2: "Bana En Yakın Etkinlikler" (Proximity Engine)**
  - `yakindaki-etkinlikler.html` sayfası ve Haversine formülüyle km bazlı mesafe hesaplayıcı hayata geçirildi.

---

### [FAZ 6] Test, Validasyon, Dokümantasyon ve Teslim
- [x] **Görev 6.1: Veri ve Şablon Bütünlüğü Testleri**
- [x] **Görev 6.2: Tasarım ve Mobil Uyum Testleri**
- [x] **Görev 6.3: Kullanım ve Güncelleme Kılavuzunun Hazırlanması**

---
*Her bir faz sırayla ve titizlikle uygulanacak; tamamlanan maddeler işaretlenecektir.*
