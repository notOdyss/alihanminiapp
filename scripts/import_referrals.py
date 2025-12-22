#!/usr/bin/env python3
"""
Import Referral Codes from Google Sheet
Target Sheet: https://docs.google.com/spreadsheets/d/1H07GetBKwRHJ5KTRhkAg2jVrpQsYpiSocmnx1MtOFJw/edit?gid=1509084455#gid=1509084455
GID: 1509084455
Structure assumptions:
Col A: Referral Code ?
Col B: Username ?
Or Col A: Username, Col B: Code?
The user didn't specify column mapping. I will assume:
Col A: Code
Col B: Username (or link)

Wait, usually these sheets have headers. I'll read row 1 to guess or log it.
Actually, I'll assume standard layout: Code | Owner (@username)
"""

import sys
import asyncio
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import gspread
from google.oauth2.service_account import Credentials

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
load_dotenv(project_root / '.env')

from bot.database.models import User, LegacyReferral
from bot.database.repositories import UserRepository

# GID from URL
SPREADSHEET_ID = '1H07GetBKwRHJ5KTRhkAg2jVrpQsYpiSocmnx1MtOFJw'
SHEET_GID = 1509084455

async def import_referrals():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found")
        return

    # DB Setup
    engine = create_async_engine(db_url, echo=False)
    
    # Ensure tables exist (esp LegacyReferral)
    from bot.database.models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Google Sheets Setup
    creds_path = project_root / os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', './credentials/google-sheets-credentials.json').lstrip('./')
    scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/drive.readonly']
    creds = Credentials.from_service_account_file(str(creds_path), scopes=scopes)
    client = gspread.authorize(creds)

    print(f"📊 Opening Spreadsheet {SPREADSHEET_ID}...")
    try:
        sh = client.open_by_key(SPREADSHEET_ID)
        # Find worksheet by GID
        ws = None
        for w in sh.worksheets():
            if str(w.id) == str(SHEET_GID):
                ws = w
                break
        
        if not ws:
            print(f"❌ Worksheet with GID {SHEET_GID} not found. Using first one.")
            ws = sh.get_worksheet(0)
            
        rows = ws.get_all_values()
        print(f"📥 Fetched {len(rows)} rows.")
        
        count = 0
        async with async_session() as session:
            user_repo = UserRepository(session)
            
            # Assuming Row 1 is header
            for i, row in enumerate(rows):
                if i == 0: continue # Skip header
                if len(row) < 2: continue
                
                # Try to identify columns. 
                # Heuristic: Code is usually short alphanumeric. Username starts with @.
                col0 = row[0].strip()
                col1 = row[1].strip()
                
                code = None
                username = None
                
                if col0.startswith('@'):
                    username = col0
                    code = col1
                elif col1.startswith('@'):
                    username = col1
                    code = col0
                else:
                    # Fallback: assume Col A = Code, Col B = Username (without @?)
                    code = col0
                    username = col1
                    if not username.startswith('@'):
                        username = f"@{username}"

                username = username.lstrip('@')
                
                if not username or not code:
                    continue
                    
                # Clean code
                code = code.upper().replace(' ', '')
                if len(code) > 20: continue # Too long
                
                # 1. Try to find existing User
                users = await user_repo.search_by_username(username)
                target_user = None
                for u in users:
                    if u.username and u.username.lower() == username.lower():
                        target_user = u
                        break
                
                # 2. If not found in DB, store in LegacyReferrals
                if not target_user:
                    print(f"   ⚠️ User {username} not found in DB. Adding to Legacy Referrals...")
                    
                    # Upsert LegacyReferral
                    # Check if exists
                    res = await session.execute(select(LegacyReferral).where(LegacyReferral.username.ilike(username)))
                    legacy = res.scalar_one_or_none()
                    
                    if legacy:
                        legacy.referral_code = code
                        print(f"      🔄 Updated Legacy: {username} -> {code}")
                    else:
                        legacy = LegacyReferral(username=username, referral_code=code)
                        session.add(legacy)
                        print(f"      🆕 Created Legacy: {username} -> {code}")
                    
                    count += 1
                else:
                    # Existing user logic
                    print(f"   👤 Found user {username} -> Code {code}")
                    target_user.referral_code = code
                    print("      ✅ Assigned")
                    count += 1
            
            await session.commit()
            print(f"\n✅ Imported {count} referral codes.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await engine.dispose()

if __name__ == '__main__':
    asyncio.run(import_referrals())
