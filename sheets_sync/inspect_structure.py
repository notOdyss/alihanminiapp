#!/usr/bin/env python3
"""
Скрипт для просмотра структуры Google Sheets таблицы
"""
import os
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

credentials_path = project_root / 'credentials/google-sheets-credentials.json'
spreadsheet_id = os.getenv('TRANSACTIONS_SPREADSHEET_ID')

scopes = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

creds = Credentials.from_service_account_file(str(credentials_path), scopes=scopes)
client = gspread.authorize(creds)

spreadsheet = client.open_by_key(spreadsheet_id)

# Лист "Платежи"
print("\n" + "="*80)
print("СТРУКТУРА ЛИСТА 'Платежи'")
print("="*80)

worksheet = spreadsheet.worksheet('Платежи')
headers = worksheet.row_values(1)

print(f"\nВсего колонок: {len(headers)}\n")

for i, header in enumerate(headers):
    print(f"{i:2d}. {header}")

# Показать несколько примеров данных
print("\n" + "="*80)
print("ПРИМЕРЫ ДАННЫХ (строки 2-5)")
print("="*80 + "\n")

for row_num in range(2, 6):
    row = worksheet.row_values(row_num)
    print(f"\n--- Строка {row_num} ---")
    for i, (header, value) in enumerate(zip(headers, row)):
        if value:  # Показываем только заполненные поля
            print(f"  {header}: {value}")

# Лист "Баланс"
print("\n" + "="*80)
print("СТРУКТУРА ЛИСТА 'Баланс'")
print("="*80)

balance_sheet = spreadsheet.worksheet('Баланс')
balance_headers = balance_sheet.row_values(1)

print(f"\nВсего колонок: {len(balance_headers)}\n")

for i, header in enumerate(balance_headers):
    print(f"{i:2d}. {header}")

print("\n" + "="*80)
print("ПРИМЕРЫ ДАННЫХ БАЛАНСА (строки 2-4)")
print("="*80 + "\n")

for row_num in range(2, 5):
    row = balance_sheet.row_values(row_num)
    print(f"\n--- Строка {row_num} ---")
    for i, (header, value) in enumerate(zip(balance_headers, row)):
        if value:
            print(f"  {header}: {value}")
