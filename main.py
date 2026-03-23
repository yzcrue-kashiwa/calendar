import requests
from bs4 import BeautifulSoup
import json

URL = "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php"
OUTPUT_FILE = "events.json"


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

    weeks = soup.select("td.month-week")

    for week in weeks:
        # 日付（7日）
        days = week.select(".dayname td div")

        # 1部・2部テーブル
        tables = week.select("table.month-event")

        if len(tables) < 2:
            continue

        first_half = tables[0].select("td")
        second_half = tables[1].select("td")

        for i in range(len(days)):
            day_text = days[i].text.strip()

            # 数字じゃない（前月・次月）除外
            if not day_text.isdigit():
                continue

            day = int(day_text)
            date_str = f"{year}-{month:02d}-{day:02d}"

            # ===== 1部 =====
            if i < len(first_half):
                text = first_half[i].text.strip()
                if "1部○" in text:
                    events.append({
                        "date": date_str,
                        "type": "1部○",
                        "source": "Couleur"
                    })

            # ===== 2部 =====
            if i < len(second_half):
                text = second_half[i].text.strip()
                if "2部○" in text:
                    events.append({
                        "date": date_str,
                        "type": "2部○",
                        "source": "Couleur"
                    })

    return events


def main():
    events = fetch_month(2026, 3)

    # 重複削除
    unique = {(e["date"], e["type"], e["source"]): e for e in events}
    events = list(unique.values())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

    print("=================================")
    print("Saved", len(events), "events")
    print("=================================")


if __name__ == "__main__":
    main()
