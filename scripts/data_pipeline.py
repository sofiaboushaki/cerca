# -*- coding: utf-8 -*-
"""
Cerca - Data Pipeline & Aggregator Engine
Faz 1: Veri Analizi, Temizleme, 81 İl Eşlemesi ve İlişkisel Köprülerin Kurulması
"""

import os
import sys
import json
import re
import html
import unicodedata
import pandas as pd
from datetime import datetime

# UTF-8 ayarı
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "_data")
os.makedirs(DATA_DIR, exist_ok=True)

# 81 İl Eşleme Tablosu (Plaka Kodu -> İsim ve SEO Slug)
SEHIRLER_MAP = {
    1: {"ad": "Adana", "slug": "adana", "plaka": "01"},
    2: {"ad": "Adıyaman", "slug": "adiyaman", "plaka": "02"},
    3: {"ad": "Afyonkarahisar", "slug": "afyonkarahisar", "plaka": "03"},
    4: {"ad": "Ağrı", "slug": "agri", "plaka": "04"},
    5: {"ad": "Amasya", "slug": "amasya", "plaka": "05"},
    6: {"ad": "Ankara", "slug": "ankara", "plaka": "06"},
    7: {"ad": "Antalya", "slug": "antalya", "plaka": "07"},
    8: {"ad": "Artvin", "slug": "artvin", "plaka": "08"},
    9: {"ad": "Aydın", "slug": "aydin", "plaka": "09"},
    10: {"ad": "Balıkesir", "slug": "balikesir", "plaka": "10"},
    11: {"ad": "Bilecik", "slug": "bilecik", "plaka": "11"},
    12: {"ad": "Bingöl", "slug": "bingol", "plaka": "12"},
    13: {"ad": "Bitlis", "slug": "bitlis", "plaka": "13"},
    14: {"ad": "Bolu", "slug": "bolu", "plaka": "14"},
    15: {"ad": "Burdur", "slug": "burdur", "plaka": "15"},
    16: {"ad": "Bursa", "slug": "bursa", "plaka": "16"},
    17: {"ad": "Çanakkale", "slug": "canakkale", "plaka": "17"},
    18: {"ad": "Çankırı", "slug": "cankiri", "plaka": "18"},
    19: {"ad": "Çorum", "slug": "corum", "plaka": "19"},
    20: {"ad": "Denizli", "slug": "denizli", "plaka": "20"},
    21: {"ad": "Diyarbakır", "slug": "diyarbakir", "plaka": "21"},
    22: {"ad": "Edirne", "slug": "edirne", "plaka": "22"},
    23: {"ad": "Elazığ", "slug": "elazig", "plaka": "23"},
    24: {"ad": "Erzincan", "slug": "erzincan", "plaka": "24"},
    25: {"ad": "Erzurum", "slug": "erzurum", "plaka": "25"},
    26: {"ad": "Eskişehir", "slug": "eskisehir", "plaka": "26"},
    27: {"ad": "Gaziantep", "slug": "gaziantep", "plaka": "27"},
    28: {"ad": "Giresun", "slug": "giresun", "plaka": "28"},
    29: {"ad": "Gümüşhane", "slug": "gumushane", "plaka": "29"},
    30: {"ad": "Hakkari", "slug": "hakkari", "plaka": "30"},
    31: {"ad": "Hatay", "slug": "hatay", "plaka": "31"},
    32: {"ad": "Isparta", "slug": "isparta", "plaka": "32"},
    33: {"ad": "Mersin", "slug": "mersin", "plaka": "33"},
    34: {"ad": "İstanbul", "slug": "istanbul", "plaka": "34"},
    35: {"ad": "İzmir", "slug": "izmir", "plaka": "35"},
    36: {"ad": "Kars", "slug": "kars", "plaka": "36"},
    37: {"ad": "Kastamonu", "slug": "kastamonu", "plaka": "37"},
    38: {"ad": "Kayseri", "slug": "kayseri", "plaka": "38"},
    39: {"ad": "Kırklareli", "slug": "kirklareli", "plaka": "39"},
    40: {"ad": "Kırşehir", "slug": "kirsehir", "plaka": "40"},
    41: {"ad": "Kocaeli", "slug": "kocaeli", "plaka": "41"},
    42: {"ad": "Konya", "slug": "konya", "plaka": "42"},
    43: {"ad": "Kütahya", "slug": "kutahya", "plaka": "43"},
    44: {"ad": "Malatya", "slug": "malatya", "plaka": "44"},
    45: {"ad": "Manisa", "slug": "manisa", "plaka": "45"},
    46: {"ad": "Kahramanmaraş", "slug": "kahramanmaras", "plaka": "46"},
    47: {"ad": "Mardin", "slug": "mardin", "plaka": "47"},
    48: {"ad": "Muğla", "slug": "mugla", "plaka": "48"},
    49: {"ad": "Muş", "slug": "mus", "plaka": "49"},
    50: {"ad": "Nevşehir", "slug": "nevsehir", "plaka": "50"},
    51: {"ad": "Niğde", "slug": "nigde", "plaka": "51"},
    52: {"ad": "Ordu", "slug": "ordu", "plaka": "52"},
    53: {"ad": "Rize", "slug": "rize", "plaka": "53"},
    54: {"ad": "Sakarya", "slug": "sakarya", "plaka": "54"},
    55: {"ad": "Samsun", "slug": "samsun", "plaka": "55"},
    56: {"ad": "Siirt", "slug": "siirt", "plaka": "56"},
    57: {"ad": "Sinop", "slug": "sinop", "plaka": "57"},
    58: {"ad": "Sivas", "slug": "sivas", "plaka": "58"},
    59: {"ad": "Tekirdağ", "slug": "tekirdag", "plaka": "59"},
    60: {"ad": "Tokat", "slug": "tokat", "plaka": "60"},
    61: {"ad": "Trabzon", "slug": "trabzon", "plaka": "61"},
    62: {"ad": "Tunceli", "slug": "tunceli", "plaka": "62"},
    63: {"ad": "Şanlıurfa", "slug": "sanliurfa", "plaka": "63"},
    64: {"ad": "Uşak", "slug": "usak", "plaka": "64"},
    65: {"ad": "Van", "slug": "van", "plaka": "65"},
    66: {"ad": "Yozgat", "slug": "yozgat", "plaka": "66"},
    67: {"ad": "Zonguldak", "slug": "zonguldak", "plaka": "67"},
    68: {"ad": "Aksaray", "slug": "aksaray", "plaka": "68"},
    69: {"ad": "Bayburt", "slug": "bayburt", "plaka": "69"},
    70: {"ad": "Karaman", "slug": "karaman", "plaka": "70"},
    71: {"ad": "Kırıkkale", "slug": "kirikkale", "plaka": "71"},
    72: {"ad": "Batman", "slug": "batman", "plaka": "72"},
    73: {"ad": "Şırnak", "slug": "sirnak", "plaka": "73"},
    74: {"ad": "Bartın", "slug": "bartin", "plaka": "74"},
    75: {"ad": "Ardahan", "slug": "ardahan", "plaka": "75"},
    76: {"ad": "Iğdır", "slug": "igdir", "plaka": "76"},
    77: {"ad": "Yalova", "slug": "yalova", "plaka": "77"},
    78: {"ad": "Karabük", "slug": "karabuk", "plaka": "78"},
    79: {"ad": "Kilis", "slug": "kilis", "plaka": "79"},
    80: {"ad": "Osmaniye", "slug": "osmaniye", "plaka": "80"},
    81: {"ad": "Düzce", "slug": "duzce", "plaka": "81"}
}

# Tip ID -> Kategori Adı ve Slug Eşlemesi
TIP_MAP = {
    2: {"ad": "Konser", "slug": "konser", "icon": "fa-music"},
    1: {"ad": "Tiyatro", "slug": "tiyatro", "icon": "fa-masks-theater"},
    40: {"ad": "Stand-Up & Komedi", "slug": "stand-up", "icon": "fa-microphone"},
    36: {"ad": "Çocuk & Aile", "slug": "cocuk", "icon": "fa-child"},
    16: {"ad": "Festival", "slug": "festival", "icon": "fa-campground"},
    0: {"ad": "Kültür & Sanat", "slug": "kultur-sanat", "icon": "fa-palette"},
    3: {"ad": "Girişimcilik & Eğitim", "slug": "egitim", "icon": "fa-graduation-cap"},
    37: {"ad": "Sinema & Gösterim", "slug": "sinema", "icon": "fa-film"},
    45: {"ad": "Spor & Dans", "slug": "spor-dans", "icon": "fa-person-running"}
}

def clean_html_text(text):
    """HTML entity'lerini ve etiketlerini temizleyerek arama & SEO için saf metin üretir."""
    if not isinstance(text, str) or not text.strip():
        return ""
    # HTML entities decode
    decoded = html.unescape(text)
    # Temizle
    cleaned = re.sub(r'<[^>]+>', ' ', decoded)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def clean_slug(val):
    if not isinstance(val, str):
        return ""
    val = val.strip().lower()
    val = re.sub(r'[^a-z0-9\-]', '', val)
    val = re.sub(r'\-+', '-', val).strip('-')
    return val

def run_pipeline():
    print("=" * 60)
    print("CERCA DATA PIPELINE BAŞLATILIYOR...")
    print("=" * 60)

    # 1. MEKANLAR
    print("\n[1/4] Mekanlar okunuyor ve işleniyor...")
    df_mekan = pd.read_csv(os.path.join(BASE_DIR, 'mekanlar.csv'), low_memory=False)
    print(f"Toplam mekan sayısı: {len(df_mekan)}")

    mekan_dict = {}
    city_venue_count = {}

    for _, r in df_mekan.iterrows():
        mid = int(r['id'])
        sid = int(r['sehirId']) if pd.notna(r['sehirId']) else 0
        sehir_info = SEHIRLER_MAP.get(sid, {"ad": "Diğer", "slug": "diger", "plaka": "00"})
        
        slug = clean_slug(r['slug']) if pd.notna(r['slug']) else f"mekan-{mid}"
        baslik = str(r['baslik']).strip() if pd.notna(r['baslik']) else "İsimsiz Mekan"
        adres = clean_html_text(str(r['adres'])) if pd.notna(r['adres']) else ""
        aciklama = clean_html_text(str(r['aciklama'])) if pd.notna(r['aciklama']) else ""
        seo_aciklama = str(r['seoAciklama']).strip() if pd.notna(r['seoAciklama']) else aciklama[:160]

        enlem = float(r['enlem']) if pd.notna(r['enlem']) else 0.0
        boylam = float(r['boylam']) if pd.notna(r['boylam']) else 0.0

        mekan_dict[mid] = {
            "id": mid,
            "baslik": baslik,
            "kisaBaslik": str(r['kisaBaslik']).strip() if pd.notna(r['kisaBaslik']) else baslik,
            "slug": slug,
            "sehirId": sid,
            "sehirAdi": sehir_info["ad"],
            "sehirSlug": sehir_info["slug"],
            "adres": adres,
            "aciklama": aciklama,
            "seoBaslik": str(r['seoBaslik']).strip() if pd.notna(r['seoBaslik']) else baslik,
            "seoAciklama": seo_aciklama,
            "enlem": enlem,
            "boylam": boylam,
            "etkinlikSayisi": 0,
            "aktifSeansSayisi": 0
        }

        if sid in SEHIRLER_MAP:
            city_venue_count[sid] = city_venue_count.get(sid, 0) + 1

    # 2. SANATCILAR
    print("\n[2/4] Sanatçılar okunuyor ve işleniyor...")
    df_sanat = pd.read_csv(os.path.join(BASE_DIR, 'sanatcilar.csv'), low_memory=False)
    print(f"Toplam sanatçı sayısı: {len(df_sanat)}")

    sanatci_dict = {}
    for _, r in df_sanat.iterrows():
        sid = int(r['id'])
        slug = clean_slug(r['slug']) if pd.notna(r['slug']) else f"sanatci-{sid}"
        adi_soyadi = str(r['adiSoyadi']).strip() if pd.notna(r['adiSoyadi']) else str(r['ad']).strip()
        biografi = str(r['biografi']) if pd.notna(r['biografi']) else ""
        bio_plain = clean_html_text(biografi)

        sanatci_dict[sid] = {
            "id": sid,
            "adiSoyadi": adi_soyadi,
            "slug": slug,
            "dogumYeri": str(r['dogumYeri']).strip() if pd.notna(r['dogumYeri']) else "",
            "biografi": biografi,
            "bioOzet": bio_plain[:240] + ("..." if len(bio_plain) > 240 else ""),
            "etkinlikAdedi": int(r['etkinlikAdedi']) if pd.notna(r['etkinlikAdedi']) else 0,
            "seoBaslik": str(r['seoBaslik']).strip() if pd.notna(r['seoBaslik']) else adi_soyadi,
            "seoAciklama": str(r['seoAciklama']).strip() if pd.notna(r['seoAciklama']) else bio_plain[:160]
        }

    # 3. SEANSLAR & İLİŞKİSEL KÖPRÜLER
    print("\n[3/4] Seanslar analiz ediliyor (268.000+ kayıt)...")
    df_seans = pd.read_csv(os.path.join(BASE_DIR, 'seanslar.csv'), low_memory=False)

    event_sessions = {}
    city_event_count = {}
    category_count = {}

    simdiki_zaman = datetime.now()

    for _, r in df_seans.iterrows():
        eid = int(r['etkinlikId']) if pd.notna(r['etkinlikId']) else None
        if not eid:
            continue
        
        mid = int(r['mekanId']) if pd.notna(r['mekanId']) else 0
        sid = int(r['sehirId']) if pd.notna(r['sehirId']) else 0
        tip = int(r['tip']) if pd.notna(r['tip']) else 0
        tarih_str = str(r['tarih']).strip() if pd.notna(r['tarih']) else ""
        aktif = int(r['aktif']) if pd.notna(r['aktif']) else 0
        seans_tipi = str(r['seansTipi']).strip() if pd.notna(r['seansTipi']) else "past"

        if eid not in event_sessions:
            event_sessions[eid] = {
                "toplam_seans": 0,
                "aktif_seans": 0,
                "mekan_ids": set(),
                "sehir_ids": set(),
                "seanslar": []
            }

        event_sessions[eid]["toplam_seans"] += 1
        if mid:
            event_sessions[eid]["mekan_ids"].add(mid)
            if mid in mekan_dict:
                mekan_dict[mid]["etkinlikSayisi"] += 1
                if aktif == 1 and seans_tipi == 'active':
                    mekan_dict[mid]["aktifSeansSayisi"] += 1

        if sid:
            event_sessions[eid]["sehir_ids"].add(sid)
            if sid in SEHIRLER_MAP:
                city_event_count[sid] = city_event_count.get(sid, 0) + 1

        if tip in TIP_MAP:
            category_count[tip] = category_count.get(tip, 0) + 1

        if aktif == 1 and seans_tipi == 'active':
            event_sessions[eid]["aktif_seans"] += 1

        # En son seans örneklerini sakla (max 5 seans)
        if len(event_sessions[eid]["seanslar"]) < 5 and tarih_str:
            mekan_adi = mekan_dict.get(mid, {}).get("baslik", "Mekan Belirtilmedi")
            sehir_adi = SEHIRLER_MAP.get(sid, {}).get("ad", "")
            event_sessions[eid]["seanslar"].append({
                "tarih": tarih_str,
                "mekanId": mid,
                "mekanAdi": mekan_adi,
                "sehirId": sid,
                "sehirAdi": sehir_adi,
                "aktif": aktif,
                "seansTipi": seans_tipi
            })

    # 4. ETKİNLİKLER
    print("\n[4/4] Etkinlikler okunuyor ve işleniyor...")
    df_etk = pd.read_csv(os.path.join(BASE_DIR, 'etkinlikler.csv'), low_memory=False)
    print(f"Toplam etkinlik sayısı: {len(df_etk)}")

    etkinlik_listesi = []
    aktif_etkinlik_sayisi = 0
    arsiv_etkinlik_sayisi = 0

    for _, r in df_etk.iterrows():
        eid = int(r['id'])
        slug = clean_slug(r['slug']) if pd.notna(r['slug']) else f"etkinlik-{eid}"
        adi = str(r['adi']).strip() if pd.notna(r['adi']) else "İsimsiz Etkinlik"
        tip = int(r['tip']) if pd.notna(r['tip']) else 0
        tip_info = TIP_MAP.get(tip, {"ad": "Kültür & Sanat", "slug": "kultur-sanat", "icon": "fa-palette"})
        
        ozet = str(r['ozet']) if pd.notna(r['ozet']) else ""
        ozet_plain = clean_html_text(ozet)
        
        bilmeniz = str(r['bilmenizGerekenler']) if pd.notna(r['bilmenizGerekenler']) else ""
        bilmeniz_plain = clean_html_text(bilmeniz)

        alt_tur = str(r['alt_tur']).strip() if pd.notna(r['alt_tur']) else tip_info["ad"]
        sure = str(r['sure']).strip() if pd.notna(r['sure']) else ""
        puan = float(r['puan']) if pd.notna(r['puan']) and r['puan'] > 0 else 0.0
        puan_adet = int(r['puanAdet']) if pd.notna(r['puanAdet']) else 0

        session_meta = event_sessions.get(eid, {
            "toplam_seans": 0,
            "aktif_seans": 0,
            "mekan_ids": set(),
            "sehir_ids": set(),
            "seanslar": []
        })

        is_active = session_meta["aktif_seans"] > 0
        if is_active:
            aktif_etkinlik_sayisi += 1
        else:
            arsiv_etkinlik_sayisi += 1

        # Mekan ve şehir bilgisi
        mekan_adlari = [mekan_dict[m]["baslik"] for m in session_meta["mekan_ids"] if m in mekan_dict]
        sehir_adlari = [SEHIRLER_MAP[s]["ad"] for s in session_meta["sehir_ids"] if s in SEHIRLER_MAP]
        sehir_sluglari = [SEHIRLER_MAP[s]["slug"] for s in session_meta["sehir_ids"] if s in SEHIRLER_MAP]

        seo_baslik = str(r['seoBaslik']).strip() if pd.notna(r['seoBaslik']) else f"{adi} Biletleri ve Seansları"
        seo_aciklama = str(r['seoAciklama']).strip() if pd.notna(r['seoAciklama']) else ozet_plain[:160]

        etkinlik_obj = {
            "id": eid,
            "adi": adi,
            "slug": slug,
            "tipId": tip,
            "tipAdi": tip_info["ad"],
            "tipSlug": tip_info["slug"],
            "tipIcon": tip_info["icon"],
            "altTur": alt_tur,
            "sure": sure,
            "puan": puan,
            "puanAdet": puan_adet,
            "ozet": ozet,
            "ozetKisa": ozet_plain[:220] + ("..." if len(ozet_plain) > 220 else ""),
            "bilmenizGerekenler": bilmeniz,
            "bilmenizKisa": bilmeniz_plain[:200],
            "isActive": is_active,
            "toplamSeans": session_meta["toplam_seans"],
            "sehirler": sehir_adlari[:4],
            "sehirSluglari": sehir_sluglari[:4],
            "mekanlar": mekan_adlari[:3],
            "seanslar": session_meta["seanslar"],
            "seoBaslik": seo_baslik,
            "seoAciklama": seo_aciklama
        }

        etkinlik_listesi.append(etkinlik_obj)

    # 5. ÇIKTILARI HAZIRLAMA (JSON MODELLERİ)
    print("\n[5/5] JSON modelleri üretiliyor...")

    # A) Şehirler Modeli
    sehirler_data = []
    for sid, sinfo in SEHIRLER_MAP.items():
        vcount = city_venue_count.get(sid, 0)
        ecount = city_event_count.get(sid, 0)
        sehirler_data.append({
            "id": sid,
            "ad": sinfo["ad"],
            "slug": sinfo["slug"],
            "plaka": sinfo["plaka"],
            "mekanSayisi": vcount,
            "etkinlikSayisi": ecount,
            "seoBaslik": f"{sinfo['ad']} Etkinlikleri, Konserler ve Tiyatrolar",
            "seoAciklama": f"{sinfo['ad']} şehrindeki en güncel konserler, tiyatro oyunları, festivaller ve etkinlik mekanları Cerca'da."
        })
    # En çok etkinlik olan şehirler en üstte
    sehirler_data.sort(key=lambda x: x["etkinlikSayisi"], reverse=True)
    with open(os.path.join(DATA_DIR, "sehirler.json"), "w", encoding="utf-8") as f:
        json.dump(sehirler_data, f, ensure_ascii=False, indent=2)

    # B) Kategoriler Modeli
    kategoriler_data = []
    for tid, tinfo in TIP_MAP.items():
        count = category_count.get(tid, 0)
        kategoriler_data.append({
            "id": tid,
            "ad": tinfo["ad"],
            "slug": tinfo["slug"],
            "icon": tinfo["icon"],
            "etkinlikSayisi": count,
            "seoBaslik": f"Türkiye {tinfo['ad']} Etkinlikleri ve Biletleri",
            "seoAciklama": f"Türkiye genelindeki tüm güncel {tinfo['ad']} etkinlikleri, seansları, mekanları ve bilet bilgileri Cerca'da."
        })
    kategoriler_data.sort(key=lambda x: x["etkinlikSayisi"], reverse=True)
    with open(os.path.join(DATA_DIR, "kategoriler.json"), "w", encoding="utf-8") as f:
        json.dump(kategoriler_data, f, ensure_ascii=False, indent=2)

    # C) Mekanlar (En popüler ve koordinatlı mekanlar - Top 600)
    populer_mekanlar = sorted(list(mekan_dict.values()), key=lambda x: x["etkinlikSayisi"], reverse=True)[:600]
    with open(os.path.join(DATA_DIR, "mekanlar_populer.json"), "w", encoding="utf-8") as f:
        json.dump(populer_mekanlar, f, ensure_ascii=False, indent=2)

    # D) Sanatçılar (En çok etkinliği olanlar - Top 500)
    populer_sanatcilar = sorted(list(sanatci_dict.values()), key=lambda x: x["etkinlikAdedi"], reverse=True)[:500]
    with open(os.path.join(DATA_DIR, "sanatcilar_populer.json"), "w", encoding="utf-8") as f:
        json.dump(populer_sanatcilar, f, ensure_ascii=False, indent=2)

    # E) Çekirdek Etkinlikler (Aktif olanlar + En popüler arşiv etkinlikleri)
    aktifler = [e for e in etkinlik_listesi if e["isActive"]]
    arsiv_populer = sorted([e for e in etkinlik_listesi if not e["isActive"]], key=lambda x: x["toplamSeans"], reverse=True)[:1500]
    cekirdek_etkinlikler = aktifler + arsiv_populer
    with open(os.path.join(DATA_DIR, "etkinlikler_core.json"), "w", encoding="utf-8") as f:
        json.dump(cekirdek_etkinlikler, f, ensure_ascii=False, indent=2)

    # F) Platform İstatistikleri (Trust Badges & Hero Bilgileri)
    istatistikler = {
        "toplamEtkinlik": len(df_etk),
        "aktifEtkinlik": aktif_etkinlik_sayisi,
        "arsivEtkinlik": arsiv_etkinlik_sayisi,
        "toplamMekan": len(df_mekan),
        "toplamSanatci": len(df_sanat),
        "toplamSeans": len(df_seans),
        "kapsananSehirSayisi": len([s for s in sehirler_data if s['mekanSayisi'] > 0]),
        "guncellenmeTarihi": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(DATA_DIR, "istatistikler.json"), "w", encoding="utf-8") as f:
        json.dump(istatistikler, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("VERİ MOTORU BAŞARIYLA TAMAMLANDI!")
    print(f"Toplam Etkinlik: {istatistikler['toplamEtkinlik']} ({aktif_etkinlik_sayisi} aktif seanslı)")
    print(f"Toplam Mekan: {istatistikler['toplamMekan']}")
    print(f"Toplam Sanatçı: {istatistikler['toplamSanatci']}")
    print(f"Toplam Seans: {istatistikler['toplamSeans']}")
    print(f"Çıktı klasörü: {DATA_DIR}")
    print("=" * 60)

if __name__ == '__main__':
    run_pipeline()
