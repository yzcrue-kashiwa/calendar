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

    # ===== デバッグここから =====
    print("====== HTML CHECK ======")
    print(res.text[:2000])
    print("====== END ======")

    if "1部" in res.text:
        print("✅ 1部 見つかった！")
    else:
        print("❌ 1部 見つからない")

    # ===== デバッグここまで =====

    soup = BeautifulSoup(res.text, "html.parser")

    events = []

    cells = soup.select("td")

    for cell in cells:
        text = cell.get_text()

        # ○が含まれるセルだけチェック
        if "○" in text:
            print("---- EVENT CELL ----")
            print(cell)
            print("--------------------")

        # 日付取得
        day_tag = cell.find("span", class_="day")
        if not day_tag:
            continue

        day = day_tag.text.strip()
        date_str = f"{year}-{month:02d}-{int(day):02d}"

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
    all_events = fetch_month(2026, 3)

    # 重複削除
    unique = {(e["date"], e["type"], e["source"]): e for e in all_events}
    all_events = list(unique.values())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("=================================")
    print("Saved", len(all_events), "events")
    print("=================================")


if __name__ == "__main__":
    main()
