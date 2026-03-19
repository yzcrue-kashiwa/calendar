import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

URL = "https://couleur.studio-colore.tokyo/yoyaku-toiawase/"

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

def scrape():
    res = requests.get(URL, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    events = []
    rows = soup.select("table tr")

    current_date = None

    for row in rows:
        cols = [c.text.strip() for c in row.find_all("td")]

        if not cols:
            continue

        if "/" in cols[0]:
            current_date = parse_date(cols[0])

        if len(cols) >= 2 and current_date:
            status = cols[1]

            if "○" in status:
                for t in ["一部", "二部", "貸切"]:
                    if t in cols[0] or t in status:
                        events.append({
                            "date": current_date,
                            "type": t
                        })

    return events

def main():
    data = scrape()

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()                        events.append({
                            "date": current_date,
                            "type": t
                        })

    return events

def main():
    data = scrape()

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
