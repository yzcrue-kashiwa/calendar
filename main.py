import requests
from bs4 import BeautifulSoup
import json

URL = "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php"

OUTPUT_FILE = "events.json"

VALID_PARTS = ["1部", "2部"]

def fetch_month(year, month):
    payload = {
        "action": "xo_event_calendar_month",
        "id": "xo-event-calendar-1",
        "month": f"{year}-{month}",
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
        "base_month": f"{year}-{month}"
    }

    res = requests.post(URL, data=payload)
    soup = BeautifulSoup(res.text, "html.parser")

    events = []

    # 各日付セル
    days = soup.select("td")

    for day in days:
        date_attr = day.get("data-date")
        if not date_attr:
            continue

        text = day.get_text(separator=" ").replace("　", "").strip()

        # 1部・2部のみ抽出
        for part in VALID_PARTS:
            if part in text and "○" in text:
                events.append({
                    "date": date_attr,
                    "type": f"{part}○",
                    "source": "Couleur"
                })

    return events


def main():
    all_events = []

    # とりあえず今月
    events = fetch_month(2026, 3)
    all_events.extend(events)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("Saved", len(all_events), "events")


if __name__ == "__main__":
    main()
