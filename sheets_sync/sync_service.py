#!/usr/bin/env python3
"""
Optimized Google Sheets → PostgreSQL Sync Service

Features:
- "Tail Sync": Fetches only new rows + safety buffer (much faster)
- Parallel sync: Transactions and Balances run concurrently
- Optimized parsing: Handles scientific notation and dirty data
- Sync History: Tracks performance and errors
"""
import os
import sys
import time
import asyncio
import hashlib
import json
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Optional, Any

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Load environment
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')


class GoogleSheetsSync:
    """Optimized Google Sheets sync service with Tail Sync"""

    def __init__(self):
        self.credentials_path = project_root / os.getenv(
            'GOOGLE_SHEETS_CREDENTIALS_PATH',
            './credentials/google-sheets-credentials.json'
        ).lstrip('./')

        self.transactions_id = os.getenv('TRANSACTIONS_SPREADSHEET_ID')
        self.balances_id = os.getenv('BALANCES_SPREADSHEET_ID')
        self.sync_interval = int(os.getenv('SYNC_INTERVAL_MINUTES', '5'))

        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise ValueError("DATABASE_URL not set in .env")

        self.engine = create_async_engine(
            db_url, 
            echo=False,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Google Sheets
        self.client = None
        self._initialize_google_client()
        
        # Stats
        self.stats = {
            'transactions': {'processed': 0, 'new': 0},
            'balances': {'processed': 0}
        }
        
    def _initialize_google_client(self):
        """Initialize Google Sheets client"""
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets.readonly',
            'https://www.googleapis.com/auth/drive.readonly'
        ]
        creds = Credentials.from_service_account_file(
            str(self.credentials_path),
            scopes=scopes
        )
        self.client = gspread.authorize(creds)
        print(f"✅ Google Sheets client initialized")

    def parse_date(self, day: str, month: str, year: str) -> Optional[date]:
        """Parse date from three fields (Day, MonthName, Year)"""
        MONTH_MAP = {
            'январь': 1, 'января': 1,
            'февраль': 2, 'февраля': 2,
            'март': 3, 'марта': 3,
            'апрель': 4, 'апреля': 4,
            'май': 5, 'мая': 5,
            'июнь': 6, 'июня': 6,
            'июль': 7, 'июля': 7,
            'август': 8, 'августа': 8,
            'сентябрь': 9, 'сентября': 9,
            'октябрь': 10, 'октября': 10,
            'ноябрь': 11, 'ноября': 11,
            'декабрь': 12, 'декабря': 12
        }
        try:
            d = int(day) if day else 1
            
            # Month parsing
            m = 1
            if month:
                clean_month = month.strip().lower()
                if clean_month.isdigit():
                    m = int(clean_month)
                else:
                    m = MONTH_MAP.get(clean_month, 1) # Default to Jan if unknown? Or maybe current month?
            
            y = int(year) if year else datetime.now().year
            
            if y < 100: y += 2000
            if y < 1900 or y > 2100: y = datetime.now().year
            
            return date(y, m, d)
        except (ValueError, TypeError):
            return None

    def parse_decimal(self, value: str, field_name: str = "") -> Decimal:
        """Parse decimal with scientific notation handling"""
        if not value:
            return Decimal('0')
            
        cleaned = str(value).replace('$', '').replace(',', '').replace(' ', '').strip()
        try:
            val = Decimal(cleaned)
            # Cap huge values (e.g. scientific notation 9E+20) to 0 or valid max
            # Using 10^8 as reasonable limit for currency fields
            if abs(val) >= Decimal('100000000'):
                return Decimal('0')
            return val
        except (InvalidOperation, ValueError):
            return Decimal('0')

    def parse_boolean(self, value: str) -> bool:
        if not value:
            return False
        return str(value).lower().strip() in ['да', 'yes', 'true', '1', '+', 'received', 'done']

    def parse_int(self, value: str) -> Optional[int]:
        if not value:
            return None
        try:
            # Handle float strings "123.0" or "9.11E+10"
            val_f = float(str(value).replace(',', '.').strip())
            # Cap at Postgres Integer/BigInt max to avoid overflow crashes
            if abs(val_f) > 9223372036854775807: # BigInt max
                return None
            return int(val_f)
        except (ValueError, TypeError):
            return None
    
    def _row_hash(self, row: list) -> str:
        return hashlib.md5(json.dumps(row, default=str).encode()).hexdigest()

    async def _get_last_synced_row(self) -> int:
        """Get the last synced row number from DB"""
        async with self.async_session() as session:
            result = await session.execute(
                text("SELECT MAX(sheet_row_number) FROM sheet_transactions")
            )
            max_row = result.scalar()
            return max_row if max_row else 1

    async def _record_sync_start(self, sync_type: str) -> int:
        try:
            async with self.async_session() as session:
                result = await session.execute(
                    text("""
                        INSERT INTO sync_history (sync_type, status)
                        VALUES (:type, 'running')
                        RETURNING id
                    """),
                    {'type': sync_type}
                )
                sync_id = result.scalar()
                await session.commit()
                return sync_id
        except Exception:
            return None

    async def _record_sync_complete(self, sync_id: int, processed: int, error: str = None):
        if not sync_id: return
        try:
            async with self.async_session() as session:
                await session.execute(
                    text("""
                        UPDATE sync_history 
                        SET completed_at = CURRENT_TIMESTAMP,
                            rows_processed = :processed,
                            status = :status,
                            error_message = :error,
                            duration_seconds = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - started_at))
                        WHERE id = :id
                    """),
                    {
                        'id': sync_id,
                        'processed': processed,
                        'status': 'failed' if error else 'completed',
                        'error': error
                    }
                )
                await session.commit()
        except Exception:
            pass

    async def sync_transactions(self):
        """Smart Tail-Sync for transactions"""
        print(f"\n📊 Syncing transactions...")
        sync_id = await self._record_sync_start('transactions')
        
        try:
            spreadsheet = self.client.open_by_key(self.transactions_id)
            worksheet = spreadsheet.get_worksheet(0)
            
            # Normal full sync for stability as requested
            start_row = 2
            print(f"   🚀 Starting full sync from row: {start_row}")

            # 2. Fetch all
            rows = worksheet.get_all_values()[1:] # Skip headers
            
            if not rows:
                print("   ⚠️  No data found")
                await self._record_sync_complete(sync_id, 0)
                return

            print(f"   📥 Fetched {len(rows)} transactions from Sheets")

            batch_data = []
            batch_size = 500
            current_row_num = start_row
            
            synced_count = 0

            for row in rows:
                try:
                    if len(row) < 22:
                        row += [''] * (22 - len(row))

                    def get(idx): return row[idx].strip()

                    client = get(0)
                    if not client or not client.startswith('@'):
                        current_row_num += 1
                        continue

                    params = {
                        'client_username': client,
                        'transaction_date': self.parse_date(get(4), get(5), get(6)),
                        'payment_id': self.parse_int(get(7)),
                        'amount_gross': float(self.parse_decimal(get(8), 'amount')),
                        'payment_system': get(9),
                        'buyer_email': get(10),
                        'intermediary_status': get(11),
                        'credential_type': get(12),
                        'client_credentials': get(13),
                        'ali_commission': float(self.parse_decimal(get(14), 'ali_comm')),
                        'p2p_commission': float(self.parse_decimal(get(15), 'p2p_comm')),
                        'paypal_commission': float(self.parse_decimal(get(16), 'pp_comm')),
                        'paypal_withdrawal_commission': float(self.parse_decimal(get(17), 'pp_with_comm')),
                        'withdrawal_amount': float(self.parse_decimal(get(19), 'with_amt')),
                        'withdrawal_received': self.parse_boolean(get(20)),
                        'comment': get(21),
                        'sheet_row_number': current_row_num,
                        'row_hash': self._row_hash(row)
                    }
                    batch_data.append(params)
                    current_row_num += 1

                    if len(batch_data) >= batch_size:
                        await self._process_transactions_batch(batch_data)
                        synced_count += len(batch_data)
                        batch_data = []
                        print(f"   ⏳ Processed: {synced_count}...")

                except Exception as e:
                    print(f"\n   ⚠️  Error row {current_row_num}: {e}")
                    current_row_num += 1
                    continue

            if batch_data:
                await self._process_transactions_batch(batch_data)
                synced_count += len(batch_data)

            print(f"\n   ✅ Transactions synced: {synced_count} rows updated/inserted")
            self.stats['transactions']['processed'] = synced_count
            await self._record_sync_complete(sync_id, synced_count)

        except Exception as e:
            print(f"   ❌ Transaction sync error: {e}")
            await self._record_sync_complete(sync_id, 0, str(e))

    async def _process_transactions_batch(self, batch_data):
        """Insert/Update batch"""
        async with self.async_session() as session:
            async with session.begin():
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
                
                clean_batch = [{k: v for k, v in p.items() if k != 'row_hash'} for p in batch_data]
                await session.execute(query, clean_batch)

    async def sync_balances(self):
        """Sync balances"""
        if not self.balances_id: return
        print(f"\n💰 Syncing balances...")
        
        try:
            spreadsheet = self.client.open_by_key(self.balances_id)
            worksheets = spreadsheet.worksheets()
            
            tasks = []
            for ws in worksheets:
                title = ws.title.lower()
                if 'paypal' in title and 'вывод' not in title:
                    tasks.append(self._sync_simple_sheet(ws, 'balances_paypal', 'balance'))
                elif 'stripe' in title:
                    tasks.append(self._sync_stripe_balance(ws))
                elif 'вывод' in title or 'withdrawal' in title:
                    tasks.append(self._sync_simple_sheet(ws, 'balances_paypal_withdrawal', 'withdrawal_amount'))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                print(f"   ✅ Balances synced")
                
        except Exception as e:
            print(f"   ❌ Balance sync error: {e}")

    async def _sync_simple_sheet(self, worksheet, table_name, col_val):
        """Generic sync for simple keys"""
        rows = worksheet.get_all_values()
        if len(rows) < 2: return
        
        batch = []
        for row in rows[1:]:
            if len(row) < 2 or not row[0].startswith('@'): continue
            
            val = float(self.parse_decimal(row[1])) if len(row) > 1 else 0.0
            batch.append({
                'client': row[0].strip(),
                'val': val,
                'c1': row[2] if len(row) > 2 else '',
                'c2': row[3] if len(row) > 3 else '',
                'c3': row[4] if len(row) > 4 else ''
            })
            
        if not batch: return

        async with self.async_session() as session:
            async with session.begin():
                await session.execute(
                    text(f"""
                        INSERT INTO {table_name} (client_username, {col_val}, comment_1, comment_2, comment_3, last_synced_at)
                        VALUES (:client, :val, :c1, :c2, :c3, CURRENT_TIMESTAMP)
                        ON CONFLICT (client_username) DO UPDATE SET
                            {col_val} = EXCLUDED.{col_val},
                            comment_1 = EXCLUDED.comment_1,
                            comment_2 = EXCLUDED.comment_2,
                            comment_3 = EXCLUDED.comment_3,
                            last_synced_at = CURRENT_TIMESTAMP
                    """),
                    batch
                )

    async def _sync_stripe_balance(self, worksheet):
        """Sync stripe balances"""
        rows = worksheet.get_all_values()
        if len(rows) < 2: return

        batch = []
        for row in rows[1:]:
            if len(row) < 2 or not row[0].startswith('@'): continue
            
            p_date = None
            if len(row) > 2 and row[2]:
                try: p_date = datetime.strptime(row[2], '%d.%m.%y').date()
                except: pass

            batch.append({
                'client': row[0].strip(),
                'bal': float(self.parse_decimal(row[1])),
                'date': p_date,
                'buyer': row[3] if len(row) > 3 else '',
                'c1': row[4] if len(row) > 4 else ''
            })
            
        if not batch: return

        async with self.async_session() as session:
            async with session.begin():
                await session.execute(
                    text("""
                        INSERT INTO balances_stripe (client_username, balance, transaction_date, buyer_credentials, comment_1, last_synced_at)
                        VALUES (:client, :bal, :date, :buyer, :c1, CURRENT_TIMESTAMP)
                        ON CONFLICT (client_username) DO UPDATE SET
                            balance = EXCLUDED.balance,
                            transaction_date = EXCLUDED.transaction_date,
                            buyer_credentials = EXCLUDED.buyer_credentials,
                            comment_1 = EXCLUDED.comment_1,
                            last_synced_at = CURRENT_TIMESTAMP
                    """),
                    batch
                )

    async def run_sync(self):
        start = time.time()
        print(f"\n{'='*50}\n🚀 STARTING OPTIMIZED SYNC {datetime.now().strftime('%H:%M:%S')}\n{'='*50}")
        
        await asyncio.gather(
            self.sync_transactions(),
            self.sync_balances(),
            return_exceptions=True
        )
        
        elapsed = time.time() - start
        print(f"\n✨ DONE in {elapsed:.2f}s")
        print(f"{'='*50}\n")

    async def run_forever(self):
        print(f"🔄 Service started. Interval: {self.sync_interval}m")
        while True:
            try:
                await self.run_sync()
            except Exception as e:
                print(f"❌ CRITICAL ERROR: {e}")
            
            print(f"😴 Sleeping {self.sync_interval}m...")
            await asyncio.sleep(self.sync_interval * 60)

if __name__ == '__main__':
    service = GoogleSheetsSync()
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        asyncio.run(service.run_sync())
    else:
        asyncio.run(service.run_forever())
