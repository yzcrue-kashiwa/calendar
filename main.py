def fetch_month(site, year, month):

    payload = {
        "action": "xo_event_calendar_month",
        "id": "xo-event-calendar-1",
        "month": f"{year}-{month}",
        "base_month": f"{year}-{month}"
    }

    print(f"\n🌐 {site['name']} {year}-{month}")

    res = post_with_retry(site["url"], payload)
    if res is None:
        print("❌ FAILED")
        return []

    print("STATUS:", res.status_code)
    print("LEN:", len(res.text))

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

            print(f"{site['name']} {date} | {text}")

            is_1 = ("1部○" in text) and ("1部×" not in text)
            is_2 = ("2部○" in text) and ("2部×" not in text)

            if "撮影×" in text:
                is_1 = False
                is_2 = False

            if is_1:
                events.append({"site": site["name"], "date": date, "part": "1部"})

            if is_2:
                events.append({"site": site["name"], "date": date, "part": "2部"})

    print(f"📦 {site['name']} events:", len(events))
    return events
