import requests
from bs4 import BeautifulSoup
import json
import datetime

# -----------------------------
# 設定
# -----------------------------
SITES = [
    {"url": "https://couleur.studio-colore.tokyo/yoyaku-toiawase/", "source": "Couleur"},
    {"url": "https://claris-studio-colore-mixbox.com/reserve/", "source": "Claris"}
]

OUTPUT_FILE = "events.json"

# 1部と2部のみ取得
VALID_PARTS = ["1部", "2部"]

all_events = []

# -----------------------------
# 各サイトを処理
# -----------------------------
for site in SITES:
    try:
        res = requests.get(site["url"], timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"サイト {site['source']} にアクセスできません: {e}")
        continue

    soup = BeautifulSoup(res.text, "html.parser")

    # ここはサイトによって CSS セレクタを調整
    # 例: 日付セルが <div class="reserve-day" data-date="2026-03-19"> など
    day_elements = soup.select(".reserve-day, .day, button")

    for day_el in day_elements:
        # data-date属性 or テキストを取得
        date_text = day_el.get("data-date") or day_el.get_text()
        if not date_text:
            continue

        # 日付としてパース
        try:
            date_obj = datetime.datetime.strptime(date_text.strip(), "%Y-%m-%d")
        except:
            continue

        # 部情報の取得
        part_elements = day_el.select(".part, .time-slot, button")
        for part_el in part_elements:
            part_text = part_el.get_text().strip()
            for valid in VALID_PARTS:
                if valid in part_text and "○" in part_text:
                    all_events.append({
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "type": part_text,
                        "source": site["source"]
                    })

# -----------------------------
# JSON 保存
# -----------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_events, f, ensure_ascii=False, indent=2)

print(f"Saved {len(all_events)} events.")
