import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# サイトごとの部上限設定
SITE_CONFIG = {
    "Couleur": {"url": "https://couleur.studio-colore.tokyo/yoyaku-toiawase/", "max_part": 2},
    "Claris": {"url": "https://claris-studio-colore-mixbox.com/reserve/", "max_part": 2},
    "Colore": {"url": "https://fuel-studio-colore.com/reserve/", "max_part": 2},
}

def normalize_part(text):
    # 半角全角スペース削除、1部○形式に統一
    text = text.replace(" ", "").replace("　", "")
    return text

def scrape_site(name, config):
    url = config["url"]
    max_part = config["max_part"]
    res = requests.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    
    events = []
    
    # 日付ごとの予約情報が <table> または <div class="reserve"> などにある想定
    # ※実際の構造に合わせて selector を調整
    for row in soup.select(".reserve-row"):  
        date_tag = row.select_one(".reserve-date")
        if not date_tag:
            continue
        date_str = date_tag.get_text().strip()
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue
        
        # 部情報
        for part_tag in row.select(".reserve-part"):
            part_text = normalize_part(part_tag.get_text())
            if "部○" not in part_text:
                continue
            part_number = int(part_text[0])
            if part_number > max_part:
                continue  # 存在しない部はスキップ
            events.append({
                "date": date_obj.strftime("%Y-%m-%d"),
                "type": part_text,
                "source": name
            })
    return events

all_events = []
for name, config in SITE_CONFIG.items():
    all_events.extend(scrape_site(name, config))

# 重複を削除
unique_events = [dict(t) for t in {tuple(e.items()) for e in all_events}]

# JSON 保存
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(unique_events, f, ensure_ascii=False, indent=2)

print(f"Saved {len(unique_events)} events.")
