import hashlib
import hmac
import json
from datetime import datetime
from typing import Any
from urllib.parse import parse_qsl, unquote

from aiohttp import web
from aiohttp.web import Request, Response, json_response

from bot.config import settings
from bot.database.connection import db_manager
from bot.database.repositories import UserRepository, InteractionRepository, TransactionRepository


def validate_init_data(init_data: str, bot_token: str) -> dict | None:
    """Validate Telegram Mini App init data."""
    try:
        parsed_data = dict(parse_qsl(init_data, keep_blank_values=True))
        received_hash = parsed_data.pop("hash", None)

        if not received_hash:
            return None

        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed_data.items())
        )

        secret_key = hmac.new(
            b"WebAppData",
            bot_token.encode(),
            hashlib.sha256
        ).digest()

        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()

        if calculated_hash != received_hash:
            return None

        if "user" in parsed_data:
            parsed_data["user"] = json.loads(unquote(parsed_data["user"]))

        return parsed_data
    except Exception:
        return None


def get_user_from_init_data(init_data: dict) -> dict | None:
    """Extract user data from validated init data."""
    return init_data.get("user")


async def auth_middleware(request: Request, handler) -> Response:
    """Middleware to validate Telegram Mini App authentication."""
    if request.path.startswith("/api/"):
        init_data = request.headers.get("X-Telegram-Init-Data", "")

        if not init_data:
            return json_response(
                {"error": "Missing authentication"},
                status=401
            )

        validated_data = validate_init_data(init_data, settings.BOT_TOKEN)
        if not validated_data:
            return json_response(
                {"error": "Invalid authentication"},
                status=401
            )

        request["telegram_data"] = validated_data
        request["telegram_user"] = get_user_from_init_data(validated_data)

    return await handler(request)


async def get_user_profile(request: Request) -> Response:
    """Get user profile and stats."""
    tg_user = request.get("telegram_user")
    if not tg_user:
        return json_response({"error": "User not found"}, status=400)

    user_id = tg_user["id"]

    async with db_manager.session() as session:
        user_repo = UserRepository(session)
        interaction_repo = InteractionRepository(session)
        transaction_repo = TransactionRepository(session)

        await user_repo.update_webapp_visit(user_id)

        stats = await user_repo.get_user_stats(user_id)
        interaction_stats = await interaction_repo.get_interaction_stats(user_id)
        transaction_stats = await transaction_repo.get_transaction_stats(user_id)

    return json_response({
        "user": {
            "id": tg_user["id"],
            "username": tg_user.get("username"),
            "first_name": tg_user.get("first_name"),
            "last_name": tg_user.get("last_name"),
        },
        "stats": stats,
        "interactions_by_type": interaction_stats,
        "transactions_by_status": transaction_stats
    })


async def get_user_interactions(request: Request) -> Response:
    """Get user interaction history."""
    tg_user = request.get("telegram_user")
    if not tg_user:
        return json_response({"error": "User not found"}, status=400)

    user_id = tg_user["id"]
    limit = int(request.query.get("limit", 50))
    offset = int(request.query.get("offset", 0))

    async with db_manager.session() as session:
        interaction_repo = InteractionRepository(session)
        interactions = await interaction_repo.get_user_interactions(user_id, limit, offset)

        return json_response({
            "interactions": [
                {
                    "id": i.id,
                    "type": i.interaction_type,
                    "action": i.action,
                    "data": i.data,
                    "created_at": i.created_at.isoformat()
                }
                for i in interactions
            ]
        })


async def get_user_transactions(request: Request) -> Response:
    """Get user transaction history."""
    tg_user = request.get("telegram_user")
    if not tg_user:
        return json_response({"error": "User not found"}, status=400)

    user_id = tg_user["id"]
    limit = int(request.query.get("limit", 50))
    offset = int(request.query.get("offset", 0))

    async with db_manager.session() as session:
        transaction_repo = TransactionRepository(session)
        transactions = await transaction_repo.get_user_transactions(user_id, limit, offset)

        return json_response({
            "transactions": [
                {
                    "id": tx.id,
                    "payment_method": tx.payment_method,
                    "amount": tx.amount,
                    "currency": tx.currency,
                    "status": tx.status,
                    "created_at": tx.created_at.isoformat(),
                    "completed_at": tx.completed_at.isoformat() if tx.completed_at else None
                }
                for tx in transactions
            ]
        })


async def create_transaction(request: Request) -> Response:
    """Create a new transaction from Mini App."""
    tg_user = request.get("telegram_user")
    if not tg_user:
        return json_response({"error": "User not found"}, status=400)

    try:
        data = await request.json()
    except Exception:
        return json_response({"error": "Invalid JSON"}, status=400)

    payment_method = data.get("payment_method")
    amount = data.get("amount")
    currency = data.get("currency")

    if not payment_method:
        return json_response({"error": "Payment method required"}, status=400)

    user_id = tg_user["id"]

    async with db_manager.session() as session:
        transaction_repo = TransactionRepository(session)
        tx = await transaction_repo.create(
            user_id=user_id,
            payment_method=payment_method,
            amount=amount,
            currency=currency
        )

        return json_response({
            "transaction": {
                "id": tx.id,
                "payment_method": tx.payment_method,
                "amount": tx.amount,
                "currency": tx.currency,
                "status": tx.status,
                "created_at": tx.created_at.isoformat()
            }
        }, status=201)


async def log_webapp_event(request: Request) -> Response:
    """Log a Mini App event/interaction."""
    tg_user = request.get("telegram_user")
    if not tg_user:
        return json_response({"error": "User not found"}, status=400)

    try:
        data = await request.json()
    except Exception:
        return json_response({"error": "Invalid JSON"}, status=400)

    event_type = data.get("event_type", "webapp")
    action = data.get("action", "unknown")
    event_data = data.get("data")

    user_id = tg_user["id"]

    async with db_manager.session() as session:
        interaction_repo = InteractionRepository(session)
        await interaction_repo.create(
            user_id=user_id,
            interaction_type=f"webapp_{event_type}",
            action=action,
            data=event_data
        )

    return json_response({"status": "ok"})


async def get_user_balance(request: Request) -> Response:
    """Get user balance information."""
    tg_user = request.get("telegram_user")
    if not tg_user:
        return json_response({"error": "User not found"}, status=400)

    user_id = tg_user["id"]

    async with db_manager.session() as session:
        transaction_repo = TransactionRepository(session)
        transactions = await transaction_repo.get_user_transactions(user_id, limit=1000)

        paypal_balance = sum(
            float(tx.amount or 0)
            for tx in transactions
            if tx.payment_method == "PayPal" and tx.status == "completed"
        )

        stripe_balance = sum(
            float(tx.amount or 0)
            for tx in transactions
            if tx.payment_method == "Stripe" and tx.status == "completed"
        )

        withdrawal = sum(
            float(tx.amount or 0)
            for tx in transactions
            if tx.status == "pending"
        )

        total = paypal_balance + stripe_balance

        return json_response({
            "total": total,
            "paypal": paypal_balance,
            "stripe": stripe_balance,
            "withdrawal": withdrawal
        })


async def get_user_statistics(request: Request) -> Response:
    """Get user statistics."""
    tg_user = request.get("telegram_user")
    if not tg_user:
        return json_response({"error": "User not found"}, status=400)

    user_id = tg_user["id"]

    async with db_manager.session() as session:
        transaction_repo = TransactionRepository(session)
        user_repo = UserRepository(session)

        transactions = await transaction_repo.get_user_transactions(user_id, limit=1000)
        user = await user_repo.get_by_id(user_id)

        if not user:
            return json_response({"error": "User not found"}, status=404)

        completed_transactions = [tx for tx in transactions if tx.status == "completed"]
        total_checks = len(completed_transactions)
        total_sum = sum(float(tx.amount or 0) for tx in completed_transactions)
        avg_check = total_sum / total_checks if total_checks > 0 else 0

        account_age_days = (datetime.utcnow() - user.created_at).days
        months = max(account_age_days / 30, 1)

        avg_checks_month = total_checks / months
        avg_sum_month = total_sum / months

        return json_response({
            "avgCheck": avg_check,
            "totalChecks": total_checks,
            "totalSum": total_sum,
            "avgChecksMonth": avg_checks_month,
            "avgSumMonth": avg_sum_month
        })


async def create_referral_code(request: Request) -> Response:
    """Create a referral code for user."""
    tg_user = request.get("telegram_user")
    if not tg_user:
        return json_response({"error": "User not found"}, status=400)

    user_id = tg_user["id"]

    import secrets
    import string

    code = 'REF' + ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

    async with db_manager.session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_id(user_id)

        if user:
            user.referral_code = code
            await session.commit()

            return json_response({
                "code": code,
                "clicks": 0,
                "registrations": 0
            })

    return json_response({"error": "Failed to create referral code"}, status=500)


async def get_referral_code(request: Request) -> Response:
    """Get user's referral code if it exists."""
    tg_user = request.get("telegram_user")
    if not tg_user:
        return json_response({"error": "User not found"}, status=400)

    user_id = tg_user["id"]

    async with db_manager.session() as session:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_id(user_id)

        if user and user.referral_code:
            return json_response({
                "code": user.referral_code,
                "clicks": 0,
                "registrations": 0
            })

    return json_response({"code": None})


async def health_check(request: Request) -> Response:
    """Health check endpoint."""
    return json_response({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


def create_app() -> web.Application:
    """Create aiohttp web application."""
    app = web.Application(middlewares=[auth_middleware])

    app.router.add_get("/health", health_check)

    app.router.add_get("/api/profile", get_user_profile)
    app.router.add_get("/api/balance", get_user_balance)
    app.router.add_get("/api/statistics", get_user_statistics)
    app.router.add_get("/api/interactions", get_user_interactions)
    app.router.add_get("/api/transactions", get_user_transactions)
    app.router.add_post("/api/transactions", create_transaction)
    app.router.add_post("/api/events", log_webapp_event)
    app.router.add_get("/api/referral", get_referral_code)
    app.router.add_post("/api/referral", create_referral_code)

    return app
