# -*- coding: utf-8 -*-
"""
Cerca - GitHub Pages Static Site Generator (SSG)
Bu betik, Cerca portalını GitHub Pages için hazır statik bir klasöre ('docs/') derler.
İçerik:
- Ana sayfa ve kurumsal sayfalar
- 9 Kategori sayfası (/kategori/{slug}/index.html)
- 81 İl sayfası (/sehir/{slug}/index.html)
- Popüler/aktif etkinlikler, mekanlar ve sanatçılar (/etkinlik/{slug}/index.html vb.)
- Akıllı 404.html (Evergreen Client-Side SPA Yönlendirici: Diğer 20.000 etkinliği de 404 vermeden tarayıcıda anında render eder)
- .nojekyll ve sitemap'ler, robots.txt, assets
"""

import os
import sys
import json
import shutil
import sqlite3
import yaml
from liquid import Environment

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DATA_DIR = os.path.join(BASE_DIR, "_data")
INCLUDES_DIR = os.path.join(BASE_DIR, "_includes")
LAYOUTS_DIR = os.path.join(BASE_DIR, "_layouts")
DB_PATH = os.path.join(DATA_DIR, "cerca_seanslar.db")

print(f"[*] Cerca GitHub Pages derleyicisi başlatıldı. Hedef Klasör: {DOCS_DIR}")

# 1. Veri ve Şablon Yükleme
def load_all_data():
    data = {}
    with open(os.path.join(DATA_DIR, "cerca_settings.yml"), 'r', encoding='utf-8') as f:
        data['cerca_settings'] = yaml.safe_load(f)

    for fn in ["sehirler.json", "kategoriler.json", "mekanlar_populer.json", "sanatcilar_populer.json", "etkinlikler_core.json", "istatistikler.json"]:
        p = os.path.join(DATA_DIR, fn)
        key = fn.replace(".json", "")
        with open(p, 'r', encoding='utf-8') as f:
            data[key] = json.load(f)
    return data

DATA = load_all_data()

import re
def resolve_includes(text):
    for inc_file in os.listdir(INCLUDES_DIR):
        if inc_file.endswith(".html"):
            inc_path = os.path.join(INCLUDES_DIR, inc_file)
            with open(inc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            pattern = r"\{%\s*include\s+[\"']?" + re.escape(inc_file) + r"[\"']?\s*(?:[a-zA-Z0-9_\-]+=[^\%]+)?%\}"
            text = re.sub(pattern, content, text)
    return text

with open(os.path.join(LAYOUTS_DIR, "default.html"), 'r', encoding='utf-8') as f:
    RAW_DEFAULT_LAYOUT = f.read().split('---', 2)[-1]
RESOLVED_DEFAULT_LAYOUT = resolve_includes(RAW_DEFAULT_LAYOUT)

with open(os.path.join(LAYOUTS_DIR, "event.html"), 'r', encoding='utf-8') as f:
    RAW_EVENT_LAYOUT = resolve_includes(f.read().split('---', 2)[-1])

with open(os.path.join(LAYOUTS_DIR, "venue.html"), 'r', encoding='utf-8') as f:
    RAW_VENUE_LAYOUT = resolve_includes(f.read().split('---', 2)[-1])

with open(os.path.join(LAYOUTS_DIR, "artist.html"), 'r', encoding='utf-8') as f:
    RAW_ARTIST_LAYOUT = resolve_includes(f.read().split('---', 2)[-1])

env = Environment()
env.add_filter("absolute_url", lambda val: f"https://cerca.com.tr{val}" if val else "https://cerca.com.tr")
env.add_filter("relative_url", lambda val: val if val else "")

def render_page(layout_body, page_meta, content=""):
    full_html_str = RESOLVED_DEFAULT_LAYOUT.replace("{{ content }}", layout_body)
    template = env.from_string(full_html_str)
    return template.render(
        site={"data": DATA},
        page=page_meta,
        content=content
    )

from data_pipeline import SEHIRLER_MAP

def get_event_sessions(event_id, limit=60):
    if not os.path.exists(DB_PATH) or not event_id:
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT id, mekanAdi, sehirId, tarih, aktif, seansTipi 
            FROM seanslar 
            WHERE etkinlikId = ? 
            ORDER BY aktif DESC, tarih DESC 
            LIMIT ?
        """, (event_id, limit))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def format_sessions_table(rows):
    if not rows:
        return '<p class="text-muted" style="padding: 10px 0;">Bu etkinlik için güncel seans bilgisi taranmaktadır.</p>'
    table_html = """
    <table style="width: 100%; min-width: 600px; border-collapse: collapse; font-size: 0.9rem; text-align: left;">
      <thead>
        <tr style="border-bottom: 2px solid var(--cerca-border); color: var(--cerca-text-muted);">
          <th style="padding: 10px 12px;">Tarih & Saat</th>
          <th style="padding: 10px 12px;">Şehir</th>
          <th style="padding: 10px 12px;">Mekan</th>
          <th style="padding: 10px 12px;">Durum</th>
          <th style="padding: 10px 12px; text-align: right;">İşlem</th>
        </tr>
      </thead>
      <tbody>
    """
    for r in rows:
        sid, mekan, sehir_id, tarih, aktif, seans_tipi = r
        try:
            city_code = int(float(sehir_id)) if sehir_id is not None and str(sehir_id).strip() != '' else 0
        except (ValueError, TypeError):
            city_code = 0
        sehir_info = SEHIRLER_MAP.get(city_code, {"ad": "Türkiye"})
        status_badge = '<span style="color: var(--cerca-success); font-weight: 700; font-size: 0.8rem; background: var(--cerca-success-light); padding: 3px 8px; border-radius: 999px;"><i class="fas fa-circle-check"></i> Satışta</span>' if (aktif == 1 and seans_tipi == 'active') else '<span style="color: var(--cerca-past); font-size: 0.8rem; background: var(--cerca-past-light); padding: 3px 8px; border-radius: 999px;"><i class="fas fa-clock-rotate-left"></i> Tamamlandı</span>'
        btn_html = '<a href="#" class="cerca-btn-nearme" style="padding: 4px 12px; font-size: 0.8rem; text-decoration: none;">Bilet Al</a>' if (aktif == 1 and seans_tipi == 'active') else '<span style="color: var(--cerca-text-muted); font-size: 0.8rem;">Arşiv</span>'
        table_html += f"""
        <tr style="border-bottom: 1px solid var(--cerca-surface);">
          <td style="padding: 12px; font-weight: 600; color: var(--cerca-heading);"><i class="fas fa-calendar-day" style="color: var(--cerca-primary); margin-right: 6px;"></i> {str(tarih)[:16]}</td>
          <td style="padding: 12px;">📍 {sehir_info['ad']}</td>
          <td style="padding: 12px; color: var(--cerca-text);">{mekan or '-'}</td>
          <td style="padding: 12px;">{status_badge}</td>
          <td style="padding: 12px; text-align: right;">{btn_html}</td>
        </tr>
        """
    table_html += "</tbody></table>"
    return table_html

def get_venue_sessions(venue_id, limit=40):
    if not os.path.exists(DB_PATH) or not venue_id:
        return []
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT id, etkinlikAdi, sehirId, tarih, aktif, seansTipi, etkinlikId 
            FROM seanslar 
            WHERE mekanId = ? 
            ORDER BY aktif DESC, tarih DESC 
            LIMIT ?
        """, (venue_id, limit))
        rows = c.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def format_venue_sessions_table(rows):
    if not rows:
        return ""
    table_html = """
    <div style="background: #FFFFFF; border: 1px solid var(--cerca-border); border-radius: var(--radius-md); padding: 24px; margin-bottom: 30px; box-shadow: var(--shadow-sm);">
      <h3 style="font-size: 1.25rem; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
        <i class="fas fa-calendar-days" style="color: var(--cerca-primary);"></i>
        Bu Mekandaki Seanslar & Turne Programı
      </h3>
      <div style="overflow-x: auto;">
        <table style="width: 100%; min-width: 600px; border-collapse: collapse; font-size: 0.9rem; text-align: left;">
          <thead>
            <tr style="border-bottom: 2px solid var(--cerca-border); color: var(--cerca-text-muted);">
              <th style="padding: 10px 12px;">Tarih & Saat</th>
              <th style="padding: 10px 12px;">Etkinlik Adı</th>
              <th style="padding: 10px 12px;">Durum</th>
              <th style="padding: 10px 12px; text-align: right;">Bilet / Detay</th>
            </tr>
          </thead>
          <tbody>
    """
    for r in rows:
        sid, etkinlik_adi, sehir_id, tarih, aktif, seans_tipi, etkinlik_id = r
        status_badge = '<span style="color: var(--cerca-success); font-weight: 700; font-size: 0.8rem; background: var(--cerca-success-light); padding: 3px 8px; border-radius: 999px;"><i class="fas fa-circle-check"></i> Satışta</span>' if (aktif == 1 and seans_tipi == 'active') else '<span style="color: var(--cerca-past); font-size: 0.8rem; background: var(--cerca-past-light); padding: 3px 8px; border-radius: 999px;"><i class="fas fa-clock-rotate-left"></i> Arşiv</span>'
        table_html += f"""
        <tr style="border-bottom: 1px solid var(--cerca-surface);">
          <td style="padding: 12px; font-weight: 600; color: var(--cerca-heading);"><i class="fas fa-calendar-day" style="color: var(--cerca-primary); margin-right: 6px;"></i> {str(tarih)[:16]}</td>
          <td style="padding: 12px; font-weight: 600; color: var(--cerca-text);">{etkinlik_adi or '-'}</td>
          <td style="padding: 12px;">{status_badge}</td>
          <td style="padding: 12px; text-align: right;"><a href="/etkinlikler/" class="cerca-btn-nearme" style="padding: 4px 12px; font-size: 0.8rem; text-decoration: none;">Detay</a></td>
        </tr>
        """
    table_html += "</tbody></table></div></div>"
    return table_html

def render_event_cards(events_list, limit=36):
    if not events_list:
        return """
        <div style="grid-column: 1 / -1; padding: 40px 20px; text-align: center; background: #FFFFFF; border: 1px solid var(--cerca-border); border-radius: var(--radius-md);">
          <i class="fas fa-calendar-xmark text-muted" style="font-size: 2rem; margin-bottom: 10px; display: block;"></i>
          <h3 style="font-size: 1.1rem; margin-bottom: 6px;">Etkinlik Bulunamadı</h3>
          <p class="text-muted">Yakın zamanda yeni seanslar eklenecektir.</p>
        </div>
        """
    cards = []
    for e in events_list[:limit]:
        status_badge = '<span class="cerca-badge-status active"><i class="fas fa-circle-check"></i> Satışta</span>' if e.get("isActive") else '<span class="cerca-badge-status past"><i class="fas fa-clock-rotate-left"></i> Arşiv</span>'
        city_row = f'<div class="cerca-card-meta-row"><i class="fas fa-location-dot text-muted"></i><span>{", ".join(e["sehirler"][:2])}</span></div>' if e.get("sehirler") else ""
        venue_row = f'<div class="cerca-card-meta-row"><i class="fas fa-landmark text-muted"></i><span>{e["mekanlar"][0]}</span></div>' if e.get("mekanlar") else ""
        cat_badge = e.get("altTur") or e.get("tipAdi") or "Kültür & Sanat"
        cat_icon = e.get("tipIcon") or "fa-ticket"
        c = f"""
        <article class="cerca-card">
          <div class="cerca-card-header">
            <span class="cerca-badge-cat"><i class="fas {cat_icon}"></i> {cat_badge}</span>
            {status_badge}
          </div>
          <div class="cerca-card-body">
            <h3 class="cerca-card-title"><a href="/etkinlik/{e['slug']}/">{e['adi']}</a></h3>
            <div class="cerca-card-meta">
              {city_row}
              {venue_row}
            </div>
            <p class="cerca-card-summary">{e.get('ozetKisa') or e.get('seoAciklama') or ''}</p>
            <div class="cerca-card-footer">
              <span class="text-muted" style="font-size: 0.8rem;"><i class="fas fa-ticket"></i> {e.get('toplamSeans', 1)} Seans</span>
              <a href="/etkinlik/{e['slug']}/" class="cerca-card-btn">Bilet & İncele <i class="fas fa-chevron-right"></i></a>
            </div>
          </div>
        </article>
        """
        cards.append(c)
    return "\n".join(cards)

def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def write_file(dest_path, content):
    ensure_dir(dest_path)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 2. Temizlik ve Temel Dosyalar
if os.path.exists(DOCS_DIR):
    shutil.rmtree(DOCS_DIR)
os.makedirs(DOCS_DIR, exist_ok=True)

# .nojekyll (GitHub Pages Jekyll bypass)
write_file(os.path.join(DOCS_DIR, ".nojekyll"), "")

# Assets kopyalama
shutil.copytree(os.path.join(BASE_DIR, "assets"), os.path.join(DOCS_DIR, "assets"), dirs_exist_ok=True)

# Data JSON kopyalama (İstemci tarafı arama ve dinamik SPA için)
os.makedirs(os.path.join(DOCS_DIR, "_data"), exist_ok=True)
for fn in ["sehirler.json", "kategoriler.json", "mekanlar_populer.json", "sanatcilar_populer.json", "etkinlikler_core.json", "istatistikler.json"]:
    src = os.path.join(DATA_DIR, fn)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(DOCS_DIR, "_data", fn))

# Sitemap ve robots.txt kopyalama
for sitemap_fn in ["sitemap.xml", "sitemap-ana.xml", "sitemap-etkinlikler.xml", "sitemap-kategoriler.xml", "sitemap-mekanlar.xml", "sitemap-sanatcilar.xml", "sitemap-sehirler.xml", "robots.txt"]:
    src = os.path.join(BASE_DIR, sitemap_fn)
    if os.path.exists(src):
        shutil.copy(src, os.path.join(DOCS_DIR, sitemap_fn))

# 3. Kök Sayfaları Derleme
static_pages = [
    ("index.html", {"title": "Cerca | Türkiye Etkinlik, Konser, Tiyatro ve Mekan Rehberi", "layout": "default"}),
    ("sehirler.html", {"title": "81 İl Etkinlik Rehberi | Cerca", "layout": "default"}),
    ("mekanlar.html", {"title": "Popüler Konser ve Gösteri Mekanları | Cerca", "layout": "default"}),
    ("sanatcilar.html", {"title": "Sanatçılar ve Turne Takvimleri | Cerca", "layout": "default"}),
    ("yakindaki-etkinlikler.html", {"title": "Yakınımdaki Canlı Etkinlikler | Cerca", "layout": "default"}),
    ("hakkimizda.html", {"title": "Hakkımızda | Cerca", "layout": "default"}),
    ("iletisim.html", {"title": "İletişim | Cerca", "layout": "default"}),
    ("gizlilik-politikasi.html", {"title": "Gizlilik Politikası | Cerca", "layout": "default"}),
]

for src_name, meta in static_pages:
    src_p = os.path.join(BASE_DIR, src_name)
    if os.path.exists(src_p):
        with open(src_p, 'r', encoding='utf-8') as f:
            raw_content = f.read().split('---', 2)[-1]
        resolved_content = resolve_includes(raw_content)
        html = render_page(resolved_content, meta)
        write_file(os.path.join(DOCS_DIR, src_name), html)
        # Clean URLs (/sehirler/ -> /sehirler/index.html)
        if src_name != "index.html":
            slug = src_name.replace(".html", "")
            write_file(os.path.join(DOCS_DIR, slug, "index.html"), html)

print("[✓] Temel sayfalar ve temiz URL index.html dosyaları üretildi.")

# 4. 9 Kategori Sayfasını Derleme (/kategori/{slug}/index.html)
for cat in DATA["kategoriler"]:
    cat_slug = cat["slug"]
    cat_events = [e for e in DATA["etkinlikler_core"] if e.get("tipSlug") == cat_slug or cat_slug in e.get("altTur", "").lower()]
    cat_events.sort(key=lambda x: (not x.get("isActive", False), -x.get("toplamSeans", 0)))
    cards_html = render_event_cards(cat_events, limit=48)
    
    cat_body = f"""
    <div class="cerca-container" style="padding-top: 30px; padding-bottom: 60px;">
      <nav aria-label="Ekmek Kırıntısı" style="margin-bottom: 20px; font-size: 0.85rem; color: var(--cerca-text-muted);">
        <a href="/">Ana Sayfa</a> &raquo;
        <span style="color: var(--cerca-text); font-weight: 600;">{cat['ad']}</span>
      </nav>
      <div class="cerca-section-header">
        <div>
          <h1 class="cerca-section-title"><i class="fas {cat.get('icon', 'fa-ticket')}" style="color: var(--cerca-primary);"></i> {cat['ad']} Etkinlikleri</h1>
          <p class="text-muted">Türkiye genelindeki tüm güncel {cat['ad']} biletleri ve seans saatleri ({len(cat_events)} etkinlik listelendi)</p>
        </div>
      </div>
      <div class="cerca-grid">
        {cards_html}
      </div>
    </div>
    """
    page_meta = {
        "title": f"{cat['ad']} Etkinlikleri | Cerca",
        "seo_title": f"Türkiye {cat['ad']} Etkinlikleri ve Biletleri | Cerca",
        "seo_description": f"Türkiye genelindeki tüm {cat['ad']} etkinlikleri, seansları ve bilet bilgileri Cerca'da.",
        "layout": "default"
    }
    rendered = render_page(cat_body, page_meta)
    write_file(os.path.join(DOCS_DIR, "kategori", cat_slug, "index.html"), rendered)

print(f"[✓] 9 Kategori sayfası üretildi.")

# 5. 81 İl Sayfasını Derleme (/sehir/{slug}/index.html)
for city in DATA["sehirler"]:
    city_slug = city["slug"]
    city_events = [e for e in DATA["etkinlikler_core"] if city_slug in e.get("sehirSluglari", []) or any(city_slug in m.lower() for m in e.get("mekanlar", []))]
    city_events.sort(key=lambda x: (not x.get("isActive", False), -x.get("toplamSeans", 0)))
    cards_html = render_event_cards(city_events, limit=36)
    
    city_body = f"""
    <div class="cerca-container" style="padding-top: 30px; padding-bottom: 60px;">
      <nav aria-label="Ekmek Kırıntısı" style="margin-bottom: 20px; font-size: 0.85rem; color: var(--cerca-text-muted);">
        <a href="/">Ana Sayfa</a> &raquo;
        <a href="/sehirler/">Şehirler</a> &raquo;
        <span style="color: var(--cerca-text); font-weight: 600;">{city['ad']}</span>
      </nav>
      <div class="cerca-section-header">
        <div>
          <h1 class="cerca-section-title">📍 {city['ad']} Etkinlikleri ve Biletleri</h1>
          <p class="text-muted">{city['ad']} ilinde düzenlenen güncel konser, tiyatro, stand-up ve sahne performansları</p>
        </div>
      </div>
      <div class="cerca-grid">
        {cards_html}
      </div>
    </div>
    """
    page_meta = {
        "title": f"{city['ad']} Etkinlikleri | Cerca",
        "seo_title": f"{city['ad']} Etkinlikleri, Konserler ve Tiyatro Biletleri | Cerca",
        "seo_description": f"{city['ad']} etkinlik takvimi, popüler konserler ve tiyatro biletleri Cerca'da.",
        "layout": "default"
    }
    rendered = render_page(city_body, page_meta)
    write_file(os.path.join(DOCS_DIR, "sehir", city_slug, "index.html"), rendered)

print(f"[✓] 81 İl sayfası derlendi.")

# 6. Popüler/Aktif Etkinlikleri Derleme (İlk 500 Etkinlik + Tüm Aktif Etkinlikler)
events_to_build = [e for e in DATA["etkinlikler_core"] if e.get("isActive") or e.get("toplamSeans", 0) > 10][:600]
print(f"[*] {len(events_to_build)} popüler etkinlik sayfası statik HTML olarak derleniyor...")

for event in events_to_build:
    venue_name = event.get("mekanlar", ["İstanbul"])[0] if event.get("mekanlar") else "Mekan Belirtilmemiş"
    city_name = event.get("sehirler", ["İstanbul"])[0] if event.get("sehirler") else "İstanbul"
    city_slug = event.get("sehirSluglari", ["istanbul"])[0] if event.get("sehirSluglari") else "istanbul"
    session_date = str(event.get("seanslar", [{}])[0].get("tarih", "Belirtilmemiş"))[:16] if event.get("seanslar") else "Yakında"
    
    session_rows = get_event_sessions(event.get("id"), limit=60)
    sessions_html = format_sessions_table(session_rows)
    total_sessions = len(session_rows) if session_rows else event.get("toplamSeans", 1)

    page_meta = {
        "title": event["adi"],
        "seo_title": f"{event['adi']} Biletleri ve Seansları | Cerca",
        "seo_description": event.get("seoAciklama") or event["ozetKisa"],
        "category_name": event.get("altTur") or event.get("tipAdi"),
        "category_slug": event.get("tipSlug") or "konser",
        "category_icon": event.get("tipIcon") or "fa-ticket",
        "is_active": event["isActive"],
        "is_past": not event["isActive"],
        "venue_name": venue_name,
        "venue_slug": "mekan",
        "city_name": city_name,
        "city_slug": city_slug,
        "session_date": session_date,
        "summary": event.get("ozet"),
        "rules": event.get("bilmenizGerekenler"),
        "duration": event.get("sure") or "120",
        "sessions_html": sessions_html,
        "total_sessions_count": total_sessions,
        "layout": "event"
    }
    rendered = render_page(RAW_EVENT_LAYOUT, page_meta, content=event.get("ozet", ""))
    write_file(os.path.join(DOCS_DIR, "etkinlik", event["slug"], "index.html"), rendered)

print(f"[✓] Popüler etkinlik sayfaları derlendi.")

# 7. Popüler Mekan Sayfalarını Derleme
venues_to_build = DATA["mekanlar_populer"][:250]
for venue in venues_to_build:
    venue_sessions = get_venue_sessions(venue.get("id"), limit=40)
    venue_sessions_html = format_venue_sessions_table(venue_sessions)
    page_meta = {
        "title": venue["baslik"],
        "seo_title": f"{venue['baslik']} Etkinlikleri, Adres ve Ulaşım | Cerca",
        "seo_description": f"{venue['baslik']} nerede, nasıl gidilir, güncel konser ve tiyatro takvimi. {venue['adres']}",
        "city_name": venue["sehirAdi"],
        "city_slug": venue["sehirSlug"],
        "address": venue["adres"],
        "lat": venue["enlem"],
        "lon": venue["boylam"],
        "description": venue.get("aciklama"),
        "sessions_html": venue_sessions_html,
        "layout": "venue"
    }
    v_title_lower = venue["baslik"].lower()
    matching_events = [e for e in DATA["etkinlikler_core"] if any(v_title_lower in m.lower() for m in e.get("mekanlar", []))][:16]
    venue_content = f"""
    <div class="cerca-grid">
      {render_event_cards(matching_events)}
    </div>
    """
    rendered = render_page(RAW_VENUE_LAYOUT, page_meta, content=venue_content)
    write_file(os.path.join(DOCS_DIR, "mekan", venue["slug"], "index.html"), rendered)

print(f"[✓] {len(venues_to_build)} mekan sayfası derlendi.")

# 8. Popüler Sanatçı Sayfalarını Derleme
artists_to_build = DATA["sanatcilar_populer"][:250]
for artist in artists_to_build:
    page_meta = {
        "title": artist["adiSoyadi"],
        "seo_title": f"{artist['adiSoyadi']} Konserleri ve Turne Takvimi | Cerca",
        "seo_description": f"{artist['adiSoyadi']} turne programı, konser tarihleri, biletleri ve detaylı biyografisi Cerca'da.",
        "birth_place": artist.get("dogumYeri"),
        "bio": artist.get("biografi"),
        "layout": "artist"
    }
    art_tokens = [t for t in artist["adiSoyadi"].lower().split() if len(t) > 2]
    matching_events = [e for e in DATA["etkinlikler_core"] if any(t in e.get("adi", "").lower() for t in art_tokens)][:16]
    artist_content = f"""
    <div class="cerca-grid">
      {render_event_cards(matching_events)}
    </div>
    """
    rendered = render_page(RAW_ARTIST_LAYOUT, page_meta, content=artist_content)
    write_file(os.path.join(DOCS_DIR, "sanatci", artist["slug"], "index.html"), rendered)

print(f"[✓] {len(artists_to_build)} sanatçı sayfası derlendi.")

# 9. Akıllı Evergreen 404.html (GitHub Pages SPA & Dinamik Render Motoru)
# Kullanıcı GitHub Pages üzerinde doğrudan pre-render edilmemiş diğer etkinliklere girerse 404 yerine anında dinamik olarak render edilir.
spa_404_body = """
<div class="cerca-container" style="padding: 60px 20px; text-align: center;">
  <div id="cerca-dynamic-loader">
    <i class="fas fa-spinner fa-spin" style="font-size: 3rem; color: var(--cerca-primary); margin-bottom: 20px;"></i>
    <h2 style="font-size: 1.5rem; margin-bottom: 10px;">Etkinlik Bilgileri Yükleniyor...</h2>
    <p class="text-muted">Cerca etkinlik ve seans arşivinden kayıtlar getiriliyor, lütfen bekleyiniz.</p>
  </div>
  <div id="cerca-dynamic-content" style="display: none; text-align: left;"></div>
  <div id="cerca-not-found" style="display: none;">
    <div class="cerca-evergreen-banner" style="max-width: 600px; margin: 0 auto 30px;">
      <div class="cerca-evergreen-icon"><i class="fas fa-compass"></i></div>
      <div class="cerca-evergreen-content">
        <h4>Aradığınız Sayfa Taşınmış veya Güncellenmiş Olabilir</h4>
        <p>Aşağıdaki arama çubuğunu kullanarak veya popüler kategorilerden devam edebilirsiniz.</p>
      </div>
    </div>
    <div style="margin-top: 30px;">
      <a href="/" class="cerca-btn-nearme" style="text-decoration: none; padding: 10px 24px; font-size: 1rem;"><i class="fas fa-house"></i> Ana Sayfaya Dön</a>
      <a href="/kategori/konser/" class="cerca-btn-nearme" style="text-decoration: none; padding: 10px 24px; font-size: 1rem; margin-left: 10px;"><i class="fas fa-music"></i> Konserleri Keşfet</a>
    </div>
  </div>
</div>

<script>
(function() {
  const path = window.location.pathname;
  const parts = path.split('/').filter(p => p.length > 0);
  
  if (parts.length >= 2 && (parts[0] === 'etkinlik' || parts[0] === 'mekan' || parts[0] === 'sanatci')) {
    const slug = parts[1];
    fetch('/_data/etkinlikler_core.json')
      .then(res => res.json())
      .then(events => {
        const found = events.find(e => e.slug === slug || slug.includes(e.slug) || e.slug.includes(slug));
        if (found) {
          document.getElementById('cerca-dynamic-loader').style.display = 'none';
          const content = document.getElementById('cerca-dynamic-content');
          content.style.display = 'block';
          content.innerHTML = `
            <div style="background: #fff; padding: 30px; border-radius: 12px; border: 1px solid var(--cerca-border); margin-top: 20px;">
              <span class="cerca-badge-cat" style="margin-bottom: 12px; display: inline-block;">
                <i class="fas ${found.tipIcon || 'fa-ticket'}"></i> ${found.tipAdi || 'Kültür & Sanat'}
              </span>
              <h1 style="font-size: 2.2rem; margin-bottom: 16px;">${found.adi}</h1>
              <p style="font-size: 1.05rem; line-height: 1.8; color: var(--cerca-text);">${found.ozet || found.ozetKisa || 'Detaylı etkinlik bilgisi güncellenmektedir.'}</p>
              <div style="margin-top: 25px;">
                <a href="/" class="cerca-btn-nearme" style="text-decoration: none;">Tüm Etkinliklere Dön</a>
              </div>
            </div>
          `;
          document.title = found.adi + " | Cerca";
          return;
        }
        showNotFound();
      })
      .catch(() => showNotFound());
  } else {
    showNotFound();
  }

  function showNotFound() {
    document.getElementById('cerca-dynamic-loader').style.display = 'none';
    document.getElementById('cerca-not-found').style.display = 'block';
  }
})();
</script>
"""

page_404_meta = {
    "title": "Sayfa Bulunamadı | Cerca",
    "seo_title": "Etkinlik Arama | Cerca",
    "layout": "default"
}
rendered_404 = render_page(spa_404_body, page_404_meta)
write_file(os.path.join(DOCS_DIR, "404.html"), rendered_404)
write_file(os.path.join(DOCS_DIR, "CNAME"), "cerca.com.tr\n")
print(f"[✓] Akıllı Evergreen 404.html ve CNAME oluşturuldu.")

print("\n" + "="*60)
print(f"BAŞARILI: Cerca GitHub Pages statik sitesi hazır!")
print(f"Klasör Yolu: {DOCS_DIR}")
print(f"Toplam dosya ve sayfa sayısı üretildi. GitHub Pages ayarlarında '/docs' klasörünü seçebilirsiniz.")
print("="*60)
