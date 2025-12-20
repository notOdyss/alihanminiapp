#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подключения к Google Sheets
"""
import os
import sys
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Загрузка переменных окружения
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

def test_google_sheets_connection():
    """Проверка подключения к Google Sheets"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ К GOOGLE SHEETS")
    print("=" * 60)

    # Проверка наличия файла credentials
    credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', './credentials/google-sheets-credentials.json')
    credentials_full_path = project_root / credentials_path.lstrip('./')

    print(f"\n1. Проверка файла credentials...")
    print(f"   Путь: {credentials_full_path}")

    if not credentials_full_path.exists():
        print(f"   ❌ ОШИБКА: Файл не найден!")
        print(f"\n   Пожалуйста, поместите JSON файл с credentials в:")
        print(f"   {credentials_full_path}")
        print(f"\n   Инструкции см. в GOOGLE_SHEETS_SETUP.md")
        return False

    print(f"   ✅ Файл найден!")

    # Проверка переменных окружения
    print(f"\n2. Проверка переменных окружения...")
    transactions_id = os.getenv('TRANSACTIONS_SPREADSHEET_ID')
    balances_id = os.getenv('BALANCES_SPREADSHEET_ID')

    if not transactions_id:
        print(f"   ❌ ОШИБКА: TRANSACTIONS_SPREADSHEET_ID не установлен в .env")
        return False
    print(f"   ✅ TRANSACTIONS_SPREADSHEET_ID: {transactions_id}")

    if not balances_id:
        print(f"   ⚠️  ПРЕДУПРЕЖДЕНИЕ: BALANCES_SPREADSHEET_ID не установлен (не обязательно)")
    else:
        print(f"   ✅ BALANCES_SPREADSHEET_ID: {balances_id}")

    # Подключение к Google Sheets
    print(f"\n3. Подключение к Google Sheets API...")
    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]

        creds = Credentials.from_service_account_file(
            str(credentials_full_path),
            scopes=scopes
        )
        client = gspread.authorize(creds)
        print(f"   ✅ Успешно авторизованы!")

    except Exception as e:
        print(f"   ❌ ОШИБКА при авторизации: {e}")
        return False

    # Проверка доступа к таблице транзакций
    print(f"\n4. Проверка доступа к таблице транзакций...")
    try:
        spreadsheet = client.open_by_key(transactions_id)
        print(f"   ✅ Доступ получен!")
        print(f"   📊 Название таблицы: {spreadsheet.title}")

        # Список листов
        worksheets = spreadsheet.worksheets()
        print(f"   📄 Листы в таблице:")
        for ws in worksheets:
            row_count = ws.row_count
            col_count = ws.col_count
            print(f"      - {ws.title} ({row_count} строк × {col_count} столбцов)")

        # Чтение первых нескольких строк из первого листа
        if worksheets:
            first_sheet = worksheets[0]
            print(f"\n   📝 Первые 3 строки из листа '{first_sheet.title}':")
            values = first_sheet.get_all_values()[:3]
            for i, row in enumerate(values, 1):
                # Показываем только первые 5 колонок для краткости
                row_preview = row[:5]
                print(f"      Строка {i}: {row_preview}")

    except gspread.exceptions.SpreadsheetNotFound:
        print(f"   ❌ ОШИБКА: Таблица не найдена!")
        print(f"   Проверьте TRANSACTIONS_SPREADSHEET_ID в .env")
        return False
    except gspread.exceptions.APIError as e:
        print(f"   ❌ ОШИБКА API: {e}")
        print(f"   Возможно, Service Account не имеет доступа к таблице.")
        print(f"   Убедитесь что вы поделились таблицей с Service Account email")
        return False
    except Exception as e:
        print(f"   ❌ ОШИБКА: {e}")
        return False

    # Проверка доступа к таблице балансов (если указана)
    if balances_id:
        print(f"\n5. Проверка доступа к таблице балансов...")
        try:
            spreadsheet = client.open_by_key(balances_id)
            print(f"   ✅ Доступ получен!")
            print(f"   📊 Название таблицы: {spreadsheet.title}")

            worksheets = spreadsheet.worksheets()
            print(f"   📄 Листы в таблице:")
            for ws in worksheets:
                print(f"      - {ws.title}")

        except Exception as e:
            print(f"   ⚠️  ОШИБКА при доступе к таблице балансов: {e}")
            print(f"   (Это не критично, можно продолжать)")

    print(f"\n{'=' * 60}")
    print(f"✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
    print(f"{'=' * 60}")
    print(f"\nМожно переходить к синхронизации данных.")
    print(f"Запустите: python3 sheets_sync/sync_service.py")
    print(f"")

    return True

if __name__ == '__main__':
    success = test_google_sheets_connection()
    sys.exit(0 if success else 1)
