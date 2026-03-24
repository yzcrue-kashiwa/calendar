import requests
from bs4 import BeautifulSoup
import json

YEAR = 2026
MONTH = 4   # ← 今は4月になってるので注意

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

def normalize(text):
    return (
        text.replace("⚪︎", "○")
            .replace("◯", "○")
            .replace(" ", "")
            .replace("　", "")
            .strip()
    )

def fetch(site):
    payload = {
        "action": "xo_event_calendar_month",
        "id": "xo-event-calendar-1",
        "month": f"{YEAR}-{MONTH}",
        "event": "1",
        "categories": "",
        "holidays": "all",
        "prev": "1",
        "next": "-1",
        "start_of_week": "1",
        "months": "1",
        "navigation": "1",
        "title_format": "",
        "is_locale": "1",
        "columns": "1",
        "base_month": f"{YEAR}-{MONTH}"
    }

    print(f"\n🌐 {site['name']}")
    res = requests.post(site["url"], data=payload)
    soup = BeautifulSoup(res.text, "html.parser")

    events = []

    weeks = soup.select("td.month-week")
    print("🧩 weeks:", len(weeks))

    for week in weeks:

        days = week.select("table.month-dayname td div")
        tables = week.select("table.month-event")

        if len(tables) < 2:
            continue

        first = tables[0].select("td")
        second = tables[1].select("td")

        for i, d in enumerate(days):

            if "other-month" in d.get("class", []):
                continue

            day = d.text.strip()
            if not day.isdigit():
                continue

            date = f"{YEAR}-{str(MONTH).zfill(2)}-{str(day).zfill(2)}"

            t1 = normalize(first[i].get_text()) if i < len(first) else ""
            t2 = normalize(second[i].get_text()) if i < len(second) else ""

            print(date, t1, t2)

            if "1部○" in t1:
                events.append({
                    "site": site["name"],
                    "date": date,
                    "part": "1部",
                    "status": "available"
                })

            if "2部○" in t2:
                events.append({
                    "site": site["name"],
                    "date": date,
                    "part": "2部",
                    "status": "available"
                })

    print(f"📦 {site['name']} events:", len(events))
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
