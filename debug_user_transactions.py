import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def check_user_transactions():
    if not DATABASE_URL:
        print("DATABASE_URL is not set")
        return

    engine = create_async_engine(DATABASE_URL)
    try:
        async with engine.begin() as conn:
            print("🔍 Searching for 'thxfortheslapali'...")
            
            # Check exact match
            result = await conn.execute(text("SELECT COUNT(*) FROM sheet_transactions WHERE client_username = '@notodyss'"))
            count = result.scalar()
            print(f"Total rows (@thxfortheslapali): {count}")

            # Check rows with date
            result = await conn.execute(text("SELECT COUNT(*) FROM sheet_transactions WHERE client_username = '@thxfortheslapali' AND transaction_date IS NOT NULL"))
            count_dates = result.scalar()
            print(f"Rows with valid date: {count_dates}")

            # Check withdrawal_received (for access)
            result = await conn.execute(text("SELECT COUNT(*) FROM sheet_transactions WHERE client_username = '@thxfortheslapali' AND withdrawal_received = TRUE"))
            count_received = result.scalar()
            print(f"Rows with withdrawal_received=TRUE: {count_received}")

            # Check sample row
            result = await conn.execute(text("SELECT * FROM sheet_transactions WHERE client_username = '@thxfortheslapali' LIMIT 1"))
            row = result.fetchone()
            if row:
                print(f"Sample row: {row}")
            
            # Check fuzzy
            result = await conn.execute(text("SELECT DISTINCT client_username FROM sheet_transactions WHERE client_username ILIKE '%thxfortheslapali%'"))
            rows = result.fetchall()
            if rows:
                print("Found similar usernames:")
                for row in rows:
                    print(f" - {row[0]}")
            else:
                print("No similar usernames found.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_user_transactions())
