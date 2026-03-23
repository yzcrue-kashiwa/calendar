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

    cells = soup.select("table.xo-month td")

    for cell in cells:
        # 日付
        day_num = cell.find("span", class_="day")
        if not day_num:
            continue

        day = day_num.text.strip()
        date_str = f"{year}-{month:02d}-{int(day):02d}"

        # イベント（←ここが重要）
        event_titles = cell.select(".xo-event-title")

        for e in event_titles:
            text = e.text.replace("　", "").strip()

            for part in VALID_PARTS:
                if part in text and "○" in text:
                    events.append({
                        "date": date_str,
                        "type": f"{part}○",
                        "source": "Couleur"
                    })

    return events


def main():
    all_events = fetch_month(2026, 3)

    # 重複削除
    unique = {(e["date"], e["type"], e["source"]): e for e in all_events}
    all_events = list(unique.values())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("Saved", len(all_events), "events")


if __name__ == "__main__":
    main()
