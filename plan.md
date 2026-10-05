# CERCA — SEO Odaklı, Google & Yandex Dostu Etkinlik ve Mekan Keşif Platformu
## Kapsamlı Mimari, SEO ve Veri Analitiği Master Planı (`plan.md`)

---

## 1. YÖNETİCİ ÖZETİ VE MARKA VİZYONU

### 1.1 Marka Kimliği: "Cerca"
- **İsim Anlamı:** İspanyolca/Latince kökenli *"Cerca"* kelimesi **"Yakın / Yakınlık"** anlamına gelir.
- **Konsept:** Kullanıcının bulunduğu konuma, şehre, semte en yakın kültür, sanat, konser, tiyatro, stand-up ve festival etkinliklerini harita ve mesafe bazlı sunan; mekanları ve sanatçıları birbirine bağlayan Türkiye'nin en kapsamlı kültür-sanat arama motoru ve rehberi.
- **Tasarım Dili:** Enerjik, modern, güven veren **Turuncu (Orange - `#FF6600` / `#FF7A00`)** vurgular ve göz yormayan sıcak açık tonlar (Krem `#FAF8F5`, Saf Beyaz `#FFFFFF`, Açık Gri `#F1F3F5`, Kömür Grisi `#1A1D20`).
- **Temel Mimari:** GitHub referansı verilen `jekyll-theme-chirpy` tabanlı, ancak salt bir teknik blogdan tam teşekküllü bir **Programatik SEO (pSEO) ve Etkinlik Portalı** mimarisine dönüştürülmüş hibrit statik/dinamik yapı.

---

## 2. MEVCUT VERİ SETİ VE ANALİTİK RAPORU

Yapılan veri incelemelerinde 4 ana veri tablosu ve aralarındaki ilişkiler tespit edilmiştir:

| Dosya Adı | Boyut | Kayıt Sayısı | Kritik Sütunlar ve Veri Kalitesi |
| :--- | :--- | :--- | :--- |
| **`etkinlikler.csv`** | ~38 MB | **21.247** | `id`, `adi`, `slug`, `ozet` (%100 dolu), `bilmenizGerekenler` (%69.3 dolu), `seoBaslik` (%100 dolu), `seoAciklama` (%100 dolu), `tip`, `alt_tur`, `puan`, `sure` |
| **`mekanlar.csv`** | ~1.8 MB | **4.407** | `id`, `baslik`, `slug`, `adres` (%100 dolu), `enlem`, `boylam` (%100 dolu!), `sehirId` (İl plaka kodları), `aciklama`, `seoBaslik`, `seoAciklama` |
| **`sanatcilar.csv`** | ~2.5 MB | **2.650** | `id`, `adiSoyadi`, `slug`, `biografi` (%100 dolu), `sanatciTipi`, `dogumYeri`, `etkinlikAdedi`, `seoBaslik`, `seoAciklama` |
| **`seanslar.csv`** | ~45 MB | **268.245** | `id`, `etkinlikId`, `mekanId`, `sehirId`, `tarih`, `kapanisTarihi`, `aktif`, `seansTipi`, `alt_tur`, `eventTagSlug` |

### Veri Analitiği Bulguları:
1. **Koordinat Gücü:** 4.407 mekanın tamamında enlem (`enlem`) ve boylam (`boylam`) koordinatları mevcuttur. Bu, Cerca markasının "yakınımdaki etkinlikler" konum filtrelemesi ve yerel SEO (Local SEO / Google Maps optimizasyonu) için muazzam bir avantajdır.
2. **Zengin İçerik Oranı:** Etkinliklerin özetleri ve SEO açıklamaları %100 doluluk oranına sahiptir. Sanatçı biyografileri mevcuttur. Bu durum Google'ın "Thin Content" (Zayıf İçerik) filtresine takılmadan dizinlenecek binlerce sayfa oluşturmayı mümkün kılar.
3. **Şehir Dağılımı:** `sehirId` değerleri Türkiye il plaka kodlarıyla birebir eşleşmektedir (34 = İstanbul, 35 = İzmir, 06 = Ankara, 07 = Antalya, 48 = Muğla, 16 = Bursa vb.).
4. **İlişkisel Bütünlük:** `seanslar.csv`, etkinlikler ile mekanlar arasındaki köprüyü kurar. Bir etkinliğin hangi mekanlarda ve hangi tarihlerde sahnelendiği doğrudan bu tablo üzerinden çözülür.

---

## 3. SEO VE VERİ STRATEJİSİ: İNDEKS KAYBINI ÖNLEME DOKTRİNİ

> [!IMPORTANT]
> **Kullanıcının En Kritik Talebi:** *"Google'da indekslenen sayfalarımızın silinmemesi için en iyi dizayn, tasarım ve düşünceyi istiyorum. Tam bir SEO odaklı ve veri analisti gibi düşün."*

### 3.1 Neden Etkinlik Sitelerinin Sayfaları Google'dan Silinir (De-indexing)?
1. **Sona Eren Etkinliklerin 404/410'a Düşürülmesi:** Klasik etkinlik siteleri konser bitince sayfayı siler veya 404 döndürür. Googlebot sayfayı taradığında 404 görür ve sayfayı dizinden çıkarır; kazanılan tüm backlink, sayfa otoritesi ve kelime sıralamaları yok olur.
2. **Thin Content & Soft 404:** Etkinlik bittiğinde "Bu etkinlik sona ermiştir" yazıp başka hiçbir içerik bırakmayan sayfalar Google tarafından "Soft 404" olarak işaretlenir.
3. **Kopya Başlık ve Meta Etiketleri:** Birden fazla seansta aynı başlık ve açıklamaların yinelenmesi durumunda Google sayfaları kanonize edemez ve dizinden düşürür.
4. **Yetim Sayfalar (Orphan Pages):** Bir etkinliğe iç bağlantı (internal link) kalmadığında arama motoru botları sayfayı taramayı bırakır.
5. **Aşırı Yavaş Tarama Bütçesi İsrafı:** 300.000 URL'lik devasa bir yapıda filtre parametrelerinin (`?sort=date&filter=35`) dizine açılması tarama bütçesini tüketir.

### 3.2 Cerca "Evergreen URL" (Asla Silinmeyen Sayfa) Mimarisi
- **Kural 1: Sıfır 404 Prensibi (200 OK ile Kalıcı Yaşam):**
  Bir etkinlik tarihi geçmiş olsa dahi sayfası **asla silinmeyecek ve 404 döndürmeyecektir**. Sayfa her zaman `HTTP 200 OK` durum kodu verir.
- **Kural 2: Akıllı Yaşam Döngüsü (Event Lifecycle UI):**
  - **Aktif Etkinlik Durumu:** Canlı bilet/seans takvimi, tarih, saat, mekan, yol tarifi butonu ve rezervasyon/bilet linki en üstte vurgulanır.
  - **Geçmiş Etkinlik Durumu:** Sayfanın en üstünde şık, bilgilendirici bir rozet yer alır:
    > *"Bu etkinlik [Tarih] tarihinde [Mekan Adı - Şehir]'de gerçekleşmiştir."*
  - **Kalıcı Değer Önerisi (Link Equity Kurtarma):**
    Hemen altında iki dinamik bileşen yüklenir:
    1. *"Bu Sanatçının Yaklaşan Diğer Konserleri & Etkinlikleri"*
    2. *"Bu Mekandaki ([Mekan Adı]) Yaklaşan Diğer Etkinlikler"*
    3. *"[Şehir] Bölgesindeki Benzer [Kategori] Etkinlikleri"*
    Böylece sayfa asla ölü bir sayfa (Dead End) olmaz; kullanıcıyı ve arama motoru botunu sitenin yaşayan diğer sayfalarına yönlendirir.
- **Kural 3: Zengin Yapılandırılmış Veri (Schema.org / JSON-LD):**
  - Aktif etkinlikler için: `eventStatus: "https://schema.org/EventScheduled"`.
  - Geçmiş etkinlikler için: Schema geçerli tutulur, `startDate` ve `endDate` geçmiş tarih olarak korunur, Google Etkinlik zengin sonuçlarında arşivlenmiş etkinlik otoritesi korunur.
  - Mekan sayfaları için: `Place` ve `LocalBusiness` şeması, `geo: GeoCoordinates` (enlem-boylam), `address: PostalAddress`.
  - Sanatçı sayfaları için: `Person` veya `MusicGroup` şeması, `sameAs` profilleri.
  - Her sayfada hiyerarşik `BreadcrumbList` şeması (Google arama sonuçlarında kırıntı navigasyonu görünümü).

### 3.3 Hiyerarşik Programatik SEO (pSEO) URL Yapısı
Kusursuz iç linkleme ve silolar (Hub & Spoke Architecture):

```
Ana Sayfa (cerca.com.tr)
├── /sehir/ (Tüm Şehirler Dizini)
│   ├── /sehir/istanbul/ (İstanbul Etkinlikleri - City Hub)
│   │   ├── /sehir/istanbul/konser/ (İstanbul Konserleri)
│   │   ├── /sehir/istanbul/tiyatro/ (İstanbul Tiyatroları)
│   │   └── /sehir/istanbul/stand-up/ (İstanbul Stand-Up Gösterileri)
│   └── /sehir/izmir/ ...
├── /kategori/ (Tüm Kategoriler Dizini)
│   ├── /kategori/konser/
│   ├── /kategori/tiyatro/
│   └── /kategori/stand-up/
├── /mekan/ (Mekan Dizini - 4.407 Mekan)
│   └── /mekan/{mekan-slug}/ (Örn: /mekan/soldout-performance-hall/)
│       ├── Mekan Detayı, Haritası, Adresi, Ulaşım Bilgisi
│       ├── Bu Mekandaki Yaklaşan Etkinlikler
│       └── Bu Mekanda Gerçekleşmiş Geçmiş Etkinlikler
├── /sanatci/ (Sanatçı Dizini - 2.650 Sanatçı)
│   └── /sanatci/{sanatci-slug}/ (Örn: /sanatci/bulent-emrah-parlak/)
│       ├── Biyografi, Sanatçı Bilgileri
│       └── Turne Takvimi / Konserleri
└── /etkinlik/ (Etkinlik Sayfaları - 21.247 Etkinlik)
    └── /etkinlik/{etkinlik-slug}/ (Örn: /etkinlik/mahser-i-cumbus-oyunu/)
        ├── Seanslar, Tarih, Saat, Mekan Bağlantısı
        ├── Kurallar ("Bilmeniz Gerekenler")
        └── Breadcrumb: Ana Sayfa > Şehir > Kategori > Etkinlik Adı
```

---

## 4. TEMA, BİLEŞEN VE DÜZEN MİMARİSİ (MODÜLER YAPI)

Kullanıcının doğrudan talepleri doğrultusunda sistem parçalara bölünmüştür:

### 4.1 Renk Paleti ve Tasarım Dili
- **Ana Marka Rengi:** Cerca Turuncusu (`--cerca-primary: #FF6600;`, hover `--cerca-primary-hover: #E65C00;`)
- **İkincil Vurgu Rengi:** Sıcak Amber / Güneş Turuncusu (`--cerca-accent: #FF944D;`)
- **Arka Plan Rengi (Light Theme):** Sıcak Krem & Saf Beyaz (`--cerca-bg: #FAF9F6;`, kartlar `--cerca-card-bg: #FFFFFF;`)
- **Yazı Renkleri:** Okunabilir koyu tonlar (`--cerca-text: #1E2022;`, ikincil metin `--cerca-text-muted: #68717A;`)
- **Kenarlık ve Çizgiler:** İnce, modern ayrım çizgileri (`--cerca-border: #EAECEF;`)

### 4.2 Merkezi Ayar Dosyası (`_data/cerca_settings.yml` & `_config.yml`)
Kullanıcı istediği zaman logoyu, site başlığını, sloganı ve renk kodlarını tek bir dosyadan değiştirebilecektir:
```yaml
# Cerca Platform Ayarları (cerca_settings.yml)
brand:
  name: "Cerca"
  tagline: "Sana En Yakın Etkinlikler, Konserler ve Mekanlar"
  logo: "/assets/img/logo.svg"
  logo_dark: "/assets/img/logo-white.svg"
  favicon: "/assets/img/favicon.png"
  default_city: "istanbul"

theme:
  primary_color: "#FF6600"
  primary_hover: "#E65C00"
  accent_color: "#FF944D"
  bg_light: "#FAF9F6"
  text_dark: "#1E2022"

seo:
  meta_title_suffix: " | Cerca Etkinlik Rehberi"
  default_description: "Şehrinizdeki en güncel konserler, tiyatro oyunları, festivaller ve etkinlik mekanları Cerca'da. Yakınınızdaki kültürü hemen keşfedin."
  site_url: "https://cerca.com.tr"
  google_site_verification: ""
  yandex_verification: ""

scripts:
  google_analytics_id: ""
  yandex_metrica_id: ""
  google_tag_manager_id: ""
```

### 4.3 Modüler Şablon Dosyaları (Header, Footer, Navbar, Code Injections)
Kullanıcının istediği gibi tüm parçalar bağımsız ve kolayca kod eklenebilir dosyalara ayrılmıştır:

1. **`_includes/header.html`:** Sayfanın en üst başlık alanı, bildirim çubuğu veya üst karşılama alanı.
2. **`_includes/navbar.html`:** Logo, şehir seçici (Dropdown: İstanbul, İzmir, Ankara vb.), kategori menüsü, yakınımdaki etkinlikler butonu ve canlı arama kutusu.
3. **`_includes/footer.html`:** Kurumsal bağlantılar, popüler şehirler SEO link listesi, popüler mekanlar listesi, telif hakkı ve sosyal medya ikonları.
4. **`_includes/seo_head.html`:** Otomatik OpenGraph (Facebook), Twitter Cards, Canonical linkler, meta robot etiketleri ve Schema.org JSON-LD kodları.
5. **`_includes/custom_head_code.html`:** Kullanıcının özel CSS, AdSense veya Meta doğrulama kodlarını yapıştırabileceği boşluk.
6. **`_includes/custom_footer_code.html`:** Kullanıcının Google Analytics, Yandex Metrica, Hotjar, Chatbot veya özel JavaScript kodlarını yapıştırabileceği bağımsız dosya.

---

## 5. BÜYÜK VERİ (BIG DATA) VE DERLEME (BUILD) MİMARİSİ

### 5.1 Sorun ve Çözüm: 28.000 Sayfa Nasıl Derlenir?
- Standart bir Jekyll kurulumunda 28.000 markdown dosyası derlenmeye çalışıldığında Ruby derleyicisi saatler sürebilir veya bellek sınırını aşabilir.
- **Cerca Yüksek Performanslı Çözümü:**
  1. **Python Veri İşleme Motoru (`scripts/data_pipeline.py`):**
     - CSV dosyalarını temizler, UTF-8 karakter dönüşümlerini garanti altına alır.
     - Şehirleri il kodlarından isimlere çözer (`34 -> istanbul`, `35 -> izmir`, `6 -> ankara` vb.).
     - Etkinlikleri, mekanları, sanatçıları ve seansları ilişkisel bir biçimde indeksler.
     - Gelecek (aktif) ve geçmiş etkinlikleri sınıflandırır.
  2. **Hibrit Statik + Veri API Modeli:**
     - **En Çok Aranan Çekirdek Sayfalar:** Şehir hub'ları (81 il), Kategori hub'ları (30+ kategori), En popüler mekanlar (1.000+ mekan), En popüler sanatçılar (1.000+ sanatçı) ve Aktif etkinlikler saf statik HTML olarak derlenir.
     - **Parçalı XML Haritaları (Segmented Sitemaps):** Googlebot ve Yandex botları için `sitemap-index.xml` altında 5 farklı sitemap oluşturulur (`sitemap-cities.xml`, `sitemap-venues.xml`, `sitemap-artists.xml`, `sitemap-events-active.xml`, `sitemap-events-archive.xml`).
  3. **İstemci Tarafı Yakınlık / Mesafe Filtreleme ("Cerca Geolocation Engine"):**
     - Mekanların koordinatları (`enlem`, `boylam`) kullanılarak tarayıcıda kullanıcının konum izniyle 5 km, 10 km, 25 km çapındaki etkinlikleri ve mekanları anında listeleme yeteneği.

---

## 6. UYGULAMA FAZLARI (FAZ PLANI)

Proje aşağıdaki 6 faz halinde yürütülecektir:

- **Faz 1: Veri Analizi, Temizleme ve Veri Tabanı Köprülerinin Kurulması**
  - Karakter kodlama (encoding) kontrollerinin tamamlanması.
  - CSV'lerdeki ilişkilerin (`etkinlikId`, `mekanId`, `sehirId`, `sanatci`) JSON/SQLite/Veri modellerine aktarılması.
  - İl kodları tablosunun oluşturulması (01 Adana - 81 Düzce).

- **Faz 2: Cerca Çekirdek Tema ve Tasarım Sisteminin İnşası (Orange & Light Tone)**
  - Chirpy temasının Cerca tasarım diline göre özelleştirilmesi.
  - CSS değişkenlerinin (`--cerca-primary`, `--cerca-bg` vb.) tanımlanması.
  - Modüler include dosyalarının oluşturulması (`navbar.html`, `header.html`, `footer.html`, `custom_head_code.html`, `custom_footer_code.html`).
  - Merkezi ayar dosyasının (`_data/cerca_settings.yml`) yapılandırılması.

- **Faz 3: Şablonlar ve Sayfa Düzenleri (Layouts & UI)**
  - `home.html` (Göz alıcı ana sayfa: Şehir seçimi, yakınımdakiler, öne çıkan konser ve tiyatrolar).
  - `event.html` (Etkinlik detay sayfası: Seanslar, mekan haritası, kurallar, benzer etkinlikler).
  - `venue.html` (Mekan detay sayfası: Mekan bilgisi, Google Maps entegrasyonu, yaklaşan ve geçmiş etkinlikler).
  - `artist.html` (Sanatçı detay sayfası: Biyografi, konser takvimi).
  - `city.html` & `category.html` (SEO Hub sayfaları).

- **Faz 4: İleri Düzey SEO, Schema.org ve Arama Motoru İndeksleme Güvencesi**
  - Event, Place, Person, LocalBusiness ve BreadcrumbList JSON-LD şemaları.
  - Evergreen URL mantığı (geçmiş etkinliklerin 200 OK ile tutulması ve link equity aktarımı).
  - Segmentli XML Sitemap mimarisi ve optimize `robots.txt`.
  - Canonical URL ve OpenGraph/Twitter Card meta entegrasyonu.

- **Faz 5: Hızlı Arama ve "Cerca" Konum Bazlı Keşif Motoru**
  - İstemci taraflı arama indeksi.
  - GPS tabanlı "Bana En Yakın Etkinlikler" (Proximity search) modülü.

- **Faz 6: Test, Doğrulama ve Canlıya Hazırlık Raporlaması**
  - Lighthouse SEO & Performance denetimi.
  - Google Rich Results Test simülasyonu.
  - Kullanıcı kılavuzu ve yönetim dokümantasyonu.

---
*Bu plan, Cerca platformunun sürdürülebilir, yüksek indekslenme oranına sahip ve gelecekte en ufak bir pürüz çıkarmayacak şekilde çalışmasını temin etmek için hazırlanmıştır.*
