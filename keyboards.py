from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from locales import t


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en"),
        ]
    ])


def main_menu(lang: str = "ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_views"),       callback_data="cat_views")
    builder.button(text=t(lang, "btn_reactions"),   callback_data="cat_reactions")
    builder.button(text=t(lang, "btn_subscribers"), callback_data="cat_subscribers")
    builder.button(text=t(lang, "btn_boosts"),      callback_data="cat_boosts")
    builder.button(text=t(lang, "btn_starts"),      callback_data="cat_starts")
    builder.button(text=t(lang, "btn_comments"),    callback_data="cat_comments")
    builder.button(text=t(lang, "btn_polls"),       callback_data="cat_polls")
    builder.button(text=t(lang, "btn_reposts"),     callback_data="cat_reposts")
    builder.button(text=t(lang, "btn_live"),        callback_data="cat_live")
    builder.button(text=t(lang, "btn_profile"),     callback_data="profile")
    builder.button(text=t(lang, "btn_deposit"),     callback_data="deposit")
    builder.button(text=t(lang, "btn_history"),     callback_data="history")
    builder.adjust(2)
    return builder.as_markup()


def back_button(lang: str = "ru"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_back"), callback_data="main_menu")]
    ])


def confirm_keyboard(service_id: int, link: str, quantity: int, total_rub: float, lang: str = "ru") -> InlineKeyboardMarkup:
    safe_link = link.replace("_", "___")
    data = f"confirm_{service_id}_{quantity}_{total_rub}_{safe_link}"
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_confirm"), callback_data=data)
    builder.button(text=t(lang, "btn_reject"),  callback_data="main_menu")
    return builder.as_markup()


def admin_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Список пользователей",          callback_data="admin_users")
    builder.button(text="📦 Список заказов",                callback_data="admin_orders")
    builder.button(text="📊 Статистика",                    callback_data="admin_stats")
    builder.button(text="💰 Добавить баланс пользователю",  callback_data="admin_add_balance")
    builder.button(text="🔙 В главное меню",                callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def views_submenu(lang: str = "ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="📄 На один пост",              callback_data="sub_views_single")
    builder.button(text="📚 На несколько последних",    callback_data="sub_views_multi")
    builder.button(text="⏱️ С выбором скорости",        callback_data="sub_views_speed")
    builder.button(text="🔒 Для закрытых каналов",      callback_data="sub_views_private")
    builder.button(text="🧠 Умные просмотры",           callback_data="sub_views_smart")
    builder.button(text="📹 Telesco.pe (кружочки)",     callback_data="sub_views_telesco")
    builder.button(text="🔄 Авто-просмотры",            callback_data="sub_views_auto")
    builder.button(text="📖 Просмотры историй",         callback_data="sub_views_stories")
    builder.button(text="⭐️ Premium просмотры",         callback_data="sub_views_premium")
    builder.button(text=t(lang, "btn_back_main"),       callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()


def reactions_submenu(lang: str = "ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="😀 Обычные реакции",               callback_data="sub_reactions_normal")
    builder.button(text="🔒 Для закрытых каналов",          callback_data="sub_reactions_private")
    builder.button(text="🔐 Подписки в закрытые каналы",    callback_data="sub_reactions_subscribe")
    builder.button(text="⭐️ Premium реакции",              callback_data="sub_reactions_premium")
    builder.button(text="➕ Реакции + просмотры",           callback_data="sub_reactions_plus")
    builder.button(text="🔄 Авто-реакции",                  callback_data="sub_reactions_auto")
    builder.button(text="📖 Реакции на истории",            callback_data="sub_reactions_stories")
    builder.button(text=t(lang, "btn_back_main"),           callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()


def subscribers_submenu(lang: str = "ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Обычные подписчики",    callback_data="sub_subs_normal")
    builder.button(text="📺 С автопросмотрами",     callback_data="sub_subs_autoview")
    builder.button(text="🟢 24/7 онлайн",           callback_data="sub_subs_online")
    builder.button(text="📢 Живые с рекламы",       callback_data="sub_subs_live")
    builder.button(text="⭐️ Premium подписчики",    callback_data="sub_subs_premium")
    builder.button(text=t(lang, "btn_back_main"),   callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()


def boosts_submenu(lang: str = "ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Для открытых каналов",  callback_data="sub_boosts_open")
    builder.button(text="🔒 Для закрытых каналов",  callback_data="sub_boosts_closed")
    builder.button(text="🇷🇺 RU аккаунты",          callback_data="sub_boosts_ru")
    builder.button(text=t(lang, "btn_back_main"),   callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()


def starts_submenu(lang: str = "ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="🤖 Обычные старты",        callback_data="sub_starts_normal")
    builder.button(text="🔄 С активностью",         callback_data="sub_starts_activity")
    builder.button(text="⭐️ Premium старты",        callback_data="sub_starts_premium")
    builder.button(text="🔗 Рефералы для ботов",    callback_data="sub_starts_referral")
    builder.button(text=t(lang, "btn_back_main"),   callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()


def comments_submenu(lang: str = "ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="🎲 Рандомные комментарии", callback_data="sub_comments_random")
    builder.button(text="✏️ Кастомные комментарии", callback_data="sub_comments_custom")
    builder.button(text="🤖 ИИ комментарии",        callback_data="sub_comments_ai")
    builder.button(text=t(lang, "btn_back_main"),   callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()


def polls_submenu(lang: str = "ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="🗳 Голоса в опросах",  callback_data="sub_polls_normal")
    builder.button(text=t(lang, "btn_back_main"), callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def reposts_submenu(lang: str = "ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Репосты постов",        callback_data="sub_reposts_posts")
    builder.button(text="📸 Репосты историй",       callback_data="sub_reposts_stories")
    builder.button(text="🌍 С геотаргетингом",      callback_data="sub_reposts_geo")
    builder.button(text="⭐️ Premium репосты",       callback_data="sub_reposts_premium")
    builder.button(text=t(lang, "btn_back_main"),   callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()


def live_submenu(lang: str = "ru"):
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Живые подписчики",      callback_data="sub_live_subs")
    builder.button(text=t(lang, "btn_back_main"),   callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()
