import asyncio
import logging
import sqlite3
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode

from config import BOT_TOKEN, STAR_TO_RUB
from database import (
    get_user, create_user, add_balance_rub, deduct_balance_rub,
    add_order, update_order_status, get_user_orders
)
from twiboost_api import get_services, add_order as tw_add_order, get_order_status
from keyboards import (
    main_menu, back_button, confirm_keyboard, admin_menu,
    views_submenu, reactions_submenu, subscribers_submenu,
    boosts_submenu, starts_submenu, comments_submenu, polls_submenu,
    reposts_submenu, live_submenu
)
from states import OrderStates, DepositStates, DynamicOrderStates
from utils import calculate_price_rub, calculate_total_rub, safe_decode_link
from service_schemas import get_schema_for_service, FIELD_LINK, FIELD_QUANTITY, FIELD_POSTS_COUNT, FIELD_VOTE_OPTION, FIELD_COMMENT_TEXT

router = Router()
bot = Bot(token=BOT_TOKEN)

services_cache = []
services_by_network = {}
price_cache = {}

async def load_services():
    global services_cache, services_by_network, price_cache
    services_cache = await get_services()
    price_cache = {}
    for s in services_cache:
        service_id = s["service"]
        rate = float(s["rate"])
        price_rub = calculate_price_rub(service_id, rate)
        price_cache[service_id] = price_rub
        s["_price_rub"] = price_rub
    for s in services_cache:
        net = s.get("network", "Other")
        services_by_network.setdefault(net, []).append(s)
    logging.info(f"Loaded {len(services_cache)} services")

class Pagination:
    def __init__(self, items, page_size=8):
        self.items = items
        self.page_size = page_size
        self.total_pages = (len(items) + page_size - 1) // page_size
    def get_page(self, page):
        start = (page - 1) * self.page_size
        end = start + self.page_size
        return self.items[start:end], page, self.total_pages

# ---------------------- Фильтры для подкатегорий (исправленные) ----------------------
SUBCATEGORY_FILTERS = {
    # Просмотры
    "views_single": lambda s: ("просмотры на пост" in s["name"].lower() or "просмотры [" in s["name"].lower()) and not any(x in s["name"].lower() for x in ["последних", "будущих", "в минуту", "закрытых", "умные", "авто", "telesco", "историю", "кружочки", "реакц"]),
    "views_multi": lambda s: any(x in s["name"].lower() for x in ["последних постов", "последние посты"]),
    "views_speed": lambda s: "в минуту" in s["name"].lower(),
    "views_private": lambda s: "закрытых каналов" in s["name"].lower() and ("privateviewss" in s["name"].lower() or "для закрытых каналов" in s["name"].lower()),
    "views_smart": lambda s: "умные" in s["name"].lower() or "лесенкой" in s["name"].lower(),
    "views_telesco": lambda s: "telesco.pe" in s["name"].lower(),
    "views_auto": lambda s: "авто просмотры" in s["name"].lower(),
    # Реакции
    "reactions_normal": lambda s: ("реакц" in s["name"].lower() or "реакция" in s["name"].lower()) and "закрытых каналов" not in s["name"].lower() and "закрытом канале" not in s["name"].lower() and "премиум" not in s["name"].lower() and "premium" not in s["name"].lower() and "+ просмотры" not in s["name"].lower(),
    "reactions_private": lambda s: "реакц" in s["name"].lower() and ("закрытых каналов" in s["name"].lower() or "закрытом канале" in s["name"].lower()),
    "reactions_subscribe": lambda s: "подписчик" in s["name"].lower() and ("закрытых каналов" in s["name"].lower() or "закрытом канале" in s["name"].lower() or "для реакций" in s["name"].lower()),
    "reactions_premium": lambda s: ("реакц" in s["name"].lower() or "реакция" in s["name"].lower()) and ("премиум" in s["name"].lower() or "premium" in s["name"].lower()),
    "reactions_plus": lambda s: "реакц" in s["name"].lower() and "+ просмотры" in s["name"].lower(),
    "reactions_auto": lambda s: "авто" in s["name"].lower() and "реакц" in s["name"].lower(),
    # Подписчики
    "subs_normal": lambda s: "подписчик" in s["name"].lower() and not any(x in s["name"].lower() for x in ["авто просмотры", "24/7", "живые", "премиум", "premium", "закрытых каналов", "закрытом канале"]),
    "subs_autoview": lambda s: "подписчик" in s["name"].lower() and "авто просмотры" in s["name"].lower(),
    "subs_online": lambda s: "подписчик" in s["name"].lower() and ("24/7" in s["name"] or "онлайн" in s["name"].lower()),
    "subs_live": lambda s: "подписчик" in s["name"].lower() and "живые" in s["name"].lower(),
    # Бусты
    "boosts_open": lambda s: "буст" in s["name"].lower() and "закрытых" not in s["name"].lower() and "ru" not in s["name"].lower(),
    "boosts_closed": lambda s: "буст" in s["name"].lower() and "закрытых" in s["name"].lower(),
    "boosts_ru": lambda s: "буст" in s["name"].lower() and "ru" in s["name"].lower(),
    # Старты бота
    "starts_normal": lambda s: "старты бота" in s["name"].lower() and "активность" not in s["name"].lower() and "премиум" not in s["name"].lower() and "premium" not in s["name"].lower(),
    "starts_activity": lambda s: "старты бота" in s["name"].lower() and "активность" in s["name"].lower(),
    "starts_premium": lambda s: "премиум старты бота" in s["name"].lower() or "telegram premium старты бота" in s["name"].lower(),
    "starts_referral": lambda s: "рефералы для ботов" in s["name"].lower(),
    # Комментарии
    "comments_random": lambda s: "комментар" in s["name"].lower() and "рандомные" in s["name"].lower(),
    "comments_custom": lambda s: "кастомные комментарии" in s["name"].lower(),
    "comments_ai": lambda s: "ии комментарии" in s["name"].lower(),
    # Голоса
    "polls_normal": lambda s: "голоса" in s["name"].lower() or "опрос" in s["name"].lower(),
    # Репосты
    "reposts_posts": lambda s: "репост" in s["name"].lower() and "истори" not in s["name"].lower(),
    "reposts_stories": lambda s: "репост" in s["name"].lower() and "истори" in s["name"].lower(),
    "reposts_geo": lambda s: "репост" in s["name"].lower() and any(c in s["name"] for c in ["Италия","Германия","Турция","Израиль","Индонезия","Китай","США","Россия","Индия","Арабские"]),
    # Живые
    "live_views": lambda s: "живые" in s["name"].lower() and ("просмотр" in s["name"].lower() or "просмотры" in s["name"].lower()),
    "live_subs": lambda s: "живые" in s["name"].lower() and "подписчик" in s["name"].lower(),
    "live_comments": lambda s: "живые" in s["name"].lower() and "комментар" in s["name"].lower(),
    "live_reactions": lambda s: "живые" in s["name"].lower() and ("реакц" in s["name"].lower() or "лайк" in s["name"].lower()),
}

# ---------------------- Вспомогательные функции для динамического заказа ----------------------
async def ask_next_field(message: Message, state: FSMContext):
    data = await state.get_data()
    idx = data.get("field_index", 0)
    fields = data["schema"]["fields"]
    if idx >= len(fields):
        await create_dynamic_order(message, state)
        return
    field = fields[idx]
    prompt = field.get("prompt", f"Введите {field['name']}:")
    if "example" in field:
        prompt += f"\n📝 Пример: {field['example']}"
    if field["type"] == "days":
        buttons = [[InlineKeyboardButton(text=opt, callback_data=f"days_{idx}_{opt}")] for opt in field["options"]]
        buttons.append([InlineKeyboardButton(text="🔙 Отмена", callback_data="main_menu")])
        await message.answer(prompt, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    else:
        await message.answer(prompt, reply_markup=back_button())
    await state.set_state(DynamicOrderStates.waiting_for_field)

async def validate_field(field, value: str, service_name: str):
    if field["type"] == FIELD_LINK:
        if not value.startswith(("https://t.me/", "http://t.me/")):
            return False, None, "❌ Ссылка должна начинаться с https://t.me/ или http://t.me/"
        if "закрытых каналов" in service_name.lower() or "закрытом канале" in service_name.lower() or "private" in service_name.lower():
            if "/c/" not in value:
                return False, None, "❌ Для закрытого канала ссылка должна быть в формате https://t.me/c/123456789/301"
        return True, value, ""
    elif field["type"] == FIELD_QUANTITY:
        if not value.isdigit():
            return False, None, "❌ Введите целое число"
        return True, int(value), ""
    elif field["type"] == FIELD_POSTS_COUNT:
        if not value.isdigit():
            return False, None, "❌ Введите целое число"
        cnt = int(value)
        if cnt < 1 or cnt > 100:
            return False, None, "❌ Количество будущих постов должно быть от 1 до 100"
        return True, cnt, ""
    elif field["type"] == FIELD_VOTE_OPTION:
        if not value.isdigit():
            return False, None, "❌ Введите номер варианта (целое число)"
        opt = int(value)
        if opt < 1:
            return False, None, "❌ Номер варианта должен быть положительным"
        return True, opt, ""
    elif field["type"] == FIELD_COMMENT_TEXT:
        if len(value.strip()) < 1:
            return False, None, "❌ Введите текст комментария"
        return True, value.strip(), ""
    else:
        return True, value, ""

@router.message(DynamicOrderStates.waiting_for_field)
async def dynamic_field_text(message: Message, state: FSMContext):
    if message.text.startswith('/'):
        await state.clear()
        await message.answer("Заказ отменён.", reply_markup=main_menu())
        return
    data = await state.get_data()
    idx = data.get("field_index", 0)
    fields = data["schema"]["fields"]
    if idx >= len(fields):
        return
    field = fields[idx]
    ok, value, error = await validate_field(field, message.text.strip(), data["service"]["name"])
    if not ok:
        await message.answer(error)
        return
    collected = data.get("collected_fields", {})
    collected[field["name"]] = value
    await state.update_data(collected_fields=collected, field_index=idx+1)
    await ask_next_field(message, state)

@router.callback_query(F.data.startswith("days_"))
async def dynamic_field_days(callback: CallbackQuery, state: FSMContext):
    _, idx_str, days_value = callback.data.split("_", 2)
    idx = int(idx_str)
    data = await state.get_data()
    fields = data["schema"]["fields"]
    if idx >= len(fields):
        await callback.answer("Ошибка")
        return
    collected = data.get("collected_fields", {})
    collected[fields[idx]["name"]] = days_value
    await state.update_data(collected_fields=collected, field_index=idx+1)
    await ask_next_field(callback.message, state)
    await callback.answer()

async def create_dynamic_order(message: Message, state: FSMContext):
    data = await state.get_data()
    service = data["service"]
    service_id = service["service"]
    collected = data["collected_fields"]
    link = collected.get("link")
    quantity = collected.get("quantity")
    if not link or not quantity:
        await message.answer("❌ Не все обязательные поля заполнены.", reply_markup=main_menu())
        await state.clear()
        return
    rate = float(service["rate"])
    price_rub_per_1000 = calculate_price_rub(service_id, rate)
    total_rub = calculate_total_rub(price_rub_per_1000, quantity)
    user = get_user(message.from_user.id)
    if user["rub_balance"] < total_rub:
        await message.answer(f"❌ Недостаточно средств. Ваш баланс: {user['rub_balance']:.3f} ₽", reply_markup=main_menu())
        await state.clear()
        return
    if not deduct_balance_rub(message.from_user.id, total_rub):
        await message.answer("❌ Ошибка списания средств.", reply_markup=main_menu())
        await state.clear()
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
            f"Статус: выполняется...",
            reply_markup=main_menu()
        )
    else:
        add_balance_rub(message.from_user.id, total_rub)
        await message.answer("❌ Ошибка при создании заказа. Средства возвращены.", reply_markup=main_menu())
    await state.clear()

# ---------------------- Основные команды ----------------------
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = get_user(message.from_user.id)
    if not user:
        create_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
        user = get_user(message.from_user.id)
    await message.answer(
        f"✨ Добро пожаловать в BlondeBoost!\n\n"
        f"💰 Ваш баланс: {user['rub_balance']:.3f} ₽\n\n"
        "Пополните баланс через Telegram Stars (1 Star = 1.25 ₽) и заказывайте услуги.",
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
    text = f"👤 *Ваш профиль*\n\nID: {callback.from_user.id}\nИмя: {callback.from_user.full_name}\n💰 Баланс: {balance:.3f} ₽"
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "deposit")
async def deposit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "💰 Введите сумму пополнения в **Stars** (целое число от 1 до 100 000):\n\n"
        "1 Star = 1.25 ₽ будет зачислено на баланс.\n"
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
        description=f"Вы получите {rub_amount:.2f} ₽ на баланс",
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
            await message.answer("❌ Ошибка при создании заказа. Средства возвращены.")

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

# ---------------------- Категории и подкатегории ----------------------
@router.callback_query(F.data.startswith("cat_"))
async def show_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    cat = callback.data.split("_")[1]
    if cat == "views":
        await callback.message.edit_text("📸 Выберите тип просмотров:", reply_markup=views_submenu())
    elif cat == "reactions":
        await callback.message.edit_text("❤️ Выберите тип реакций:", reply_markup=reactions_submenu())
    elif cat == "subscribers":
        await callback.message.edit_text("👥 Выберите тип подписчиков:", reply_markup=subscribers_submenu())
    elif cat == "boosts":
        await callback.message.edit_text("🚀 Выберите тип бустов:", reply_markup=boosts_submenu())
    elif cat == "starts":
        await callback.message.edit_text("🤖 Выберите тип стартов бота:", reply_markup=starts_submenu())
    elif cat == "comments":
        await callback.message.edit_text("✏️ Выберите тип комментариев:", reply_markup=comments_submenu())
    elif cat == "polls":
        await callback.message.edit_text("🗳 Выберите тип голосований:", reply_markup=polls_submenu())
    elif cat == "reposts":
        await callback.message.edit_text("🔄 Выберите тип репостов:", reply_markup=reposts_submenu())
    elif cat == "live":
        await callback.message.edit_text("👨‍🦱 Выберите тип живых услуг:", reply_markup=live_submenu())
    else:
        await callback.message.edit_text("Категория временно недоступна.", reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data.startswith("sub_"))
async def handle_subcategory(callback: CallbackQuery, state: FSMContext):
    sub = callback.data.split("_", 1)[1]
    if sub not in SUBCATEGORY_FILTERS:
        await callback.answer("Подкатегория не найдена")
        return
    filter_func = SUBCATEGORY_FILTERS[sub]
    filtered = [s for s in services_cache if filter_func(s) and s.get("network") in ("Telegram", "Telegram Premium")]
    if not filtered:
        await callback.message.edit_text("В этой подкатегории пока нет услуг.", reply_markup=back_button())
        return
    filtered.sort(key=lambda s: s.get("_price_rub", float(s["rate"])))
    await state.update_data(category_services=filtered, category_name=sub, page=1, sort_order="asc")
    await send_category_page(callback.message, sub, filtered, 1, state)
    await callback.answer()

async def send_category_page(message, cat, services, page, state):
    pag = Pagination(services, page_size=8)
    items, current_page, total_pages = pag.get_page(page)
    text = f"📂 Категория: {cat}\n\nСтраница {current_page}/{total_pages}\n\n"
    buttons = []
    for s in items:
        price_rub = s.get("_price_rub", calculate_price_rub(s["service"], float(s["rate"])))
        text += f"🔹 {s['name']}\n   Цена: {price_rub:.2f} ₽/1000\n\n"
        buttons.append([InlineKeyboardButton(text=s['name'][:30], callback_data=f"service_{s['service']}")])
    nav = []
    if current_page > 1:
        nav.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"page|{cat}|{current_page-1}"))
    if current_page < total_pages:
        nav.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"page|{cat}|{current_page+1}"))
    if nav:
        buttons.append(nav)
    data = await state.get_data()
    sort_order = data.get("sort_order", "asc")
    sort_buttons = [
        InlineKeyboardButton(text="💰 По возрастанию" + (" ✅" if sort_order == "asc" else ""), callback_data=f"sort|{cat}|asc"),
        InlineKeyboardButton(text="💰 По убыванию" + (" ✅" if sort_order == "desc" else ""), callback_data=f"sort|{cat}|desc"),
        InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")
    ]
    buttons.append(sort_buttons)
    await message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@router.callback_query(F.data.startswith("page|"))
async def paginate_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("processing"):
        await callback.answer("Подождите...")
        return
    await state.update_data(processing=True)
    try:
        _, cat, page_str = callback.data.split("|")
        page = int(page_str)
        services = data.get("category_services")
        if not services:
            await callback.answer("Ошибка")
            return
        await send_category_page(callback.message, cat, services, page, state)
    except Exception as e:
        logging.error(f"Paginate error: {e}")
        await callback.answer("Ошибка")
    finally:
        await state.update_data(processing=False)
    await callback.answer()

@router.callback_query(F.data.startswith("sort|"))
async def sort_services(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("processing"):
        await callback.answer("Подождите...")
        return
    await state.update_data(processing=True)
    try:
        _, cat, order = callback.data.split("|")
        services = data.get("category_services", [])
        if not services:
            await callback.answer("Ошибка")
            return
        services_sorted = sorted(services, key=lambda s: s.get("_price_rub", float(s["rate"])), reverse=(order == "desc"))
        await state.update_data(category_services=services_sorted, sort_order=order, page=1)
        await send_category_page(callback.message, cat, services_sorted, 1, state)
    except Exception as e:
        logging.error(f"Sort error: {e}")
        await callback.answer("Ошибка")
    finally:
        await state.update_data(processing=False)
    await callback.answer()

# ---------------------- Выбор конкретной услуги ----------------------
@router.callback_query(F.data.startswith("service_"))
async def service_selected(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    service_id = int(callback.data.split("_")[1])
    service = next((s for s in services_cache if s["service"] == service_id), None)
    if not service:
        await callback.answer("Услуга не найдена")
        return
    schema = get_schema_for_service(service_id, service["name"])
    if schema:
        await state.update_data(service_id=service_id, service=service, schema=schema, collected_fields={})
        await start_dynamic_order(callback.message, state, schema)
    else:
        price_rub_per_1000 = calculate_price_rub(service_id, float(service["rate"]))
        await state.update_data(service_id=service_id, service=service, price_rub_per_1000=price_rub_per_1000)
        await callback.message.edit_text(
            f"📦 *{service['name']}*\n💰 Цена: {price_rub_per_1000:.2f} ₽/1000\n📊 Мин: {service['min']} | Макс: {service['max']}\n\nВведите ссылку:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=back_button()
        )
        await state.set_state(OrderStates.waiting_for_link)
    await callback.answer()

async def start_dynamic_order(message, state, schema):
    fields = schema.get("fields", [])
    if not fields:
        await message.answer("Ошибка: нет полей для заказа.", reply_markup=main_menu())
        return
    await state.update_data(field_index=0, total_fields=len(fields))
    if "pre_check" in schema:
        # Создаём кнопки, если они указаны в схеме
        buttons = []
        if "buttons" in schema and isinstance(schema["buttons"], list):
            for btn in schema["buttons"]:
                buttons.append([InlineKeyboardButton(text=btn["text"], callback_data=btn["callback"])])
        buttons.append([InlineKeyboardButton(text="Понятно, продолжить", callback_data="continue_dynamic")])
        await message.answer(schema["pre_check"], parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        await state.set_state(DynamicOrderStates.waiting_for_continue)
    else:
        await ask_next_field(message, state)

@router.callback_query(F.data == "continue_dynamic")
async def continue_dynamic(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await ask_next_field(callback.message, state)
    await callback.answer()

@router.callback_query(F.data == "sub_reactions_subscribe")
async def redirect_to_subscribe(callback: CallbackQuery, state: FSMContext):
    """Перенаправление из предупреждения в подкатегорию подписчиков для закрытых каналов"""
    await callback.message.delete()
    filter_func = SUBCATEGORY_FILTERS.get("reactions_subscribe")
    if not filter_func:
        await callback.message.answer("Подкатегория не найдена.", reply_markup=back_button())
        return
    filtered = [s for s in services_cache if filter_func(s) and s.get("network") in ("Telegram", "Telegram Premium")]
    if not filtered:
        await callback.message.answer("В этой подкатегории пока нет услуг.", reply_markup=back_button())
        return
    filtered.sort(key=lambda s: s.get("_price_rub", float(s["rate"])))
    await state.update_data(category_services=filtered, category_name="reactions_subscribe", page=1, sort_order="asc")
    await send_category_page(callback.message, "reactions_subscribe", filtered, 1, state)
    await callback.answer()

# ---------------------- Стандартный заказ ----------------------
@router.message(OrderStates.waiting_for_link)
async def get_link(message: Message, state: FSMContext):
    if message.text.startswith('/'):
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu())
        return
    link = message.text.strip()
    data = await state.get_data()
    service_name = data.get("service", {}).get("name", "")
    if not link.startswith(("https://t.me/", "http://t.me/")):
        await message.answer("❌ Ссылка должна начинаться с https://t.me/")
        return
    if ("закрытых каналов" in service_name.lower() or "закрытом канале" in service_name.lower()) and "/c/" not in link:
        await message.answer("❌ Для закрытого канала ссылка должна быть формата https://t.me/c/123456789/301")
        return
    await state.update_data(link=link)
    await message.answer("Введите количество (целое число):")
    await state.set_state(OrderStates.waiting_for_quantity)

@router.message(OrderStates.waiting_for_quantity)
async def get_quantity(message: Message, state: FSMContext):
    if message.text.startswith('/'):
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu())
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
        f"📋 *Подтверждение заказа*\nУслуга: {service['name']}\nСсылка: {data['link']}\nКоличество: {quantity}\n💰 Сумма: {total_rub:.3f} ₽\n\nПодтверждаете?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=confirm_keyboard(service["service"], data["link"], quantity, total_rub)
    )
    await state.set_state(OrderStates.confirm)

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
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
        await callback.message.edit_text(f"❌ Недостаточно средств. Баланс: {user['rub_balance']:.3f} ₽", reply_markup=back_button())
        await state.clear()
        await callback.answer()
        return
    if not deduct_balance_rub(callback.from_user.id, total_rub):
        await callback.message.edit_text("❌ Ошибка списания средств.", reply_markup=back_button())
        await state.clear()
        return
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
            f"✅ Заказ #{local_order_id} принят!\nУслуга: {service['name']}\nКоличество: {quantity}\nСписано: {total_rub:.3f} ₽",
            reply_markup=main_menu()
        )
    else:
        add_balance_rub(callback.from_user.id, total_rub)
        await callback.message.edit_text("❌ Ошибка при создании заказа. Средства возвращены.", reply_markup=main_menu())
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

# ---------------------- Админ-панель (базовая) ----------------------
from config import ADMIN_ID
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

@router.message(Command("admin_panel"))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    if not is_admin(message.from_user.id):
        await message.answer("❌ Нет доступа.")
        return
    await message.answer("🔧 *Админ-панель*", parse_mode=ParseMode.MARKDOWN, reply_markup=admin_menu())