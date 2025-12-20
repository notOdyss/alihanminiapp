import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def migrate():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found")
        return

    engine = create_async_engine(database_url, echo=True)

    print("Applying migration 009_optimize_username_search.sql...")
    
    with open("api/migrations/009_optimize_username_search.sql", "r") as f:
        sql = f.read()

    async with engine.begin() as conn:
        for statement in sql.split(';'):
            if statement.strip():
                await conn.execute(text(statement))
    
    print("Migration completed successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate())
