import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time

# ===== 設定 =====
TODAY = datetime.now()
DAYS = 10

SITES = [
    {"name": "couleur", "url": "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php"},
    {"name": "claris", "url": "https://claris-studio-colore-mixbox.com/wp-admin/admin-ajax.php"},
    {"name": "fuel", "url": "https://fuel-studio-colore.com/wp-admin/admin-ajax.php"}
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest"
}

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

# ===== 日付 =====
def generate_target_dates():
    return [
        (TODAY + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(DAYS)
    ]

def get_target_months():
    months = set()
    for i in range(DAYS):
        d = TODAY + timedelta(days=i)
        months.add((d.year, d.month))
    return list(months)

# ===== 通信（リトライ） =====
def post_with_retry(url, payload):
    for i in range(3):
        try:
            print(f"🌐 TRY {i+1}: {url}")
            res = requests.post(url, data=payload, headers=HEADERS, timeout=30)
            print("✅ SUCCESS", res.status_code)
            return res
        except Exception as e:
            print(f"❌ ERROR {i+1}:", e)
            time.sleep(2)

    print("🔥 ALL RETRY FAILED")
    return None

# ===== 🔥 fuel対応：最終状態判定 =====
def check_part(text, part):

    # 貸切以降カット
    if "貸切" in text:
        text = text.split("貸切")[0]

    results = []
    i = 0

    while i < len(text):
        if text[i:i+3] == f"{part}○":
            results.append("○")
            i += 3
        elif text[i:i+3] == f"{part}×":
            results.append("×")
            i += 3
        else:
            i += 1

    if not results:
        return False

    # 最後の状態だけ採用
    return results[-1] == "○"

# ===== 月取得 =====
def fetch_month(site, year, month):

    print("\n🚀 FETCH START:", site["name"], year, month)

    payload = {
        "action": "xo_event_calendar_month",
        "id": "xo-event-calendar-1",
        "month": f"{year}-{month}",
        "base_month": f"{year}-{month}",
        "event": "1",
        "categories": "",
        "holidays": "all",
        "prev": "1",
        "next": "-1",
        "start_of_week": "1",
        "months": "1",
        "navigation": "1",
        "columns": "1"
    }

    res = post_with_retry(site["url"], payload)

    if res is None:
        print("❌ SKIP:", site["name"])
        return []

    print("STATUS:", res.status_code)
    print("LEN:", len(res.text))

    soup = BeautifulSoup(res.text, "html.parser")
    weeks = soup.select(".month-week")

    print("🧩 weeks:", len(weeks))

    if len(weeks) == 0:
        print("⚠️ HTML SAMPLE:", res.text[:300])
        return []

    events = []

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

            text = ""
            for r in rows:
                if i < len(r):
                    text += normalize(r[i].get_text())

            print(f"{site['name']} {date} | {text}")

            # ===== 判定 =====
            is_1 = check_part(text, "1部")
            is_2 = check_part(text, "2部")

            # 撮影NG除外
            if "撮影×" in text:
                is_1 = False
                is_2 = False

            if is_1:
                print("✅ ADD 1部:", date)
                events.append({
                    "site": site["name"],
                    "date": date,
                    "part": "1部"
                })

            if is_2:
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

    print("🚀 START")

    target_dates = set(generate_target_dates())
    target_months = get_target_months()

    print("🎯 TARGET:", target_dates)
    print("📅 MONTHS:", target_months)

    all_events = []

    for site in SITES:
        for (year, month) in target_months:
            events = fetch_month(site, year, month)
            all_events.extend(events)

    # ===== 10日分に絞る =====
    filtered = [e for e in all_events if e["date"] in target_dates]

    # ===== 重複削除 =====
    unique = []
    seen = set()

    for e in filtered:
        key = (e["site"], e["date"], e["part"])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    # ===== ソート =====
    unique.sort(key=lambda x: (x["date"], x["site"], x["part"]))

    print("\n==============================")
    print("📊 TOTAL:", len(unique))
    print("==============================")

    # ===== 保存 =====
    with open("docs/events.json", "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print("💾 saved docs/events.json")

# ===== 実行 =====
if __name__ == "__main__":
    main()
