from pathlib import Path
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.transactions import (
    get_payment_methods_keyboard,
    get_stripe_methods_keyboard, # Stripe specific
    get_review_keyboard,
    get_back_to_amount_keyboard,
    get_payment_confirmation_keyboard,
    PAYMENT_DESCRIPTIONS,
    WALLET_ADDRESSES, # We need these for confirmation step
    STRIPE_LINK # And this
)
from bot.keyboards.main import get_back_to_main_keyboard
from bot.database.repositories import TransactionRepository
from bot.database.models import User
from bot.states import TransactionStates
from bot.services.calculator import FeeCalculator
from bot.services.logger import telegram_logger

router = Router(name="transactions")
logger = logging.getLogger(__name__)

BANNER_PATH = Path(__file__).parent.parent / "assets" / "exchangeali.jpg"

# --- Message Management Helper (One Message Policy) ---

async def update_interface(
    event: Message | CallbackQuery,
    text: str,
    keyboard = None,
    photo_path: Path = BANNER_PATH,
    state: FSMContext = None
) -> None:
    """
    Unified interface updater.
    - If Callback: Edits the message (caption or text).
    - If Message (User Input): Deletes user message, deletes old bot message (if tracked), sends new one.
    - Ensures only one bot message exists.
    """
    # Try to delete user message if it's a message event
    if isinstance(event, Message):
        try:
            await event.delete()
        except Exception:
            pass # Can't delete in private chat usually, but good to try

    # Retrieve last bot message ID from state
    last_msg_id = None
    if state:
        data = await state.get_data()
        last_msg_id = data.get("last_bot_msg_id")

    message_destionation = event.message if isinstance(event, CallbackQuery) else event

    # Try editing if we have a target message (Callback or Stored ID)
    target_msg = event.message if isinstance(event, CallbackQuery) else None
    
    # If we are in a callback, we can try to edit directly
    if isinstance(event, CallbackQuery):
        try:
            if photo_path and photo_path.exists():
                # If message has photo, edit caption
                if event.message.photo:
                    await event.message.edit_caption(caption=text, reply_markup=keyboard, parse_mode="HTML")
                    if state:
                        await state.update_data(last_bot_msg_id=event.message.message_id)
                    return
                else:
                    # If message is text but we want photo, delete and resend
                    await event.message.delete()
                    # Fall through to send new message
            else:
                 # If no photo needed, edit text
                await event.message.edit_text(text=text, reply_markup=keyboard, parse_mode="HTML")
                if state:
                    await state.update_data(last_bot_msg_id=event.message.message_id)
                return
        except Exception as e:
            logger.warning(f"Edit failed, falling back to resend: {e}")
            pass

    # Fallback or Message event: specific handling
    # If we have a stored ID and we are processing a new user message, we might want to delete the old bot message
    if isinstance(event, Message) and last_msg_id:
        try:
            await event.bot.delete_message(chat_id=event.chat.id, message_id=last_msg_id)
        except Exception:
            pass
    
    # Send new message
    sent_msg = None
    if photo_path and photo_path.exists():
        photo = FSInputFile(photo_path)
        sent_msg = await message_destionation.answer_photo(photo=photo, caption=text, reply_markup=keyboard, parse_mode="HTML")
    else:
        sent_msg = await message_destionation.answer(text=text, reply_markup=keyboard, parse_mode="HTML")
    
    # Update state with new message ID
    if state and sent_msg:
        await state.update_data(last_bot_msg_id=sent_msg.message_id)

async def safe_answer_callback(callback: CallbackQuery) -> None:
    try:
        await callback.answer()
    except Exception:
        pass


# --- Flow Handlers ---

@router.callback_query(F.data == "new_transaction")
async def start_transaction(callback: CallbackQuery, state: FSMContext) -> None:
    await safe_answer_callback(callback)
    
    # Aggressive Cleanup: Try to find old message before clearing state
    data = await state.get_data()
    last_msg_id = data.get("last_bot_msg_id")
    if last_msg_id:
        try:
            await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=last_msg_id)
        except Exception:
            pass
            
    await state.clear() # Reset any previous state
    
    text = (
        "🆕 <b>Новая транзакция</b>\n\n"
        "Выберите способ оплаты:"
    )
    await update_interface(callback, text, get_payment_methods_keyboard(), state=state)

@router.callback_query(F.data.in_(PAYMENT_DESCRIPTIONS.keys()))
async def select_method(callback: CallbackQuery, state: FSMContext) -> None:
    await safe_answer_callback(callback)
    payment_method = callback.data
    
    # Store selected method
    await state.update_data(payment_method=payment_method)
    
    # Move to Amount Input
    await state.set_state(TransactionStates.amount_input)
    
    text = (
        f"💰 <b>Введите сумму для обмена (USD)</b>\n\n"
        f"Вы выбрали: {PAYMENT_DESCRIPTIONS.get(payment_method, callback.data).splitlines()[0]}\n"
        "👇 Напишите число (например: 100)"
    )
    
    await update_interface(callback, text, get_back_to_amount_keyboard(), state=state)

@router.callback_query(F.data == "change_amount")
async def change_amount(callback: CallbackQuery, state: FSMContext) -> None:
    # Re-trigger amount selection using stored data
    data = await state.get_data()
    payment_method = data.get("payment_method")
    if not payment_method:
        await start_transaction(callback, state) # Fallback
        return

    await safe_answer_callback(callback)
    await state.set_state(TransactionStates.amount_input)
    
    text = (
        f"💰 <b>Введите новую сумму (USD)</b>\n"
        "👇 Напишите число:"
    )
    await update_interface(callback, text, get_back_to_amount_keyboard(), state=state)

@router.message(TransactionStates.amount_input)
async def process_amount(message: Message, state: FSMContext) -> None:
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError
    except ValueError:
        # Invalid input, stay in state but update simple error
        text = "⚠️ <b>Ошибка:</b> Введите корректное число больше 0."
        await update_interface(message, text, get_back_to_amount_keyboard(), state=state)
        return

    # Calculate Fees
    data = await state.get_data()
    payment_method = data.get("payment_method", "pay_paypal") # Default safe
    
    result = FeeCalculator.calculate(amount, payment_method)
    
    # Store result for confirmation
    await state.update_data(calculation=result)
    
    # Create Review Text
    method_name = PAYMENT_DESCRIPTIONS.get(payment_method, payment_method).splitlines()[0]
    
    review_text = (
        f"🧾 <b>Подтверждение транзакции</b>\n\n"
        f"🔹 Метод: {method_name}\n"
        f"🔹 Вы отправляете: <b>${result['input_amount']:.2f}</b>\n"
        f"🔸 Комиссия сервиса: ${result['service_fee']:.2f}\n"
        f"🔸 P2P Комиссия: ${result['p2p_fee']:.2f}\n"
        f"🔸 Комиссия шлюза: {result['method_fee_percent']}%\n\n"
        f"💵 <b>Вы получите: ${result['total_payout']:.2f}</b>\n\n"
        "Проверьте данные и подтвердите создание заявки."
    )
    
    # Clear state (keep data, remove state to prevent typing)
    # await state.set_state(None) # Optional: keep state if we want them to be able to type new number? 
    # Let's keep state None so they have to click Back to change
    await state.set_state(None)
    
    await update_interface(message, review_text, get_review_keyboard(), state=state)

@router.callback_query(F.data == "confirm_transaction")
async def confirm_transaction(callback: CallbackQuery, state: FSMContext, session: AsyncSession, db_user: User) -> None:
    await safe_answer_callback(callback)
    data = await state.get_data()
    result = data.get("calculation")
    payment_method_key = data.get("payment_method")
    
    if not result:
        await start_transaction(callback, state)
        return

    # Create Transaction in DB
    transaction_repo = TransactionRepository(session)
    transaction = await transaction_repo.create(
        user_id=db_user.id,
        payment_method=payment_method_key,
        amount=str(result['input_amount']), # Storing input amount
        currency="USD"
    )

    # Export to Google Sheets
    try:
        logger.info(f"Attempting to export transaction {transaction.id} to Google Sheets...")
        from bot.services.sheets_writer import sheets_writer
        await sheets_writer.append_ticket(transaction, db_user)
        logger.info(f"Export to Google Sheets requested for transaction {transaction.id}")
    except Exception as e:
        logger.error(f"Sheets Export Failed: {e}", exc_info=True)
    
    # Notify Admin via Log Bot
    try:
        tg_user_obj = type('TgUser', (), {
            'id': db_user.id,
            'username': db_user.username,
            'first_name': db_user.first_name,
            'last_name': db_user.last_name,
            'language_code': db_user.language_code,
            'is_premium': False
        })
        log_msg = f"🆕 <b>Transaction Created</b>\nMethod: {payment_method_key}\nAmount: ${result['input_amount']:.2f}\nPayout: ${result['total_payout']:.2f}"
        await telegram_logger.log_transaction(tg_user_obj, log_msg)
    except Exception:
        pass

    # Show Final Interface with Payment Details
    
    # Get payment details text based on method
    address_info = ""
    if payment_method_key == "pay_paypal":
        address_info = f"📧 Email: <code>{WALLET_ADDRESSES['paypal_email']}</code>"
    elif payment_method_key == "pay_crypto":
        address_info = (
            f"👉 USDT TRC20: <code>{WALLET_ADDRESSES['usdt_trc20']}</code>\n"
            f"👉 USDT BEP20: <code>{WALLET_ADDRESSES['usdt_bep20']}</code>\n"
            f"👉 BTC: <code>{WALLET_ADDRESSES['btc']}</code>"
        )
    elif "stripe" in payment_method_key:
        address_info = f"🔗 Ссылка: {STRIPE_LINK}"

    final_text = (
        "✅ <b>Заявка создана!</b>\n\n"
        f"Сумма к оплате: <b>${result['input_amount']:.2f}</b>\n\n"
        f"{address_info}\n\n"
        "⏳ <b>После оплаты нажмите кнопку «Я оплатил» ниже.</b>"
    )
    
    await update_interface(callback, final_text, get_payment_confirmation_keyboard(), state=state)
    # Store transaction ID for the next step
    await state.update_data(transaction_id=transaction.id)

@router.callback_query(F.data == "i_paid")
async def payment_confirmed(callback: CallbackQuery, state: FSMContext, session: AsyncSession, db_user: User) -> None:
    await safe_answer_callback(callback)
    data = await state.get_data()
    result = data.get("calculation")
    
    # Notify Admin
    try:
        tg_user_obj = type('TgUser', (), {
            'id': db_user.id,
            'username': db_user.username,
            'first_name': db_user.first_name,
            'last_name': db_user.last_name,
            'language_code': db_user.language_code,
            'is_premium': False
        })
        amount = result['input_amount'] if result else "?"
        log_msg = f"✅ <b>Payment Confirmed by User</b>\nAmount: ${amount}"
        await telegram_logger.log_transaction(tg_user_obj, log_msg)
    except Exception:
        pass

    final_text = (
        "✅ <b>Оплата подтверждена!</b>\n\n"
        "Ваш платеж поступит на обработку. Ожидайте зачисления средств.\n"
        "Если возникнут вопросы - администратор свяжется с вами."
    )
    
    await update_interface(callback, final_text, get_back_to_main_keyboard(), state=state)
    await state.clear()


@router.callback_query(F.data == "cancel_transaction")
async def cancel_transaction(callback: CallbackQuery, state: FSMContext) -> None:
    await safe_answer_callback(callback)
    await state.clear()
    
    text = "❌ Транзакция отменена."
    await update_interface(callback, text, get_back_to_main_keyboard(), state=state)

