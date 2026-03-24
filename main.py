import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

URL = "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php"

def fetch_calendar(year, month):
    payload = {
        "action": "xo_event_calendar_month",
        "id": "xo-event-calendar-1",
        "month": f"{year}-{month}",
        "event": "1"
    }

    res = requests.post(URL, data=payload)
    print("STATUS:", res.status_code)
    print("LEN:", len(res.text))

    return res.text


def parse_calendar(html, year, month):
    soup = BeautifulSoup(html, "html.parser")
    events = []

    weeks = soup.select("td.month-week")
    print("🧩 weeks found:", len(weeks))

    for week in weeks:
        days = week.select(".month-dayname td div")

        event_tables = week.select("table.month-event")

        # 1部 / 2部
        first_events = event_tables[0].select("td") if len(event_tables) > 0 else []
        second_events = event_tables[1].select("td") if len(event_tables) > 1 else []

        for i, d in enumerate(days):
            day_text = d.text.strip()

            # 日付じゃない場合スキップ
            if not day_text.isdigit():
                continue

            # 前月・翌月除外
            if "other-month" in d.get("class", []):
                continue

            day = int(day_text)

            try:
                dt = datetime(year, month, day)
            except:
                continue

            date_str = dt.strftime("%Y-%m-%d")

            # --- 1部 ---
            if i < len(first_events):
                text = first_events[i].text.strip()
                if "1部○" in text:
                    events.append({
                        "date": date_str,
                        "part": "1部",
                        "status": "available"
                    })
                    print("✅ ADD 1部:", date_str)

            # --- 2部 ---
            if i < len(second_events):
                text = second_events[i].text.strip()
                if "2部○" in text:
                    events.append({
                        "date": date_str,
                        "part": "2部",
                        "status": "available"
                    })
                    print("✅ ADD 2部:", date_str)

    return events


def save_json(events):
    print("📊 FINAL events:", len(events))

    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

    print("💾 saved: events.json")


if __name__ == "__main__":
    today = datetime.now()
    year = today.year
    month = today.month

    print("🌐 Fetching Couleur...")

    html = fetch_calendar(year, month)
    events = parse_calendar(html, year, month)

    save_json(events)
