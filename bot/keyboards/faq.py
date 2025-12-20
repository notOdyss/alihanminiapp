from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Main FAQ categories
FAQ_CATEGORIES: dict[str, str] = {
    "faq_cat_commission": "💰 Комиссии",
    "faq_cat_howto": "📖 Как пользоваться",
    "faq_cat_withdrawals": "💸 Выводы",
    "faq_cat_services": "🛠 Доп. услуги",
    "faq_cat_rules": "⚖️ Правила",
}

# Sub-items per category
FAQ_SUBCATEGORIES: dict[str, dict[str, str]] = {
    "faq_cat_commission": {
        "faq_commission_main": "💼 Комиссия обменника",
        "faq_commission_calc": "🧮 Примеры расчёта",
        "faq_commission_best": "✨ Самый выгодный способ",
    },
    "faq_cat_howto": {
        "faq_howto_steps": "📝 Пошаговая инструкция",
        "faq_howto_screenshot": "📸 Скриншот обязателен?",
        "faq_howto_invoice": "🧾 Можно ли отправить инвойс?",
    },
    "faq_cat_withdrawals": {
        "faq_withdraw_min": "💵 Минимальная сумма",
        "faq_withdraw_timing": "⏱ Сроки вывода",
        "faq_withdraw_countries": "🌍 Доступные страны",
        "faq_withdraw_abroad": "✈️ Вывод зарубеж",
        "faq_withdraw_bybit": "📲 Вывод с Bybit",
        "faq_withdraw_keep": "💾 Оставить на аккаунте",
    },
    "faq_cat_services": {
        "faq_service_beatstars": "🎵 PayPal + BeatStars",
        "faq_service_bank_bind": "🏦 Привязка банка",
        "faq_service_youtube": "📺 YouTube, BMI, Royalty",
        "faq_service_splits": "🔀 Подписки и сплиты",
    },
    "faq_cat_rules": {
        "faq_rules_refund": "🔄 Возврат средств",
        "faq_rules_deadline": "📅 Срок хранения средств",
    },
}

# Full answers
FAQ_ANSWERS: dict[str, str] = {
    # Commission category
    "faq_commission_main": (
        "💼 <b>Комиссия обменника</b>\n\n"
        "📊 <b>Итоговая комиссия:</b>\n"
        "• 15% — PayPal\n"
        "• 16% — Stripe\n"
        "• 17,5% — Bank Account\n\n"
        "📋 <b>Состав комиссий:</b>\n\n"
        "💼 Комиссия обменника:\n"
        "• 6% — PayPal\n"
        "• 7% — Stripe\n"
        "• 8,5% — Bank Account\n\n"
        "🧾 Внутренняя комиссия (налоги):\n"
        "• 6% + 5$ (для всех способов)\n\n"
        "🔁 P2P-комиссия (вывод на карту/крипту):\n"
        "• 3%"
    ),
    "faq_commission_calc": (
        "🧮 <b>Примеры расчёта</b>\n\n"
        "💳 PayPal → 1000$ − 15% − 5$ = <b>845$</b>\n"
        "💸 Stripe → 1000$ − 16% − 5$ = <b>835$</b>\n"
        "🏦 Bank Account → 1000$ − 17,5% − 5$ = <b>820$</b>\n\n"
        "💡 Воспользуйтесь нашим калькулятором:\n"
        "Просто напишите <code>calc сумма</code>"
    ),
    "faq_commission_best": (
        "✨ <b>Самый выгодный способ</b>\n\n"
        "Самый выгодный способ — <b>PayPal Friends and Family</b>.\n\n"
        "Плюс можно воспользоваться акциями для снижения комиссии."
    ),

    # How to use category
    "faq_howto_steps": (
        "📝 <b>Как пользоваться обменником</b>\n\n"
        "1️⃣ Узнай способ оплаты у клиента\n"
        "2️⃣ Отправь клиенту реквизиты — доступны в боте @exchangerali_bot\n"
        "3️⃣ Попроси скриншот оплаты (обязательно)\n"
        "4️⃣ Отправь товар/услугу и предоставь доказательства\n"
        "5️⃣ Отправь скриншоты админу @herr_leutenant\n"
        "6️⃣ Отправь свои реквизиты для вывода\n"
        "7️⃣ Дождись срока и получи вывод"
    ),
    "faq_howto_screenshot": (
        "📸 <b>Скриншот обязателен?</b>\n\n"
        "✅ Да, вывод без скриншота <b>не осуществляется</b>."
    ),
    "faq_howto_invoice": (
        "🧾 <b>Можно ли отправить инвойс?</b>\n\n"
        "✅ Да, напиши @thxfortheslapali"
    ),

    # Withdrawals category
    "faq_withdraw_min": (
        "💵 <b>Минимальная сумма вывода</b>\n\n"
        "• $20\n"
        "• или 2000 рублей"
    ),
    "faq_withdraw_timing": (
        "⏱ <b>Сроки вывода</b>\n\n"
        "💳 PayPal — 24-48 часов\n"
        "💸 Stripe — до 7 рабочих дней\n"
        "🏦 Bank Account — до 14 рабочих дней"
    ),
    "faq_withdraw_countries": (
        "🌍 <b>В какие страны доступен вывод?</b>\n\n"
        "Вывод доступен на все страны СНГ, которые есть на Bybit."
    ),
    "faq_withdraw_abroad": (
        "✈️ <b>Возможен ли вывод зарубеж?</b>\n\n"
        "✅ Да, напиши @herr_leutenant"
    ),
    "faq_withdraw_bybit": (
        "📲 <b>Вывод с Bybit</b>\n\n"
        "📺 Видеоинструкция (ПК):\n"
        "YouTube — инструкция для компьютера\n\n"
        "📱 Видеоинструкция (Телефон):\n"
        "YouTube — инструкция для телефона\n\n"
        "💸 Также у нас есть услуга вывода криптовалюты на ваш банк.\n"
        "Подробнее — @herr_leutenant"
    ),
    "faq_withdraw_keep": (
        "💾 <b>Можно ли оставить средства на аккаунте?</b>\n\n"
        "✅ Да, для платежей на PayPal.\n"
        "Сообщи админу @herr_leutenant\n\n"
        "⚠️ Максимальный срок хранения — 2 месяца."
    ),

    # Services category
    "faq_service_beatstars": (
        "🎵 <b>Подключение PayPal к BeatStars</b>\n\n"
        "✅ Да, подключаем.\n\n"
        "📋 Условия:\n"
        "• Стоимость услуги — 500 рублей\n"
        "• Комиссия как при выводе с PayPal\n"
        "• Скриншот после каждой продажи обязателен\n"
        "• Передать @babytakeyourtime логин и пароль от BeatStars"
    ),
    "faq_service_bank_bind": (
        "🏦 <b>Привязка банка</b>\n\n"
        "За привязкой банка к:\n"
        "• BMI / ASCAP\n"
        "• BeatStars Pay\n"
        "• Tipalti\n"
        "• CreateMusicGroup\n"
        "• и др.\n\n"
        "👉 Обращайтесь к @thxfortheslapali"
    ),
    "faq_service_youtube": (
        "📺 <b>YouTube, BMI, Royalty, Publishing</b>\n\n"
        "✅ Монетизация YouTube — да, поможем\n"
        "✅ Регистрация в BMI — без проблем\n"
        "✅ Royalty и Publishing выплаты — тоже через нас\n\n"
        "👉 Напиши @thxfortheslapali"
    ),
    "faq_service_splits": (
        "🔀 <b>Подписки и переводы (сплиты)</b>\n\n"
        "🔹 Можно ли сплитануть продажу?\n"
        "✅ Да, указывай при отправке скрина\n\n"
        "🔹 Можно ли оплатить подписку/услуги?\n"
        "✅ Да. Напиши @babytakeyourtime"
    ),

    # Rules category
    "faq_rules_refund": (
        "🔄 <b>Возврат средств, апелляции</b>\n\n"
        "Если клиент ошибочно оплатил дважды или неверно — возврат возможен <b>только до вывода</b> средств. После вывода — нет.\n\n"
        "⚠️ При спорах («товар не получен», «ненадлежащее качество», «мошенничество») банк проводит проверку.\n\n"
        "Если спор решён не в Вашу пользу — сумма и комиссия списываются с нас и удерживаются с Вашего баланса/будущих выплат.\n\n"
        "При отказе погасить задолженность — дело передаётся в юридический отдел."
    ),
    "faq_rules_deadline": (
        "📅 <b>Срок нахождения средств до возврата</b>\n\n"
        "30 (тридцать) дней с момента поступления платежа (на все реквизиты)."
    ),

    # Contract (standalone)
    "faq_contract": (
        "📄 <b>Договор</b>\n\n"
        "🔗 <a href='https://drive.google.com/file/d/18mL7rz1aeCs38rWkoVaP9VkrSXi9stnX/view?usp=sharing'>Открыть договор</a>"
    ),
}


def get_faq_keyboard() -> InlineKeyboardMarkup:
    """Main FAQ menu with categories."""
    buttons = [
        [InlineKeyboardButton(text=text, callback_data=callback)]
        for callback, text in FAQ_CATEGORIES.items()
    ]
    # Contract as full-width button at bottom
    buttons.append([
        InlineKeyboardButton(text="📄 Договор", callback_data="faq_contract")
    ])
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_faq_category_keyboard(category: str) -> InlineKeyboardMarkup:
    """Get sub-items for a category."""
    subcats = FAQ_SUBCATEGORIES.get(category, {})
    buttons = [
        [InlineKeyboardButton(text=text, callback_data=callback)]
        for callback, text in subcats.items()
    ]
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад в FAQ", callback_data="faq")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_faq_answer_keyboard(category: str | None = None) -> InlineKeyboardMarkup:
    """Back button after viewing an answer."""
    buttons = []
    if category:
        buttons.append([
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=category
            )
        ])
    buttons.append([
        InlineKeyboardButton(
            text="📋 FAQ меню",
            callback_data="faq"
        )
    ])
    buttons.append([
        InlineKeyboardButton(
            text="🏠 Главное меню",
            callback_data="back_to_main"
        )
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
