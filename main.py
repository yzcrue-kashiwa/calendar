import requests
from bs4 import BeautifulSoup
import json

YEAR = 2026
MONTH = 3

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

def fetch(site):
    payload = {
        "action": "xo_event_calendar_month",
        "id": site["id"],
        "month": f"{YEAR}-{MONTH}",
        "event": "1",
        "categories": "",
        "holidays": "all",
        "start_of_week": "1",
        "months": "1",
        "navigation": "1"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    print(f"\n🌐 {site['name']}")

    res = requests.post(site["url"], data=payload, headers=headers)

    print("STATUS:", res.status_code)
    print("LEN:", len(res.text))
    print("xo-event count:", res.text.count("xo-event"))

    return parse(res.text, site["name"])

def parse(html, site_name):
    soup = BeautifulSoup(html, "html.parser")
    events = []

    tds = soup.select("td")

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

        date = f"{YEAR}-{str(MONTH).zfill(2)}-{str(day).zfill(2)}"

        text = normalize(td.get_text())

        print(site_name, date, text)

        if "1部○" in text:
            events.append({
                "site": site_name,
                "date": date,
                "part": "1部",
                "status": "available"
            })
            print(f"✅ {site_name} 1部 {date}")

        if "2部○" in text:
            events.append({
                "site": site_name,
                "date": date,
                "part": "2部",
                "status": "available"
            })
            print(f"✅ {site_name} 2部 {date}")

    print(f"📦 {site_name} events:", len(events))
    return events

def main():
    all_events = []

    for site in SITES:
        all_events.extend(fetch(site))

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
