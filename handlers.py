import asyncio
import logging
import sqlite3
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode

from config import BOT_TOKEN, STAR_TO_RUB, ADMIN_ID
from database import (
    init_db, get_user, create_user, add_balance_rub, deduct_balance_rub,
    add_order, update_order_status, get_user_orders, get_all_users, get_all_orders
)
from twiboost_api import get_services, add_order as tw_add_order, get_order_status
from keyboards import main_menu, back_button, confirm_keyboard
from states import OrderStates, DepositStates
from utils import calculate_price_rub, calculate_total_rub, safe_decode_link

router = Router()
bot = Bot(token=BOT_TOKEN)

# Кэш услуг
services_cache = []
services_by_network = {}

async def load_services():
    global services_cache, services_by_network
    services_cache = await get_services()
    for s in services_cache:
        net = s.get("network", "Other")
        services_by_network.setdefault(net, []).append(s)
    logging.info(f"Loaded {len(services_cache)} services")

class Pagination:
    def __init__(self, items, page_size=5):
        self.items = items
        self.page_size = page_size
        self.total_pages = (len(items) + page_size - 1) // page_size

    def get_page(self, page):
        start = (page - 1) * self.page_size
        end = start + self.page_size
        return self.items[start:end], page, self.total_pages

# ---------------------- Обычные пользователи ----------------------
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = get_user(message.from_user.id)
    if not user:
        create_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
        user = get_user(message.from_user.id)
    await message.answer(
        f"✨ Добро пожаловать в BlondeBoost!\n\n"
        "Я бот для накрутки услуг Telegram.\n"
        f"💰 Ваш баланс: {user['rub_balance']:.3f} ₽\n\n"
        "Пополните баланс через Telegram Stars (1 Star = 1.5 ₽) и заказывайте услуги.",
        reply_markup=main_menu()
    )

@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = get_user(callback.from_user.id)
    balance = user["rub_balance"] if user else 0.0
    await callback.message.edit_text(
        f"✨ Главное меню\n💰 Баланс: {balance:.3f} ₽",
        reply_markup=main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user = get_user(callback.from_user.id)
    balance = user["rub_balance"] if user else 0.0
    text = (f"👤 *Ваш профиль*\n\n"
            f"ID: {callback.from_user.id}\n"
            f"Имя: {callback.from_user.full_name}\n"
            f"💰 Баланс: {balance:.3f} ₽")
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "deposit")
async def deposit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "💰 Введите сумму пополнения в **Stars** (целое число от 1 до 100 000):\n\n"
        "1 Star = 1.5 ₽ будет зачислено на баланс.\n"
        "Пример: `100`",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_button()
    )
    await state.set_state(DepositStates.waiting_for_stars_amount)
    await callback.answer()

@router.message(DepositStates.waiting_for_stars_amount)
async def process_deposit_amount(message: Message, state: FSMContext):
    if message.text.startswith('/'):
        await state.clear()
        await message.answer("Операция отменена.", reply_markup=main_menu())
        return
    if not message.text.isdigit():
        await message.answer("❌ Введите целое число.")
        return
    stars = int(message.text)
    if stars < 1 or stars > 100000:
        await message.answer("❌ Сумма должна быть от 1 до 100 000 Stars.")
        return
    rub_amount = stars * STAR_TO_RUB
    await bot.send_invoice(
        chat_id=message.chat.id,
        title=f"Пополнение баланса на {stars} Stars",
        description=f"Вы получите {rub_amount:.2f} ₽ на баланс бота",
        payload=f"deposit_{stars}_{rub_amount}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=f"{stars} Stars", amount=stars)],
        start_parameter="deposit"
    )
    await state.clear()

@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext):
    await state.clear()
    payload = message.successful_payment.invoice_payload
    if payload.startswith("deposit_"):
        parts = payload.split("_")
        stars = int(parts[1])
        rub_amount = float(parts[2])
        add_balance_rub(message.from_user.id, rub_amount)
        await message.answer(f"✅ Баланс пополнен на {rub_amount:.2f} ₽ ( {stars} Stars )")
    else:
        await process_order_payment(message)
    await message.answer("Главное меню:", reply_markup=main_menu())

async def process_order_payment(message: Message):
    # формат: order|service_id|quantity|total_rub|link
    payload = message.successful_payment.invoice_payload
    parts = payload.split("|")
    if parts[0] == "order":
        service_id = int(parts[1])
        quantity = int(parts[2])
        total_rub = float(parts[3])
        link = parts[4]
        service = next((s for s in services_cache if s["service"] == service_id), None)
        if not service:
            await message.answer("❌ Ошибка: услуга не найдена. Средства возвращены.")
            add_balance_rub(message.from_user.id, total_rub)
            return
        tw_resp = await tw_add_order(service_id, link, quantity)
        if "order" in tw_resp:
            tw_order_id = tw_resp["order"]
            local_order_id = add_order(
                user_id=message.from_user.id,
                tw_order_id=tw_order_id,
                service_id=service_id,
                service_name=service["name"],
                link=link,
                quantity=quantity,
                price_rub=total_rub,
                status="processing"
            )
            await message.answer(
                f"✅ Заказ #{local_order_id} принят!\n"
                f"Услуга: {service['name']}\n"
                f"Количество: {quantity}\n"
                f"Списано: {total_rub:.3f} ₽\n"
                f"Статус: выполняется..."
            )
        else:
            add_balance_rub(message.from_user.id, total_rub)
            await message.answer(
                f"❌ Ошибка при создании заказа. Средства возвращены.\n"
                f"Попробуйте позже."
            )

@router.callback_query(F.data == "history")
async def show_history(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    orders = get_user_orders(callback.from_user.id, limit=10)
    if not orders:
        text = "📜 У вас пока нет заказов."
    else:
        text = "📜 *Последние заказы:*\n\n"
        for o in orders:
            text += f"#{o[0]} | {o[1]} | {o[2]} ед. | {o[3]:.3f} ₽ | {o[4]}\n{o[5]}\n\n"
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_button())
    await callback.answer()

# ---------------------- Категории и выбор услуги ----------------------
@router.callback_query(F.data.startswith("cat_"))
async def show_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    cat = callback.data.split("_")[1]
    filtered = []
    for s in services_cache:
        net = s.get("network")
        name = s["name"].lower()
        if cat == "views" and net == "Telegram" and ("просмотры на пост" in name or "просмотры [" in name) and "историю" not in name and "бусты" not in name:
            filtered.append(s)
        elif cat == "reactions" and net == "Telegram" and ("реакци" in name or "реакция" in name):
            filtered.append(s)
        elif cat == "subscribers" and net == "Telegram" and "подписчик" in name:
            filtered.append(s)
        elif cat == "boosts" and net == "Telegram" and "буст" in name:
            filtered.append(s)
        elif cat == "starts" and net == "Telegram" and ("старты бота" in name or "старт бота" in name):
            filtered.append(s)
        elif cat == "comments" and net == "Telegram" and "комментар" in name:
            filtered.append(s)
        elif cat == "polls" and net == "Telegram" and ("голоса" in name or "опрос" in name):
            filtered.append(s)
        elif cat == "reposts" and net == "Telegram" and "репост" in name:
            filtered.append(s)
        elif cat == "premium" and net == "Telegram Premium":
            filtered.append(s)
    if not filtered:
        await callback.message.edit_text("В этой категории нет услуг.", reply_markup=back_button())
        await callback.answer()
        return
    await state.update_data(category_services=filtered, category_name=cat, page=1)
    await send_category_page(callback.message, cat, filtered, 1, state)
    await callback.answer()

async def send_category_page(message, cat, services, page, state):
    pag = Pagination(services, page_size=5)
    items, current_page, total_pages = pag.get_page(page)
    text = f"📂 Категория: {cat}\n\nВыберите услугу (страница {current_page}/{total_pages}):\n"
    buttons = []
    for s in items:
        price_rub = calculate_price_rub(s["service"], float(s["rate"]))
        text += f"🔹 {s['name']}\n   Цена: {price_rub:.2f} ₽/1000\n"
        buttons.append([InlineKeyboardButton(text=s['name'][:30], callback_data=f"service_{s['service']}")])
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"page_{cat}_{current_page-1}"))
    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"page_{cat}_{current_page+1}"))
    if nav_buttons:
        buttons.append(nav_buttons)
    buttons.append([InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")])
    await message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("page_"))
async def paginate_callback(callback: CallbackQuery, state: FSMContext):
    _, cat, page_str = callback.data.split("_")
    page = int(page_str)
    data = await state.get_data()
    services = data.get("category_services")
    if not services:
        await callback.answer("Ошибка, попробуйте снова")
        return
    await send_category_page(callback.message, cat, services, page, state)
    await callback.answer()

@router.callback_query(F.data.startswith("service_"))
async def service_selected(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    service_id = int(callback.data.split("_")[1])
    service = next((s for s in services_cache if s["service"] == service_id), None)
    if not service:
        await callback.answer("Услуга не найдена")
        return
    price_rub_per_1000 = calculate_price_rub(service_id, float(service["rate"]))
    await state.update_data(service_id=service_id, service=service, price_rub_per_1000=price_rub_per_1000)
    await callback.message.edit_text(
        f"📦 *{service['name']}*\n"
        f"💰 Цена: {price_rub_per_1000:.2f} ₽ за 1000 ед.\n"
        f"📊 Мин: {service['min']} | Макс: {service['max']}\n\n"
        f"Введите ссылку на пост/канал/профиль:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=back_button()
    )
    await state.set_state(OrderStates.waiting_for_link)
    await callback.answer()

@router.message(OrderStates.waiting_for_link)
async def get_link(message: Message, state: FSMContext):
    # Если ввели команду — отменяем состояние
    if message.text.startswith('/'):
        await state.clear()
        await message.answer("Команда отменена. Возврат в главное меню.", reply_markup=main_menu())
        return
    link = message.text.strip()
    if not link.startswith("https://t.me/") and not link.startswith("http://t.me/"):
        await message.answer("❌ Введите корректную ссылку Telegram (начинается с https://t.me/)")
        return
    await state.update_data(link=link)
    await message.answer("Введите количество (целое число):")
    await state.set_state(OrderStates.waiting_for_quantity)

@router.message(OrderStates.waiting_for_quantity)
async def get_quantity(message: Message, state: FSMContext):
    if message.text.startswith('/'):
        await state.clear()
        await message.answer("Команда отменена. Возврат в главное меню.", reply_markup=main_menu())
        return
    if not message.text.isdigit():
        await message.answer("❌ Введите целое число")
        return
    quantity = int(message.text)
    data = await state.get_data()
    service = data["service"]
    if quantity < service["min"] or quantity > service["max"]:
        await message.answer(f"❌ Количество должно быть от {service['min']} до {service['max']}")
        return
    price_rub_per_1000 = data["price_rub_per_1000"]
    total_rub = calculate_total_rub(price_rub_per_1000, quantity)
    await state.update_data(quantity=quantity, total_rub=total_rub)
    await message.answer(
        f"📋 *Подтверждение заказа*\n"
        f"Услуга: {service['name']}\n"
        f"Ссылка: {data['link']}\n"
        f"Количество: {quantity}\n"
        f"💰 Сумма: {total_rub:.3f} ₽\n\n"
        f"Подтверждаете?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=confirm_keyboard(service["service"], data["link"], quantity, total_rub)
    )
    await state.set_state(OrderStates.confirm)

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    # формат: confirm_serviceId_quantity_totalRub_link
    service_id = int(parts[1])
    quantity = int(parts[2])
    total_rub = float(parts[3])
    encoded_link = "_".join(parts[4:])
    link = safe_decode_link(encoded_link)
    service = next((s for s in services_cache if s["service"] == service_id), None)
    if not service:
        await callback.answer("Услуга не найдена")
        return
    user = get_user(callback.from_user.id)
    if user["rub_balance"] < total_rub:
        await callback.message.edit_text(
            f"❌ Недостаточно средств. Ваш баланс: {user['rub_balance']:.3f} ₽\nПополните баланс в главном меню.",
            reply_markup=back_button()
        )
        await state.clear()
        await callback.answer()
        return
    # Списание рублей
    if not deduct_balance_rub(callback.from_user.id, total_rub):
        await callback.message.edit_text("❌ Ошибка списания средств. Попробуйте позже.")
        await state.clear()
        return
    # Отправка заказа в Twiboost
    tw_resp = await tw_add_order(service_id, link, quantity)
    if "order" in tw_resp:
        tw_order_id = tw_resp["order"]
        local_order_id = add_order(
            user_id=callback.from_user.id,
            tw_order_id=tw_order_id,
            service_id=service_id,
            service_name=service["name"],
            link=link,
            quantity=quantity,
            price_rub=total_rub,
            status="processing"
        )
        await callback.message.edit_text(
            f"✅ Заказ #{local_order_id} принят!\n"
            f"Услуга: {service['name']}\n"
            f"Количество: {quantity}\n"
            f"Списано: {total_rub:.3f} ₽\n"
            f"Статус: выполняется...",
            reply_markup=main_menu()
        )
    else:
        add_balance_rub(callback.from_user.id, total_rub)
        await callback.message.edit_text(
            f"❌ Ошибка при создании заказа. Средства возвращены.\n"
            f"Попробуйте позже.",
            reply_markup=main_menu()
        )
    await state.clear()
    await callback.answer()

# ---------------------- Фоновая проверка статусов ----------------------
async def status_checker():
    while True:
        await asyncio.sleep(60)
        conn = sqlite3.connect("blondeboost.db")
        c = conn.cursor()
        c.execute("SELECT order_id, tw_order_id FROM orders WHERE status = 'processing'")
        rows = c.fetchall()
        conn.close()
        for order_id, tw_order_id in rows:
            status_data = await get_order_status(tw_order_id)
            tw_status = status_data.get("status")
            if tw_status == "Completed":
                update_order_status(order_id, "completed", str(status_data))
                conn2 = sqlite3.connect("blondeboost.db")
                c2 = conn2.cursor()
                c2.execute("SELECT user_id FROM orders WHERE order_id = ?", (order_id,))
                user_id_row = c2.fetchone()
                conn2.close()
                if user_id_row:
                    try:
                        await bot.send_message(user_id_row[0], f"✅ Ваш заказ #{order_id} выполнен!")
                    except:
                        pass
            elif tw_status in ("Canceled", "Fail"):
                update_order_status(order_id, "failed", str(status_data))
