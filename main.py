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
        text = text.replace(" ", "").replace("　", "")
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

            for row in rows:
                # ★ td + th 両方取る
                cols = [c.text.strip() for c in row.find_all(["td", "th"])]

                if len(cols) < 2:
                    continue

                # ★ 日付（1列目）
                date_text = cols[0]
                current_date = parse_date(date_text)

                if not current_date:
                    continue

                print("DATE:", current_date)

                # ★ 各枠チェック
                types = ["一部", "二部", "貸切"]

                for i, t in enumerate(types):
                    if i + 1 < len(cols):
                        status_text = cols[i + 1]

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
        all_events += scrape_site(site)

    print("TOTAL EVENTS:", len(all_events))

    all_events.sort(key=lambda x: x["date"] if x["date"] else "")

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
