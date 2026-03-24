import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

SITES = [
    {
        "name": "Couleur",
        "url": "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php",
        "calendar_id": "xo-event-calendar-1"
    }
]

# 🔥 文字ゆらぎ除去
def clean(text):
    return (
        text.replace("\n", "")
            .replace("\t", "")
            .replace(" ", "")
            .replace("　", "")
            .strip()
    )

# 🔥 取得（User-Agent付き）
def fetch_month(site, year, month):
    payload = {
        "action": "xo_event_calendar_month",
        "id": site["calendar_id"],
        "month": f"{year}-{month}",
        "event": 1,
        "start_of_week": 1,
        "months": 1,
        "navigation": 1,
        "is_locale": 1
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        res = requests.post(
            site["url"],
            data=payload,
            headers=headers,
            timeout=10
        )
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"❌ Fetch error: {e}")
        return None


# 🔥 パース
def parse(html, year, month):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    weeks = soup.select("td.month-week")
    print(f"🧩 weeks found: {len(weeks)}")

    for week in weeks:
        days = week.select(".month-dayname td div")
        event_tables = week.select("table.month-event")

        if len(event_tables) < 2:
            continue

        for i, d in enumerate(days):
            day_text = clean(d.text)

            if not day_text.isdigit():
                continue

            day = int(day_text)
            date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"

            # ---- 1部 ----
            try:
                raw1 = event_tables[0].select("td")[i].text
                t1 = clean(raw1)

                print(f"[DEBUG 1部] {date} -> '{t1}'")

                if "1部○" in t1:
                    print(f"✅ ADD 1部: {date}")
                    results.append({
                        "date": date,
                        "part": "1部",
                        "status": "available"
                    })
            except Exception as e:
                print("1部 error:", e)

            # ---- 2部 ----
            try:
                raw2 = event_tables[1].select("td")[i].text
                t2 = clean(raw2)

                print(f"[DEBUG 2部] {date} -> '{t2}'")

                if "2部○" in t2:
                    print(f"✅ ADD 2部: {date}")
                    results.append({
                        "date": date,
                        "part": "2部",
                        "status": "available"
                    })
            except Exception as e:
                print("2部 error:", e)

    print(f"📦 parse結果: {len(results)}件")
    return results


# 🔥 メイン処理
def main():
    today = datetime.now()
    year = today.year
    month = today.month

    all_events = []

    for site in SITES:
        print(f"🌐 Fetching {site['name']}...")
        html = fetch_month(site, year, month)

        if not html:
            continue

        events = parse(html, year, month)
        print(f"📥 取得イベント数: {len(events)}")

        # 🔥 上書きじゃなく追加
        all_events.extend(events)

    print("================================")
    print(f"📊 FINAL events: {len(all_events)}")
    print(all_events)
    print("================================")

    # ⚠️ 0件チェック
    if len(all_events) == 0:
        print("⚠️ WARNING: イベント0件！（取得失敗の可能性）")

    # 保存
    os.makedirs("calendar", exist_ok=True)

    with open("calendar/events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("💾 JSON書き込み完了")


if __name__ == "__main__":
    main()
