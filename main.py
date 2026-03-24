import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

# ===== 設定 =====
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

# ===== 文字正規化 =====
def normalize(text):
    return (
        text.replace("⚪︎", "○")
            .replace("◯", "○")
            .replace(" ", "")
            .replace("　", "")
            .replace("\n", "")
            .strip()
    )

# ===== 日付範囲チェック =====
def in_range(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return TODAY <= d < END

# ===== 月取得 =====
def fetch_month(site, year, month):

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

    print(f"\n🌐 {site['name']} {year}-{month}")
    res = requests.post(site["url"], data=payload)

    print("STATUS:", res.status_code)
    print("LEN:", len(res.text))

    soup = BeautifulSoup(res.text, "html.parser")

    events = []

    weeks = soup.select("td.month-week")
    print("🧩 weeks:", len(weeks))

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

            # 🔥 10日制限
            if not in_range(date):
                continue

            texts = []
            for r in rows:
                if i < len(r):
                    texts.append(normalize(r[i].get_text()))

            merged = "".join(texts)

            print(f"{site['name']} {date} | {merged}")

            # 空きだけ
            if "1部○" in merged:
                print("✅ ADD 1部:", date)
                events.append({
                    "site": site["name"],
                    "date": date,
                    "part": "1部"
                })

            if "2部○" in merged:
                print("✅ ADD 2部:", date)
                events.append({
                    "site": site["name"],
                    "date": date,
                    "part": "2部"
                })

    print(f"📦 {site['name']} events:", len(events))
    return events

# ===== メイン =====
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

    print("\n==============================")
    print("📊 TOTAL:", len(all_events))
    print("==============================")

    # 重複削除
    unique = []
    seen = set()

    for e in all_events:
        key = (e["site"], e["date"], e["part"])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    # ソート
    unique.sort(key=lambda x: (x["date"], x["site"], x["part"]))

    # 保存
    with open("docs/events.json", "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print("💾 saved docs/events.json")

# ===== 実行 =====
if __name__ == "__main__":
    main()
