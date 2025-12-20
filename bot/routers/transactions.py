from pathlib import Path
import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.transactions import (
    get_payment_methods_keyboard,
    get_payment_detail_keyboard,
    get_stripe_methods_keyboard,
    get_stripe_detail_keyboard,
    PAYMENT_DESCRIPTIONS,
    STRIPE_METHOD_DESC,
    WALLET_ADDRESSES
)
from bot.keyboards.main import get_back_to_main_keyboard
from bot.database.repositories import TransactionRepository
from bot.database.models import User

router = Router(name="transactions")
logger = logging.getLogger(__name__)


async def safe_answer_callback(callback: CallbackQuery, text: str = None, show_alert: bool = False) -> bool:
    """Safely answer callback query, handling expired queries."""
    try:
        await callback.answer(text=text, show_alert=show_alert)
        return True
    except TelegramBadRequest as e:
        if "query is too old" in str(e) or "query ID is invalid" in str(e):
            logger.warning(f"Callback query expired: {e}")
            return False
        raise

BANNER_PATH = Path(__file__).parent.parent / "assets" / "exchangeali.jpg"


async def send_with_photo(
    callback: CallbackQuery,
    text: str,
    keyboard,
    try_edit: bool = True
) -> None:
    """Send or edit message with photo."""
    if try_edit:
        try:
            await callback.message.edit_caption(
                caption=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            return
        except Exception:
            pass

    try:
        await callback.message.delete()
    except Exception:
        pass

    if BANNER_PATH.exists():
        photo = FSInputFile(BANNER_PATH)
        await callback.message.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )


@router.callback_query(F.data == "new_transaction")
async def new_transaction(callback: CallbackQuery) -> None:
    await safe_answer_callback(callback)

    text = (
        "🆕 <b>Новая транзакция</b>\n\n"
        "Выберите способ оплаты:"
    )

    await send_with_photo(callback, text, get_payment_methods_keyboard())


@router.callback_query(F.data == "pay_paypal")
async def pay_paypal(callback: CallbackQuery) -> None:
    await safe_answer_callback(callback)
    text = PAYMENT_DESCRIPTIONS["pay_paypal"]
    await send_with_photo(callback, text, get_payment_detail_keyboard("pay_paypal"))


@router.callback_query(F.data == "pay_crypto")
async def pay_crypto(callback: CallbackQuery) -> None:
    await safe_answer_callback(callback)
    text = PAYMENT_DESCRIPTIONS["pay_crypto"]
    await send_with_photo(callback, text, get_payment_detail_keyboard("pay_crypto"))


@router.callback_query(F.data == "pay_stripe")
async def pay_stripe(callback: CallbackQuery) -> None:
    await safe_answer_callback(callback)
    text = PAYMENT_DESCRIPTIONS["pay_stripe"]
    await send_with_photo(callback, text, get_payment_detail_keyboard("pay_stripe"))


@router.callback_query(F.data == "pay_stripe_list")
async def pay_stripe_list(callback: CallbackQuery) -> None:
    await safe_answer_callback(callback)

    text = (
        "💳 <b>Способы оплаты через Stripe</b>\n\n"
        "Все способы ведут на единую страницу оплаты.\n"
        "Выберите для подробностей:"
    )

    await send_with_photo(callback, text, get_stripe_methods_keyboard())


@router.callback_query(F.data.startswith("stripe_"))
async def stripe_method_detail(callback: CallbackQuery) -> None:
    await safe_answer_callback(callback)

    method_key = callback.data
    text = STRIPE_METHOD_DESC.get(method_key, "Описание недоступно.")

    await send_with_photo(callback, text, get_stripe_detail_keyboard())


# Copy address handlers - send copyable message
@router.callback_query(F.data == "copy_paypal_email")
async def copy_paypal_email(callback: CallbackQuery) -> None:
    await safe_answer_callback(callback)
    email = WALLET_ADDRESSES["paypal_email"]
    await callback.message.answer(
        f"<code>{email}</code>\n\n👆 Нажмите чтобы скопировать",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "copy_usdt_trc20")
async def copy_usdt_trc20(callback: CallbackQuery) -> None:
    await safe_answer_callback(callback)
    address = WALLET_ADDRESSES["usdt_trc20"]
    await callback.message.answer(
        f"<b>USDT TRC20:</b>\n<code>{address}</code>\n\n👆 Нажмите чтобы скопировать",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "copy_usdt_bep20")
async def copy_usdt_bep20(callback: CallbackQuery) -> None:
    await safe_answer_callback(callback)
    address = WALLET_ADDRESSES["usdt_bep20"]
    await callback.message.answer(
        f"<b>USDT BEP20:</b>\n<code>{address}</code>\n\n👆 Нажмите чтобы скопировать",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "copy_btc")
async def copy_btc(callback: CallbackQuery) -> None:
    await safe_answer_callback(callback)
    address = WALLET_ADDRESSES["btc"]
    await callback.message.answer(
        f"<b>BTC:</b>\n<code>{address}</code>\n\n👆 Нажмите чтобы скопировать",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "confirm_payment")
async def confirm_payment(
    callback: CallbackQuery,
    session: AsyncSession,
    db_user: User
) -> None:
    transaction_repo = TransactionRepository(session)

    await transaction_repo.create(
        user_id=db_user.id,
        payment_method="pending_selection"
    )

    await safe_answer_callback(callback, "Транзакция создана!", show_alert=True)

    text = (
        "✅ <b>Транзакция создана</b>\n\n"
        "После оплаты отправьте скриншот админу @herr_leutenant"
    )

    await send_with_photo(callback, text, get_back_to_main_keyboard())
