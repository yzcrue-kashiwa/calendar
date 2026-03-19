from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

# -----------------------------
# ChromeDriver 設定（ヘッドレス）
# -----------------------------
chrome_options = Options()
chrome_options.add_argument("--headless")  # ヘッドレスモード
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
service = Service()  # chromedriver が PATH にある場合

driver = webdriver.Chrome(service=service, options=chrome_options)
wait = WebDriverWait(driver, 10)

all_events = []

# -----------------------------
# 各サイトを処理
# -----------------------------
for site in SITES:
    driver.get(site["url"])
    
    # ページ内のカレンダーや日付が読み込まれるまで待機
    # ここでは例として「予約ボタンや日付セルが出るまで待つ」
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".reserve-day, .day, button")))
    except:
        print(f"サイト {site['source']} の読み込みに失敗")
        continue

    # 日付セル取得
    day_elements = driver.find_elements(By.CSS_SELECTOR, ".reserve-day, .day, button")

    for day_el in day_elements:
        # 日付テキストを取得（YYYY-MM-DD形式に変換）
        date_text = day_el.get_attribute("data-date") or day_el.text
        if not date_text:
            continue
        try:
            date_obj = datetime.datetime.strptime(date_text.strip(), "%Y-%m-%d")
        except:
            continue  # 日付でないセルはスキップ

        # 各部の情報を取得
        part_elements = day_el.find_elements(By.CSS_SELECTOR, ".part, .time-slot, button")
        for part_el in part_elements:
            part_text = part_el.text.strip()
            for valid in VALID_PARTS:
                if valid in part_text and "○" in part_text:
                    all_events.append({
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "type": part_text,
                        "source": site["source"]
                    })

driver.quit()

# -----------------------------
# JSON 保存
# -----------------------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_events, f, ensure_ascii=False, indent=2)

print(f"Saved {len(all_events)} events.")
