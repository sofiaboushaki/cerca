# -*- coding: utf-8 -*-
"""
Cerca - Static Site Builder
Jekyll uyumlu modüler şablonları (_includes, _layouts, _data) derler.
"""

import os
import sys
import json
import shutil
import re
import yaml
from liquid import Environment

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(BASE_DIR, "_site")
DATA_DIR = os.path.join(BASE_DIR, "_data")
INCLUDES_DIR = os.path.join(BASE_DIR, "_includes")

def load_data():
    data = {}
    cerca_settings_path = os.path.join(DATA_DIR, "cerca_settings.yml")
    if os.path.exists(cerca_settings_path):
        with open(cerca_settings_path, 'r', encoding='utf-8') as f:
            data['cerca_settings'] = yaml.safe_load(f)
    
    for fn in ["sehirler.json", "kategoriler.json", "mekanlar_populer.json", "sanatcilar_populer.json", "etkinlikler_core.json", "istatistikler.json"]:
        p = os.path.join(DATA_DIR, fn)
        if os.path.exists(p):
            key = fn.replace(".json", "")
            with open(p, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)
    return data

def resolve_includes(text):
    """Jekyll stilindeki {% include dosya.html %} etiketlerini çözümler."""
    for inc_file in os.listdir(INCLUDES_DIR):
        if inc_file.endswith(".html"):
            inc_path = os.path.join(INCLUDES_DIR, inc_file)
            with open(inc_path, 'r', encoding='utf-8') as f:
                content = f.read()
            pattern = r"\{%\s*include\s+[\"']?" + re.escape(inc_file) + r"[\"']?\s*(?:[a-zA-Z0-9_\-]+=[^\%]+)?%\}"
            text = re.sub(pattern, content, text)
    return text

def build():
    print("=" * 60)
    print("CERCA STATİK DERLEYİCİ ÇALIŞIYOR...")
    print("=" * 60)
    os.makedirs(SITE_DIR, exist_ok=True)

    # 1. Assets kopyala
    src_assets = os.path.join(BASE_DIR, "assets")
    dst_assets = os.path.join(SITE_DIR, "assets")
    if os.path.exists(dst_assets):
        shutil.rmtree(dst_assets)
    shutil.copytree(src_assets, dst_assets)

    # 2. _data kopyala (İstemci fetch için)
    dst_data = os.path.join(SITE_DIR, "_data")
    if os.path.exists(dst_data):
        shutil.rmtree(dst_data)
    shutil.copytree(DATA_DIR, dst_data)

    # 3. robots.txt & sitemap.xml
    for fn in ["robots.txt", "sitemap.xml"]:
        p = os.path.join(BASE_DIR, fn)
        if os.path.exists(p):
            shutil.copy2(p, os.path.join(SITE_DIR, fn))

    site_data = load_data()
    print(f"Yüklenen Veri Setleri: {list(site_data.keys())}")

    env = Environment()
    # Jekyll filtreleri
    env.add_filter("absolute_url", lambda val: f"https://cerca.com.tr{val}" if val else "https://cerca.com.tr")
    env.add_filter("relative_url", lambda val: val if val else "")

    # Layout yükle ve includes çöz
    layout_path = os.path.join(BASE_DIR, "_layouts", "default.html")
    with open(layout_path, 'r', encoding='utf-8') as f:
        layout_str = f.read()
    
    full_layout_resolved = resolve_includes(layout_str)

    pages = [
        ("index.html", "index.html"),
        ("sehirler.html", "sehirler.html"),
        ("mekanlar.html", "mekanlar.html"),
        ("sanatcilar.html", "sanatcilar.html"),
        ("yakindaki-etkinlikler.html", "yakindaki-etkinlikler.html"),
        ("hakkimizda.html", "hakkimizda.html"),
        ("iletisim.html", "iletisim.html"),
        ("gizlilik-politikasi.html", "gizlilik-politikasi.html")
    ]

    for src_page, out_name in pages:
        src_path = os.path.join(BASE_DIR, src_page)
        if not os.path.exists(src_path):
            continue

        with open(src_path, 'r', encoding='utf-8') as f:
            raw = f.read()

        front_matter = {}
        body = raw
        if raw.startswith('---'):
            parts = raw.split('---', 2)
            if len(parts) >= 3:
                front_matter = yaml.safe_load(parts[1]) or {}
                body = parts[2]

        # Includes çöz
        body = resolve_includes(body)

        # 1. Body render
        body_template = env.from_string(body)
        body_rendered = body_template.render(
            site={"data": site_data},
            page=front_matter
        )

        # 2. Layout içine yerleştirip render et
        full_page_str = full_layout_resolved.replace("{{ content }}", body_rendered)
        full_template = env.from_string(full_page_str)
        final_html = full_template.render(
            site={"data": site_data},
            page=front_matter
        )

        out_path = os.path.join(SITE_DIR, out_name)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(final_html)

        print(f"✔ Derlendi: {out_name} ({len(final_html)} bayt)")

    print("\n" + "=" * 60)
    print(f"TÜM SİTE BAŞARIYLA DERLENDİ! Çıktı Klasörü: {SITE_DIR}")
    print("=" * 60)

if __name__ == '__main__':
    build()
