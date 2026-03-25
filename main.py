import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json

SITES = {
    "couleur": "https://couleur.example.com",
    "claris": "https://claris.example.com",
    "fuel": "https://fuel.example.com"
}

# ===== 10日間リストを作る =====
def get_target_dates():
    today = datetime.today()
    dates = []

    for i in range(10):
        d = today + timedelta(days=i)
        dates.append(d.strftime("%Y-%m-%d"))

    return dates

# ===== 月データ取得 =====
def fetch_month(site_name, base_url, year, month):

    url = base_url

    payload = {
        "action": "xo_event_calendar_month",
        "id": "xo-event-calendar-1",
        "year": year,
        "month": month
    }

    print(f"\n🌐 {site_name} {year}-{month}")

    r = requests.post(url, data=payload)
    print("STATUS:", r.status_code)

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

            # ===== 判定 =====
            has1 = "1部○" in text
            has2 = "2部○" in text

            if has1:
                events.append({
                    "date": date,
                    "site": site_name,
                    "part": "1部"
                })

            if has2:
                events.append({
                    "date": date,
                    "site": site_name,
                    "part": "2部"
                })

    print(f"📦 {site_name} events:", len(events))
    return events

# ===== メイン =====
def main():

    target_dates = set(get_target_dates())
    print("🎯 TARGET:", target_dates)

    today = datetime.today()

    months = set()

    # 対象日から必要な月を自動算出
    for i in range(10):
        d = today + timedelta(days=i)
        months.add((d.year, d.month))

    all_events = []

    for site, url in SITES.items():

        for (y, m) in months:
            events = fetch_month(site, url, y, m)

            for ev in events:
                if ev["date"] in target_dates:
                    print("✅ ADD:", ev)
                    all_events.append(ev)

    print("\n====================")
    print("📊 TOTAL:", len(all_events))
    print("====================")

    with open("docs/events.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("💾 saved docs/events.json")

if __name__ == "__main__":
    main()
