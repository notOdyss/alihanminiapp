from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Payment method groups
PAYMENT_GROUPS: dict[str, str] = {
    "pay_paypal": "💳 PayPal",
    "pay_crypto": "🪙 Криптовалюта",
    "pay_stripe": "💳 Карты и другие способы",
}

# Stripe sub-methods (all use the same link)
STRIPE_METHODS: dict[str, str] = {
    "stripe_card": "💳 Debit / Credit Card",
    "stripe_apple": "🍎 Apple Pay",
    "stripe_google": "📱 Google Pay",
    "stripe_cashapp": "💵 Cash App",
    "stripe_klarna": "🛒 Klarna",
    "stripe_affirm": "✨ Affirm",
    "stripe_link": "🔗 Link",
    "stripe_alipay": "🔴 AliPay",
    "stripe_wechat": "💬 WeChat Pay",
    "stripe_amazon": "📦 Amazon Pay",
    "stripe_ach": "🏦 Bank Account (ACH)",
}

STRIPE_LINK = "https://buy.stripe.com/5kA5klcf3arC3DO4gg"

# Payment descriptions
PAYMENT_DESCRIPTIONS: dict[str, str] = {
    "pay_paypal": (
        "💳 <b>PayPal</b>\n\n"
        "📧 Email для оплаты:\n"
        "<code>recomaivia@gmail.com</code>\n\n"
        "💡 Отправьте платёж на этот email через PayPal.\n"
        "После оплаты обязательно сделайте скриншот."
    ),
    "pay_crypto": (
        "🪙 <b>Криптовалюта</b>\n\n"
        "Принимаем: <b>USDT (TRC20, BEP20)</b> и <b>BTC</b>\n\n"
        "📋 <b>Адреса кошельков:</b>\n\n"
        "👉 <b>USDT TRC20:</b>\n"
        "<code>TXtFDSaQmDVkcUjUgebHqjAYDPCQSX63nU</code>\n\n"
        "👉 <b>USDT BEP20:</b>\n"
        "<code>0x5153df0aee547bc26e96848eac042a2e9367e368</code>\n\n"
        "👉 <b>BTC:</b>\n"
        "<code>3B5mwDD5B2BhWuWYihA4cciDpknb6u5gwi</code>\n\n"
        "⚠️ <b>ВНИМАНИЕ:</b> USDT (Tether) только по сети TRC20 или BEP20!\n\n"
        "📝 После оплаты уведомите админа о сумме для подтверждения."
    ),
    "pay_stripe": (
        "💳 <b>Карты и другие способы</b>\n\n"
        "Доступные методы оплаты:\n"
        "• Debit / Credit Card\n"
        "• Apple Pay / Google Pay\n"
        "• Cash App / Klarna / Affirm\n"
        "• AliPay / WeChat Pay\n"
        "• Amazon Pay\n"
        "• Bank Account (ACH)\n\n"
        "Все эти способы работают через единую платёжную систему Stripe."
    ),
}

# Stripe method descriptions (when clicked individually)
STRIPE_METHOD_DESC: dict[str, str] = {
    "stripe_card": "💳 <b>Debit / Credit Card</b>\n\nОплата банковской картой Visa, Mastercard, Amex.",
    "stripe_apple": "🍎 <b>Apple Pay</b>\n\nБыстрая оплата с iPhone/iPad/Mac.",
    "stripe_google": "📱 <b>Google Pay</b>\n\nОплата через Google Pay.",
    "stripe_cashapp": "💵 <b>Cash App</b>\n\nОплата через Cash App.",
    "stripe_klarna": "🛒 <b>Klarna</b>\n\nОплата через Klarna (Buy Now, Pay Later).",
    "stripe_affirm": "✨ <b>Affirm</b>\n\nОплата в рассрочку через Affirm.",
    "stripe_link": "🔗 <b>Link</b>\n\nБыстрая оплата через Link by Stripe.",
    "stripe_alipay": "🔴 <b>AliPay</b>\n\nОплата через AliPay.",
    "stripe_wechat": "💬 <b>WeChat Pay</b>\n\nОплата через WeChat Pay.",
    "stripe_amazon": "📦 <b>Amazon Pay</b>\n\nОплата через Amazon Pay.",
    "stripe_ach": "🏦 <b>Bank Account (ACH)</b>\n\nПрямой перевод с банковского счёта (США).",
}


def get_payment_methods_keyboard() -> InlineKeyboardMarkup:
    """Main payment methods selection."""
    buttons = [
        [InlineKeyboardButton(text=text, callback_data=callback)]
        for callback, text in PAYMENT_GROUPS.items()
    ]
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_stripe_methods_keyboard() -> InlineKeyboardMarkup:
    """List all Stripe sub-methods."""
    buttons = []
    # 2 buttons per row for compact display
    row = []
    for callback, text in STRIPE_METHODS.items():
        row.append(InlineKeyboardButton(text=text, callback_data=callback))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="new_transaction")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_payment_detail_keyboard(payment_type: str) -> InlineKeyboardMarkup:
    """Detail view with action buttons."""
    buttons = []

    if payment_type == "pay_paypal":
        buttons.append([
            InlineKeyboardButton(
                text="📋 Скопировать email",
                callback_data="copy_paypal_email"
            )
        ])
    elif payment_type == "pay_crypto":
        buttons.append([
            InlineKeyboardButton(
                text="📋 USDT TRC20",
                callback_data="copy_usdt_trc20"
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                text="📋 USDT BEP20",
                callback_data="copy_usdt_bep20"
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                text="📋 BTC",
                callback_data="copy_btc"
            )
        ])
    elif payment_type == "pay_stripe":
        buttons.append([
            InlineKeyboardButton(
                text="🔗 Открыть ссылку для оплаты",
                url=STRIPE_LINK
            )
        ])
        buttons.append([
            InlineKeyboardButton(
                text="📋 Все способы оплаты",
                callback_data="pay_stripe_list"
            )
        ])

    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="new_transaction")
    ])
    buttons.append([
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_stripe_detail_keyboard() -> InlineKeyboardMarkup:
    """Single Stripe method detail."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔗 Перейти к оплате",
                    url=STRIPE_LINK
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Все способы",
                    callback_data="pay_stripe_list"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="back_to_main"
                )
            ]
        ]
    )


# Wallet addresses for copy functionality
WALLET_ADDRESSES = {
    "usdt_trc20": "TXtFDSaQmDVkcUjUgebHqjAYDPCQSX63nU",
    "usdt_bep20": "0x5153df0aee547bc26e96848eac042a2e9367e368",
    "btc": "3B5mwDD5B2BhWuWYihA4cciDpknb6u5gwi",
    "paypal_email": "recomaivia@gmail.com",
}
