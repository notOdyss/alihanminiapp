from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.repositories import UserRepository, InteractionRepository, TransactionRepository
from logbot.keyboards.admin import (
    get_admin_main_keyboard,
    get_user_detail_keyboard,
    get_back_keyboard,
    get_search_cancel_keyboard
)

router = Router(name="admin")


class AdminStates(StatesGroup):
    waiting_user_search = State()
    waiting_user_id = State()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS or user_id == settings.LOG_CHAT_ID


@router.message(Command("admin"))
@router.message(Command("start"))
async def admin_panel(message: Message, session: AsyncSession) -> None:
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Access denied. This bot is for admins only.")
        return

    user_repo = UserRepository(session)
    interaction_repo = InteractionRepository(session)
    transaction_repo = TransactionRepository(session)

    total_users = await user_repo.get_total_count()
    total_interactions = await interaction_repo.get_total_count()
    total_transactions = await transaction_repo.get_total_count()

    text = (
        "🔐 <b>Admin Panel</b>\n\n"
        f"👥 Total Users: <b>{total_users}</b>\n"
        f"📊 Total Interactions: <b>{total_interactions}</b>\n"
        f"💳 Total Transactions: <b>{total_transactions}</b>\n\n"
        "Select an option below:"
    )

    await message.answer(
        text=text,
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_main")
async def admin_main(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await state.clear()

    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied.", show_alert=True)
        return

    user_repo = UserRepository(session)
    interaction_repo = InteractionRepository(session)
    transaction_repo = TransactionRepository(session)

    total_users = await user_repo.get_total_count()
    total_interactions = await interaction_repo.get_total_count()
    total_transactions = await transaction_repo.get_total_count()

    text = (
        "🔐 <b>Admin Panel</b>\n\n"
        f"👥 Total Users: <b>{total_users}</b>\n"
        f"📊 Total Interactions: <b>{total_interactions}</b>\n"
        f"💳 Total Transactions: <b>{total_transactions}</b>\n\n"
        "Select an option below:"
    )

    await callback.answer()
    await callback.message.edit_text(
        text=text,
        reply_markup=get_admin_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery, session: AsyncSession) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied.", show_alert=True)
        return

    user_repo = UserRepository(session)
    interaction_repo = InteractionRepository(session)
    transaction_repo = TransactionRepository(session)

    total_users = await user_repo.get_total_count()
    total_interactions = await interaction_repo.get_total_count()
    total_transactions = await transaction_repo.get_total_count()

    pending = await transaction_repo.get_total_by_status("pending")
    completed = await transaction_repo.get_total_by_status("completed")
    failed = await transaction_repo.get_total_by_status("failed")

    text = (
        "📊 <b>Detailed Statistics</b>\n\n"
        f"👥 <b>Users</b>\n"
        f"   Total: {total_users}\n\n"
        f"📊 <b>Interactions</b>\n"
        f"   Total: {total_interactions}\n"
        f"   Avg per user: {total_interactions / max(total_users, 1):.1f}\n\n"
        f"💳 <b>Transactions</b>\n"
        f"   Total: {total_transactions}\n"
        f"   ⏳ Pending: {pending}\n"
        f"   ✅ Completed: {completed}\n"
        f"   ❌ Failed: {failed}"
    )

    await callback.answer()
    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_search")
async def admin_search(callback: CallbackQuery, state: FSMContext) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied.", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_user_search)

    text = (
        "🔍 <b>Search User</b>\n\n"
        "Enter username or user ID to search:"
    )

    await callback.answer()
    await callback.message.edit_text(
        text=text,
        reply_markup=get_search_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(StateFilter(AdminStates.waiting_user_search))
async def process_user_search(message: Message, session: AsyncSession, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return

    search_query = message.text.strip()
    user_repo = UserRepository(session)

    if search_query.isdigit():
        user = await user_repo.get_by_id(int(search_query))
        if user:
            await show_user_details(message, session, user.id)
            await state.clear()
            return
        else:
            await message.answer(
                "❌ User not found by ID.",
                reply_markup=get_back_keyboard()
            )
            await state.clear()
            return

    users = await user_repo.search_by_username(search_query.replace("@", ""))

    if not users:
        await message.answer(
            "❌ No users found.",
            reply_markup=get_back_keyboard()
        )
        await state.clear()
        return

    if len(users) == 1:
        await show_user_details(message, session, users[0].id)
        await state.clear()
        return

    text = "🔍 <b>Search Results</b>\n\n"
    for user in users:
        username = f"@{user.username}" if user.username else "No username"
        text += f"• {username} (ID: <code>{user.id}</code>)\n"

    text += "\nEnter user ID to view details:"
    await state.set_state(AdminStates.waiting_user_id)

    await message.answer(
        text=text,
        reply_markup=get_search_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(StateFilter(AdminStates.waiting_user_id))
async def process_user_id(message: Message, session: AsyncSession, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return

    if not message.text.isdigit():
        await message.answer("❌ Please enter a valid user ID.")
        return

    user_id = int(message.text)
    await show_user_details(message, session, user_id)
    await state.clear()


async def show_user_details(
    message: Message,
    session: AsyncSession,
    user_id: int
) -> None:
    user_repo = UserRepository(session)
    stats = await user_repo.get_user_stats(user_id)

    if not stats:
        await message.answer(
            "❌ User not found.",
            reply_markup=get_back_keyboard()
        )
        return

    username = f"@{stats['username']}" if stats['username'] else "No username"
    created = stats['created_at'].strftime("%Y-%m-%d %H:%M") if stats['created_at'] else "Unknown"
    last_active = stats['last_active_at'].strftime("%Y-%m-%d %H:%M") if stats['last_active_at'] else "Unknown"

    text = (
        f"👤 <b>User Details</b>\n\n"
        f"🆔 ID: <code>{stats['user_id']}</code>\n"
        f"👤 Username: {username}\n"
        f"📛 Name: {stats['first_name'] or 'Unknown'}\n"
        f"📅 Registered: {created}\n"
        f"🕐 Last Active: {last_active}\n\n"
        f"📊 <b>Activity</b>\n"
        f"   💬 Interactions: {stats['interactions_count']}\n"
        f"   💳 Transactions: {stats['transactions_count']}\n"
        f"   🌐 WebApp Sessions: {stats['webapp_sessions']}\n\n"
        f"🚫 Blocked: {'Yes' if stats['is_blocked'] else 'No'}"
    )

    await message.answer(
        text=text,
        reply_markup=get_user_detail_keyboard(user_id, stats['is_blocked']),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_recent")
async def admin_recent_users(callback: CallbackQuery, session: AsyncSession) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied.", show_alert=True)
        return

    user_repo = UserRepository(session)
    users = await user_repo.get_recent_users(10)

    text = "👥 <b>Recent Users</b>\n\n"
    for user in users:
        username = f"@{user.username}" if user.username else "No username"
        created = user.created_at.strftime("%m-%d %H:%M")
        text += f"• {username} (<code>{user.id}</code>) - {created}\n"

    if not users:
        text += "No users yet."

    await callback.answer()
    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_transactions")
async def admin_transactions(callback: CallbackQuery, session: AsyncSession) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied.", show_alert=True)
        return

    transaction_repo = TransactionRepository(session)

    total = await transaction_repo.get_total_count()
    pending = await transaction_repo.get_total_by_status("pending")
    completed = await transaction_repo.get_total_by_status("completed")
    failed = await transaction_repo.get_total_by_status("failed")

    text = (
        "💳 <b>Transactions Overview</b>\n\n"
        f"📊 Total: {total}\n"
        f"⏳ Pending: {pending}\n"
        f"✅ Completed: {completed}\n"
        f"❌ Failed: {failed}"
    )

    await callback.answer()
    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("user_interactions_"))
async def user_interactions(callback: CallbackQuery, session: AsyncSession) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied.", show_alert=True)
        return

    user_id = int(callback.data.replace("user_interactions_", ""))
    interaction_repo = InteractionRepository(session)

    interactions = await interaction_repo.get_user_interactions(user_id, limit=20)
    stats = await interaction_repo.get_interaction_stats(user_id)

    text = f"📜 <b>User {user_id} Interactions</b>\n\n"

    if stats:
        text += "<b>By Type:</b>\n"
        for itype, count in stats.items():
            text += f"   {itype}: {count}\n"
        text += "\n"

    text += "<b>Recent (last 20):</b>\n"
    for interaction in interactions[:20]:
        time = interaction.created_at.strftime("%m-%d %H:%M")
        action = interaction.action[:30] + "..." if len(interaction.action) > 30 else interaction.action
        text += f"• [{time}] {interaction.interaction_type}: {action}\n"

    if not interactions:
        text += "No interactions yet."

    await callback.answer()
    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_keyboard(f"admin_user_{user_id}"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("user_transactions_"))
async def user_transactions(callback: CallbackQuery, session: AsyncSession) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied.", show_alert=True)
        return

    user_id = int(callback.data.replace("user_transactions_", ""))
    transaction_repo = TransactionRepository(session)

    transactions = await transaction_repo.get_user_transactions(user_id, limit=20)
    stats = await transaction_repo.get_transaction_stats(user_id)

    text = f"💳 <b>User {user_id} Transactions</b>\n\n"

    if stats:
        text += "<b>By Status:</b>\n"
        for status, count in stats.items():
            emoji = {"pending": "⏳", "completed": "✅", "failed": "❌"}.get(status, "❓")
            text += f"   {emoji} {status}: {count}\n"
        text += "\n"

    text += "<b>Recent (last 20):</b>\n"
    for tx in transactions[:20]:
        time = tx.created_at.strftime("%m-%d %H:%M")
        emoji = {"pending": "⏳", "completed": "✅", "failed": "❌"}.get(tx.status, "❓")
        text += f"• [{time}] {emoji} {tx.payment_method}\n"

    if not transactions:
        text += "No transactions yet."

    await callback.answer()
    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_keyboard(f"admin_user_{user_id}"),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("admin_user_"))
async def admin_user_detail(callback: CallbackQuery, session: AsyncSession) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied.", show_alert=True)
        return

    user_id = int(callback.data.replace("admin_user_", ""))
    user_repo = UserRepository(session)
    stats = await user_repo.get_user_stats(user_id)

    if not stats:
        await callback.answer("User not found", show_alert=True)
        return

    username = f"@{stats['username']}" if stats['username'] else "No username"
    created = stats['created_at'].strftime("%Y-%m-%d %H:%M") if stats['created_at'] else "Unknown"
    last_active = stats['last_active_at'].strftime("%Y-%m-%d %H:%M") if stats['last_active_at'] else "Unknown"

    text = (
        f"👤 <b>User Details</b>\n\n"
        f"🆔 ID: <code>{stats['user_id']}</code>\n"
        f"👤 Username: {username}\n"
        f"📛 Name: {stats['first_name'] or 'Unknown'}\n"
        f"📅 Registered: {created}\n"
        f"🕐 Last Active: {last_active}\n\n"
        f"📊 <b>Activity</b>\n"
        f"   💬 Interactions: {stats['interactions_count']}\n"
        f"   💳 Transactions: {stats['transactions_count']}\n"
        f"   🌐 WebApp Sessions: {stats['webapp_sessions']}\n\n"
        f"🚫 Blocked: {'Yes' if stats['is_blocked'] else 'No'}"
    )

    await callback.answer()
    await callback.message.edit_text(
        text=text,
        reply_markup=get_user_detail_keyboard(user_id, stats['is_blocked']),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("admin_block_"))
async def admin_toggle_block(callback: CallbackQuery, session: AsyncSession) -> None:
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Access denied.", show_alert=True)
        return

    parts = callback.data.split("_")
    # Format: admin_block_{action}_{user_id}
    # action: on (to block), off (to unblock)
    action = parts[2]
    user_id = int(parts[3])

    user_repo = UserRepository(session)
    is_blocked = (action == "on")
    success = await user_repo.set_block_status(user_id, is_blocked)

    if success:
        status_text = "blocked" if is_blocked else "unblocked"
        await callback.answer(f"User {status_text} successfully!", show_alert=True)
        # Refresh details
        await admin_user_detail(callback, session)
    else:
        await callback.answer("Failed to update user status.", show_alert=True)
