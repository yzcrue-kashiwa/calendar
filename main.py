import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

SITES = [
    {
        "name": "Couleur",
        "url": "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php",
        "calendar_id": "xo-event-calendar-1"
    },
    {
        "name": "Colore",
        "url": "https://fuel-studio-colore.com/wp-admin/admin-ajax.php",
        "calendar_id": "xo-event-calendar-1"
    },
    {
        "name": "Claris",
        "url": "https://claris-studio-colore-mixbox.com/wp-admin/admin-ajax.php",
        "calendar_id": "xo-event-calendar-1"
    }
]

def fetch_month(site, year, month):
    payload = {
        "action": "xo_event_calendar_month",
        "id": site["calendar_id"],
        "month": f"{year}-{month}",
        "event": 1,
        "start_of_week": 1,
        "months": 1,
        "navigation": 1,
        "is_locale": 1
    }

    try:
        res = requests.post(site["url"], data=payload, timeout=10)
        res.raise_for_status()
        return res.text
    except:
        print(f"❌ Failed: {site['name']}")
        return None


def parse(html, year, month):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    weeks = soup.select("td.month-week")

    for week in weeks:
        days = week.select(".month-dayname td div")
        event_tables = week.select("table.month-event")

        if len(event_tables) < 2:
            continue

        for i, d in enumerate(days):
            day_text = d.text.strip()

            if not day_text.isdigit():
                continue

            day = int(day_text)
            date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"

            # 1部
            try:
                t1 = event_tables[0].select("td")[i].text
                if "1部" in t1 and "○" in t1:
                    results.append({
                        "date": date,
                        "part": "1部",
                        "status": "available"
                    })
            except:
                pass

            # 2部
            try:
                t2 = event_tables[1].select("td")[i].text
                if "2部" in t2 and "○" in t2:
                    results.append({
                        "date": date,
                        "part": "2部",
                        "status": "available"
                    })
            except:
                pass

    return results


def main():
    today = datetime.now()
    year = today.year
    month = today.month

    all_events = []

    for site in SITES:
        print(f"Fetching {site['name']}...")
        html = fetch_month(site, year, month)
        if not html:
            continue

        events = parse(html, year, month)
        all_events.extend(events)

    # 🔥 ここが超重要
    os.makedirs("calendar", exist_ok=True)

    with open("calendar/events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(all_events)} events")


if __name__ == "__main__":
    main()
