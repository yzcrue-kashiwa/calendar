import requests
from bs4 import BeautifulSoup
import json
import datetime

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

    # カレンダーの全セル取得
    cells = soup.select("table.xo-month td")

    for cell in cells:
        text = cell.get_text(separator=" ").replace("　", "").strip()

        # 日付取得（セル内の数字）
        day_number = None
        for t in cell.stripped_strings:
            if t.isdigit():
                day_number = int(t)
                break

        if not day_number:
            continue

        # 日付生成
        date_str = f"{year}-{month:02d}-{day_number:02d}"

        # 部チェック
        for part in VALID_PARTS:
            if part in text and "○" in text:
                events.append({
                    "date": date_str,
                    "type": f"{part}○",
                    "source": "Couleur"
                })

    return events


def main():
    all_events = []

    events = fetch_month(2026, 3)
    all_events.extend(events)

    # 重複削除（超重要）
    unique = { (e["date"], e["type"], e["source"]): e for e in all_events }
    all_events = list(unique.values())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("Saved", len(all_events), "events")


if __name__ == "__main__":
    main()
