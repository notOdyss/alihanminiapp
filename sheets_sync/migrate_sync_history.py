#!/usr/bin/env python3
"""Run sync_history migration"""
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os

load_dotenv(Path(__file__).parent.parent / '.env')

async def run_migration():
    engine = create_async_engine(os.getenv('DATABASE_URL'))
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sync_history (
                id SERIAL PRIMARY KEY,
                sync_type VARCHAR(50) NOT NULL,
                started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP WITH TIME ZONE,
                rows_processed INT DEFAULT 0,
                rows_changed INT DEFAULT 0,
                status VARCHAR(20) DEFAULT 'running',
                error_message TEXT,
                duration_seconds DECIMAL(10, 2)
            )
        """))
        await conn.execute(text('CREATE INDEX IF NOT EXISTS idx_sync_history_started ON sync_history(started_at DESC)'))
        await conn.execute(text('CREATE INDEX IF NOT EXISTS idx_sync_history_type ON sync_history(sync_type, started_at DESC)'))
    print('✅ sync_history table created')
    await engine.dispose()

if __name__ == '__main__':
    asyncio.run(run_migration())
