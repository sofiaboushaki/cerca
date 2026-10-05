import traceback
import sys

try:
    from server import EVENT_SLUG_MAP, RAW_EVENT_LAYOUT, render_page
    event = EVENT_SLUG_MAP.get('cem-adrian-konseri')
    print('Event found:', bool(event))
    page_meta = {
        'title': event['adi'],
        'seo_title': f"{event['adi']} Biletleri",
        'seo_description': event['ozetKisa'],
        'category_name': 'Konser',
        'category_slug': 'konser',
        'category_icon': 'fa-music',
        'is_active': True,
        'is_past': False,
        'venue_name': 'Mekan',
        'venue_slug': 'mekan',
        'city_name': 'İstanbul',
        'city_slug': 'istanbul',
        'session_date': '2026-10-15',
        'summary': event['ozet'],
        'rules': event['bilmenizGerekenler'],
        'duration': '120',
        'layout': 'event',
        'event_data': {
            'adi': event['adi'],
            'isActive': True,
            'seoAciklama': event['seoAciklama'],
            'tarih': '2026-10-15',
            'mekanAdi': 'Mekan',
            'sehirAdi': 'İstanbul'
        }
    }
    rendered = render_page(RAW_EVENT_LAYOUT, page_meta, content=event['ozet'])
    print('Rendered OK! Length:', len(rendered))
except Exception as e:
    traceback.print_exc()
