import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

SITES = [
    {
        "name": "couleur",
        "url": "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php",
        "id": "xo-event-calendar-1"
    },
    {
        "name": "claris",
        "url": "https://claris-studio-colore-mixbox.com/wp-admin/admin-ajax.php",
        "id": "xo-event-calendar-1"
    },
    {
        "name": "fuel",
        "url": "https://fuel-studio-colore.com/wp-admin/admin-ajax.php",
        "id": "xo-event-calendar-1"
    }
]

def normalize(text):
    return (
        text.replace("⚪︎", "○")
            .replace("◯", "○")
            .replace(" ", "")
            .replace("　", "")
            .replace("\n", "")
            .strip()
    )

def fetch_site(site):
    today = datetime.now()
    year = today.year
    month = today.month

    payload = {
        "action": "xo_event_calendar_month",
        "id": site["id"],
        "month": f"{year}-{month}",
        "event": "1",
        "start_of_week": "1"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print(f"\n🌐 Fetching {site['name']}...")

    res = requests.post(site["url"], data=payload, headers=headers)

    print("STATUS:", res.status_code)
    print("LEN:", len(res.text))

    return parse_html(res.text, site["name"], year, month)

def parse_html(html, site_name, year, month):
    soup = BeautifulSoup(html, "html.parser")
    events = []

    tds = soup.select("table.xo-month td")

    print("🧩 cells:", len(tds))

    for td in tds:

        if "other-month" in td.get("class", []):
            continue

        date_tag = td.select_one(".date")
        if not date_tag:
            continue

        day = date_tag.text.strip()
        if not day.isdigit():
            continue

        date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"

        # 👇 ここが核心
        event_tags = td.select(".xo-event")

        for ev in event_tags:
            text = normalize(ev.get_text())

            print(site_name, date_str, text)

            if "1部○" in text:
                events.append({
                    "site": site_name,
                    "date": date_str,
                    "part": "1部",
                    "status": "available"
                })
                print(f"✅ {site_name} 1部: {date_str}")

            if "2部○" in text:
                events.append({
                    "site": site_name,
                    "date": date_str,
                    "part": "2部",
                    "status": "available"
                })
                print(f"✅ {site_name} 2部: {date_str}")

    print(f"📦 {site_name} events:", len(events))
    return events

def main():
    all_events = []

    for site in SITES:
        all_events.extend(fetch_site(site))

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
