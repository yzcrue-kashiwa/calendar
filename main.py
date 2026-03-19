import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

# 対象サイトリスト
sites = [
    {"name": "Couleur", "url": "https://couleur.studio-colore.tokyo/yoyaku-toiawase/"},
    {"name": "Claris",  "url": "https://claris-studio-colore-mixbox.com/reserve/"}
]

# 今回は存在する部を1部と2部のみに限定
valid_parts = ["1部○", "2部○"]

# 保存用リスト
events = []

# 今日から10日間だけ取得
start_date = datetime.today()
end_date = start_date + timedelta(days=10)

for site in sites:
    r = requests.get(site["url"])
    soup = BeautifulSoup(r.text, "html.parser")
    
    # 日付ごとのブロック取得（サイトによって要調整）
    day_blocks = soup.find_all(attrs={"data-day": True})
    
    for block in day_blocks:
        date_str = block.get("data-day").strip()
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except:
            continue
        if not (start_date <= date_obj <= end_date):
            continue
        
        # 部テキスト取得
        parts = block.get_text(separator=" ").split()
        for part in parts:
            part_clean = part.strip()
            if part_clean in valid_parts:
                events.append({
                    "date": date_str,
                    "type": part_clean,
                    "source": site["name"]
                })

# JSONに保存
with open("events.json", "w", encoding="utf-8") as f:
    json.dump(events, f, ensure_ascii=False, indent=2)

print(f"Saved {len(events)} events.")
