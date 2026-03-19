import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# スタジオごとの予約ページURL
studios = {
    "Couleur": "https://couleur.studio-colore.tokyo/yoyaku-toiawase/",
    "Claris": "https://claris-studio-colore-mixbox.com/reserve/"
}

all_reservations = []

for studio_name, url in studios.items():
    resp = requests.get(url)
    resp.encoding = resp.apparent_encoding
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # ここで各日付の予約行を取得（サイトに応じてCSSセレクタは調整）
    # 仮に日付は <th class="date">、部数は <td class="time"> 内にある場合
    table_rows = soup.select("table tr")
    
    for row in table_rows:
        date_cell = row.select_one("th.date")
        if not date_cell:
            continue
        date_text = date_cell.get_text(strip=True)
        try:
            date_obj = datetime.strptime(date_text, "%Y-%m-%d")
        except:
            continue  # 日付でなければスキップ
        
        # 各部のセルを確認
        time_cells = row.select("td.time")
        for cell in time_cells:
            time_text = cell.get_text(strip=True)
            # 「1部」「2部」だけ取得、「貸切」は除外
            if time_text in ["1部○", "2部○"]:
                all_reservations.append({
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "type": time_text,
                    "source": studio_name
                })

# JSON出力
with open("reservations.json", "w", encoding="utf-8") as f:
    json.dump(all_reservations, f, ensure_ascii=False, indent=2)

print(f"取得件数: {len(all_reservations)}")
