# -*- coding: utf-8 -*-
"""
Cerca - XML Sitemap Generator
Google ve Yandex için bölümlendirilmiş (segmented) XML sitemap'leri üretir:
- sitemap.xml (Sitemap Index)
- sitemap-etkinlikler.xml (Tüm 21.247 Etkinlik)
- sitemap-mekanlar.xml (Tüm 4.407 Mekan)
- sitemap-sanatcilar.xml (Tüm 2.650 Sanatçı)
- sitemap-sehirler.xml (81 İl Hub'ı)
- sitemap-kategoriler.xml (Kategori Hub'ları)
- sitemap-ana.xml (Kurumsal ve Ana Sayfalar)
"""

import os
import sys
import xml.sax.saxutils as saxutils
from datetime import datetime
import pandas as pd

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(BASE_DIR, "_site")
DOMAIN = "https://cerca.com.tr"
TODAY = datetime.now().strftime("%Y-%m-%d")

def escape_url(url):
    return saxutils.escape(url)

def build_sitemaps():
    print("=" * 60)
    print("CERCA XML SITEMAP MOTORU ÇALIŞIYOR...")
    print("=" * 60)

    sitemaps_created = []

    # 1. SITEMAP-ANA.XML (Kök ve Kurumsal Sayfalar)
    print("\n[1/6] Ana sayfalar sitemap'i oluşturuluyor...")
    static_pages = [
        {"loc": f"{DOMAIN}/", "priority": "1.0", "changefreq": "daily"},
        {"loc": f"{DOMAIN}/sehirler/", "priority": "0.9", "changefreq": "weekly"},
        {"loc": f"{DOMAIN}/mekanlar/", "priority": "0.9", "changefreq": "weekly"},
        {"loc": f"{DOMAIN}/sanatcilar/", "priority": "0.9", "changefreq": "weekly"},
        {"loc": f"{DOMAIN}/yakindaki-etkinlikler/", "priority": "0.85", "changefreq": "daily"},
        {"loc": f"{DOMAIN}/hakkimizda/", "priority": "0.7", "changefreq": "monthly"},
        {"loc": f"{DOMAIN}/iletisim/", "priority": "0.7", "changefreq": "monthly"},
        {"loc": f"{DOMAIN}/gizlilik-politikasi/", "priority": "0.5", "changefreq": "monthly"}
    ]
    xml_ana = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in static_pages:
        xml_ana.append(f'  <url><loc>{escape_url(p["loc"])}</loc><lastmod>{TODAY}</lastmod><changefreq>{p["changefreq"]}</changefreq><priority>{p["priority"]}</priority></url>')
    xml_ana.append('</urlset>')
    content_ana = "\n".join(xml_ana)
    with open(os.path.join(BASE_DIR, "sitemap-ana.xml"), "w", encoding="utf-8") as f:
        f.write(content_ana)
    sitemaps_created.append("sitemap-ana.xml")
    print(f"✔ sitemap-ana.xml: {len(static_pages)} URL")

    # 2. SITEMAP-SEHIRLER.XML (81 İl)
    print("\n[2/6] Şehirler sitemap'i oluşturuluyor...")
    df_mekan = pd.read_csv(os.path.join(BASE_DIR, 'mekanlar.csv'), low_memory=False)
    # Şehir ID'lerini al
    sehir_ids = df_mekan['sehirId'].dropna().astype(int).unique()
    
    # 81 İl Haritası
    from data_pipeline import SEHIRLER_MAP
    xml_sehir = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sehir_count = 0
    for sid, sinfo in SEHIRLER_MAP.items():
        url = f"{DOMAIN}/sehir/{sinfo['slug']}/"
        xml_sehir.append(f'  <url><loc>{escape_url(url)}</loc><lastmod>{TODAY}</lastmod><changefreq>daily</changefreq><priority>0.9</priority></url>')
        sehir_count += 1
    xml_sehir.append('</urlset>')
    with open(os.path.join(BASE_DIR, "sitemap-sehirler.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(xml_sehir))
    sitemaps_created.append("sitemap-sehirler.xml")
    print(f"✔ sitemap-sehirler.xml: {sehir_count} Şehir URL")

    # 3. SITEMAP-KATEGORILER.XML (Kategori Hub'ları)
    print("\n[3/6] Kategoriler sitemap'i oluşturuluyor...")
    categories = ["konser", "tiyatro", "stand-up", "festival", "cocuk", "kultur-sanat", "sinema", "egitim", "spor-dans"]
    xml_cat = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for cat in categories:
        url = f"{DOMAIN}/kategori/{cat}/"
        xml_cat.append(f'  <url><loc>{escape_url(url)}</loc><lastmod>{TODAY}</lastmod><changefreq>daily</changefreq><priority>0.9</priority></url>')
    xml_cat.append('</urlset>')
    with open(os.path.join(BASE_DIR, "sitemap-kategoriler.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(xml_cat))
    sitemaps_created.append("sitemap-kategoriler.xml")
    print(f"✔ sitemap-kategoriler.xml: {len(categories)} Kategori URL")

    # 4. SITEMAP-MEKANLAR.XML (4.407 Mekan)
    print("\n[4/6] Mekanlar sitemap'i oluşturuluyor (4.407 mekan)...")
    xml_mekan = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    mekan_count = 0
    seen_venues = set()
    for _, r in df_mekan.iterrows():
        slug = str(r['slug']).strip() if pd.notna(r['slug']) else f"mekan-{r['id']}"
        if slug in seen_venues:
            continue
        seen_venues.add(slug)
        url = f"{DOMAIN}/mekan/{slug}/"
        xml_mekan.append(f'  <url><loc>{escape_url(url)}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>')
        mekan_count += 1
    xml_mekan.append('</urlset>')
    with open(os.path.join(BASE_DIR, "sitemap-mekanlar.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(xml_mekan))
    sitemaps_created.append("sitemap-mekanlar.xml")
    print(f"✔ sitemap-mekanlar.xml: {mekan_count} Mekan URL")

    # 5. SITEMAP-SANATCILAR.XML (2.650 Sanatçı)
    print("\n[5/6] Sanatçılar sitemap'i oluşturuluyor (2.650 sanatçı)...")
    df_sanat = pd.read_csv(os.path.join(BASE_DIR, 'sanatcilar.csv'), low_memory=False)
    xml_sanat = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sanat_count = 0
    seen_artists = set()
    for _, r in df_sanat.iterrows():
        slug = str(r['slug']).strip() if pd.notna(r['slug']) else f"sanatci-{r['id']}"
        if slug in seen_artists:
            continue
        seen_artists.add(slug)
        url = f"{DOMAIN}/sanatci/{slug}/"
        xml_sanat.append(f'  <url><loc>{escape_url(url)}</loc><lastmod>{TODAY}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>')
        sanat_count += 1
    xml_sanat.append('</urlset>')
    with open(os.path.join(BASE_DIR, "sitemap-sanatcilar.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(xml_sanat))
    sitemaps_created.append("sitemap-sanatcilar.xml")
    print(f"✔ sitemap-sanatcilar.xml: {sanat_count} Sanatçı URL")

    # 6. SITEMAP-ETKINLIKLER.XML (21.247 Etkinlik)
    print("\n[6/6] Etkinlikler sitemap'i oluşturuluyor (21.247 etkinlik)...")
    df_etk = pd.read_csv(os.path.join(BASE_DIR, 'etkinlikler.csv'), low_memory=False)
    xml_etk = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    etk_count = 0
    seen_events = set()
    for _, r in df_etk.iterrows():
        slug = str(r['slug']).strip() if pd.notna(r['slug']) else f"etkinlik-{r['id']}"
        if slug in seen_events:
            continue
        seen_events.add(slug)
        url = f"{DOMAIN}/etkinlik/{slug}/"
        xml_etk.append(f'  <url><loc>{escape_url(url)}</loc><lastmod>{TODAY}</lastmod><changefreq>daily</changefreq><priority>0.85</priority></url>')
        etk_count += 1
    xml_etk.append('</urlset>')
    with open(os.path.join(BASE_DIR, "sitemap-etkinlikler.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(xml_etk))
    sitemaps_created.append("sitemap-etkinlikler.xml")
    print(f"✔ sitemap-etkinlikler.xml: {etk_count} Etkinlik URL")

    # 7. SITEMAP INDEX (sitemap.xml)
    print("\n[7/7] Master Sitemap Index (sitemap.xml) oluşturuluyor...")
    xml_index = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    for sm in sitemaps_created:
        xml_index.append(f'  <sitemap><loc>{DOMAIN}/{sm}</loc><lastmod>{TODAY}</lastmod></sitemap>')
    xml_index.append('</sitemapindex>')
    
    content_index = "\n".join(xml_index)
    with open(os.path.join(BASE_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(content_index)

    # Dosyaları _site dizinine de kopyala
    os.makedirs(SITE_DIR, exist_ok=True)
    all_sitemaps = sitemaps_created + ["sitemap.xml"]
    for sm in all_sitemaps:
        src = os.path.join(BASE_DIR, sm)
        dst = os.path.join(SITE_DIR, sm)
        with open(src, "r", encoding="utf-8") as f_in, open(dst, "w", encoding="utf-8") as f_out:
            f_out.write(f_in.read())

    print("\n" + "=" * 60)
    print("TÜM SITEMAP'LER BAŞARIYLA OLUŞTURULDU!")
    total_urls = len(static_pages) + sehir_count + len(categories) + mekan_count + sanat_count + etk_count
    print(f"Toplam İndekslenen URL: {total_urls}")
    print("Sitemap Dizini: sitemap.xml")
    print(f"Parçalı Haritalar: {', '.join(sitemaps_created)}")
    print("=" * 60)

if __name__ == '__main__':
    build_sitemaps()
