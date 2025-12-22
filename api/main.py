#!/usr/bin/env python3
"""
FastAPI сервер для webapp
Отдает данные из PostgreSQL (синхронизированные из Google Sheets)
"""
import os
import hmac
import hashlib
import json
import urllib.parse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from decimal import Decimal

import sentry_sdk
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, func

from bot.database.repositories import UserRepository, TransactionRepository
from bot.services.logger import telegram_logger

# Загрузка переменных окружения
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

# --- CONFIGURATION & MONITORING ---
SENTRY_DSN = os.getenv('SENTRY_DSN')
if SENTRY_DSN:
    pass
    # sentry_sdk.init(
    #     dsn=SENTRY_DSN,
    #     traces_sample_rate=1.0,
    #     profiles_sample_rate=1.0,
    # )

# Создание FastAPI приложения
app = FastAPI(title="AlihanBot API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Dependency для получения сессии БД
async def get_db():
    async with async_session_maker() as session:
        yield session


# Pydantic models для ответов API
class BalanceResponse(BaseModel):
    total: float
    paypal: float
    stripe: float
    withdrawal: float


class StatisticsResponse(BaseModel):
    avgCheck: float
    totalChecks: int
    totalSum: float
    avgChecksMonth: float
    avgSumMonth: float


class Transaction(BaseModel):
    id: int
    payment_method: str
    amount: float
    created_at: str
    status: str


class TransactionsResponse(BaseModel):
    transactions: List[Transaction]
    total: int


# Утилиты
# Robust Username Extraction
def get_username_from_telegram_user(user_data: dict) -> Optional[str]:
    """Helper to extract and normalize username"""
    username = user_data.get('username')
    if not username:
        return None
    
    # Store clean version
    clean_username = username.strip()
    if not clean_username.startswith('@'):
        clean_username = f"@{clean_username}"
    
    return clean_username

def validate_telegram_data(init_data: str, bot_token: str) -> bool:
    """
    Валидация данных от Telegram.
    Проверяет hash на основе BOT_TOKEN.
    """
    try:
        if not bot_token:
            return False

        vals = urllib.parse.parse_qs(init_data)
        if 'hash' not in vals:
            return False

        data_check_string = "\n".join([
            f"{k}={v[0]}" for k, v in sorted(vals.items()) if k != 'hash'
        ])

        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256
        ).digest()

        h = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        return h == vals['hash'][0]
    except Exception as e:
        print(f"Validation error: {e}")
        return False

def parse_telegram_init_data(init_data: str) -> dict:
    """Парсинг Telegram initData для получения user ID с валидацией"""
    # 1. Получаем токен бота
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # 2. Если токена нет - отключаем валидацию (ТОЛЬКО ДЛЯ DEV/TEST)
    if not BOT_TOKEN:
        print("WARNING: BOT_TOKEN not set, skipping validation")
    else:
        # Check for mock data (localhost dev bypass)
        vals = urllib.parse.parse_qs(init_data)
        if vals.get('hash', [''])[0] == 'mock_hash' and 'mock_local_dev_data' in init_data:
             print("WARNING: Mock data detected, skipping validation")
        else:
            is_valid = validate_telegram_data(init_data, BOT_TOKEN)
            if not is_valid:
                print(f"Validation failed for init_data: {init_data[:50]}...")
                raise HTTPException(status_code=401, detail="Invalid Telegram data hash. Authentication failed.")
            
    # 3. Парсим данные
    try:
        parts = init_data.split('&')
        user_data = {}
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                if key == 'user':
                    user_json = urllib.parse.unquote(value)
                    user_data = json.loads(user_json)
                    break
        return user_data
    except Exception as e:
        print(f"Error parsing init data: {e}")
        return {}

async def check_client_access(username: str, db: AsyncSession, user_id: int) -> bool:
    """Check if client has access based on threshold or admin status"""
    # Access threshold logic
    # Admin check
    admin_ids = eval(os.getenv('ADMIN_IDS', '[]'))
    if user_id in admin_ids:
        return True

    # Blocked check
    user_query = text("SELECT is_blocked FROM users WHERE id = :user_id")
    user_result = await db.execute(user_query, {"user_id": user_id})
    user_row = user_result.fetchone()
    if user_row and user_row[0]:
        return False

    # User threshold check
    query = text("""
        SELECT can_view_data
        FROM client_thresholds
        WHERE LOWER(client_username) = LOWER(:username)
    """)
    
    result = await db.execute(query, {"username": username})
    row = result.fetchone()

    if row and row[0]:
        return True

    # Volume check
    earnings_query = text("""
        SELECT COALESCE(SUM(withdrawal_amount), 0)
        FROM sheet_transactions
        WHERE LOWER(client_username) = LOWER(:username)
          AND withdrawal_received = TRUE
    """)

    earnings_result = await db.execute(earnings_query, {"username": username})
    total_earnings = float(earnings_result.scalar() or 0.0)
    
    return total_earnings >= 0.0 # Allow for now but track volume


class EventRequest(BaseModel):
    type: str
    data: Optional[Dict[str, Any]] = None


@app.post("/api/events")
async def track_event(
    event: EventRequest,
    x_telegram_init_data: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Track WebApp events (e.g., session_start)"""
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Telegram init data required")

    user_data = parse_telegram_init_data(x_telegram_init_data)
    user_id = user_data.get('id')
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found")

    if event.type == 'session_start':
        user_repo = UserRepository(db)
        # Create user if not exists (using a mock object that mimics aiogram User)
        class TgUserMock:
            def __init__(self, data):
                self.id = data.get('id')
                self.username = data.get('username')
                self.first_name = data.get('first_name')
                self.last_name = data.get('last_name')
                self.language_code = data.get('language_code')
                self.is_premium = data.get('is_premium', False)
        
        await user_repo.get_or_create(TgUserMock(user_data))
        await user_repo.update_webapp_visit(user_id)
        
    return {"status": "ok"}


# API Endpoints
@app.get("/api/balance", response_model=BalanceResponse)
async def get_balance(
    x_telegram_init_data: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Получить балансы клиента"""
    # Парсим Telegram user
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Telegram init data required")

    user_data = parse_telegram_init_data(x_telegram_init_data)
    username = get_username_from_telegram_user(user_data)
    user_id = user_data.get('id')

    if not username:
        raise HTTPException(status_code=400, detail="Username not found")

    # Проверка доступа
    has_access = await check_client_access(username, db, user_id)
    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You need to reach $500 threshold to view your data."
        )

    # Получаем балансы из базы
    paypal_query = text("SELECT balance FROM balances_paypal WHERE client_username = :username")
    stripe_query = text("SELECT balance FROM balances_stripe WHERE client_username = :username")
    withdrawal_query = text("SELECT withdrawal_amount FROM balances_paypal_withdrawal WHERE client_username = :username")

    paypal_result = await db.execute(paypal_query, {"username": username})
    stripe_result = await db.execute(stripe_query, {"username": username})
    withdrawal_result = await db.execute(withdrawal_query, {"username": username})

    paypal_balance = paypal_result.scalar() or 0.0
    stripe_balance = stripe_result.scalar() or 0.0
    withdrawal_amount = withdrawal_result.scalar() or 0.0

    total = float(paypal_balance) + float(stripe_balance) + float(withdrawal_amount)

    return BalanceResponse(
        total=total,
        paypal=float(paypal_balance),
        stripe=float(stripe_balance),
        withdrawal=float(withdrawal_amount)
    )


@app.get("/api/statistics", response_model=StatisticsResponse)
async def get_statistics(
    x_telegram_init_data: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Получить статистику клиента"""
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Missing X-Telegram-Init-Data header. Please open in Telegram.")

    user_data = parse_telegram_init_data(x_telegram_init_data)
    username = get_username_from_telegram_user(user_data)
    user_id = user_data.get('id')

    if not username:
        raise HTTPException(status_code=400, detail="Username not found")

    # Проверка доступа
    has_access = await check_client_access(username, db, user_id)
    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You need to reach $500 threshold to view your data."
        )

    # Статистика за все время
    total_query = text("""
        SELECT
            COUNT(*) as total_checks,
            COALESCE(SUM(withdrawal_amount), 0) as total_sum,
            COALESCE(AVG(withdrawal_amount), 0) as avg_check
        FROM sheet_transactions
        WHERE client_username = :username
          AND withdrawal_received = TRUE
    """)

    total_result = await db.execute(total_query, {"username": username})
    total_row = total_result.fetchone()

    total_checks = total_row[0] if total_row else 0
    total_sum = float(total_row[1]) if total_row else 0.0
    avg_check = float(total_row[2]) if total_row else 0.0

    # Статистика по месяцам (для расчета средних)
    monthly_query = text("""
        SELECT
            DATE_TRUNC('month', transaction_date) as month,
            COUNT(*) as checks_count,
            SUM(withdrawal_amount) as month_sum
        FROM sheet_transactions
        WHERE client_username = :username
          AND withdrawal_received = TRUE
          AND transaction_date IS NOT NULL
        GROUP BY DATE_TRUNC('month', transaction_date)
        ORDER BY month DESC
    """)

    monthly_result = await db.execute(monthly_query, {"username": username})
    monthly_rows = monthly_result.fetchall()

    # Считаем средние по месяцам
    if monthly_rows:
        avg_checks_month = sum(row[1] for row in monthly_rows) / len(monthly_rows)
        avg_sum_month = sum(float(row[2]) for row in monthly_rows) / len(monthly_rows)
    else:
        avg_checks_month = 0
        avg_sum_month = 0.0

    return StatisticsResponse(
        avgCheck=avg_check,
        totalChecks=total_checks,
        totalSum=total_sum,
        avgChecksMonth=avg_checks_month,
        avgSumMonth=avg_sum_month
    )


@app.get("/api/transactions", response_model=TransactionsResponse)
async def get_transactions(
    x_telegram_init_data: Optional[str] = Header(None),
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Получить транзакции клиента"""
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Telegram init data required")

    user_data = parse_telegram_init_data(x_telegram_init_data)
    username = get_username_from_telegram_user(user_data)
    user_id = user_data.get('id')

    if not username:
        raise HTTPException(status_code=400, detail="Username not found")

    # Проверка доступа
    has_access = await check_client_access(username, db, user_id)
    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You need to reach $500 threshold to view your data."
        )

    # Получаем транзакции
    transactions_query = text("""
        SELECT
            id,
            payment_system,
            amount_gross,
            transaction_date,
            CASE
                WHEN withdrawal_received THEN 'completed'
                ELSE 'pending'
            END as status
        FROM sheet_transactions
        WHERE (LOWER(client_username) = LOWER(:username) 
           OR LOWER(client_username) = LOWER(:username_no_at))
        ORDER BY transaction_date DESC NULLS LAST, id DESC
        LIMIT :limit OFFSET :offset
    """)

    count_query = text("""
        SELECT COUNT(*)
        FROM sheet_transactions
        WHERE (LOWER(client_username) = LOWER(:username) 
           OR LOWER(client_username) = LOWER(:username_no_at))
    """)

    print(f"DEBUG: Fetching transactions for {username}")
    
    username_no_at = username.lstrip('@')
    
    transactions_result = await db.execute(transactions_query, {
        "username": username,
        "username_no_at": username_no_at,
        "limit": limit,
        "offset": offset
    })
    count_result = await db.execute(count_query, {
        "username": username,
        "username_no_at": username_no_at
    })

    transactions_rows = transactions_result.fetchall()
    total_count = count_result.scalar() or 0

    transactions = [
        Transaction(
            id=row[0],
            payment_method=row[1] or "Unknown",
            amount=float(row[2]) if row[2] else 0.0,
            created_at=row[3].isoformat() if row[3] else datetime.now().isoformat(),
            status=row[4]
        )
        for row in transactions_rows
    ]

    return TransactionsResponse(
        transactions=transactions,
        total=total_count
    )


# ... (Keep existing code)

class TransactionCreateRequest(BaseModel):
    payment_method: str
    amount: float
    currency: str = "USD"
    external_id: Optional[str] = None
    email: Optional[str] = None


@app.post("/api/transactions")
async def create_transaction(
    request: TransactionCreateRequest,
    x_telegram_init_data: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Create a new transaction ticket"""
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Telegram init data required")

    user_data = parse_telegram_init_data(x_telegram_init_data)
    user_id = user_data.get('id')
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID not found")
        
    # Check access (including block status)
    username = get_username_from_telegram_user(user_data) or "unknown"
    if not await check_client_access(username, db, user_id):
         raise HTTPException(status_code=403, detail="Access denied")

    # Create transaction
    transaction_repo = TransactionRepository(db)
    
    # Store amount as string to match schema if needed, or float if schema allows
    # Based on models.py, amount is String(50), so convert to str
    transaction = await transaction_repo.create(
        user_id=user_id,
        payment_method=request.payment_method,
        amount=str(request.amount),
        currency=request.currency
    )

    # Convert SQLAlchemy model to Pydantic model for response
    # We need to manually construct the User object for logging since we only have ID/data
    tg_user_obj = type('TgUser', (), {
        'id': user_id,
        'username': user_data.get('username'),
        'first_name': user_data.get('first_name'),
        'last_name': user_data.get('last_name'),
        'language_code': user_data.get('language_code'),
        'is_premium': user_data.get('is_premium', False)
    })
    
    # Send Notification to Log Bot
    try:
        await telegram_logger.log_transaction(tg_user_obj, f"{request.payment_method} (${request.amount})")
    except Exception as e:
        print(f"Failed to send log notification: {e}")

    return {
        "status": "ok", 
        "transaction_id": transaction.id,
        "message": "Ticket created successfully"
    }


# ... (Keep existing code)

# Helper function definition for premium access
async def check_premium_access(username: str, db: AsyncSession, user_id: int) -> bool:
    """
    Check if client has access to premium features (Buyer Lookup).
    Condition: >$1000 Gross Volume in the last 30 days.
    """
    # Admins always have access
    admin_ids = eval(os.getenv('ADMIN_IDS', '[]'))
    if user_id in admin_ids:
        return True

    # Calculate volume (Lifetime)
    query = text("""
        SELECT COALESCE(SUM(amount_gross), 0)
        FROM sheet_transactions
        WHERE client_username = :username
          AND withdrawal_received = TRUE
          -- Removed 30 day limit filter
    """)

    result = await db.execute(query, {"username": username})
    volume_30d = float(result.scalar() or 0.0)
    
    return volume_30d >= 1000.0


class BuyerStatsResponse(BaseModel):
    email: str
    total_transactions: int
    total_volume: float   # Gross
    total_net: float      # Net / Clean Money
    first_seen: Optional[str]
    last_seen: Optional[str]
    unique_partners: int


@app.get("/api/buyer/lookup", response_model=BuyerStatsResponse)
async def lookup_buyer(
    email: str,
    x_telegram_init_data: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Lookup statistics for a specific buyer email (Premium feature).
    """
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Telegram init data required")

    user_data = parse_telegram_init_data(x_telegram_init_data)
    username = get_username_from_telegram_user(user_data)
    user_id = user_data.get('id')

    if not username:
        raise HTTPException(status_code=400, detail="Username not found")

    # 1. Check Basic Access
    has_basic_access = await check_client_access(username, db, user_id)
    if not has_basic_access:
        raise HTTPException(status_code=403, detail="Basic access required")

    # 2. Check Premium Access
    has_premium = await check_premium_access(username, db, user_id)
    if not has_premium:
        raise HTTPException(
            status_code=403, 
            detail="Premium access required. You need >$1000 volume in the last 30 days."
        )

    # 3. Lookup Buyer Stats
    # Added (COALESCE(SUM(withdrawal_amount), 0)) for Net/Clean money
    query = text("""
        SELECT
            COUNT(*),
            COALESCE(SUM(amount_gross), 0),
            MIN(transaction_date),
            MAX(transaction_date),
            COUNT(DISTINCT client_username),
            COALESCE(SUM(withdrawal_amount), 0)
        FROM sheet_transactions
        WHERE buyer_email = :email
    """)

    result = await db.execute(query, {"email": email})
    row = result.fetchone()

    if not row or row[0] == 0:
        raise HTTPException(status_code=404, detail="Buyer not found")

    return BuyerStatsResponse(
        email=email,
        total_transactions=row[0],
        total_volume=float(row[1]),
        first_seen=row[2].isoformat() if row[2] else None,
        last_seen=row[3].isoformat() if row[3] else None,
        unique_partners=row[4],
        total_net=float(row[5])
    )


# Update access-status to include premium status
@app.get("/api/access-status")
async def check_access_status_v2(
    x_telegram_init_data: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """Check both basic and premium access status"""
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Telegram init data required")

    user_data = parse_telegram_init_data(x_telegram_init_data)
    username = get_username_from_telegram_user(user_data)
    user_id = user_data.get('id')

    if not username:
        raise HTTPException(status_code=400, detail="Username not found")

    # Reuse existing logic for basic access (copy-paste from original or refactor)
    # Ideally refactor, but for stability I will use the existing logic structure + new check
    
    # ... (Existing logic for basic access) ...
    query = text("""
        SELECT
            can_view_data,
            total_earnings,
            threshold_amount,
            threshold_reached
        FROM client_thresholds
        WHERE client_username = :username
    """)
    result = await db.execute(query, {"username": username})
    row = result.fetchone()

    # Manual calc fallback
    if not row:
        earnings_query = text("""
            SELECT COALESCE(SUM(withdrawal_amount), 0)
            FROM sheet_transactions
            WHERE client_username = :username
              AND withdrawal_received = TRUE
        """)
        earnings_result = await db.execute(earnings_query, {"username": username})
        total_earnings = float(earnings_result.scalar() or 0.0)
        threshold_amount = 500.0
        can_view_data = total_earnings >= threshold_amount
        threshold_reached = can_view_data
    else:
        can_view_data = row[0]
        total_earnings = float(row[1]) if row[1] else 0.0
        threshold_amount = float(row[2]) if row[2] else 500.0
        threshold_reached = row[3]

    admin_ids = eval(os.getenv('ADMIN_IDS', '[]'))
    is_admin = user_id in admin_ids
    if is_admin:
        can_view_data = True
        threshold_reached = True

    # NEW: Check Premium Access
    can_lookup_buyer = await check_premium_access(username, db, user_id)

    # Fetch db_user for referral_code
    user_repo = UserRepository(db)
    db_user = await user_repo.get_by_id(user_id)
    referral_code = db_user.referral_code if db_user else None

    return {
        "has_access": can_view_data,
        "total_earnings": total_earnings,
        "threshold_amount": threshold_amount,
        "threshold_reached": threshold_reached,
        "progress_percentage": min(100, (total_earnings / threshold_amount * 100)) if threshold_amount > 0 else 100,
        "is_admin": is_admin,
        "can_lookup_buyer": can_lookup_buyer,  # New field
        "referral_code": referral_code,
        "is_referral_custom": total_earnings > 300 # Helper for frontend logic
    }

# Remove the old access-status endpoint since we overwrote it (or ensure uniqueness)
# Python will overwrite, but let's be clean. I'll replace the existing one.


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# Для админов - статистика по всем клиентам
@app.get("/api/admin/top-clients")
async def get_top_clients(
    x_telegram_init_data: Optional[str] = Header(None),
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Топ клиентов по обороту (только для админов)"""
    if not x_telegram_init_data:
        raise HTTPException(status_code=401, detail="Telegram init data required")

    user_data = parse_telegram_init_data(x_telegram_init_data)
    user_id = user_data.get('id')

    # Проверка что это админ
    admin_ids = eval(os.getenv('ADMIN_IDS', '[]'))
    if user_id not in admin_ids:
        raise HTTPException(status_code=403, detail="Admin access required")

    query = text("""
        SELECT
            client_username,
            COUNT(*) as transactions,
            SUM(amount_gross) as total_amount,
            SUM(withdrawal_amount) as total_withdrawals
        FROM sheet_transactions
        WHERE client_username IS NOT NULL
        GROUP BY client_username
        ORDER BY SUM(amount_gross) DESC
        LIMIT :limit
    """)

    result = await db.execute(query, {"limit": limit})
    rows = result.fetchall()

    clients = [
        {
            "username": row[0],
            "transactions": row[1],
            "total_amount": float(row[2]) if row[2] else 0.0,
            "total_withdrawals": float(row[3]) if row[3] else 0.0
        }
        for row in rows
    ]

    return {"clients": clients}


# --- Referral System ---

class UpdateReferralCodeRequest(BaseModel):
    new_code: str

@app.post("/api/user/referral_code")
async def update_referral_code(
    request: UpdateReferralCodeRequest,
    auth: str = Header(None, alias="X-Telegram-Init-Data"),
    db: AsyncSession = Depends(get_db)
):
    """
    Allow users with > $300 turnover to set a custom referral code.
    """
    user_data = parse_telegram_init_data(auth)
    user_id = user_data["id"]

    try:
        # Validate new code format (alphanumeric, etc.)
        if not request.new_code.isalnum() or len(request.new_code) < 3 or len(request.new_code) > 20:
             raise HTTPException(status_code=400, detail="Invalid code format. Use 3-20 alphanumeric characters.")

        # Check turnover
        transaction_repo = TransactionRepository(db)
        stats = await transaction_repo.get_statistics(user_id)
        
        total_turnover = stats['total_sum']
        
        if total_turnover < 300:
            raise HTTPException(status_code=403, detail=f"Insufficient turnover (${total_turnover:.2f} < $300)")

        user_repo = UserRepository(db)
        success = await user_repo.set_referral_code(user_id, request.new_code.upper())
        
        if not success:
             raise HTTPException(status_code=409, detail="Code already taken")
             
        return {"status": "success", "new_code": request.new_code.upper()}

    except HTTPException:
        raise
    except Exception as e:
        telegram_logger.error(f"Error updating referral code: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8080"))
    
    # HTTPS Configuration
    ssl_keyfile = os.getenv("SSL_KEY_FILE")
    ssl_certfile = os.getenv("SSL_CERT_FILE")
    
    if ssl_keyfile and ssl_certfile and os.path.exists(ssl_keyfile) and os.path.exists(ssl_certfile):
        print(f"Starting with SSL: key={ssl_keyfile}, cert={ssl_certfile}")
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile
        )
    else:
        print("Starting without SSL (HTTP only)")
        uvicorn.run(app, host="0.0.0.0", port=port)
