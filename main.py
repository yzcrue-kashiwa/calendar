import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

# 🔥 対象サイト
SITES = [
    {
        "name": "couleur",
        "url": "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php",
        "calendar_id": "xo-event-calendar-1"
    },
    {
        "name": "fuel",
        "url": "https://fuel-studio-colore.com/wp-admin/admin-ajax.php",
        "calendar_id": "xo-event-calendar-1"
    }
]


# 🔥 文字正規化（超重要）
def normalize(text):
    return (
        text.replace("⚪︎", "○")
            .replace(" ", "")
            .replace("　", "")
            .strip()
    )


# 🔥 ○判定
def is_available(text):
    return "○" in text


def fetch_calendar(site, year, month):
    payload = {
        "action": "xo_event_calendar_month",
        "id": site["calendar_id"],
        "month": f"{year}-{month}",
        "event": "1"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": site["url"].replace("/wp-admin/admin-ajax.php", "/"),
        "Origin": site["url"].split("/wp-admin")[0]
    }

    res = requests.post(site["url"], data=payload, headers=headers)

    print(f"🌐 {site['name']} STATUS:", res.status_code)
    print("LEN:", len(res.text))

    return res.text


def parse_calendar(html, year, month, site_name):
    soup = BeautifulSoup(html, "html.parser")
    events = []

    weeks = soup.select("td.month-week")
    print(f"🧩 {site_name} weeks:", len(weeks))

    for week in weeks:
        days = week.select(".month-dayname td div")
        event_tables = week.select("table.month-event")

        first_events = event_tables[0].select("td") if len(event_tables) > 0 else []
        second_events = event_tables[1].select("td") if len(event_tables) > 1 else []

        for i, d in enumerate(days):
            day_text = d.text.strip()

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

            # ---------- 1部 ----------
            if i < len(first_events):
                raw = first_events[i].text
                text = normalize(raw)

                print(f"[{site_name} 1部] {date_str} -> '{text}'")

                if "1部" in text and is_available(text):
                    events.append({
                        "site": site_name,
                        "date": date_str,
                        "part": "1部",
                        "status": "available"
                    })
                    print(f"✅ ADD {site_name} 1部:", date_str)

            # ---------- 2部 ----------
            if i < len(second_events):
                raw = second_events[i].text
                text = normalize(raw)

                print(f"[{site_name} 2部] {date_str} -> '{text}'")

                if "2部" in text and is_available(text):
                    events.append({
                        "site": site_name,
                        "date": date_str,
                        "part": "2部",
                        "status": "available"
                    })
                    print(f"✅ ADD {site_name} 2部:", date_str)

    return events


def main():
    today = datetime.now()
    year = today.year
    month = today.month

    all_events = []

    print("🚀 START")

    for site in SITES:
        html = fetch_calendar(site, year, month)
        events = parse_calendar(html, year, month, site["name"])

        print(f"📦 {site['name']} events:", len(events))
        all_events.extend(events)

    print("================================")
    print("📊 TOTAL events:", len(all_events))
    print("================================")

    # 🔥 保存（Pages用）
    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("💾 saved: events.json")


if __name__ == "__main__":
    main()
