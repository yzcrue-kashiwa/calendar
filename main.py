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
    }
]

def clean(text):
    return (
        text.replace("\n", "")
            .replace("\t", "")
            .replace(" ", "")
            .replace("　", "")
            .strip()
    )

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

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://couleur.studio-colore.tokyo/",
        "Origin": "https://couleur.studio-colore.tokyo",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        res = requests.post(site["url"], data=payload, headers=headers, timeout=10)

        print("STATUS:", res.status_code)
        print("LEN:", len(res.text))

        res.raise_for_status()
        return res.text

    except Exception as e:
        print(f"❌ Fetch error: {e}")
        return None


def parse(html, year, month):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    weeks = soup.select("td.month-week")
    print(f"🧩 weeks found: {len(weeks)}")

    for week in weeks:
        days = week.select(".month-dayname td div")
        event_tables = week.select("table.month-event")

        if len(event_tables) < 2:
            continue

        for i, d in enumerate(days):
            day_text = clean(d.text)

            if not day_text.isdigit():
                continue

            day = int(day_text)
            date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"

            # 1部
            try:
                t1 = clean(event_tables[0].select("td")[i].text)
                if "1部○" in t1:
                    print(f"✅ ADD 1部: {date}")
                    results.append({
                        "date": date,
                        "part": "1部",
                        "status": "available"
                    })
            except:
                pass

            # 2部
            try:
                t2 = clean(event_tables[1].select("td")[i].text)
                if "2部○" in t2:
                    print(f"✅ ADD 2部: {date}")
                    results.append({
                        "date": date,
                        "part": "2部",
                        "status": "available"
                    })
            except:
                pass

    print(f"📦 parse結果: {len(results)}件")
    return results


def main():
    today = datetime.now()
    year = today.year
    month = today.month

    all_events = []

    for site in SITES:
        print(f"🌐 Fetching {site['name']}...")
        html = fetch_month(site, year, month)

        if not html:
            continue

        events = parse(html, year, month)
        all_events.extend(events)

    print("================================")
    print(f"📊 FINAL events: {len(all_events)}")
    print("================================")

    # 🔥 保存（両方に書く）
    paths = [
        "calendar/events.json",
        "docs/calendar/events.json"
    ]

    for path in paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(all_events, f, ensure_ascii=False, indent=2)
        print(f"💾 saved: {path}")


if __name__ == "__main__":
    main()
