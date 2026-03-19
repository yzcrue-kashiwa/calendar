import requests
import json
from datetime import datetime, timedelta

# === 設定 ===
API_URLS = {
    "Couleur": "https://couleur.studio-colore.tokyo/api/reserve",  # 実際のAPIを確認
    "Claris": "https://claris-studio-colore-mixbox.com/api/reserve"
}

# 取得する期間（日数）
DAYS_AHEAD = 10

# 有効な部（存在する部だけ）
VALID_SECTIONS = ["1部", "2部"]

# 出力ファイル
OUTPUT_FILE = "events.json"


def fetch_events(source, api_url):
    """サイトのAPIからイベントを取得"""
    events = []
    for day_offset in range(DAYS_AHEAD):
        date = (datetime.now() + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        # APIに送るパラメータ例（実際のAPIに合わせて変更）
        params = {"date": date}
        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch {source} for {date}")
            continue

        try:
            data = response.json()  # JSON形式で返ってくることを想定
        except Exception as e:
            print(f"Invalid JSON from {source} for {date}: {e}")
            continue

        # dataの構造は { "sections": [{"name": "1部", "available": true}, ...] } を想定
        for section in data.get("sections", []):
            section_name = section.get("name", "").strip()
            available = section.get("available", False)
            if available and section_name in VALID_SECTIONS:
                events.append({
                    "date": date,
                    "type": f"{section_name}○",
                    "source": source
                })
    return events


def main():
    all_events = []
    for source, api_url in API_URLS.items():
        events = fetch_events(source, api_url)
        all_events.extend(events)

    # JSON保存
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(all_events)} events.")


if __name__ == "__main__":
    main()
