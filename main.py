import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

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
    today = datetime.now()
    year = today.year
    month = today.month

    payload = {
        "action": "xo_event_calendar_month",
        "id": site["id"],
        "month": f"{year}-{month}",
        "event": "1",
        "start_of_week": "1"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    print(f"\n🌐 Fetching {site['name']}...")

    try:
        res = requests.post(site["url"], data=payload, headers=headers, timeout=10)

        print("STATUS:", res.status_code)
        print("LEN:", len(res.text))

        if res.status_code != 200:
            return []

        return parse_html(res.text, site["name"], year, month)

    except Exception as e:
        print("ERROR:", e)
        return []

# =========================
# パース（最重要）
# =========================

def parse_html(html, site_name, year, month):
    soup = BeautifulSoup(html, "html.parser")
    events = []

    tds = soup.select("table.xo-month td")

    print("🧩 cells:", len(tds))

    for td in tds:

        # 前月・翌月除外
        if "other-month" in td.get("class", []):
            continue

        # 日付取得
        date_tag = td.select_one(".date")
        if not date_tag:
            continue

        day = date_tag.text.strip()

        if not day.isdigit():
            continue

        date_str = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"

        # 👇 ここが最重要（分解して取得）
        texts = [normalize(t) for t in td.stripped_strings]

        # デバッグ
        print(site_name, date_str, texts)

        # -------------------------
        # 判定（強化版）
        # -------------------------
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
