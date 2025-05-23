import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import csv
import re

SPREADSHEET_ID = "1BFsLgq_23b14JUMax3g3J65eDGO6OjxgW9ptxB0VW20"
SHEET_NAME = "進捗状況"


def authorize():
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json', scope)
    return gspread.authorize(creds)


def get_user_list(sheet):
    j_values = sheet.col_values(10)[1:]
    return sorted(set(name.strip() for name in j_values if name.strip()))


def run_script(user_name):
    client = authorize()
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

    # --- 優先度の行を探す ---
    l_values = sheet.col_values(12)  # L列

    target_row = next((idx for idx, val in enumerate(
        l_values[1:], start=2) if val == "最優先"), None)
    if not target_row:
        target_row = next((idx for idx, val in enumerate(
            l_values[1:], start=2) if val == "優先"), None)

    if not target_row:
        return "⚠️ 『最優先』『優先』タスクが見つかりませんでした。"

    # 日付を datetime オブジェクトで入力
    sheet.update_cell(target_row, 6, datetime.now().strftime("%Y-%m-%d"))
    sheet.update_cell(target_row, 10, user_name)
    sheet.update_cell(target_row, 12, "編集中")

    title = sheet.cell(target_row, 2).value.strip()
    filename = f"{title}_台本.csv"

    url = sheet.cell(target_row, 8).value
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
    if not match:
        return "⚠️ H列のURLからスプレッドシートIDを取得できませんでした。"

    sub_sheet = client.open_by_key(match.group(1)).worksheet("４台本")
    a_values = sub_sheet.col_values(1)[2:]
    b_values = sub_sheet.col_values(2)[2:]
    max_len = max(len(a_values), len(b_values))
    rows = [(a_values[i] if i < len(a_values) else "", b_values[i]
             if i < len(b_values) else "") for i in range(max_len)]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["台詞", "キャラクター"])
        writer.writerows(rows)

    return f"✅ 『{filename}』として台本CSVを出力しました。"
