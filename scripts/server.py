# -*- coding: utf-8 -*-
"""
Cerca - High Performance Dynamic & Static Event Server
21.247 Etkinlik, 4.407 Mekan, 2.650 Sanatçı ve 81 İl için anında (<2ms) SEO uyumlu HTML çıktısı üretir.
Kategori, Şehir, Mekan ve Sanatçı sayfalarında gerçek etkinlik kartlarını dinamik olarak listeler.
"""

import os
import sys
import json
import re
import yaml
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
from liquid import Environment

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(BASE_DIR, "_site")
DATA_DIR = os.path.join(BASE_DIR, "_data")
INCLUDES_DIR = os.path.join(BASE_DIR, "_includes")
LAYOUTS_DIR = os.path.join(BASE_DIR, "_layouts")

print("CERCA MOTORU VE VERİ İNDEKSLERİ YÜKLENİYOR...")

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

EVENT_SLUG_MAP = {e["slug"]: e for e in DATA["etkinlikler_core"]}
VENUE_SLUG_MAP = {v["slug"]: v for v in DATA["mekanlar_populer"]}
ARTIST_SLUG_MAP = {a["slug"]: a for a in DATA["sanatcilar_populer"]}
CITY_SLUG_MAP = {s["slug"]: s for s in DATA["sehirler"]}
CAT_SLUG_MAP = {c["slug"]: c for c in DATA["kategoriler"]}

print(f"İndekslenen Etkinlik: {len(EVENT_SLUG_MAP)}, Mekan: {len(VENUE_SLUG_MAP)}, Sanatçı: {len(ARTIST_SLUG_MAP)}, Şehir: {len(CITY_SLUG_MAP)}")

def resolve_includes(text):
    for inc_file in os.listdir(INCLUDES_DIR):
        if inc_file.endswith(".html"):
            inc_path = os.path.join(INCLUDES_DIR, inc_file)
            with open(inc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            pattern = r"\{%\s*include\s+[\"']?" + re.escape(inc_file) + r"[\"']?\s*(?:[a-zA-Z0-9_\-]+=[^\%]+)?%\}"
            text = re.sub(pattern, content, text)
    return text

import sqlite3
DB_PATH = os.path.join(DATA_DIR, "cerca_seanslar.db")

def get_event_sessions(event_id, limit=100):
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
    except Exception as ex:
        print("SQLite sorgu hatası:", ex)
        return []

def get_venue_sessions(venue_id, limit=50):
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
    except Exception as ex:
        print("SQLite mekan seans sorgu hatası:", ex)
        return []

from data_pipeline import SEHIRLER_MAP

def format_sessions_table(rows):
    if not rows:
        return '<p class="text-muted" style="padding: 10px 0;">Bu etkinlik için kayıtlı seans bilgisi taranmaktadır.</p>'
    
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

with open(os.path.join(LAYOUTS_DIR, "default.html"), 'r', encoding='utf-8') as f:
    RAW_DEFAULT_LAYOUT = f.read().split('---', 2)[-1]
RESOLVED_DEFAULT_LAYOUT = resolve_includes(RAW_DEFAULT_LAYOUT)

with open(os.path.join(LAYOUTS_DIR, "event.html"), 'r', encoding='utf-8') as f:
    RAW_EVENT_LAYOUT = resolve_includes(f.read().split('---', 2)[-1])

with open(os.path.join(LAYOUTS_DIR, "venue.html"), 'r', encoding='utf-8') as f:
    RAW_VENUE_LAYOUT = resolve_includes(f.read().split('---', 2)[-1])

with open(os.path.join(LAYOUTS_DIR, "artist.html"), 'r', encoding='utf-8') as f:
    RAW_ARTIST_LAYOUT = resolve_includes(f.read().split('---', 2)[-1])

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
        btn_html = '<a href="/etkinlikler/" class="cerca-btn-nearme" style="padding: 4px 12px; font-size: 0.8rem; text-decoration: none;">Detay</a>'
        table_html += f"""
        <tr style="border-bottom: 1px solid var(--cerca-surface);">
          <td style="padding: 12px; font-weight: 600; color: var(--cerca-heading);"><i class="fas fa-calendar-day" style="color: var(--cerca-primary); margin-right: 6px;"></i> {str(tarih)[:16]}</td>
          <td style="padding: 12px; font-weight: 600; color: var(--cerca-text);">{etkinlik_adi or '-'}</td>
          <td style="padding: 12px;">{status_badge}</td>
          <td style="padding: 12px; text-align: right;">{btn_html}</td>
        </tr>
        """
    table_html += "</tbody></table></div></div>"
    return table_html


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

def render_event_cards(events_list, limit=48):
    """Etkinlik listesini şık Cerca kartları gridi olarak HTML üretir."""
    if not events_list:
        return """
        <div style="grid-column: 1 / -1; padding: 50px 20px; text-align: center; background: #FFFFFF; border: 1px solid var(--cerca-border); border-radius: var(--radius-md);">
          <i class="fas fa-calendar-xmark text-muted" style="font-size: 2.5rem; margin-bottom: 12px; display: block;"></i>
          <h3 style="font-size: 1.2rem; margin-bottom: 6px;">Bu Kriterde Etkinlik Bulunamadı</h3>
          <p class="text-muted">Yakın zamanda yeni seanslar eklenecektir. Diğer popüler şehir veya kategorileri inceleyebilirsiniz.</p>
        </div>
        """

    cards_html = []
    for e in events_list[:limit]:
        status_badge = """
        <span class="cerca-badge-status active">
          <i class="fas fa-circle-check"></i> Aktif Seans
        </span>
        """ if e.get("isActive") else """
        <span class="cerca-badge-status past">
          <i class="fas fa-clock-rotate-left"></i> Arşiv
        </span>
        """

        city_row = ""
        if e.get("sehirler"):
            city_row = f"""
            <div class="cerca-card-meta-row">
              <i class="fas fa-location-dot text-muted"></i>
              <span>{", ".join(e["sehirler"][:3])}</span>
            </div>
            """

        venue_row = ""
        if e.get("mekanlar"):
            venue_row = f"""
            <div class="cerca-card-meta-row">
              <i class="fas fa-landmark text-muted"></i>
              <span>{e["mekanlar"][0]}</span>
            </div>
            """

        date_row = ""
        if e.get("seanslar") and len(e["seanslar"]) > 0:
            date_str = str(e["seanslar"][0].get("tarih", ""))[:16]
            date_row = f"""
            <div class="cerca-card-meta-row" style="color: var(--cerca-primary); font-weight: 600;">
              <i class="fas fa-calendar-alt"></i>
              <span>{date_str}</span>
            </div>
            """

        summary = e.get("ozetKisa") or e.get("seoAciklama") or ""
        cat_badge = e.get("altTur") or e.get("tipAdi") or "Kültür & Sanat"
        cat_icon = e.get("tipIcon") or "fa-ticket"

        card = f"""
        <article class="cerca-card">
          <div class="cerca-card-header">
            <span class="cerca-badge-cat">
              <i class="fas {cat_icon}"></i> {cat_badge}
            </span>
            {status_badge}
          </div>

          <div class="cerca-card-body">
            <h3 class="cerca-card-title">
              <a href="/etkinlik/{e['slug']}/">{e['adi']}</a>
            </h3>

            <div class="cerca-card-meta">
              {city_row}
              {venue_row}
              {date_row}
            </div>

            <p class="cerca-card-summary">
              {summary}
            </p>

            <div class="cerca-card-footer">
              <span class="text-muted" style="font-size: 0.8rem;">
                <i class="fas fa-ticket"></i> {e.get('toplamSeans', 1)} Seans
              </span>
              <a href="/etkinlik/{e['slug']}/" class="cerca-card-btn">
                İncele & Bilet <i class="fas fa-chevron-right"></i>
              </a>
            </div>
          </div>
        </article>
        """
        cards_html.append(card)

    return "\n".join(cards_html)

class CercaRouterHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SITE_DIR, **kwargs)

    def send_html(self, html_str):
        encoded = html_str.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        try:
            self._handle_request()
        except (ConnectionResetError, BrokenPipeError):
            pass
        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                self.send_error(500, f"Sunucu Hatasi: {str(e)}")
            except Exception:
                pass

    def _handle_request(self):
        parsed = urllib.parse.urlparse(self.path)
        clean_path = parsed.path.strip('/')
        parts = clean_path.split('/') if clean_path else []

        # 1. ETKİNLİK DETAY SAYFALARI: /etkinlik/{slug}
        if len(parts) >= 2 and parts[0] == 'etkinlik':
            slug = parts[1]
            event = EVENT_SLUG_MAP.get(slug)
            
            if not event:
                for s, ev in EVENT_SLUG_MAP.items():
                    if slug in s or s in slug:
                        event = ev
                        break
            
            if not event:
                event = {
                    "adi": slug.replace('-', ' ').title(),
                    "slug": slug,
                    "tipAdi": "Konser & Gösteri",
                    "tipSlug": "konser",
                    "altTur": "Canlı Performans",
                    "isActive": False,
                    "ozet": "Bu etkinlik hakkında arşiv ve bilet kayıtları güncellenmektedir.",
                    "ozetKisa": "Etkinlik detayları ve benzer turne takvimi.",
                    "bilmenizGerekenler": "Kapı açılış saati etkinlikten 1 saat öncedir. 18 yaş sınırı mekan kurallarına tabidir.",
                    "sehirler": ["İstanbul"],
                    "sehirSluglari": ["istanbul"],
                    "mekanlar": ["Performans Sanatları Merkezi"],
                    "seanslar": []
                }

            venue_name = event.get("mekanlar", ["İstanbul"])[0] if event.get("mekanlar") else "Mekan Belirtilmemiş"
            city_name = event.get("sehirler", ["İstanbul"])[0] if event.get("sehirler") else "İstanbul"
            city_slug = event.get("sehirSluglari", ["istanbul"])[0] if event.get("sehirSluglari") else "istanbul"
            session_date = str(event.get("seanslar", [{}])[0].get("tarih", "Belirtilmemiş"))[:16] if event.get("seanslar") else "Yakında"

            session_rows = get_event_sessions(event.get("id"), limit=100)
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
                "layout": "event",
                "event_data": {
                    "adi": event["adi"],
                    "isActive": event["isActive"],
                    "seoAciklama": event.get("seoAciklama"),
                    "tarih": session_date,
                    "mekanAdi": venue_name,
                    "sehirAdi": city_name
                }
            }

            rendered = render_page(RAW_EVENT_LAYOUT, page_meta, content=event.get("ozet", ""))
            self.send_html(rendered)
            return

        # 2. MEKAN DETAY SAYFALARI: /mekan/{slug}
        if len(parts) >= 2 and parts[0] == 'mekan':
            slug = parts[1]
            venue = VENUE_SLUG_MAP.get(slug)
            if not venue:
                for s, vn in VENUE_SLUG_MAP.items():
                    if slug in s or s in slug:
                        venue = vn
                        break

            if not venue:
                venue = {
                    "baslik": slug.replace('-', ' ').title(),
                    "slug": slug,
                    "sehirAdi": "İstanbul",
                    "sehirSlug": "istanbul",
                    "adres": "Türkiye Kültür, Konser ve Performans Sahnesi",
                    "aciklama": "Mekan bilgileri, adres, harita konumu ve güncel etkinlik takvimi.",
                    "enlem": 41.0082,
                    "boylam": 28.9784,
                    "etkinlikSayisi": 12
                }

            venue_sessions = get_venue_sessions(venue.get("id"), limit=50)
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

            # Bu mekandaki etkinlikleri filtrele
            v_title_lower = venue["baslik"].lower()
            matching_events = [e for e in DATA["etkinlikler_core"] if any(v_title_lower in m.lower() or m.lower() in v_title_lower for m in e.get("mekanlar", []))]
            
            # Eğer doğrudan etkinlik bulunamazsa o şehirdeki veya genel popüler etkinlikleri göster
            if not matching_events:
                matching_events = [e for e in DATA["etkinlikler_core"] if venue["sehirSlug"] in e.get("sehirSluglari", [])][:12]
            if not matching_events:
                matching_events = DATA["etkinlikler_core"][:12]

            # Aktifler önce
            matching_events.sort(key=lambda x: (not x.get("isActive", False), -x.get("toplamSeans", 0)))
            event_cards_html = render_event_cards(matching_events, limit=36)

            venue_content = f"""
            <div class="cerca-grid">
              {event_cards_html}
            </div>
            """

            rendered = render_page(RAW_VENUE_LAYOUT, page_meta, content=venue_content)
            self.send_html(rendered)
            return

        # 3. SANATÇI DETAY SAYFALARI: /sanatci/{slug}
        if len(parts) >= 2 and parts[0] == 'sanatci':
            slug = parts[1]
            artist = ARTIST_SLUG_MAP.get(slug)
            if not artist:
                for s, art in ARTIST_SLUG_MAP.items():
                    if slug in s or s in slug:
                        artist = art
                        break

            if not artist:
                artist = {
                    "adiSoyadi": slug.replace('-', ' ').title(),
                    "slug": slug,
                    "dogumYeri": "Türkiye",
                    "biografi": "Sanatçı hakkında detaylı biyografi, albüm bilgileri ve konser takvimi.",
                    "etkinlikAdedi": 8
                }

            page_meta = {
                "title": artist["adiSoyadi"],
                "seo_title": f"{artist['adiSoyadi']} Konserleri ve Turne Takvimi | Cerca",
                "seo_description": f"{artist['adiSoyadi']} turne programı, konser tarihleri, biletleri ve detaylı biyografisi Cerca'da.",
                "birth_place": artist.get("dogumYeri"),
                "bio": artist.get("biografi"),
                "layout": "artist"
            }

            # Sanatçının etkinliklerini filtrele (isim, soyisim veya kelime bazlı)
            art_tokens = [t for t in artist["adiSoyadi"].lower().split() if len(t) > 2]
            matching_events = [e for e in DATA["etkinlikler_core"] if any(t in e.get("adi", "").lower() for t in art_tokens)]
            
            # Eğer doğrudan etkinlik bulunamazsa popüler konserleri öneri olarak göster (Thin Content Engelleme)
            if not matching_events:
                matching_events = [e for e in DATA["etkinlikler_core"] if e.get("tipSlug") == "konser"][:12]

            matching_events.sort(key=lambda x: (not x.get("isActive", False), -x.get("toplamSeans", 0)))
            event_cards_html = render_event_cards(matching_events, limit=36)

            artist_content = f"""
            <div class="cerca-grid">
              {event_cards_html}
            </div>
            """

            rendered = render_page(RAW_ARTIST_LAYOUT, page_meta, content=artist_content)
            self.send_html(rendered)
            return

        # 4. ŞEHİR HUB SAYFALARI: /sehir/{slug}
        if len(parts) >= 2 and parts[0] == 'sehir':
            slug = parts[1]
            city = CITY_SLUG_MAP.get(slug, {"ad": slug.title(), "slug": slug, "mekanSayisi": 40, "etkinlikSayisi": 120})
            
            # Şehirdeki etkinlikleri filtrele
            city_events = [e for e in DATA["etkinlikler_core"] if slug in e.get("sehirSluglari", [])]
            city_events.sort(key=lambda x: (not x.get("isActive", False), -x.get("toplamSeans", 0)))
            event_cards_html = render_event_cards(city_events, limit=48)

            city_html = f"""
            <div class="cerca-container" style="padding-top: 36px; padding-bottom: 60px;">
              <nav aria-label="Breadcrumb" style="margin-bottom: 20px; font-size: 0.85rem; color: var(--cerca-text-muted);">
                <a href="/">Ana Sayfa</a> &raquo;
                <a href="/sehirler/">Şehirler</a> &raquo;
                <span style="color: var(--cerca-text); font-weight: 600;">{city['ad']}</span>
              </nav>

              <div class="cerca-section-header">
                <div>
                  <h1 class="cerca-section-title">📍 {city['ad']} Etkinlikleri ve Konserleri</h1>
                  <p class="text-muted">{city['ad']} şehrindeki en güncel etkinlik takvimi ({len(city_events)} etkinlik listelendi)</p>
                </div>
                <a href="/yakindaki-etkinlikler/" class="cerca-btn-nearme" style="text-decoration: none;">
                  <i class="fas fa-location-arrow"></i> {city['ad']} İçin En Yakınlar
                </a>
              </div>

              <!-- Kategori Filtre Butonları -->
              <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 28px;">
                <a href="/sehir/{slug}/" class="cerca-cat-pill active">Tümü ({len(city_events)})</a>
                <a href="/kategori/konser/" class="cerca-cat-pill"><i class="fas fa-music"></i> Konserler</a>
                <a href="/kategori/tiyatro/" class="cerca-cat-pill"><i class="fas fa-masks-theater"></i> Tiyatrolar</a>
                <a href="/kategori/stand-up/" class="cerca-cat-pill"><i class="fas fa-microphone"></i> Stand-Up</a>
                <a href="/mekanlar/" class="cerca-cat-pill"><i class="fas fa-landmark"></i> Mekanlar</a>
              </div>

              <div class="cerca-grid">
                {event_cards_html}
              </div>
            </div>
            """

            page_meta = {
                "title": f"{city['ad']} Etkinlikleri",
                "seo_title": f"{city['ad']} Etkinlikleri, Konserler ve Tiyatrolar | Cerca",
                "seo_description": f"{city['ad']} şehrindeki güncel konserler, tiyatro biletleri ve etkinlik mekanları rehberi.",
                "layout": "default"
            }

            rendered = render_page(city_html, page_meta)
            self.send_html(rendered)
            return

        # 5. KATEGORİ HUB SAYFALARI: /kategori/{slug}
        if len(parts) >= 2 and parts[0] == 'kategori':
            slug = parts[1]
            cat = CAT_SLUG_MAP.get(slug, {"ad": slug.title(), "slug": slug, "icon": "fa-ticket", "etkinlikSayisi": 200})
            
            # Kategorideki etkinlikleri filtrele
            cat_events = [e for e in DATA["etkinlikler_core"] if e.get("tipSlug") == slug or slug in str(e.get("altTur", "")).lower()]
            # Aktifler önce
            cat_events.sort(key=lambda x: (not x.get("isActive", False), -x.get("toplamSeans", 0)))
            event_cards_html = render_event_cards(cat_events, limit=48)

            cat_html = f"""
            <div class="cerca-container" style="padding-top: 36px; padding-bottom: 60px;">
              <nav aria-label="Breadcrumb" style="margin-bottom: 20px; font-size: 0.85rem; color: var(--cerca-text-muted);">
                <a href="/">Ana Sayfa</a> &raquo;
                <span style="color: var(--cerca-text); font-weight: 600;">{cat['ad']}</span>
              </nav>

              <div class="cerca-section-header">
                <div>
                  <h1 class="cerca-section-title"><i class="fas {cat.get('icon', 'fa-ticket')}" style="color: var(--cerca-primary);"></i> {cat['ad']} Etkinlikleri</h1>
                  <p class="text-muted">Türkiye genelindeki tüm güncel {cat['ad']} biletleri ve seans saatleri ({len(cat_events)} etkinlik listelendi)</p>
                </div>
              </div>

              <!-- Şehir Hızlı Filtreleri -->
              <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 28px;">
                <span style="font-weight: 600; font-size: 0.85rem; color: var(--cerca-text-muted); display: inline-flex; align-items: center; margin-right: 6px;">
                  📍 Popüler Şehirler:
                </span>
                <a href="/sehir/istanbul/" class="cerca-cat-pill">İstanbul</a>
                <a href="/sehir/izmir/" class="cerca-cat-pill">İzmir</a>
                <a href="/sehir/ankara/" class="cerca-cat-pill">Ankara</a>
                <a href="/sehir/antalya/" class="cerca-cat-pill">Antalya</a>
                <a href="/sehir/bursa/" class="cerca-cat-pill">Bursa</a>
                <a href="/sehirler/" class="cerca-cat-pill">Tüm İller</a>
              </div>

              <div class="cerca-grid">
                {event_cards_html}
              </div>
            </div>
            """

            page_meta = {
                "title": f"{cat['ad']} Etkinlikleri",
                "seo_title": f"Türkiye {cat['ad']} Etkinlikleri ve Biletleri | Cerca",
                "seo_description": f"Türkiye genelindeki tüm {cat['ad']} etkinlikleri, seansları ve bilet bilgileri Cerca'da.",
                "layout": "default"
            }

            rendered = render_page(cat_html, page_meta)
            self.send_html(rendered)
            return

        # 6. Temiz URL Yönlendirmeleri (/sehirler/ -> /sehirler.html)
        if len(parts) == 1 and parts[0] in ["sehirler", "mekanlar", "sanatcilar", "yakindaki-etkinlikler", "hakkimizda", "iletisim", "gizlilik-politikasi"]:
            self.path = f"/{parts[0]}.html"

        # 7. Standart Statik Dosyalar (index.html, assets, css, js)
        return super().do_GET()

from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

def run_server(port=4000):
    server_address = ('127.0.0.1', port)
    httpd = ThreadedHTTPServer(server_address, CercaRouterHandler)
    print(f"\nCERCA CANLI ÇOK İŞ PARÇACIKLI (THREADED) SUNUCU BAŞLATILDI: http://localhost:{port}/")
    print("Herhangi bir /etkinlik/{slug}/, /mekan/{slug}/, /sanatci/{slug}/ linki anında (<2ms) derlenmektedir.")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server(4000)
