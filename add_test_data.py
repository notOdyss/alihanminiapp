import asyncio
import os
import random
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def add_volume():
    if not DATABASE_URL:
        print("DATABASE_URL is not set")
        return

    engine = create_async_engine(DATABASE_URL)
    try:
        async with engine.begin() as conn:
            # Generate random IDs to avoid conflicts
            fake_id = random.randint(900000, 999999)
            
            query = text("""
                INSERT INTO sheet_transactions (
                    client_username,
                    transaction_date,
                    payment_id,
                    amount_gross,
                    withdrawal_amount,
                    payment_system,
                    buyer_email,
                    sheet_row_number,
                    withdrawal_received,
                    credential_type,
                    intermediary_status
                ) VALUES (
                    '@notodyss',
                    CURRENT_DATE,
                    :payment_id,
                    1100.00,
                    1100.00,
                    'PayPal',
                    'test_buyer@example.com',
                    :row_num,
                    TRUE,
                    'TEST',
                    'received'
                )
            """)
            
            await conn.execute(query, {
                "payment_id": fake_id,
                "row_num": fake_id
            })
            print(f"✅ Added $1100 transaction for @notodyss (ID: {fake_id})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_volume())
