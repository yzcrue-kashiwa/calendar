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
        now = datetime.now()
        year = now.year
        month = now.month  # ★ 月も入れる

        for table in tables:
            rows = table.find_all("tr")

            i = 0
            while i < len(rows) - 3:

                # 4行セット
                date_row = rows[i].find_all(["td", "th"])
                row1 = rows[i + 1].find_all("td")
                row2 = rows[i + 2].find_all("td")
                row3 = rows[i + 3].find_all("td")

                dates = [c.get_text(strip=True) for c in date_row]
                r1 = [c.get_text(strip=True) for c in row1]
                r2 = [c.get_text(strip=True) for c in row2]
                r3 = [c.get_text(strip=True) for c in row3]

                for d in range(min(7, len(dates))):
                    day = dates[d]

                    # 数字じゃないのはスキップ
                    if not day.isdigit():
                        continue

                    # ★ 正しい日付生成
                    date_str = f"{year}-{month:02}-{int(day):02}"

                    # -----------------
                    # 一部
                    # -----------------
                    if d < len(r1):
                        text = r1[d]
                        if "○" in text or "o" in text.lower():
                            events.append({
                                "date": date_str,
                                "type": "一部",
                                "source": site["name"]
                            })

                    # -----------------
                    # 二部
                    # -----------------
                    if d < len(r2):
                        text = r2[d]
                        if "○" in text or "o" in text.lower():
                            events.append({
                                "date": date_str,
                                "type": "二部",
                                "source": site["name"]
                            })

                    # -----------------
                    # 貸切（分解）
                    # -----------------
                    if d < len(r3):
                        text = r3[d]

                        # 1部
                        if "1部○" in text:
                            events.append({
                                "date": date_str,
                                "type": "貸切（一部）",
                                "source": site["name"]
                            })

                        # 2部
                        if "2部○" in text:
                            events.append({
                                "date": date_str,
                                "type": "貸切（二部）",
                                "source": site["name"]
                            })

                i += 4  # ★ 次の週へ

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

    # 日付順ソート
    all_events.sort(key=lambda x: x["date"])

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("=== DONE ===")


if __name__ == "__main__":
    main()
