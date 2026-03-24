import requests
from bs4 import BeautifulSoup
import json

YEAR = 2026
MONTH = 4  # ← 必ず今取得したい月に合わせる

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

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    print(f"\n🌐 Fetching {site['name']}...")

    res = requests.post(site["url"], data=payload, headers=headers)

    print("STATUS:", res.status_code)
    print("LEN:", len(res.text))

    soup = BeautifulSoup(res.text, "html.parser")

    events = []

    weeks = soup.select("td.month-week")
    print("🧩 weeks:", len(weeks))

    for week in weeks:

        # 日付
        days = week.select("table.month-dayname td div")

        # イベントテーブル
        tables = week.select("table.month-event")

        first = None
        second = None

        # 🔥 クラスで判定（順番依存しない）
        for t in tables:
            html_str = str(t)

            if "category-first-half" in html_str:
                first = t.select("td")

            elif "category-second-half" in html_str:
                second = t.select("td")

        if not first or not second:
            continue

        # 日付とイベントを横対応
        for i, d in enumerate(days):

            if "other-month" in d.get("class", []):
                continue

            day = d.text.strip()
            if not day.isdigit():
                continue

            date = f"{YEAR}-{str(MONTH).zfill(2)}-{str(day).zfill(2)}"

            t1 = normalize(first[i].get_text()) if i < len(first) else ""
            t2 = normalize(second[i].get_text()) if i < len(second) else ""

            print(f"{site['name']} {date} | {t1} | {t2}")

            # ✅ 1部
            if "1部○" in t1:
                events.append({
                    "site": site["name"],
                    "date": date,
                    "part": "1部",
                    "status": "available"
                })
                print(f"✅ ADD 1部: {date}")

            # ✅ 2部
            if "2部○" in t2:
                events.append({
                    "site": site["name"],
                    "date": date,
                    "part": "2部",
                    "status": "available"
                })
                print(f"✅ ADD 2部: {date}")

    print(f"📦 {site['name']} events:", len(events))
    return events


def main():
    all_events = []

    for site in SITES:
        all_events.extend(fetch(site))

    print("\n==============================")
    print("📊 TOTAL:", len(all_events))
    print("==============================")

    # GitHub Pages用
    with open("docs/events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    # ローカル確認用
    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("💾 saved events.json & docs/events.json")


if __name__ == "__main__":
    main()
