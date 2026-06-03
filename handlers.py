import asyncio
import logging
import sqlite3
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

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
from service_schemas import (
    get_schema_for_service,
    SUBCATEGORY_TO_SCHEMA,
    FIELD_LINK, FIELD_QUANTITY, FIELD_POSTS_COUNT, FIELD_VOTE_OPTION, FIELD_COMMENT_TEXT, FIELD_REACTION_ID
)

router = Router()
bot = Bot(token=BOT_TOKEN)

services_cache = []
services_by_network = {}
price_cache = {}


def safe_md(text: str) -> str:
    for ch in ("_", "*", "`", "["):
        text = text.replace(ch, f"\\{ch}")
    return str(text)


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


# ── Subcategory filters ────────────────────────────────────────────────────
SUBCATEGORY_FILTERS = {
    # Просмотры
    "views_single": lambda s: (
        "просмотры на пост" in s["name"].lower()
        or "просмотры [" in s["name"].lower()
    ) and not any(
        x in s["name"].lower()
        for x in [
            "последних", "будущих", "в минуту", "закрытых", "умные",
            "авто", "telesco", "историю", "кружочки", "реакц", "подписчик",
        ]
    ),
    "views_multi":   lambda s: any(x in s["name"].lower() for x in ["последних постов", "последние посты"]) and "подписчик" not in s["name"].lower(),
    "views_speed":   lambda s: "в минуту" in s["name"].lower() and "подписчик" not in s["name"].lower(),
    "views_private": lambda s: "закрытых каналов" in s["name"].lower() and ("privateviewss" in s["name"].lower() or "для закрытых каналов" in s["name"].lower()) and "подписчик" not in s["name"].lower(),
    "views_smart":   lambda s: ("умные" in s["name"].lower() or "лесенкой" in s["name"].lower()) and "подписчик" not in s["name"].lower(),
    "views_telesco": lambda s: "telesco.pe" in s["name"].lower() and "подписчик" not in s["name"].lower(),
    "views_auto":    lambda s: "авто просмотры" in s["name"].lower() and "подписчик" not in s["name"].lower(),
    "views_stories": lambda s: ("просмотры на историю" in s["name"].lower() or "просмотры историй" in s["name"].lower()) and "подписчик" not in s["name"].lower(),
    # Реакции
    "reactions_normal":    lambda s: ("реакц" in s["name"].lower() or "реакция" in s["name"].lower()) and "закрытых каналов" not in s["name"].lower() and "закрытом канале" not in s["name"].lower() and "премиум" not in s["name"].lower() and "premium" not in s["name"].lower() and "+ просмотры" not in s["name"].lower() and "подписчик" not in s["name"].lower(),
    "reactions_private":   lambda s: "реакц" in s["name"].lower() and ("закрытых каналов" in s["name"].lower() or "закрытом канале" in s["name"].lower()),
    "reactions_subscribe": lambda s: "подписчик" in s["name"].lower() and ("закрытых каналов" in s["name"].lower() or "закрытом канале" in s["name"].lower() or "для реакций" in s["name"].lower()),
    "reactions_premium":   lambda s: ("реакц" in s["name"].lower() or "реакция" in s["name"].lower()) and ("премиум" in s["name"].lower() or "premium" in s["name"].lower()),
    "reactions_plus":      lambda s: "реакц" in s["name"].lower() and "+ просмотры" in s["name"].lower(),
    "reactions_auto":      lambda s: "авто" in s["name"].lower() and "реакц" in s["name"].lower(),
    # Подписчики
    "subs_normal":   lambda s: "подписчик" in s["name"].lower() and not any(x in s["name"].lower() for x in ["авто просмотры", "24/7", "живые", "премиум", "premium", "закрытых каналов", "закрытом канале"]),
    "subs_autoview": lambda s: "подписчик" in s["name"].lower() and "авто просмотры" in s["name"].lower(),
    "subs_online":   lambda s: "подписчик" in s["name"].lower() and ("24/7" in s["name"] or "онлайн" in s["name"].lower()),
    "subs_live":     lambda s: "подписчик" in s["name"].lower() and "живые" in s["name"].lower(),
    # Бусты
    "boosts_open":   lambda s: "буст" in s["name"].lower() and "закрытых" not in s["name"].lower() and "ru" not in s["name"].lower(),
    "boosts_closed": lambda s: "буст" in s["name"].lower() and "закрытых" in s["name"].lower(),
    "boosts_ru":     lambda s: "буст" in s["name"].lower() and "ru" in s["name"].lower(),
    # Старты бота
    "starts_normal":   lambda s: "старты бота" in s["name"].lower() and "активность" not in s["name"].lower() and "премиум" not in s["name"].lower() and "premium" not in s["name"].lower(),
    "starts_activity": lambda s: "старты бота" in s["name"].lower() and "активность" in s["name"].lower(),
    "starts_premium":  lambda s: "премиум старты бота" in s["name"].lower() or "telegram premium старты бота" in s["name"].lower(),
    "starts_referral": lambda s: "рефералы для ботов" in s["name"].lower(),
    # Комментарии
    "comments_random": lambda s: "комментар" in s["name"].lower() and "рандомные" in s["name"].lower(),
    "comments_custom": lambda s: "кастомные комментарии" in s["name"].lower(),
    "comments_ai":     lambda s: "ии комментарии" in s["name"].lower(),
    # Голоса
    "polls_normal": lambda s: "голоса" in s["name"].lower() or "опрос" in s["name"].lower(),
    # Репосты
    "reposts_posts":   lambda s: "репост" in s["name"].lower() and "истори" not in s["name"].lower() and not any(c in s["name"] for c in ["Италия","Германия","Турция","Израиль","Индонезия","Китай","США","Россия","Индия","Арабские"]),
    "reposts_stories": lambda s: "репост" in s["name"].lower() and "истори" in s["name"].lower(),
    "reposts_geo":     lambda s: "репост" in s["name"].lower() and any(c in s["name"] for c in ["Италия","Германия","Турция","Израиль","Индонезия","Китай","США","Россия","Индия","Арабские"]),
    # Живые
    "live_subs": lambda s: "живые" in s["name"].lower() and "подписчик" in s["name"].lower(),
}

# Maps subcategory prefix → cat_ callback value for "Back to submenu" button
_SUBCAT_PREFIX_TO_CAT = {
    "views":     "views",
    "reactions": "reactions",
    "subs":      "subscribers",
    "boosts":    "boosts",
    "starts":    "starts",
    "comments":  "comments",
    "polls":     "polls",
    "reposts":   "reposts",
    "live":      "live",
}


def _parent_cat(subcat: str) -> str:
    prefix = subcat.split("_")[0]
    return _SUBCAT_PREFIX_TO_CAT.get(prefix, "")


# ── Short instructions per subcategory (shown inline in first field prompt) ─
SUBCATEGORY_INSTRUCTIONS = {
    # ── Просмотры ─────────────────────────────────────────────────────────
    "views_single": (
        "Просмотры добавятся на один конкретный пост.\n\n"
        "Нужна ссылка именно на ПОСТ, а не на канал.\n"
        "Как найти: откройте нужный пост в канале → нажмите «Поделиться» → «Скопировать ссылку».\n"
        "Пример ссылки: https://t.me/durov/123\n"
        "Число 123 в конце — это номер поста. Если его нет — вы скопировали ссылку на канал."
    ),
    "views_multi": (
        "Просмотры добавятся на несколько ПОСЛЕДНИХ постов канала сразу.\n\n"
        "Нужна ссылка на КАНАЛ (без номера поста в конце).\n"
        "Пример: https://t.me/durov\n\n"
        "Сколько постов получат просмотры — указано в названии услуги.\n"
        "Итоговое списание = просмотры × количество постов.\n"
        "Например: 1 000 просмотров × 10 постов = 10 000 просмотров списывается."
    ),
    "views_speed": (
        "Просмотры на конкретный пост, но приходят медленно — 1 до 70 в минуту.\n"
        "Это специально: имитирует реальный органический трафик.\n\n"
        "Нужна ссылка на ПОСТ (не на канал).\n"
        "Как найти: откройте пост → «Поделиться» → «Скопировать ссылку».\n"
        "Пример: https://t.me/durov/123\n\n"
        "Скорость фиксирована в выбранной услуге и не меняется."
    ),
    "views_private": (
        "Просмотры для постов в ЗАКРЫТОМ (приватном) канале.\n\n"
        "Перед заказом ОБЯЗАТЕЛЬНО:\n"
        "1. Откройте ваш закрытый канал → Настройки → Администраторы\n"
        "2. Добавьте бота @privateviewss_bot как администратора\n"
        "3. Дайте право «Публикация сообщений» или «Репосты»\n\n"
        "Ссылка на пост в закрытом канале выглядит так:\n"
        "https://t.me/c/1234567890/301\n"
        "Найти: откройте пост → «Поделиться» → «Скопировать ссылку».\n\n"
        "Без бота-администратора накрутка НЕ сработает, деньги не возвращаются."
    ),
    "views_smart": (
        "«Умные» просмотры приходят нарастающим темпом — сначала медленно, потом быстрее.\n"
        "Это имитирует вирусный рост публикации и выглядит максимально естественно.\n\n"
        "Нужна ссылка на ПОСТ.\n"
        "Пример: https://t.me/durov/123\n\n"
        "Диапазон: от 300 до 30 000 просмотров.\n"
        "Время выполнения: от 1 до 24 часов в зависимости от объёма."
    ),
    "views_telesco": (
        "Просмотры для видео-кружочков (круглых видео в Telegram).\n\n"
        "Как найти ссылку на кружочек:\n"
        "1. Откройте нужный кружочек в канале\n"
        "2. Нажмите на него, чтобы открылся плеер\n"
        "3. Нажмите «Поделиться» (или «...») → «Скопировать ссылку»\n\n"
        "Обычная ссылка на пост НЕ подойдёт — нужна именно ссылка на кружочек.\n"
        "Пример: https://t.me/channelname/123"
    ),
    "views_auto": (
        "Авто-просмотры: каждый НОВЫЙ пост в канале автоматически получит просмотры.\n\n"
        "Нужна ссылка на КАНАЛ (без номера поста).\n"
        "Пример: https://t.me/durov\n\n"
        "Далее вы укажете:\n"
        "• На сколько будущих постов (например 30)\n"
        "• Сколько просмотров на каждый пост\n\n"
        "Итоговое списание = кол-во постов × просмотры на каждый пост."
    ),
    "views_stories": (
        "Просмотры добавляются на историю (Story) в Telegram.\n\n"
        "Как найти ссылку на историю:\n"
        "1. Откройте историю\n"
        "2. Нажмите «...» (три точки) → «Поделиться» → «Скопировать ссылку»\n\n"
        "Формат ссылки: https://t.me/username/s/НОМЕР\n"
        "Пример: https://t.me/durov/s/5\n\n"
        "История должна быть активной — не истёкшей и не удалённой."
    ),

    # ── Реакции ───────────────────────────────────────────────────────────
    "reactions_normal": (
        "Реакции (лайки с выбранным эмодзи) добавятся под ваш пост.\n"
        "Какой именно эмодзи — указано в названии выбранной услуги.\n\n"
        "Нужна ссылка на ПОСТ (не на канал).\n"
        "Как найти: откройте пост → «Поделиться» → «Скопировать ссылку».\n"
        "Пример: https://t.me/durov/123\n\n"
        "Максимум: 150 000 реакций. Старт: в течение 15 минут после оплаты."
    ),
    "reactions_private": (
        "Реакции для поста в ЗАКРЫТОМ канале.\n\n"
        "Важно: реакции ставят аккаунты, которые уже состоят в вашем закрытом канале.\n"
        "Поэтому количество реакций не может быть больше числа подписчиков.\n\n"
        "Если подписчиков ещё нет — сначала закажите их (кнопка «Назад» → «Заказать подписчиков»).\n\n"
        "Ссылка на пост в закрытом канале:\n"
        "Формат: https://t.me/c/1234567890/301\n"
        "Найти: откройте пост → «Поделиться» → «Скопировать ссылку»."
    ),
    "reactions_subscribe": (
        "Это подписчики для ЗАКРЫТОГО канала — нужны перед заказом реакций.\n\n"
        "Нужна ПРИГЛАСИТЕЛЬНАЯ ссылка (не обычная ссылка на канал!).\n\n"
        "Как создать пригласительную ссылку:\n"
        "1. Откройте закрытый канал → Настройки\n"
        "2. Пригласительные ссылки → Создать ссылку\n"
        "3. Скопируйте ссылку вида https://t.me/+XXXXXX\n\n"
        "Обычная ссылка типа https://t.me/mychannel НЕ подойдёт."
    ),
    "reactions_premium": (
        "Реакции с аккаунтов Telegram Premium — выглядят весомее и показывают особые анимации.\n\n"
        "Нужна ссылка на ПОСТ.\n"
        "Пример: https://t.me/durov/123\n\n"
        "На следующем шаге нужен ID реакции:\n"
        "• Для обычной реакции (❤️ 👍 и т.д.) — введите 0\n"
        "• Для кастомной реакции — узнайте ID через @prem_reaction_bot:\n"
        "  откройте бота, отправьте нужный эмодзи, бот вернёт числовой ID."
    ),
    "reactions_plus": (
        "Реакции + просмотры в одном заказе. Просмотры добавятся автоматически, доплачивать не нужно.\n\n"
        "Нужна ссылка на ПОСТ.\n"
        "Пример: https://t.me/durov/123\n\n"
        "Вы указываете только количество реакций.\n"
        "Количество просмотров подберётся пропорционально.\n"
        "Старт: до 15 минут после оплаты."
    ),
    "reactions_auto": (
        "Авто-реакции: каждый НОВЫЙ пост в канале автоматически получит реакции.\n"
        "Какой эмодзи — указан в названии услуги.\n\n"
        "Нужна ссылка на КАНАЛ (без номера поста).\n"
        "Пример: https://t.me/durov\n\n"
        "Далее вы укажете:\n"
        "• На сколько будущих постов\n"
        "• Сколько реакций на каждый пост\n\n"
        "Итоговое списание = кол-во постов × реакций на каждый."
    ),

    # ── Подписчики ────────────────────────────────────────────────────────
    "subs_normal": (
        "Подписчики добавятся в ваш канал или группу.\n\n"
        "Для ОТКРЫТОГО канала — обычная ссылка:\n"
        "https://t.me/username\n\n"
        "Для ЗАКРЫТОГО канала — пригласительная ссылка:\n"
        "https://t.me/+XXXXXX\n"
        "Как создать: Настройки канала → Пригласительные ссылки → Создать.\n\n"
        "Небольшой «отлив» подписчиков после выполнения — это нормально.\n"
        "Гарантия и скорость указаны в названии конкретной услуги."
    ),
    "subs_autoview": (
        "Подписчики, которые автоматически просматривают каждый новый пост в канале.\n"
        "Это повышает охват без дополнительных заказов просмотров.\n\n"
        "Рекомендуется пригласительная ссылка:\n"
        "https://t.me/+XXXXXX\n"
        "Как создать: Настройки канала → Пригласительные ссылки → Создать.\n\n"
        "Просмотры появляются в течение 30 минут после каждого нового поста."
    ),
    "subs_online": (
        "Аккаунты, которые постоянно отображаются онлайн в вашей группе.\n"
        "Повышает доверие к группе у новых посетителей.\n\n"
        "Работает ТОЛЬКО для ГРУПП — не для обычных каналов.\n\n"
        "Нужна пригласительная ссылка:\n"
        "https://t.me/+XXXXXX\n"
        "Как создать: Настройки группы → Пригласительные ссылки → Создать.\n\n"
        "Срок работы онлайн-участников указан в названии услуги."
    ),
    "subs_live": (
        "Реальные живые люди, которые подпишутся на ваш канал через рекламу.\n"
        "Могут лайкать, комментировать, писать в личку — настоящие пользователи.\n\n"
        "Для ОТКРЫТОГО канала: https://t.me/username\n"
        "Для ЗАКРЫТОГО: пригласительная ссылка https://t.me/+XXXXXX\n\n"
        "Скорость поступления медленнее обычных подписчиков — это нормально.\n"
        "Часть может отписаться через время — это естественное поведение реальных людей."
    ),

    # ── Бусты ─────────────────────────────────────────────────────────────
    "boosts_open": (
        "Бусты повышают уровень канала — открывают Stories, кастомные реакции и другие функции.\n\n"
        "ВАЖНО: нужна специальная «буст-ссылка», а НЕ обычная ссылка на канал!\n\n"
        "Как найти буст-ссылку:\n"
        "1. Откройте ваш канал\n"
        "2. Нажмите на название → «Статистика» → вкладка «Бусты»\n"
        "3. Нажмите «Поделиться ссылкой на буст» → скопируйте\n\n"
        "Формат: https://t.me/boost/username\n\n"
        "Гарантия работает только если у канала сейчас 0 активных бустов."
    ),
    "boosts_closed": (
        "Бусты для ЗАКРЫТОГО (приватного) канала.\n\n"
        "Нужна ПРИГЛАСИТЕЛЬНАЯ ссылка:\n"
        "https://t.me/+XXXXXX\n\n"
        "Как создать:\n"
        "1. Откройте закрытый канал → Настройки\n"
        "2. Пригласительные ссылки → Создать ссылку\n"
        "3. Скопируйте ссылку вида https://t.me/+XXXXXX\n\n"
        "Обычная ссылка на канал НЕ подойдёт для закрытых каналов.\n"
        "Гарантия работает только при 0 активных бустов на старте."
    ),
    "boosts_ru": (
        "Бусты выставляются с российских аккаунтов Telegram.\n"
        "Подходит для каналов с русскоязычной аудиторией.\n\n"
        "ВАЖНО: нужна специальная «буст-ссылка», а НЕ обычная ссылка на канал!\n\n"
        "Как найти буст-ссылку для открытого канала:\n"
        "Канал → Статистика → Бусты → «Поделиться ссылкой на буст»\n"
        "Формат: https://t.me/boost/username\n\n"
        "Для закрытого канала — пригласительная ссылка: https://t.me/+XXXXXX\n\n"
        "Гарантия работает только при 0 активных бустов на старте."
    ),

    # ── Старты бота ───────────────────────────────────────────────────────
    "starts_normal": (
        "Пользователи перейдут по ссылке и нажмут /start в вашем боте.\n\n"
        "Ссылка на бота — обычная:\n"
        "https://t.me/yourbot\n\n"
        "Или реферальная (если нужно засчитать рефералов):\n"
        "https://t.me/yourbot?start=ВАШ_КОД\n\n"
        "Как найти ссылку на бота: откройте бота → нажмите «Поделиться» → скопируйте ссылку.\n"
        "Скорость и гарантия — в описании конкретной услуги."
    ),
    "starts_activity": (
        "Пользователи запускают бота, взаимодействуют с ним, а затем через несколько дней возвращаются снова.\n"
        "Это повышает метрику удержания (retention), которую видят рекламодатели.\n\n"
        "Ссылка на бота: https://t.me/yourbot\n\n"
        "Скорость ниже обычных стартов — пользователи делают повторные визиты.\n"
        "Подходит для ботов с реферальными программами и геймификацией."
    ),
    "starts_premium": (
        "Старты совершаются с аккаунтов Telegram Premium.\n"
        "Повышает авторитет бота в каталогах и поиске Telegram.\n\n"
        "Ссылка на бота: https://t.me/yourbot\n\n"
        "Premium-аккаунтов меньше, чем обычных — большие заказы выполняются дольше.\n"
        "Старт выполнения: от 0 до 24 часов."
    ),
    "starts_referral": (
        "Рефералы засчитываются в вашей реферальной программе.\n\n"
        "Нужна РЕФЕРАЛЬНАЯ ссылка с параметром ?start= — без него рефералы НЕ засчитаются!\n\n"
        "Формат: https://t.me/yourbot?start=ВАШ_КОД\n\n"
        "Как найти реферальный код: откройте раздел «Рефералы» или «Пригласить друзей» в вашем боте — там будет ваша реферальная ссылка.\n\n"
        "Обычная ссылка без ?start= не даст рефералов."
    ),

    # ── Комментарии ───────────────────────────────────────────────────────
    "comments_random": (
        "Под вашим постом появятся комментарии с случайными текстами.\n"
        "Язык комментариев указан в названии услуги (RU / EN / смешанные).\n\n"
        "Нужна ссылка на ПОСТ с включёнными комментариями.\n"
        "Пример: https://t.me/durov/123\n\n"
        "Убедитесь, что:\n"
        "• Комментарии в канале включены (не отключены в настройках)\n"
        "• Канал открытый (не закрытый)\n"
        "• Пост существует и не удалён."
    ),
    "comments_custom": (
        "Под постом появятся комментарии с вашим текстом, написанным от разных аккаунтов.\n\n"
        "Нужна ссылка на ПОСТ с включёнными комментариями.\n"
        "Пример: https://t.me/durov/123\n\n"
        "На следующем шаге введите текст комментария.\n"
        "Рекомендации: короткий нейтральный текст выглядит естественнее.\n"
        "Избегайте внешних ссылок и спамных фраз — могут заблокироваться.\n\n"
        "Один и тот же текст будет повторён указанное число раз от разных аккаунтов."
    ),
    "comments_ai": (
        "ИИ прочитает ваш пост и сгенерирует уникальные релевантные комментарии.\n"
        "Каждый комментарий — разный, соответствует теме публикации.\n\n"
        "Нужна ссылка на ПОСТ с включёнными комментариями.\n"
        "Пример: https://t.me/durov/123\n\n"
        "Лучший результат для информационных постов, новостей, обзоров.\n"
        "Для коротких постов (1–3 слова) качество ниже — ИИ нужен контекст.\n\n"
        "Убедитесь, что комментарии в канале включены."
    ),

    # ── Голоса ────────────────────────────────────────────────────────────
    "polls_normal": (
        "Голоса добавятся к выбранному варианту ответа в вашем опросе.\n\n"
        "Нужна ссылка на ПОСТ с опросом.\n"
        "Пример: https://t.me/durov/123\n\n"
        "На следующем шаге введите НОМЕР варианта:\n"
        "• Считаются сверху вниз: первый вариант = 1, второй = 2 и т.д.\n"
        "Пример: если опрос «Да / Нет / Не знаю» и нужен «Да» — вводите 1.\n\n"
        "Опрос должен быть активным и ещё не завершённым."
    ),

    # ── Репосты ───────────────────────────────────────────────────────────
    "reposts_posts": (
        "Ваш пост будет пересылаться (форвардиться) другими аккаунтами.\n"
        "Репосты отображаются в счётчике «поделились» и в Telegram Analytics.\n\n"
        "Нужна ссылка на ПОСТ (не на канал).\n"
        "Пример: https://t.me/durov/123\n\n"
        "Как найти: откройте пост → «Поделиться» → «Скопировать ссылку».\n\n"
        "Скорость: указана в названии услуги (~50–3 000 репостов в сутки)."
    ),
    "reposts_stories": (
        "Ваша история будет пересылаться другими аккаунтами в их истории.\n\n"
        "Нужна ссылка на ИСТОРИЮ.\n"
        "Формат: https://t.me/username/s/НОМЕР\n\n"
        "Как найти ссылку на историю:\n"
        "1. Откройте историю\n"
        "2. Нажмите «...» (три точки) → «Поделиться» → «Скопировать ссылку»\n\n"
        "История должна быть активной — не истёкшей (истории живут 24 часа)."
    ),
    "reposts_geo": (
        "Ваш пост будет пересылаться аккаунтами из конкретной страны.\n"
        "Страна указана в названии выбранной услуги.\n\n"
        "Нужна ссылка на ПОСТ.\n"
        "Пример: https://t.me/durov/123\n\n"
        "Как найти: откройте пост → «Поделиться» → «Скопировать ссылку».\n\n"
        "Полезно для продвижения среди аудитории конкретного региона."
    ),

    # ── Живые ────────────────────────────────────────────────────────────
    "live_subs": (
        "Реальные живые люди, которые подпишутся через рекламу.\n"
        "Могут проявлять активность: лайкать, читать, писать.\n\n"
        "Для ОТКРЫТОГО канала: https://t.me/username\n"
        "Для ЗАКРЫТОГО: пригласительная ссылка https://t.me/+XXXXXX\n\n"
        "Скорость медленнее обычных подписчиков — это нормально для живых людей.\n"
        "Часть может отписаться — это естественное поведение реальных пользователей."
    ),
}


# ── Dynamic order helpers ──────────────────────────────────────────────────

async def _edit_stored_message(state: FSMContext, text: str, markup) -> bool:
    """Edit the message stored as last_prompt_msg_id in state. Returns True on success."""
    data = await state.get_data()
    chat_id = data.get("last_prompt_chat_id")
    msg_id  = data.get("last_prompt_msg_id")
    if not chat_id or not msg_id:
        return False
    try:
        await bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=markup,
        )
        return True
    except TelegramBadRequest:
        return False


async def ask_next_field(state: FSMContext, edit_target: Message = None):
    """
    Show the prompt for the current field.

    edit_target — pass when you have a Message to edit directly (e.g. on service
    select or back-navigation via callback).  When None, the function edits the
    message stored in state under last_prompt_msg_id (used after the user types
    a text reply).
    """
    data = await state.get_data()
    idx    = data.get("field_index", 0)
    schema = data.get("schema")
    if not schema:
        if edit_target:
            try:
                await edit_target.edit_text("Ошибка состояния. Начните заново.", reply_markup=main_menu())
            except TelegramBadRequest:
                pass
        await state.clear()
        return

    fields = schema["fields"]
    if idx >= len(fields):
        await create_dynamic_order(state, edit_target)
        return

    field  = fields[idx]
    prompt = field.get("prompt", f"Введите {field['name']}:")
    if "example" in field:
        prompt += f"\n📝 Пример: {field['example']}"

    # Prepend subcategory instruction in the first field prompt
    if idx == 0:
        category_name = data.get("category_name", "")
        instruction = SUBCATEGORY_INSTRUCTIONS.get(category_name, "")
        if instruction:
            prompt = f"📋 {instruction}\n\n{prompt}"

    # Build the navigation row for the inline keyboard
    # "Назад" at field 0 returns to the service list; at field N returns to field N-1
    back_cb = f"field_back_{idx}"
    nav_row = [InlineKeyboardButton(text="🔙 Назад", callback_data=back_cb)]

    extra_rows = []
    if idx == 0 and data.get("category_name") == "reactions_private":
        extra_rows.append([InlineKeyboardButton(
            text="🔐 Заказать подписчиков сначала",
            callback_data="sub_reactions_subscribe",
        )])

    if field["type"] == "days":
        day_rows = [[InlineKeyboardButton(text=opt, callback_data=f"days_{idx}_{opt}")] for opt in field["options"]]
        markup = InlineKeyboardMarkup(inline_keyboard=day_rows + extra_rows + [nav_row])
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=extra_rows + [nav_row])

    # Edit the target message — either the one passed in, or the stored one
    if edit_target is not None:
        try:
            await edit_target.edit_text(prompt, reply_markup=markup)
        except TelegramBadRequest:
            pass
        await state.update_data(
            last_prompt_msg_id=edit_target.message_id,
            last_prompt_chat_id=edit_target.chat.id,
        )
    else:
        await _edit_stored_message(state, prompt, markup)

    await state.set_state(DynamicOrderStates.waiting_for_field)


async def validate_field(field, value: str, service_name: str):
    if field["type"] == FIELD_LINK:
        if not value.startswith(("https://t.me/", "http://t.me/")):
            return False, None, "❌ Ссылка должна начинаться с https://t.me/"
        if field.get("invite_only"):
            if "/+" not in value and "joinchat" not in value:
                return False, None, "❌ Нужна пригласительная ссылка формата https://t.me/+XXXXX"
        if field.get("private_post"):
            if "/c/" not in value:
                return False, None, "❌ Для закрытого канала ссылка должна быть формата https://t.me/c/123456789/301"
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
            return False, None, "❌ Количество постов должно быть от 1 до 100"
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
    elif field["type"] == FIELD_REACTION_ID:
        if not value.strip().lstrip('-').isdigit():
            return False, None, "❌ Введите числовой ID реакции (например 12345) или 0 для обычной"
        rid = int(value.strip())
        if rid < 0:
            return False, None, "❌ ID не может быть отрицательным. Для обычной реакции введите 0"
        return True, rid, ""
    else:
        return True, value, ""


@router.message(DynamicOrderStates.waiting_for_field)
async def dynamic_field_text(message: Message, state: FSMContext):
    if message.text.startswith('/'):
        # Cancel the order — edit the stored prompt to show the cancellation notice
        await _edit_stored_message(state, "Заказ отменён.", main_menu())
        await state.clear()
        try:
            await message.delete()
        except Exception:
            pass
        return

    data = await state.get_data()
    idx    = data.get("field_index", 0)
    schema = data.get("schema")
    if not schema:
        await state.clear()
        await message.answer("Ошибка состояния. Начните заново.", reply_markup=main_menu())
        return

    fields = schema["fields"]
    if idx >= len(fields):
        return

    field = fields[idx]
    ok, value, error = await validate_field(field, message.text.strip(), data["service"]["name"])

    # Always delete the user's message to keep the chat clean
    try:
        await message.delete()
    except Exception:
        pass

    if not ok:
        # Show the error by temporarily editing the prompt, then re-set state
        # so the user can retry.  We prepend the error to the existing prompt.
        data2   = await state.get_data()
        prompt  = field.get("prompt", f"Введите {field['name']}:")
        if "example" in field:
            prompt += f"\n📝 Пример: {field['example']}"
        if idx == 0:
            instr = SUBCATEGORY_INSTRUCTIONS.get(data2.get("category_name", ""), "")
            if instr:
                prompt = f"📋 {instr}\n\n{prompt}"
        back_cb = f"field_back_{idx}"
        extra_rows = []
        if idx == 0 and data2.get("category_name") == "reactions_private":
            extra_rows.append([InlineKeyboardButton(
                text="🔐 Заказать подписчиков сначала",
                callback_data="sub_reactions_subscribe",
            )])
        markup = InlineKeyboardMarkup(inline_keyboard=extra_rows + [[InlineKeyboardButton(text="🔙 Назад", callback_data=back_cb)]])
        await _edit_stored_message(state, f"{error}\n\n{prompt}", markup)
        return

    collected = data.get("collected_fields", {})
    collected[field["name"]] = value
    await state.update_data(collected_fields=collected, field_index=idx + 1)
    await ask_next_field(state)


@router.callback_query(F.data.startswith("days_"))
async def dynamic_field_days(callback: CallbackQuery, state: FSMContext):
    _, idx_str, days_value = callback.data.split("_", 2)
    idx = int(idx_str)
    data = await state.get_data()
    schema = data.get("schema")
    if not schema:
        await callback.answer("Ошибка состояния")
        return
    fields = schema["fields"]
    if idx >= len(fields):
        await callback.answer("Ошибка")
        return
    collected = data.get("collected_fields", {})
    collected[fields[idx]["name"]] = days_value
    await state.update_data(collected_fields=collected, field_index=idx + 1)
    await ask_next_field(state, edit_target=callback.message)
    await callback.answer()


@router.callback_query(F.data.startswith("field_back_"))
async def field_back_handler(callback: CallbackQuery, state: FSMContext):
    idx = int(callback.data.split("_", 2)[2])
    data = await state.get_data()

    if idx == 0:
        # Return to the service list for this subcategory
        cat      = data.get("category_name", "")
        services = data.get("category_services", [])
        page     = data.get("page", 1)
        sort_order = data.get("sort_order", "asc")
        if not services:
            await callback.answer("Нет данных для возврата")
            return
        await state.clear()
        await state.update_data(
            category_services=services, category_name=cat,
            page=page, sort_order=sort_order,
        )
        await send_category_page(callback.message, cat, services, page, state)
        await callback.answer()
        return

    # Return to the previous field (idx - 1), clearing that field's collected value
    prev_idx = idx - 1
    schema = data.get("schema")
    if not schema:
        await callback.answer("Ошибка состояния")
        return
    fields    = schema["fields"]
    collected = data.get("collected_fields", {})
    collected.pop(fields[prev_idx]["name"], None)
    await state.update_data(field_index=prev_idx, collected_fields=collected)
    await ask_next_field(state, edit_target=callback.message)
    await callback.answer()


async def create_dynamic_order(state: FSMContext, edit_target: Message = None):
    data = await state.get_data()
    service    = data["service"]
    service_id = service["service"]
    user_id    = data.get("user_id")
    collected  = data["collected_fields"]

    link              = collected.get("link")
    quantity_per_post = collected.get("quantity")
    posts_count       = collected.get("posts_count")
    final_quantity    = (quantity_per_post * posts_count) if (posts_count and quantity_per_post) else quantity_per_post

    async def show_result(text: str):
        markup = main_menu()
        if edit_target is not None:
            try:
                await edit_target.edit_text(text, reply_markup=markup)
                return
            except TelegramBadRequest:
                pass
        if not await _edit_stored_message(state, text, markup):
            # Last resort: send a new message
            chat_id = data.get("last_prompt_chat_id")
            if chat_id:
                try:
                    await bot.send_message(chat_id, text, reply_markup=markup)
                except Exception:
                    pass

    if not link or not final_quantity:
        await show_result("❌ Не все обязательные поля заполнены.")
        await state.clear()
        return

    rate               = float(service["rate"])
    price_rub_per_1000 = calculate_price_rub(service_id, rate)
    total_rub          = calculate_total_rub(price_rub_per_1000, final_quantity)

    user = get_user(user_id)
    if user["rub_balance"] < total_rub:
        await show_result(f"❌ Недостаточно средств. Баланс: {user['rub_balance']:.3f} ₽")
        await state.clear()
        return
    if not deduct_balance_rub(user_id, total_rub):
        await show_result("❌ Ошибка списания средств.")
        await state.clear()
        return

    tw_resp = await tw_add_order(service_id, link, final_quantity)
    if "order" in tw_resp:
        tw_order_id    = tw_resp["order"]
        local_order_id = add_order(
            user_id=user_id,
            tw_order_id=tw_order_id,
            service_id=service_id,
            service_name=service["name"],
            link=link,
            quantity=final_quantity,
            price_rub=total_rub,
            status="processing",
        )
        await show_result(
            f"✅ Заказ #{local_order_id} принят!\n"
            f"Услуга: {service['name']}\n"
            f"Количество: {final_quantity}\n"
            f"Списано: {total_rub:.3f} ₽\n"
            f"Статус: выполняется..."
        )
    else:
        add_balance_rub(user_id, total_rub)
        await show_result("❌ Ошибка при создании заказа. Средства возвращены.")
    await state.clear()


# ── Basic commands ─────────────────────────────────────────────────────────

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
        reply_markup=main_menu(),
    )


@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user    = get_user(callback.from_user.id)
    balance = user["rub_balance"] if user else 0.0
    try:
        await callback.message.edit_text(
            f"✨ Главное меню\n💰 Баланс: {balance:.3f} ₽",
            reply_markup=main_menu(),
        )
    except TelegramBadRequest:
        pass
    await callback.answer()


@router.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user    = get_user(callback.from_user.id)
    balance = user["rub_balance"] if user else 0.0
    text = (
        f"👤 *Ваш профиль*\n\n"
        f"ID: {callback.from_user.id}\n"
        f"Имя: {safe_md(callback.from_user.full_name)}\n"
        f"💰 Баланс: {balance:.3f} ₽"
    )
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
        reply_markup=back_button(),
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
        start_parameter="deposit",
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
        parts      = payload.split("_")
        stars      = int(parts[1])
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
        quantity   = int(parts[2])
        total_rub  = float(parts[3])
        link       = parts[4]
        service = next((s for s in services_cache if s["service"] == service_id), None)
        if not service:
            await message.answer("❌ Ошибка: услуга не найдена. Средства возвращены.")
            add_balance_rub(message.from_user.id, total_rub)
            return
        tw_resp = await tw_add_order(service_id, link, quantity)
        if "order" in tw_resp:
            tw_order_id    = tw_resp["order"]
            local_order_id = add_order(
                user_id=message.from_user.id,
                tw_order_id=tw_order_id,
                service_id=service_id,
                service_name=service["name"],
                link=link,
                quantity=quantity,
                price_rub=total_rub,
                status="processing",
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
            text += f"#{o[0]} | {safe_md(o[1])} | {o[2]} ед. | {o[3]:.3f} ₽ | {o[4]}\n{o[5]}\n\n"
    await callback.message.edit_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_button())
    await callback.answer()


# ── Categories & subcategories ─────────────────────────────────────────────

@router.callback_query(F.data.startswith("cat_"))
async def show_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    cat = callback.data.split("_", 1)[1]
    submenus = {
        "views":       ("📸 Выберите тип просмотров:",         views_submenu),
        "reactions":   ("❤️ Выберите тип реакций:",            reactions_submenu),
        "subscribers": ("👥 Выберите тип подписчиков:",        subscribers_submenu),
        "boosts":      ("🚀 Выберите тип бустов:",             boosts_submenu),
        "starts":      ("🤖 Выберите тип стартов бота:",       starts_submenu),
        "comments":    ("✏️ Выберите тип комментариев:",       comments_submenu),
        "polls":       ("🗳 Выберите тип голосований:",        polls_submenu),
        "reposts":     ("🔄 Выберите тип репостов:",           reposts_submenu),
        "live":        ("👨‍🦱 Выберите тип живых услуг:",      live_submenu),
    }
    if cat in submenus:
        text, kb_fn = submenus[cat]
        await callback.message.edit_text(text, reply_markup=kb_fn())
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
    filtered = [
        s for s in services_cache
        if filter_func(s) and s.get("network") in ("Telegram", "Telegram Premium")
    ]
    if not filtered:
        await callback.message.edit_text("В этой подкатегории пока нет услуг.", reply_markup=back_button())
        await callback.answer()
        return
    filtered.sort(key=lambda s: s.get("_price_rub", float(s["rate"])))
    await state.update_data(category_services=filtered, category_name=sub, page=1, sort_order="asc")
    await send_category_page(callback.message, sub, filtered, 1, state)
    await callback.answer()


async def send_category_page(message, cat: str, services: list, page: int, state: FSMContext):
    pag = Pagination(services, page_size=8)
    items, current_page, total_pages = pag.get_page(page)

    text    = f"📂 Категория: {cat}\nСтраница {current_page}/{total_pages}\n\n"
    buttons = []

    for s in items:
        price_rub = s.get("_price_rub", calculate_price_rub(s["service"], float(s["rate"])))
        text += f"🔹 {s['name']}\n   {price_rub:.2f} ₽/1000\n\n"
        buttons.append([InlineKeyboardButton(
            text=s['name'][:30],
            callback_data=f"service_{s['service']}",
        )])

    # Pagination row
    pag_row = []
    if current_page > 1:
        pag_row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"page|{cat}|{current_page-1}"))
    if current_page < total_pages:
        pag_row.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"page|{cat}|{current_page+1}"))
    if pag_row:
        buttons.append(pag_row)

    # Sort row
    data       = await state.get_data()
    sort_order = data.get("sort_order", "asc")
    buttons.append([
        InlineKeyboardButton(
            text="💰 По возрастанию" + (" ✅" if sort_order == "asc" else ""),
            callback_data=f"sort|{cat}|asc",
        ),
        InlineKeyboardButton(
            text="💰 По убыванию" + (" ✅" if sort_order == "desc" else ""),
            callback_data=f"sort|{cat}|desc",
        ),
    ])

    # Navigation row: back to submenu + main menu
    parent = _parent_cat(cat)
    back_cb = f"cat_{parent}" if parent else "main_menu"
    buttons.append([
        InlineKeyboardButton(text="🔙 В подменю",     callback_data=back_cb),
        InlineKeyboardButton(text="🏠 Главное меню",  callback_data="main_menu"),
    ])

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
        page     = int(page_str)
        services = data.get("category_services", [])
        if not services:
            await callback.answer()
            return
        await state.update_data(page=page)
        await send_category_page(callback.message, cat, services, page, state)
    except TelegramBadRequest:
        pass
    except Exception as e:
        logging.warning(f"paginate_callback error: {e}")
    finally:
        await state.update_data(processing=False)
    await callback.answer()


@router.callback_query(F.data.startswith("sort|"))
async def sort_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("processing"):
        await callback.answer("Подождите...")
        return
    await state.update_data(processing=True)
    try:
        _, cat, order = callback.data.split("|")
        services = data.get("category_services", [])
        if not services:
            await callback.answer()
            return
        services_sorted = sorted(
            services,
            key=lambda s: s.get("_price_rub", float(s["rate"])),
            reverse=(order == "desc"),
        )
        await state.update_data(category_services=services_sorted, sort_order=order, page=1)
        await send_category_page(callback.message, cat, services_sorted, 1, state)
    except TelegramBadRequest:
        pass
    except Exception as e:
        logging.warning(f"sort_callback error: {e}")
    finally:
        await state.update_data(processing=False)
    await callback.answer()


# ── Service selection ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("service_"))
async def service_selected(callback: CallbackQuery, state: FSMContext):
    prev_data = await state.get_data()
    category_name      = prev_data.get("category_name", "")
    category_services  = prev_data.get("category_services", [])
    sort_order         = prev_data.get("sort_order", "asc")
    page               = prev_data.get("page", 1)

    service_id = int(callback.data.split("_")[1])
    service = next((s for s in services_cache if s["service"] == service_id), None)
    if not service:
        await callback.answer("Услуга не найдена")
        return

    schema = SUBCATEGORY_TO_SCHEMA.get(category_name) or get_schema_for_service(service_id, service["name"])

    await state.clear()
    await state.update_data(
        service_id=service_id,
        service=service,
        schema=schema,
        collected_fields={},
        category_name=category_name,
        user_id=callback.from_user.id,
        # Preserve navigation state so "Back" from field 0 can restore the list
        category_services=category_services,
        sort_order=sort_order,
        page=page,
    )

    fields = schema.get("fields", [])
    if not fields:
        try:
            await callback.message.edit_text("Ошибка: нет полей для заказа.", reply_markup=main_menu())
        except TelegramBadRequest:
            pass
        await callback.answer()
        return

    await state.update_data(field_index=0, total_fields=len(fields))
    # Edit the service-list message in place — no new message polluting the chat
    await ask_next_field(state, edit_target=callback.message)
    await callback.answer()


# Legacy no-op: keeps old "Понятно, продолжить" buttons from hanging
@router.callback_query(F.data == "continue_dynamic")
async def continue_dynamic(callback: CallbackQuery, state: FSMContext):
    await callback.answer()


@router.callback_query(F.data == "sub_reactions_subscribe")
async def redirect_to_subscribe(callback: CallbackQuery, state: FSMContext):
    filter_func = SUBCATEGORY_FILTERS.get("reactions_subscribe")
    if not filter_func:
        await callback.answer("Подкатегория не найдена")
        return
    filtered = [
        s for s in services_cache
        if filter_func(s) and s.get("network") in ("Telegram", "Telegram Premium")
    ]
    if not filtered:
        try:
            await callback.message.edit_text("В этой подкатегории пока нет услуг.", reply_markup=back_button())
        except TelegramBadRequest:
            pass
        await callback.answer()
        return
    filtered.sort(key=lambda s: s.get("_price_rub", float(s["rate"])))
    await state.clear()
    await state.update_data(
        category_services=filtered, category_name="reactions_subscribe",
        page=1, sort_order="asc",
    )
    await send_category_page(callback.message, "reactions_subscribe", filtered, 1, state)
    await callback.answer()


# ── Standard order flow (legacy fallback) ─────────────────────────────────

@router.message(OrderStates.waiting_for_link)
async def get_link(message: Message, state: FSMContext):
    if message.text.startswith('/'):
        await state.clear()
        await message.answer("Отменено.", reply_markup=main_menu())
        return
    link = message.text.strip()
    if not link.startswith(("https://t.me/", "http://t.me/")):
        await message.answer("❌ Ссылка должна начинаться с https://t.me/")
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
    data    = await state.get_data()
    service = data["service"]
    if quantity < service["min"] or quantity > service["max"]:
        await message.answer(f"❌ Количество должно быть от {service['min']} до {service['max']}")
        return
    price_rub_per_1000 = data["price_rub_per_1000"]
    total_rub          = calculate_total_rub(price_rub_per_1000, quantity)
    await state.update_data(quantity=quantity, total_rub=total_rub)
    await message.answer(
        f"📋 Подтверждение заказа\n"
        f"Услуга: {service['name']}\n"
        f"Ссылка: {data['link']}\n"
        f"Количество: {quantity}\n"
        f"💰 Сумма: {total_rub:.3f} ₽\n\n"
        f"Подтверждаете?",
        reply_markup=confirm_keyboard(service["service"], data["link"], quantity, total_rub),
    )
    await state.set_state(OrderStates.confirm)


@router.callback_query(F.data.startswith("confirm_"))
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    parts      = callback.data.split("_")
    service_id = int(parts[1])
    quantity   = int(parts[2])
    total_rub  = float(parts[3])
    encoded_link = "_".join(parts[4:])
    link    = safe_decode_link(encoded_link)
    service = next((s for s in services_cache if s["service"] == service_id), None)
    if not service:
        await callback.answer("Услуга не найдена")
        return
    user = get_user(callback.from_user.id)
    if user["rub_balance"] < total_rub:
        await callback.message.edit_text(
            f"❌ Недостаточно средств. Баланс: {user['rub_balance']:.3f} ₽",
            reply_markup=back_button(),
        )
        await state.clear()
        await callback.answer()
        return
    if not deduct_balance_rub(callback.from_user.id, total_rub):
        await callback.message.edit_text("❌ Ошибка списания средств.", reply_markup=back_button())
        await state.clear()
        return
    tw_resp = await tw_add_order(service_id, link, quantity)
    if "order" in tw_resp:
        tw_order_id    = tw_resp["order"]
        local_order_id = add_order(
            user_id=callback.from_user.id,
            tw_order_id=tw_order_id,
            service_id=service_id,
            service_name=service["name"],
            link=link,
            quantity=quantity,
            price_rub=total_rub,
            status="processing",
        )
        await callback.message.edit_text(
            f"✅ Заказ #{local_order_id} принят!\n"
            f"Услуга: {service['name']}\n"
            f"Количество: {quantity}\n"
            f"Списано: {total_rub:.3f} ₽",
            reply_markup=main_menu(),
        )
    else:
        add_balance_rub(callback.from_user.id, total_rub)
        await callback.message.edit_text(
            "❌ Ошибка при создании заказа. Средства возвращены.",
            reply_markup=main_menu(),
        )
    await state.clear()
    await callback.answer()


# ── Background status checker ──────────────────────────────────────────────

async def status_checker():
    while True:
        await asyncio.sleep(60)
        conn = sqlite3.connect("blondeboost.db")
        c    = conn.cursor()
        c.execute("SELECT order_id, tw_order_id FROM orders WHERE status = 'processing'")
        rows = c.fetchall()
        conn.close()
        for order_id, tw_order_id in rows:
            try:
                status_data = await get_order_status(tw_order_id)
                tw_status   = status_data.get("status")
                if tw_status == "Completed":
                    update_order_status(order_id, "completed", str(status_data))
                    conn2 = sqlite3.connect("blondeboost.db")
                    c2    = conn2.cursor()
                    c2.execute("SELECT user_id FROM orders WHERE order_id = ?", (order_id,))
                    row = c2.fetchone()
                    conn2.close()
                    if row:
                        try:
                            await bot.send_message(row[0], f"✅ Ваш заказ #{order_id} выполнен!")
                        except Exception:
                            pass
                elif tw_status in ("Canceled", "Fail"):
                    update_order_status(order_id, "failed", str(status_data))
            except Exception as e:
                logging.error(f"status_checker error for order {order_id}: {e}")


# ── Admin panel ────────────────────────────────────────────────────────────

from config import ADMIN_ID


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


@router.message(Command("admin_panel"))
async def admin_panel(message: Message, state: FSMContext):
    await state.clear()
    if not is_admin(message.from_user.id):
        await message.answer("❌ Нет доступа.")
        return
    await message.answer("🔧 Панель администратора:", reply_markup=admin_menu())
