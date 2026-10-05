import traceback
try:
    from server import DATA, render_event_cards, CAT_SLUG_MAP, RAW_DEFAULT_LAYOUT, render_page
    cat_events = [e for e in DATA["etkinlikler_core"] if e.get("tipSlug") == "konser" or "konser" in str(e.get("altTur", "")).lower()]
    print("Found konser events:", len(cat_events))
    html_cards = render_event_cards(cat_events, limit=48)
    print("Rendered cards OK! Length:", len(html_cards))
    page_meta = {
        "title": "Konser Etkinlikleri",
        "seo_title": "Türkiye Konser Etkinlikleri",
        "seo_description": "Konserler",
        "layout": "default"
    }
    rendered = render_page("<div>" + html_cards + "</div>", page_meta)
    print("Rendered full page OK! Length:", len(rendered))
except Exception as e:
    traceback.print_exc()
