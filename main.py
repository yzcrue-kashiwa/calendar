import requests
import json
from datetime import datetime, timedelta

OUTPUT_FILE = "events.json"

SITES = [
    {
        "name": "Couleur",
        "url": "https://couleur.studio-colore.tokyo/wp-admin/admin-ajax.php"
    },
    {
        "name": "Claris",
        "url": "https://claris-studio-colore-mixbox.com/wp-admin/admin-ajax.php"
    }
]

VALID_PARTS = ["1部", "2部"]
DAYS = 10


def fetch(site):
    results = []

    for i in range(DAYS):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")

        payload = {
            "action": "get_reserve_data",  # ←ここ後で変える可能性あり
            "date": date
        }

        try:
            res = requests.post(site["url"], data=payload, timeout=10)
        except Exception as e:
            print("request error:", e)
            continue

        # JSONかチェック
        if "application/json" not in res.headers.get("Content-Type", ""):
            print(f"[{site['name']}] JSONじゃない → {date}")
            continue

        try:
            data = res.json()
        except:
            print(f"[{site['name']}] JSONパース失敗 → {date}")
            continue

        # 構造は仮（ここ調整ポイント）
        for item in data.get("data", []):
            text = item.get("label", "").strip()

            for part in VALID_PARTS:
                if part in text and "○" in text:
                    results.append({
                        "date": date,
                        "type": f"{part}○",
                        "source": site["name"]
                    })

    return results


def main():
    all_events = []

    for site in SITES:
        print("fetch:", site["name"])
        events = fetch(site)
        all_events.extend(events)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_events, f, ensure_ascii=False, indent=2)

    print("Saved", len(all_events), "events")


if __name__ == "__main__":
    main()
