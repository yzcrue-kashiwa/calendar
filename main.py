# main.py
import json
from datetime import datetime, timedelta

# JSONデータ読み込み（実際はスクレイピングしたデータを使う）
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 今日から10日間
start_date = datetime.today()
dates = [(start_date + timedelta(days=i)).date() for i in range(10)]

# 日付ごとに空き枠だけ整理
calendar_data = {d.isoformat(): [] for d in dates}

for event in data:
    if "貸切" in event["type"]:
        continue  # 貸切は無視
    if "○" in event["type"]:
        event_date = event["date"]
        if event_date in calendar_data:
            calendar_data[event_date].append(f"{event['type']} ({event['source']})")

# HTML生成
html_head = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>空き枠カレンダー</title>
<style>
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #999; padding: 5px; text-align: center; vertical-align: top; }
th { background: #eee; }
td { min-width: 80px; height: 60px; }
.empty { color: #ccc; }
</style>
</head>
<body>
<h2>今日から10日間の空き枠カレンダー</h2>
<table>
<tr>
<th>月</th><th>火</th><th>水</th><th>木</th><th>金</th><th>土</th><th>日</th>
</tr>
"""

# カレンダー表示（10日間分）
# 月曜始まりに調整
first_day = dates[0].weekday()  # 月=0
rows = []
current_row = [""] * first_day

for d in dates:
    day_str = str(d.day)
    events = calendar_data[d.isoformat()]
    if events:
        cell = f"{day_str}<br>" + "<br>".join(events)
    else:
        cell = f"{day_str}<br><span class='empty'>空きなし</span>"
    current_row.append(cell)
    if len(current_row) == 7:
        rows.append(current_row)
        current_row = []

# 余りを最後の行に追加
if current_row:
    while len(current_row) < 7:
        current_row.append("")
    rows.append(current_row)

# HTMLテーブル出力
html_body = ""
for row in rows:
    html_body += "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>\n"

html_tail = """
</table>
</body>
</html>
"""

# ファイルに書き出し
with open("calendar.html", "w", encoding="utf-8") as f:
    f.write(html_head + html_body + html_tail)

print("calendar.html に出力しました。")
