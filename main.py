import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

SITES = [
    {"url": "https://couleur.studio-colore.tokyo/yoyaku-toiawase/", "name": "Couleur"},
    {"url": "https://www.studio-colore.tokyo/reservation/", "name": "Colore"},
    {"url": "https://claris-studio-colore-mixbox.com/reserve/", "name": "Claris"}
]

headers = {"User-Agent": "Mozilla/5.0"}


def scrape_site(site):
    print("----")
    print("SITE:", site["name"])

    try:
        res = requests.get(site["url"], headers=headers, timeout=10)
        print("STATUS:", res.status_code)

        soup = BeautifulSoup(res.text, "html.parser")
        tables = soup.find_all("table")

        events = []
        year = datetime.now().year

        for table in tables:
            rows = table.find_all("tr")

            i = 0
            while i < len(rows) - 3:

                # 4行セット取得
                date_row = rows[i].find_all(["td", "th"])
                row1 = rows[i + 1].find_all("td")
                row2 = rows[i + 2].find_all("td")
                row3 = rows[i + 3].find_all("td")

                dates = [c.get_text(strip=True) for c in date_row]
                r1 = [c.get_text(strip=True) for c in row1]
                r2 = [c.get_text(strip=True) for c in row2]
                r3 = [c.get_text(strip=True) for c in row3]

                # 7日分ループ
                for d in range(min(7, len(dates))):
                    day = dates[d]

                    if not day.isdigit():
                        continue

                    date_str = f"{year}-{int(day):02}"

                    # 一部
                    if d < len(r1) and "○" in r1[d]:
                        events.append({
                            "date": date_str,
                            "type": "一部",
                            "source": site["name"]
                        })

                    # 二部
                    if d < len(r2) and "○" in r2[d]:
                        events.append({
                            "date": date_str,
                            "type": "二部",
                            "source": site["name"]
                        })

                    # 貸切
                    if d < len(r3) and "○" in r3[d]:
                        events.append({
                            "date": date_str,
                            "type": "貸切",
                            "source": site["name"]
                        })

                i += 4  # ★ここ重要

        print("EVENTS FOUND:", len(events))
        return events

    except Exception as e:
        print("ERROR:", e)
        return []


def main():
    print("=== START SCRAPING ===")

    all_events = []

    for site in SITES:
        all_events += scrape_site(site)

    print("TOTAL EVENTS:", len(all_events))

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
