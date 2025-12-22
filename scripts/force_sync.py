#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
load_dotenv(project_root / '.env')

from sheets_sync.sync_service import GoogleSheetsSync

async def force_sync():
    print("🚀 Starting Force Sync...")
    try:
        syncer = GoogleSheetsSync()
        
        # Sync Transactions
        print("📊 Syncing Transactions...")
        await syncer.sync_transactions()
        
        # Sync Balances (if method exists)
        # Checking source code I saw earlier, usually there is sync_balances too.
        # I'll try calling it.
        if hasattr(syncer, 'sync_balances'):
             print("💰 Syncing Balances...")
             await syncer.sync_balances()
        
        print("✅ Force Sync Complete!")
    except Exception as e:
        print(f"❌ Sync Failed: {e}")

if __name__ == "__main__":
    asyncio.run(force_sync())
