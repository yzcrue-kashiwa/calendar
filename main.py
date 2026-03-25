import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

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

# ===== 対象日 =====
def generate_target_dates():
    return [
        (TODAY + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(DAYS)
    ]

# ===== 対象月 =====
def get_target_months():
    months = set()
    for i in range(DAYS):
        d = TODAY + timedelta(days=i)
        months.add((d.year, d.month))
    return list(months)

# ===== 月取得 =====
def fetch_month(site, year, month):

    payload = {
        "action": "xo_event_calendar_month",
        "id": "xo-event-calendar-1",
        "month": f"{year}-{month}",       # ★これが正解
        "base_month": f"{year}-{month}"   # ★これも重要
    }

    print(f"\n🌐 {site['name']} {year}-{month}")

    try:
        res = requests.post(site["url"], data=payload, headers=HEADERS, timeout=10)
    except Exception as e:
        print("❌ ERROR:", e)
        return []

    print("STATUS:", res.status_code)
    print("LEN:", len(res.text))

    soup = BeautifulSoup(res.text, "html.parser")
    weeks = soup.select(".month-week")

    # ===== fallback（月ズレ対策） =====
    if len(weeks) == 0:
        print("⚠️ retry month-1")
        payload["month"] = f"{year}-{month-1}"
        payload["base_month"] = f"{year}-{month-1}"
        res = requests.post(site["url"], data=payload, headers=HEADERS)
        soup = BeautifulSoup(res.text, "html.parser")
        weeks = soup.select(".month-week")

    print("🧩 weeks:", len(weeks))

    # デバッグ
    if len(weeks) == 0:
        print("⚠️ HTML SAMPLE:", res.text[:300])
        return []

    events = []

    for week in weeks:
        days = week.select("td")

        for d in days:
            date = d.get("data-date")
            if not date:
                continue

            text = normalize(d.get_text())

            print(f"{site['name']} {date} | {text}")

            # ===== 判定 =====
            is_1 = ("1部○" in text) and ("1部×" not in text)
            is_2 = ("2部○" in text) and ("2部×" not in text)

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

    target_dates = set(generate_target_dates())
    target_months = get_target_months()

    print("🎯 TARGET:", target_dates)
    print("📅 MONTHS:", target_months)

    all_events = []

    # ===== 月ごとに全部取得 =====
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
