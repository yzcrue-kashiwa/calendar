import requests
import json
from datetime import datetime

YEAR = 2026
MONTH = 3

SITES = [
    {
        "name": "couleur",
        "url": "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php"
    },
    {
        "name": "claris",
        "url": "https://claris-studio-colore-mixbox.com/wp-admin/admin-ajax.php"
    },
    {
        "name": "fuel",
        "url": "https://fuel-studio-colore.com/wp-admin/admin-ajax.php"
    }
]

def fetch_events(site):
    payload = {
        "action": "xo_event_calendar",  # ←ここ重要
        "start": f"{YEAR}-{MONTH}-01",
        "end": f"{YEAR}-{MONTH}-31"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    print(f"\n🌐 Fetching {site['name']} events...")

    res = requests.post(site["url"], data=payload, headers=headers)

    print("STATUS:", res.status_code)
    print("LEN:", len(res.text))

    try:
        data = res.json()
    except:
        print("❌ JSONじゃない")
        print(res.text[:300])
        return []

    events = []

    for ev in data:
        title = ev.get("title", "")

        if "1部" in title and "○" in title:
            events.append({
                "site": site["name"],
                "date": ev["start"][:10],
                "part": "1部",
                "status": "available"
            })

        if "2部" in title and "○" in title:
            events.append({
                "site": site["name"],
                "date": ev["start"][:10],
                "part": "2部",
                "status": "available"
            })

    print(f"📦 {site['name']} events:", len(events))
    return events

def main():
    all_events = []

    for site in SITES:
        all_events.extend(fetch_events(site))

    print("\n==============================")
    print("📊 TOTAL:", len(all_events))
    print("==============================")

    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    with open("docs/events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("💾 saved")

if __name__ == "__main__":
    main()
