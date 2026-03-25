import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

# ===== 基準日 =====
TODAY = datetime.now()
DAYS = 10

# ===== サイト =====
SITES = [
    {"name": "couleur", "url": "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php"},
    {"name": "claris", "url": "https://claris-studio-colore-mixbox.com/wp-admin/admin-ajax.php"},
    {"name": "fuel", "url": "https://fuel-studio-colore.com/wp-admin/admin-ajax.php"}
]

# ===== 正規化 =====
def normalize(text):
    return (
        text.replace("⚪︎", "○")
            .replace("◯", "○")
            .replace(" ", "")
            .replace("　", "")
            .replace("\n", "")
            .strip()
    )

# ===== 対象日リスト生成 =====
def generate_target_dates():
    dates = []
    for i in range(DAYS):
        d = TODAY + timedelta(days=i)
        dates.append(d.strftime("%Y-%m-%d"))
    return dates

# ===== 必要な月を抽出 =====
def get_target_months(dates):
    months = set()
    for d in dates:
        dt = datetime.strptime(d, "%Y-%m-%d")
        months.add((dt.year, dt.month))
    return list(months)

# ===== 月取得 =====
def fetch_month(site, year, month, target_dates):

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

            # 🔥 ピンポイント判定（これが最強）
            if date not in target_dates:
                continue

            texts = []
            for r in rows:
                if i < len(r):
                    texts.append(normalize(r[i].get_text()))

            merged = "".join(texts)

            print(f"{site['name']} {date} | {merged}")

            if "1部○" in merged:
                events.append({"site": site["name"], "date": date, "part": "1部"})

            if "2部○" in merged:
                events.append({"site": site["name"], "date": date, "part": "2部"})

    print(f"📦 {site['name']} events:", len(events))
    return events

# ===== メイン =====
def main():

    target_dates = generate_target_dates()
    target_months = get_target_months(target_dates)

    print("🎯 TARGET DATES:", target_dates)
    print("📅 TARGET MONTHS:", target_months)

    all_events = []

    for site in SITES:
        for (year, month) in target_months:
            all_events.extend(fetch_month(site, year, month, target_dates))

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

    print("\n====================")
    print("📊 TOTAL:", len(unique))
    print("====================")

    # 保存
    with open("docs/events.json", "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print("💾 saved docs/events.json")

if __name__ == "__main__":
    main()
