import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def fix_schema():
    if not DATABASE_URL:
        print("DATABASE_URL is not set")
        return

    engine = create_async_engine(DATABASE_URL)
    try:
        async with engine.begin() as conn:
            print("🚀 Starting schema migration...")
            
            # List of columns to update in sheet_transactions
            columns = [
                "amount_gross",
                "ali_commission",
                "p2p_commission",
                "paypal_commission",
                "paypal_withdrawal_commission",
                "withdrawal_amount"
            ]
            
            for col in columns:
                print(f"Updating {col} to DECIMAL(18, 2)...")
                await conn.execute(text(f"ALTER TABLE sheet_transactions ALTER COLUMN {col} TYPE DECIMAL(18, 2);"))

            # Also update balances tables
            print("Updating balances_paypal.balance...")
            await conn.execute(text("ALTER TABLE balances_paypal ALTER COLUMN balance TYPE DECIMAL(18, 2);"))
            
            print("Updating balances_stripe.balance...")
            await conn.execute(text("ALTER TABLE balances_stripe ALTER COLUMN balance TYPE DECIMAL(18, 2);"))
            
            print("Updating balances_paypal_withdrawal.withdrawal_amount...")
            await conn.execute(text("ALTER TABLE balances_paypal_withdrawal ALTER COLUMN withdrawal_amount TYPE DECIMAL(18, 2);"))
            
            print("Updating client_thresholds...")
            await conn.execute(text("ALTER TABLE client_thresholds ALTER COLUMN total_earnings TYPE DECIMAL(18, 2);"))
            await conn.execute(text("ALTER TABLE client_thresholds ALTER COLUMN threshold_amount TYPE DECIMAL(18, 2);"))
            
            print("✅ Schema migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_schema())
