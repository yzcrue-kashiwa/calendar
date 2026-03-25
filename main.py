import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

SITES = {
    "couleur": "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php",
    "claris": "https://claris-studio-colore-mixbox.com/wp-admin/admin-ajax.php",
    "fuel": "https://fuel-studio-colore.com/wp-admin/admin-ajax.php"
}

# ===== 10日分 =====
def get_target_dates():
    today = datetime.today()
    return [
        (today + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(10)
    ]

# ===== 月取得 =====
def fetch_month(site, url, year, month):

    payload = {
        "action": "xo_event_calendar_month",
        "id": "xo-event-calendar-1",
        "year": year,
        "month": month
    }

    print(f"\n🌐 {site} {year}-{month}")

    try:
        r = requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print("❌ ERROR:", e)
        return []

    print("STATUS:", r.status_code)
    print("LEN:", len(r.text))

    soup = BeautifulSoup(r.text, "html.parser")
    weeks = soup.select(".month-week")

    print("🧩 weeks:", len(weeks))

    events = []

    for week in weeks:
        days = week.select("td")

        for d in days:
            date = d.get("data-date")
            if not date:
                continue

            text = d.get_text(strip=True)

            print(f"{site} {date} | {text}")

            if "1部○" in text:
                print("✅ ADD 1部:", date)
                events.append({
                    "date": date,
                    "site": site,
                    "part": "1部"
                })

            if "2部○" in text:
                print("✅ ADD 2部:", date)
                events.append({
                    "date": date,
                    "site": site,
                    "part": "2部"
                })

    print(f"📦 {site} events:", len(events))
    return events

# ===== メイン =====
def main():

    target_dates = set(get_target_dates())
    print("🎯 TARGET:", target_dates)

    today = datetime.today()

    # 必要な月を自動取得（ここ重要）
    months = set()
    for i in range(10):
        d = today + timedelta(days=i)
        months.add((d.year, d.month))

    all_events = []

    for site, url in SITES.items():

        for (y, m) in months:
            events = fetch_month(site, url, y, m)

            for ev in events:
                if ev["date"] in target_dates:
                    all_events.append(ev)

    print("\n====================")
    print("📊 TOTAL:", len(all_events))
    print("====================")

    with open("docs/events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("💾 saved docs/events.json")


if __name__ == "__main__":
    main()
