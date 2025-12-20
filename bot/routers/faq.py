from pathlib import Path

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile

from bot.keyboards.faq import (
    get_faq_keyboard,
    get_faq_category_keyboard,
    get_faq_answer_keyboard,
    FAQ_ANSWERS,
    FAQ_SUBCATEGORIES,
    FAQ_CATEGORIES
)

router = Router(name="faq")

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

    # If edit failed or not attempted, send new message with photo
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


@router.callback_query(F.data == "faq")
async def faq_menu(callback: CallbackQuery) -> None:
    await callback.answer()

    text = (
        "❓ <b>Часто задаваемые вопросы</b>\n\n"
        "Выберите категорию:"
    )

    await send_with_photo(callback, text, get_faq_keyboard())


# Handle category clicks
@router.callback_query(F.data.startswith("faq_cat_"))
async def faq_category(callback: CallbackQuery) -> None:
    await callback.answer()

    category = callback.data
    category_name = FAQ_CATEGORIES.get(category, "Категория")

    text = f"📂 <b>{category_name}</b>\n\nВыберите вопрос:"

    await send_with_photo(callback, text, get_faq_category_keyboard(category))


# Handle individual FAQ items
@router.callback_query(F.data.startswith("faq_commission_"))
async def faq_commission_item(callback: CallbackQuery) -> None:
    await callback.answer()
    key = callback.data
    answer = FAQ_ANSWERS.get(key, "Ответ не найден.")
    await send_with_photo(callback, answer, get_faq_answer_keyboard("faq_cat_commission"))


@router.callback_query(F.data.startswith("faq_howto_"))
async def faq_howto_item(callback: CallbackQuery) -> None:
    await callback.answer()
    key = callback.data
    answer = FAQ_ANSWERS.get(key, "Ответ не найден.")
    await send_with_photo(callback, answer, get_faq_answer_keyboard("faq_cat_howto"))


@router.callback_query(F.data.startswith("faq_withdraw_"))
async def faq_withdraw_item(callback: CallbackQuery) -> None:
    await callback.answer()
    key = callback.data
    answer = FAQ_ANSWERS.get(key, "Ответ не найден.")
    await send_with_photo(callback, answer, get_faq_answer_keyboard("faq_cat_withdrawals"))


@router.callback_query(F.data.startswith("faq_service_"))
async def faq_service_item(callback: CallbackQuery) -> None:
    await callback.answer()
    key = callback.data
    answer = FAQ_ANSWERS.get(key, "Ответ не найден.")
    await send_with_photo(callback, answer, get_faq_answer_keyboard("faq_cat_services"))


@router.callback_query(F.data.startswith("faq_rules_"))
async def faq_rules_item(callback: CallbackQuery) -> None:
    await callback.answer()
    key = callback.data
    answer = FAQ_ANSWERS.get(key, "Ответ не найден.")
    await send_with_photo(callback, answer, get_faq_answer_keyboard("faq_cat_rules"))


@router.callback_query(F.data == "faq_contract")
async def faq_contract(callback: CallbackQuery) -> None:
    await callback.answer()
    answer = FAQ_ANSWERS.get("faq_contract", "Договор не найден.")
    await send_with_photo(callback, answer, get_faq_answer_keyboard())
