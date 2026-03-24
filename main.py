import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

TODAY = datetime.now()
END = TODAY + timedelta(days=10)

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
            .replace("\n", "")
            .strip()
    )

def in_range(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return TODAY <= d < END

def fetch_month(site, year, month):

    payload = {
        "action": "xo_event_calendar_month",
        "id": "xo-event-calendar-1",
        "month": f"{year}-{month}",
    }

    print(f"\n🌐 {site['name']} {year}-{month}")
    res = requests.post(site["url"], data=payload)

    print("STATUS:", res.status_code)

    soup = BeautifulSoup(res.text, "html.parser")

    events = []

    weeks = soup.select("td.month-week")

    for week in weeks:

        days = week.select("table.month-dayname td div")
        tables = week.select("table.month-event")
        rows = [t.select("td") for t in tables]

        for i, d in enumerate(days):

            if "other-month" in d.get("class", []):
                continue

            day = d.text.strip()
            if not day.isdigit():
                continue

            date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"

            # 🔥 ここで10日制限
            if not in_range(date):
                continue

            texts = []
            for r in rows:
                if i < len(r):
                    texts.append(normalize(r[i].get_text()))

            merged = "".join(texts)

            if "1部○" in merged:
                events.append({
                    "site": site["name"],
                    "date": date,
                    "part": "1部"
                })

            if "2部○" in merged:
                events.append({
                    "site": site["name"],
                    "date": date,
                    "part": "2部"
                })

    print(f"📦 {site['name']} events:", len(events))
    return events


def main():
    all_events = []

    this_month = TODAY.month
    next_month = this_month + 1 if this_month < 12 else 1
    next_year = TODAY.year if this_month < 12 else TODAY.year + 1

    for site in SITES:

        # 今月
        all_events.extend(fetch_month(site, TODAY.year, this_month))

        # 来月
        all_events.extend(fetch_month(site, next_year, next_month))

    print("\n====================")
    print("📊 TOTAL:", len(all_events))
    print("====================")

    with open("docs/events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("💾 saved")


if __name__ == "__main__":
    main()
