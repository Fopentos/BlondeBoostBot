from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu():
    """Главное меню пользователя"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Просмотры", callback_data="cat_views")
    builder.button(text="❤️ Реакции", callback_data="cat_reactions")
    builder.button(text="👥 Подписчики", callback_data="cat_subscribers")
    builder.button(text="🚀 Бусты", callback_data="cat_boosts")
    builder.button(text="🤖 Старты бота", callback_data="cat_starts")
    builder.button(text="✏️ Комментарии", callback_data="cat_comments")
    builder.button(text="🗳 Голоса в опросах", callback_data="cat_polls")
    builder.button(text="🔄 Репосты", callback_data="cat_reposts")
    builder.button(text="⭐️ Premium услуги", callback_data="cat_premium")
    builder.button(text="👤 Профиль", callback_data="profile")
    builder.button(text="💰 Пополнить баланс", callback_data="deposit")
    builder.button(text="📜 История заказов", callback_data="history")
    builder.adjust(2)
    return builder.as_markup()

def back_button():
    """Универсальная кнопка возврата в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])

def confirm_keyboard(service_id: int, link: str, quantity: int, total_rub: float) -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения заказа.
    Кодирует ссылку через замену _ на ___ для безопасной передачи в callback_data.
    """
    safe_link = link.replace("_", "___")
    # Формат: confirm_serviceId_quantity_totalRub_link
    data = f"confirm_{service_id}_{quantity}_{total_rub}_{safe_link}"
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Подтвердить", callback_data=data)
    builder.button(text="❌ Отмена", callback_data="main_menu")
    return builder.as_markup()

def admin_menu():
    """Главное меню админ-панели"""
    builder = InlineKeyboardBuilder()
    builder.button(text="👥 Список пользователей", callback_data="admin_users")
    builder.button(text="📦 Список заказов", callback_data="admin_orders")
    builder.button(text="📊 Статистика", callback_data="admin_stats")
    builder.button(text="🔙 В главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()