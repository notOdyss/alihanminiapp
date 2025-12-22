from pathlib import Path

from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.main import get_main_menu_keyboard
from bot.services.logger import telegram_logger
from bot.database.models import User
from bot.database.repositories import UserRepository

router = Router(name="start")

BANNER_PATH = Path(__file__).parent.parent / "assets" / "exchangeali.jpg"


async def send_with_photo(
    message: Message,
    text: str,
    keyboard
) -> None:
    """Send message with photo."""
    if BANNER_PATH.exists():
        photo = FSInputFile(BANNER_PATH)
        await message.answer_photo(
            photo=photo,
            caption=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await message.answer(
            text=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )


async def edit_with_photo(
    callback: CallbackQuery,
    text: str,
    keyboard
) -> None:
    """Edit message caption or send new with photo."""
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception:
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


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    db_user: User,
    is_new_user: bool
) -> None:
    user = message.from_user
    user_repo = UserRepository(session)

    # 1. Generate Referral Code for new user if None (or existing without one)
    if not db_user.referral_code:
        code = await user_repo.generate_unique_referral_code()
        await user_repo.set_referral_code(db_user.id, code)

    # 2. Check for referrer attribution
    # 2. Check for referrer attribution
    args = command.args
    if args:
        if db_user.referrer_id:
             await telegram_logger.send_log(f"ℹ️ Referral ignored for {user.mention_html()}: Already has referrer.")
        else:
            referrer = await user_repo.assign_referrer(db_user.id, args)
            if referrer:
                try:
                    msg = f"🎉 <b>New Referral!</b>\n\nUser: {message.from_user.mention_html()}\nReferrer: {referrer.username or referrer.id} (Code: {args})"
                    await telegram_logger.send_log(msg)
                except Exception:
                    pass
            else:
                 await telegram_logger.send_log(f"⚠️ Referral failed for {user.mention_html()}: Code '{args}' not found or self-referral.")

    if is_new_user:
        try:
            await telegram_logger.log_new_user(user)
        except Exception:
            pass

    text = (
        "💬 Пользуясь обменником By Ali, вы подтверждаете согласие с <a href='https://drive.google.com/file/d/18mL7rz1aeCs38rWkoVaP9VkrSXi9stnX/view?usp=sharing'>условиями использования</a> и правилами Сервиса.\n"
        "Нарушение условий может повлечь приостановку обслуживания, удержание средств или взыскание убытков."
    )

    await send_with_photo(message, text, get_main_menu_keyboard())


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery) -> None:
    await callback.answer()

    text = (
        "👋 <b>Главное меню</b>\n\n"
        "Выберите действие:"
    )

    await edit_with_photo(callback, text, get_main_menu_keyboard())
