from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Statistics",
                    callback_data="admin_stats"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Search User",
                    callback_data="admin_search"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Recent Users",
                    callback_data="admin_recent"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📈 Transactions",
                    callback_data="admin_transactions"
                )
            ]
        ]
    )


def get_user_detail_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📜 Interactions",
                    callback_data=f"user_interactions_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Transactions",
                    callback_data=f"user_transactions_{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Back",
                    callback_data="admin_main"
                )
            ]
        ]
    )


def get_back_keyboard(callback_data: str = "admin_main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Back",
                    callback_data=callback_data
                )
            ]
        ]
    )


def get_search_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Cancel",
                    callback_data="admin_main"
                )
            ]
        ]
    )
