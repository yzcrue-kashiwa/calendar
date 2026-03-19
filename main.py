import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# スクレイピング対象サイト
SITES = [
    {"name": "Couleur", "url": "https://couleur.studio-colore.tokyo/yoyaku-toiawase/"},
    {"name": "Colore", "url": "https://fuel-studio-colore.com/reserve/"},
    {"name": "Claris", "url": "https://claris-studio-colore-mixbox.com/reserve/"}
]

events = []

for site in SITES:
    print(f"----\nSITE: {site['name']}")
    try:
        r = requests.get(site['url'], timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # 空き情報だけ取得
        tables = soup.find_all("table")
        for table in tables:
            for row in table.find_all("tr"):
                cols = row.find_all("td")
                if not cols:
                    continue
                date_text = cols[0].get_text(strip=True)
                # 「貸切」は無視
                if "貸切" in date_text or date_text == "":
                    continue
                for i, col in enumerate(cols[1:], start=1):
                    if "○" in col.get_text():
                        date_obj = datetime.today()  # 仮の今日の日付
                        events.append({
                            "date": date_obj.strftime("%Y-%m-%d"),
                            "type": f"{i}部○",
                            "source": site['name']
                        })
    except Exception as e:
        print("ERROR:", e)

# JSON に出力（GitHub Pages で HTML が読めるように /data.json）
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2)

print(f"TOTAL EVENTS: {len(events)}")
