import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
load_dotenv(project_root / '.env')

async def check_schema():
    db_url = os.getenv('DATABASE_URL')
    if not db_url: return
    engine = create_async_engine(db_url)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'sheet_transactions'"))
        print(f"Columns: {[r[0] for r in result]}")

if __name__ == '__main__':
    asyncio.run(check_schema())
