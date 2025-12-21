from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo


# URL вашего Mini App (замените на свой)
WEBAPP_URL = "https://alihanminiapp.vercel.app/"


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🆕 Новая транзакция",
                    callback_data="new_transaction"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❓ FAQ",
                    callback_data="faq"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 Приложение",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )


def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_to_main"
                )
            ]
        ]
    )
