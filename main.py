import requests
from bs4 import BeautifulSoup
import json

# =========================
# 取得する月（ここ固定！）
# =========================
YEAR = 2026
MONTH = 3   # ← 必要に応じて変える（3 or 4 試す）

# =========================
# サイト設定
# =========================

SITES = [
    {
        "name": "couleur",
        "url": "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php",
        "id": "xo-event-calendar-1"
    },
    {
        "name": "claris",
        "url": "https://claris-studio-colore-mixbox.com/wp-admin/admin-ajax.php",
        "id": "xo-event-calendar-1"
    },
    {
        "name": "fuel",
        "url": "https://fuel-studio-colore.com/wp-admin/admin-ajax.php",
        "id": "xo-event-calendar-1"
    }
]

# =========================
# 正規化
# =========================

def normalize(text):
    return (
        text.replace("⚪︎", "○")
            .replace("◯", "○")
            .replace(" ", "")
            .replace("　", "")
            .replace("\n", "")
            .strip()
    )

# =========================
# 取得
# =========================

def fetch_site(site):
    payload = {
        "action": "xo_event_calendar_month",
        "id": site["id"],
        "month": f"{YEAR}-{MONTH}",
        "event": "1",
        "start_of_week": "1"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print(f"\n🌐 Fetching {site['name']}...")

    res = requests.post(site["url"], data=payload, headers=headers)

    print("STATUS:", res.status_code)
    print("LEN:", len(res.text))

    # 👇 超重要デバッグ
    print("xo-event count:", res.text.count("xo-event"))

    # 👇 HTMLの中身ちょい確認
    print("----- HTML SAMPLE -----")
    print(res.text[:500])
    print("-----------------------")

    return parse_html(res.text, site["name"])

# =========================
# パース
# =========================

def parse_html(html, site_name):
    soup = BeautifulSoup(html, "html.parser")
    events = []

    tds = soup.select("table.xo-month td")

    print("🧩 cells:", len(tds))

    for td in tds:

        if "other-month" in td.get("class", []):
            continue

        date_tag = td.select_one(".date")
        if not date_tag:
            continue

        day = date_tag.text.strip()
        if not day.isdigit():
            continue

        date_str = f"{YEAR}-{str(MONTH).zfill(2)}-{str(day).zfill(2)}"

        # 👇 イベント取得（全部拾う）
        texts = [normalize(t) for t in td.stripped_strings]

        print(site_name, date_str, texts)

        for t in texts:

            if "1部○" in t:
                events.append({
                    "site": site_name,
                    "date": date_str,
                    "part": "1部",
                    "status": "available"
                })
                print(f"✅ {site_name} 1部: {date_str}")

            if "2部○" in t:
                events.append({
                    "site": site_name,
                    "date": date_str,
                    "part": "2部",
                    "status": "available"
                })
                print(f"✅ {site_name} 2部: {date_str}")

    print(f"📦 {site_name} events:", len(events))
    return events

# =========================
# メイン
# =========================

def main():
    all_events = []

    for site in SITES:
        events = fetch_site(site)
        all_events.extend(events)

    print("\n==============================")
    print("📊 TOTAL:", len(all_events))
    print("==============================")

    # 保存
    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    with open("docs/events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("💾 saved events.json & docs/events.json")

# =========================

if __name__ == "__main__":
    main()
