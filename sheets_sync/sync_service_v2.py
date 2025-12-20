#!/usr/bin/env python3
"""
Сервис синхронизации данных из Google Sheets в PostgreSQL (v2 - обновленный)
"""
import os
import sys
import time
import asyncio
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')


class GoogleSheetsSync:
    """Класс для синхронизации данных из Google Sheets"""

    def __init__(self):
        self.credentials_path = project_root / os.getenv(
            'GOOGLE_SHEETS_CREDENTIALS_PATH',
            './credentials/google-sheets-credentials.json'
        ).lstrip('./')

        self.spreadsheet_id = os.getenv('TRANSACTIONS_SPREADSHEET_ID')
        self.sync_interval = int(os.getenv('SYNC_INTERVAL_MINUTES', '5'))

        # PostgreSQL
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL not set in .env")

        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

        # Google Sheets client
        self.client = None
        self._initialize_google_client()

    def _initialize_google_client(self):
        """Инициализация Google Sheets клиента"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]

        creds = Credentials.from_service_account_file(
            str(self.credentials_path),
            scopes=scopes
        )
        self.client = gspread.authorize(creds)
        print(f"✅ Google Sheets client инициализирован")

    def parse_month(self, month_str: str) -> Optional[int]:
        """Парсинг месяца из русского названия"""
        months = {
            'январь': 1, 'февраль': 2, 'март': 3, 'апрель': 4,
            'май': 5, 'июнь': 6, 'июль': 7, 'август': 8,
            'сентябрь': 9, 'октябрь': 10, 'ноябрь': 11, 'декабрь': 12
        }

        if not month_str:
            return None

        month_lower = str(month_str).lower().strip()
        return months.get(month_lower)

    def parse_date(self, day: str, month: str, year: str) -> Optional[date]:
        """Парсинг даты из трех полей"""
        try:
            d = int(day) if day else None
            m = self.parse_month(month)
            y = int(year) if year else None

            if not all([d, m, y]):
                return None

            # Если год двузначный, добавляем 2000
            if y < 100:
                y += 2000

            return date(y, m, d)
        except (ValueError, TypeError):
            return None

    def parse_decimal(self, value: str) -> Decimal:
        """Парсинг decimal значения из строки"""
        if not value:
            return Decimal('0')

        # Удаляем символы валюты, пробелы и заменяем запятую на точку
        cleaned = str(value).replace('$', '').replace(',', '.').replace(' ', '').strip()

        try:
            return Decimal(cleaned)
        except:
            return Decimal('0')

    def parse_boolean(self, value: str) -> bool:
        """Парсинг boolean значения"""
        if not value:
            return False

        value_lower = str(value).lower().strip()
        return value_lower in ['да', 'yes', 'true', '1', '+']

    async def sync_transactions(self):
        """Синхронизация транзакций из листа 'Платежи'"""
        print(f"\n📊 Синхронизация транзакций...")

        try:
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet('Платежи')

            # Получаем все данные
            all_values = worksheet.get_all_values()

            if len(all_values) < 2:
                print(f"⚠️  Таблица пустая или только заголовки")
                return

            # Пропускаем заголовки
            data_rows = all_values[1:]
            print(f"   Найдено {len(data_rows)} строк данных")

            async with self.async_session() as session:
                synced_count = 0
                skipped_count = 0

                for row_num, row in enumerate(data_rows, start=2):
                    try:
                        # Безопасное получение значений по индексу
                        def get_val(idx, default=''):
                            if idx >= len(row):
                                return default
                            val = row[idx]
                            return val.strip() if val else default

                        # Маппинг колонок (из inspect_structure.py)
                        client_username = get_val(0)  # Клиент
                        day = get_val(4)  # День
                        month = get_val(5)  # Месяц
                        year = get_val(6)  # Год
                        payment_id_str = get_val(7)  # ID платежа
                        amount_gross_str = get_val(8)  # Сумма платежа. $
                        payment_system = get_val(9)  # Платежная система
                        buyer_email = get_val(10)  # Реквизиты покупателя
                        intermediary_status = get_val(11)  # Платеж получен от Reco/Corey/Ali?
                        credential_type = get_val(12)  # Тип реквизитов
                        client_credentials = get_val(13)  # Реквизиты клиента
                        ali_commission_1_str = get_val(14)  # Комиссия Ali для клиента (первая)
                        ali_commission_2_str = get_val(15)  # Комиссия Ali для клиента (вторая)
                        p2p_commission_str = get_val(16)  # Комиссия P2P
                        paypal_commission_str = get_val(17)  # Комиссия PayPal
                        paypal_withdrawal_commission_str = get_val(18)  # Комиссия PayPal на вывод
                        withdrawal_amount_str = get_val(19)  # Сумма вывода клиенту. $
                        withdrawal_received_str = get_val(20)  # Клиент получил вывод?
                        comment = get_val(21)  # Комментарий

                        # Пропускаем строки без клиента
                        if not client_username or not client_username.startswith('@'):
                            skipped_count += 1
                            continue

                        # Парсим данные
                        transaction_date = self.parse_date(day, month, year)
                        payment_id = int(payment_id_str) if payment_id_str and payment_id_str.isdigit() else None
                        amount_gross = self.parse_decimal(amount_gross_str)

                        # Комиссии (берем вторую комиссию Ali так как она более актуальная)
                        ali_commission = self.parse_decimal(ali_commission_2_str)
                        p2p_commission = self.parse_decimal(p2p_commission_str)
                        paypal_commission = self.parse_decimal(paypal_commission_str)
                        paypal_withdrawal_commission = self.parse_decimal(paypal_withdrawal_commission_str)
                        withdrawal_amount = self.parse_decimal(withdrawal_amount_str)
                        withdrawal_received = self.parse_boolean(withdrawal_received_str)

                        # Вставка или обновление
                        query = text("""
                            INSERT INTO sheet_transactions (
                                client_username, transaction_date, payment_id, amount_gross,
                                payment_system, buyer_email, intermediary_status, credential_type,
                                client_credentials, ali_commission, p2p_commission, paypal_commission,
                                paypal_withdrawal_commission, withdrawal_amount, withdrawal_received,
                                comment, sheet_row_number, last_synced_at
                            ) VALUES (
                                :client_username, :transaction_date, :payment_id, :amount_gross,
                                :payment_system, :buyer_email, :intermediary_status, :credential_type,
                                :client_credentials, :ali_commission, :p2p_commission, :paypal_commission,
                                :paypal_withdrawal_commission, :withdrawal_amount, :withdrawal_received,
                                :comment, :sheet_row_number, CURRENT_TIMESTAMP
                            )
                            ON CONFLICT (payment_id, client_username, sheet_row_number)
                            DO UPDATE SET
                                transaction_date = EXCLUDED.transaction_date,
                                amount_gross = EXCLUDED.amount_gross,
                                payment_system = EXCLUDED.payment_system,
                                buyer_email = EXCLUDED.buyer_email,
                                intermediary_status = EXCLUDED.intermediary_status,
                                credential_type = EXCLUDED.credential_type,
                                client_credentials = EXCLUDED.client_credentials,
                                ali_commission = EXCLUDED.ali_commission,
                                p2p_commission = EXCLUDED.p2p_commission,
                                paypal_commission = EXCLUDED.paypal_commission,
                                paypal_withdrawal_commission = EXCLUDED.paypal_withdrawal_commission,
                                withdrawal_amount = EXCLUDED.withdrawal_amount,
                                withdrawal_received = EXCLUDED.withdrawal_received,
                                comment = EXCLUDED.comment,
                                last_synced_at = CURRENT_TIMESTAMP
                        """)

                        await session.execute(query, {
                            'client_username': client_username,
                            'transaction_date': transaction_date,
                            'payment_id': payment_id,
                            'amount_gross': float(amount_gross),
                            'payment_system': payment_system,
                            'buyer_email': buyer_email,
                            'intermediary_status': intermediary_status,
                            'credential_type': credential_type,
                            'client_credentials': client_credentials,
                            'ali_commission': float(ali_commission),
                            'p2p_commission': float(p2p_commission),
                            'paypal_commission': float(paypal_commission),
                            'paypal_withdrawal_commission': float(paypal_withdrawal_commission),
                            'withdrawal_amount': float(withdrawal_amount),
                            'withdrawal_received': withdrawal_received,
                            'comment': comment,
                            'sheet_row_number': row_num
                        })

                        synced_count += 1

                        # Прогресс каждые 1000 строк
                        if synced_count % 1000 == 0:
                            print(f"   📝 Обработано {synced_count} транзакций...")

                    except Exception as e:
                        print(f"   ⚠️  Ошибка обработки строки {row_num}: {e}")
                        skipped_count += 1
                        continue

                await session.commit()
                print(f"   ✅ Синхронизировано: {synced_count}, пропущено: {skipped_count}")

        except Exception as e:
            print(f"   ❌ Ошибка синхронизации транзакций: {e}")
            raise

    async def sync_balances(self):
        """Синхронизация балансов из листа 'Баланс'"""
        print(f"\n💰 Синхронизация балансов...")

        try:
            spreadsheet = self.client.open_by_key(self.spreadsheet_id)
            worksheet = spreadsheet.worksheet('Баланс')

            all_values = worksheet.get_all_values()

            if len(all_values) < 2:
                print(f"⚠️  Лист балансов пустой")
                return

            data_rows = all_values[1:]  # Пропускаем заголовки

            async with self.async_session() as session:
                paypal_count = 0
                stripe_count = 0
                withdrawal_count = 0

                for row in data_rows:
                    if len(row) < 20:
                        continue

                    # PayPal баланс (колонки 0, 1-4)
                    paypal_client = row[0].strip() if len(row) > 0 else ''
                    if paypal_client and paypal_client.startswith('@'):
                        paypal_balance = self.parse_decimal(row[1] if len(row) > 1 else '0')
                        comment_1 = row[2] if len(row) > 2 else ''
                        comment_2 = row[3] if len(row) > 3 else ''
                        comment_3 = row[4] if len(row) > 4 else ''

                        query = text("""
                            INSERT INTO balances_paypal (client_username, balance, comment_1, comment_2, comment_3, last_synced_at)
                            VALUES (:client, :balance, :c1, :c2, :c3, CURRENT_TIMESTAMP)
                            ON CONFLICT (client_username)
                            DO UPDATE SET
                                balance = EXCLUDED.balance,
                                comment_1 = EXCLUDED.comment_1,
                                comment_2 = EXCLUDED.comment_2,
                                comment_3 = EXCLUDED.comment_3,
                                last_synced_at = CURRENT_TIMESTAMP
                        """)

                        await session.execute(query, {
                            'client': paypal_client,
                            'balance': float(paypal_balance),
                            'c1': comment_1,
                            'c2': comment_2,
                            'c3': comment_3
                        })
                        paypal_count += 1

                    # Stripe баланс (колонки 6, 7-11)
                    stripe_client = row[6].strip() if len(row) > 6 else ''
                    if stripe_client and stripe_client.startswith('@'):
                        stripe_balance = self.parse_decimal(row[7] if len(row) > 7 else '0')
                        trans_date_str = row[8] if len(row) > 8 else ''
                        buyer_creds = row[9] if len(row) > 9 else ''
                        comment_1 = row[10] if len(row) > 10 else ''

                        # Парсим дату (формат dd.mm.yy)
                        parsed_date = None
                        if trans_date_str:
                            try:
                                parsed_date = datetime.strptime(trans_date_str, '%d.%m.%y').date()
                            except:
                                parsed_date = None

                        query = text("""
                            INSERT INTO balances_stripe (client_username, balance, transaction_date, buyer_credentials, comment_1, last_synced_at)
                            VALUES (:client, :balance, :date, :buyer, :c1, CURRENT_TIMESTAMP)
                            ON CONFLICT (client_username)
                            DO UPDATE SET
                                balance = EXCLUDED.balance,
                                transaction_date = EXCLUDED.transaction_date,
                                buyer_credentials = EXCLUDED.buyer_credentials,
                                comment_1 = EXCLUDED.comment_1,
                                last_synced_at = CURRENT_TIMESTAMP
                        """)

                        await session.execute(query, {
                            'client': stripe_client,
                            'balance': float(stripe_balance),
                            'date': parsed_date,
                            'buyer': buyer_creds,
                            'c1': comment_1
                        })
                        stripe_count += 1

                    # PayPal Вывод (колонки 14, 15-18)
                    withdrawal_client = row[14].strip() if len(row) > 14 else ''
                    if withdrawal_client and withdrawal_client.startswith('@'):
                        withdrawal = self.parse_decimal(row[15] if len(row) > 15 else '0')
                        comment_1 = row[16] if len(row) > 16 else ''
                        comment_2 = row[17] if len(row) > 17 else ''
                        comment_3 = row[18] if len(row) > 18 else ''

                        query = text("""
                            INSERT INTO balances_paypal_withdrawal (client_username, withdrawal_amount, comment_1, comment_2, comment_3, last_synced_at)
                            VALUES (:client, :withdrawal, :c1, :c2, :c3, CURRENT_TIMESTAMP)
                            ON CONFLICT (client_username)
                            DO UPDATE SET
                                withdrawal_amount = EXCLUDED.withdrawal_amount,
                                comment_1 = EXCLUDED.comment_1,
                                comment_2 = EXCLUDED.comment_2,
                                comment_3 = EXCLUDED.comment_3,
                                last_synced_at = CURRENT_TIMESTAMP
                        """)

                        await session.execute(query, {
                            'client': withdrawal_client,
                            'withdrawal': float(withdrawal),
                            'c1': comment_1,
                            'c2': comment_2,
                            'c3': comment_3
                        })
                        withdrawal_count += 1

                await session.commit()
                print(f"   ✅ PayPal: {paypal_count}, Stripe: {stripe_count}, Выводы: {withdrawal_count}")

        except Exception as e:
            print(f"   ❌ Ошибка синхронизации балансов: {e}")

    async def run_sync(self):
        """Запуск синхронизации"""
        print(f"\n{'=' * 60}")
        print(f"🔄 НАЧАЛО СИНХРОНИЗАЦИИ - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'=' * 60}")

        try:
            await self.sync_transactions()
            await self.sync_balances()

            print(f"\n{'=' * 60}")
            print(f"✅ СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'=' * 60}\n")

        except Exception as e:
            print(f"\n{'=' * 60}")
            print(f"❌ ОШИБКА СИНХРОНИЗАЦИИ: {e}")
            print(f"{'=' * 60}\n")
            raise

    async def run_forever(self):
        """Запуск в бесконечном цикле"""
        print(f"🚀 Запуск сервиса синхронизации...")
        print(f"📊 Интервал: каждые {self.sync_interval} минут")
        print(f"📋 Spreadsheet ID: {self.spreadsheet_id}")
        print(f"\nPress Ctrl+C to stop\n")

        while True:
            try:
                await self.run_sync()
                print(f"⏳ Следующая синхронизация через {self.sync_interval} минут...")
                await asyncio.sleep(self.sync_interval * 60)

            except KeyboardInterrupt:
                print(f"\n⏹️  Остановка сервиса...")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                print(f"⏳ Повторная попытка через {self.sync_interval} минут...")
                await asyncio.sleep(self.sync_interval * 60)


async def main():
    """Главная функция"""
    sync_service = GoogleSheetsSync()

    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Разовая синхронизация
        await sync_service.run_sync()
    else:
        # Непрерывная синхронизация
        await sync_service.run_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n👋 Bye!")
        sys.exit(0)
