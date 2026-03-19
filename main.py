import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

SITES = [
    {
        "url": "https://couleur.studio-colore.tokyo/yoyaku-toiawase/",
        "name": "Couleur"
    },
    {
        "url": "https://www.studio-colore.tokyo/reservation/",
        "name": "Colore"
    },
    {
        "url": "https://claris-studio-colore-mixbox.com/reserve/",
        "name": "Claris"
    }
]

headers = {
    "User-Agent": "Mozilla/5.0"
}


def parse_date(text):
    try:
        month, day = text.split("（")[0].split("/")
        year = datetime.now().year
        return f"{year}-{int(month):02}-{int(day):02}"
    except:
        return None


def scrape_site(site):
    print("----")
    print("SITE:", site["name"])

    try:
        res = requests.get(site["url"], headers=headers, timeout=10)
        print("STATUS:", res.status_code)

        soup = BeautifulSoup(res.text, "html.parser")

        tables = soup.find_all("table")
        print("TABLE COUNT:", len(tables))

        events = []

        for table in tables:
            rows = table.find_all("tr")

            current_date = None

            for row in rows:
                cols = [c.text.strip() for c in row.find_all("td")]

                if not cols:
                    continue

                # ■ 日付判定（フォーム除外）
                if "/" in cols[0] and len(cols[0]) < 10:
                    current_date = parse_date(cols[0])

                # ■ 各枠チェック（ここが今回の核心）
                if current_date and len(cols) >= 2:

                    types = ["一部", "二部", "貸切"]

                    for i, t in enumerate(types):
                        if i + 1 < len(cols):
                            status_text = cols[i + 1]

                            # 空き判定（ゆるめ）
                            if (
                                status_text
                                and "×" not in status_text
                                and "満" not in status_text
                            ):
                                events.append({
                                    "date": current_date,
                                    "type": t,
                                    "source": site["name"]
                                })

        print("EVENTS FOUND:", len(events))
        return events

    except Exception as e:
        print("ERROR in", site["name"], ":", e)
        return []


def main():
    print("=== START SCRAPING ===")

    all_events = []

    for site in SITES:
        events = scrape_site(site)
        all_events += events

    print("TOTAL EVENTS:", len(all_events))

    # 日付順ソート
    all_events.sort(key=lambda x: x["date"] if x["date"] else "")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
