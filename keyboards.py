from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Просмотры", callback_data="cat_views")
    builder.button(text="❤️ Реакции", callback_data="cat_reactions")
    builder.button(text="👥 Подписчики", callback_data="cat_subscribers")
    builder.button(text="🚀 Бусты", callback_data="cat_boosts")
    builder.button(text="🤖 Старты бота", callback_data="cat_starts")
    builder.button(text="✏️ Комментарии", callback_data="cat_comments")
    builder.button(text="🗳 Голоса в опросах", callback_data="cat_polls")
    builder.button(text="🔄 Репосты", callback_data="cat_reposts")
    builder.button(text="👨‍🦱 Живые", callback_data="cat_live")
    builder.button(text="👤 Профиль", callback_data="profile")
    builder.button(text="💰 Пополнить баланс", callback_data="deposit")
    builder.button(text="📜 История заказов", callback_data="history")
    builder.adjust(2)
    return builder.as_markup()

def back_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])

def confirm_keyboard(service_id: int, link: str, quantity: int, total_rub: float) -> InlineKeyboardMarkup:
    safe_link = link.replace("_", "___")
    data = f"confirm_{service_id}_{quantity}_{total_rub}_{safe_link}"
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=data)
    builder.button(text="❌ Отмена", callback_data="main_menu")
    return builder.as_markup()

def admin_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Список пользователей", callback_data="admin_users")
    builder.button(text="📦 Список заказов", callback_data="admin_orders")
    builder.button(text="📊 Статистика", callback_data="admin_stats")
    builder.button(text="💰 Добавить баланс пользователю", callback_data="admin_add_balance")
    builder.button(text="🔙 В главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

# ---------- Подменю для категорий ----------
def views_submenu():
    builder = InlineKeyboardBuilder()
    builder.button(text="📄 На один пост", callback_data="sub_views_single")
    builder.button(text="📚 На несколько последних", callback_data="sub_views_multi")
    builder.button(text="⏱️ С выбором скорости", callback_data="sub_views_speed")
    builder.button(text="🔒 Для закрытых каналов", callback_data="sub_views_private")
    builder.button(text="🧠 Умные просмотры", callback_data="sub_views_smart")
    builder.button(text="📹 Telesco.pe (кружочки)", callback_data="sub_views_telesco")
    builder.button(text="🔄 Авто-просмотры", callback_data="sub_views_auto")
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()

def reactions_submenu():
    builder = InlineKeyboardBuilder()
    builder.button(text="😀 Обычные реакции", callback_data="sub_reactions_normal")
    builder.button(text="🔒 Для закрытых каналов", callback_data="sub_reactions_private")
    builder.button(text="⭐️ Premium реакции", callback_data="sub_reactions_premium")
    builder.button(text="➕ Реакции + просмотры", callback_data="sub_reactions_plus")
    builder.button(text="🔄 Авто-реакции", callback_data="sub_reactions_auto")
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()

def subscribers_submenu():
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Обычные подписчики", callback_data="sub_subs_normal")
    builder.button(text="📺 С автопросмотрами", callback_data="sub_subs_autoview")
    builder.button(text="🟢 24/7 онлайн", callback_data="sub_subs_online")
    builder.button(text="📢 Живые с рекламы", callback_data="sub_subs_live")
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()

def boosts_submenu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Для открытых каналов", callback_data="sub_boosts_open")
    builder.button(text="🔒 Для закрытых каналов", callback_data="sub_boosts_closed")
    builder.button(text="🇷🇺 RU аккаунты", callback_data="sub_boosts_ru")
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()

def starts_submenu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🤖 Обычные старты", callback_data="sub_starts_normal")
    builder.button(text="🔄 С активностью", callback_data="sub_starts_activity")
    builder.button(text="⭐️ Premium старты", callback_data="sub_starts_premium")
    builder.button(text="🔗 Рефералы для ботов", callback_data="sub_starts_referral")
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()

def comments_submenu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🎲 Рандомные комментарии", callback_data="sub_comments_random")
    builder.button(text="✏️ Кастомные комментарии", callback_data="sub_comments_custom")
    builder.button(text="🤖 ИИ комментарии", callback_data="sub_comments_ai")
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()

def polls_submenu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🗳 Голоса в опросах", callback_data="sub_polls_normal")
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def reposts_submenu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Репосты постов", callback_data="sub_reposts_posts")
    builder.button(text="📸 Репосты историй", callback_data="sub_reposts_stories")
    builder.button(text="🌍 С геотаргетингом", callback_data="sub_reposts_geo")
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()

def live_submenu():
    builder = InlineKeyboardBuilder()
    builder.button(text="👁️ Живые просмотры", callback_data="sub_live_views")
    builder.button(text="👥 Живые подписчики", callback_data="sub_live_subs")
    builder.button(text="✏️ Живые комментарии", callback_data="sub_live_comments")
    builder.button(text="❤️ Живые реакции / лайки", callback_data="sub_live_reactions")
    builder.button(text="🔙 Назад", callback_data="main_menu")
    builder.adjust(2)
    return builder.as_markup()