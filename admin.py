import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_ID
from database import get_all_users, get_all_orders, get_user, add_balance_rub
from keyboards import back_button

router = Router()

class AdminAddBalanceStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_amount = State()

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

def admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Список пользователей", callback_data="admin_users")],
        [InlineKeyboardButton(text="📦 Список заказов", callback_data="admin_orders")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="💰 Добавить баланс пользователю", callback_data="admin_add_balance")],
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")]
    ])

@router.message(Command("admin_panel"))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    await message.answer(
        "🔧 *Админ-панель BlondeBoost*\n\nВыберите действие:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=admin_menu()
    )

@router.message(Command("addbalance"))
async def cmd_add_balance(message: Message, state: FSMContext):
    await state.clear()
    if not is_admin(message.from_user.id):
        await message.answer("❌ Нет доступа")
        return
    args = message.text.split()
    if len(args) != 3:
        await message.answer("❌ Использование: `/addbalance <user_id> <сумма_в_рублях>`\nПример: `/addbalance 123456789 100`", parse_mode="Markdown")
        return
    try:
        user_id = int(args[1])
        amount = float(args[2].replace(',', '.'))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Неверный формат. ID должен быть целым числом, сумма – положительным числом (можно с точкой).")
        return
    user = get_user(user_id)
    if not user:
        await message.answer(f"❌ Пользователь с ID {user_id} не найден.")
        return
    add_balance_rub(user_id, amount)
    user = get_user(user_id)
    await message.answer(f"✅ Пользователю `{user['full_name']}` (ID: `{user_id}`) добавлено `{amount:.2f}` ₽.\nНовый баланс: `{user['rub_balance']:.3f}` ₽", parse_mode="Markdown")

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа")
        return
    users = get_all_users(limit=50)
    if not users:
        text = "📋 Список пользователей пуст."
    else:
        text = "📋 *Список пользователей (топ 50 по балансу):*\n\n"
        for u in users:
            text += f"ID: `{u[0]}` | Баланс: {u[1]:.2f} ₽ | {u[2]} | @{u[3] or 'нет'}\n"
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа")
        return
    orders = get_all_orders(limit=50)
    if not orders:
        text = "📋 Список заказов пуст."
    else:
        text = "📋 *Последние 50 заказов:*\n\n"
        for o in orders:
            text += f"#{o[0]} | Юзер: {o[1]} | {o[2]} | {o[3]} ед. | {o[4]:.2f} ₽ | {o[5]}\n{o[6]}\n\n"
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа")
        return
    import sqlite3
    conn = sqlite3.connect("blondeboost.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT SUM(price_rub) FROM orders WHERE status = 'completed'")
    total_income = c.fetchone()[0] or 0.0
    conn.close()
    text = (f"📊 *Статистика*\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"💰 Общий доход (выполненные заказы): {total_income:.2f} ₽")
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "admin_add_balance")
async def admin_add_balance_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа")
        return
    await callback.message.edit_text(
        "💰 Введите Telegram ID пользователя, которому хотите добавить баланс:\n\n"
        "(ID можно посмотреть в списке пользователей или в профиле бота)",
        reply_markup=back_button()
    )
    await state.set_state(AdminAddBalanceStates.waiting_for_user_id)
    await callback.answer()

@router.message(AdminAddBalanceStates.waiting_for_user_id)
async def admin_add_balance_get_user_id(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Нет доступа")
        await state.clear()
        return
    if not message.text.isdigit():
        await message.answer("❌ Введите числовой ID пользователя.")
        return
    user_id = int(message.text)
    user = get_user(user_id)
    if not user:
        await message.answer(f"❌ Пользователь с ID {user_id} не найден.")
        await state.clear()
        return
    await state.update_data(target_user_id=user_id)
    await message.answer(
        f"👤 Найден пользователь: {user['full_name']} (ID: {user_id})\n"
        f"Текущий баланс: {user['rub_balance']:.3f} ₽\n\n"
        f"Введите сумму в рублях для добавления (например, 100.50):"
    )
    await state.set_state(AdminAddBalanceStates.waiting_for_amount)

@router.message(AdminAddBalanceStates.waiting_for_amount)
async def admin_add_balance_get_amount(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("❌ Нет доступа")
        await state.clear()
        return
    try:
        amount = float(message.text.replace(',', '.'))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Введите положительное число (например, 100 или 50.75).")
        return
    data = await state.get_data()
    user_id = data["target_user_id"]
    add_balance_rub(user_id, amount)
    user = get_user(user_id)
    await message.answer(
        f"✅ Пользователю {user['full_name']} (ID: {user_id}) добавлено {amount:.2f} ₽.\n"
        f"Новый баланс: {user['rub_balance']:.3f} ₽",
        reply_markup=admin_menu()
    )
    await state.clear()
