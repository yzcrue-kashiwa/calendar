import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import time
import os

# ===== 設定 =====
TODAY = datetime.now()
DAYS = 10

SITES = [
    {"name": "couleur", "url": "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php"},
    {"name": "claris", "url": "https://claris-studio-colore-mixbox.com/wp-admin/admin-ajax.php"},
    {"name": "fuel", "url": "https://fuel-studio-colore.com/wp-admin/admin-ajax.php"}
]

HEADERS = {
    "User-Agent": "Mozilla/5.0",
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

# ===== claris対策 =====
def clean_text(text):
    return text.replace("撮影×", "").replace("撮影○", "")

# ===== 日付生成 =====
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

# ===== 通信（リトライ強化） =====
def post_with_retry(url, payload):
    for i in range(5):
        try:
            print(f"🌐 TRY {i+1}: {url}")
            res = requests.post(url, data=payload, headers=HEADERS, timeout=30)
            print("✅", res.status_code)
            return res
        except Exception as e:
            print(f"❌ RETRY {i+1}:", e)
            time.sleep(2)
    return None

# ===== 部判定（最終状態採用） =====
def check_part(text, part):

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

    return results[-1] == "○"

# ===== 月取得 =====
def fetch_month(site, year, month):

    print(f"\n🚀 FETCH: {site['name']} {year}-{month}")

    payload = {
        "action": "xo_event_calendar_month",
        "id": "xo-event-calendar-1",
        "month": f"{year}-{month}",
        "base_month": f"{year}-{month}",
        "event": "1",
        "start_of_week": "1"
    }

    res = post_with_retry(site["url"], payload)

    if res is None:
        print("❌ SKIP")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    weeks = soup.select(".month-week")

    print("🧩 weeks:", len(weeks))

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

            text = clean_text(text)

            print(f"{site['name']} {date} | {text}")

            if check_part(text, "1部"):
                print("✅ 1部", date)
                events.append({"site": site["name"], "date": date, "part": "1部"})

            if check_part(text, "2部"):
                print("✅ 2部", date)
                events.append({"site": site["name"], "date": date, "part": "2部"})

    print(f"📦 {site['name']}:", len(events))
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
            all_events.extend(fetch_month(site, year, month))

    # ===== フィルタ =====
    filtered = [e for e in all_events if e["date"] in target_dates]

    # ===== 重複削除 =====
    unique = []
    seen = set()

    for e in filtered:
        key = (e["site"], e["date"], e["part"])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    unique.sort(key=lambda x: (x["date"], x["site"], x["part"]))

    print("\n====================")
    print("📊 FINAL:", len(unique))
    print("====================")

    # ===== 安全書き込み（超重要） =====
    os.makedirs("docs", exist_ok=True)

    tmp = "docs/events_tmp.json"
    final = "docs/events.json"

    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    os.replace(tmp, final)

    print("💾 SAFE WRITE DONE")

# ===== 実行 =====
if __name__ == "__main__":
    main()
