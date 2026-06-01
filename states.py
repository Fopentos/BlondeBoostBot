from aiogram.fsm.state import State, StatesGroup

class OrderStates(StatesGroup):
    """Состояния для стандартного заказа (ссылка + количество)"""
    waiting_for_link = State()
    waiting_for_quantity = State()
    confirm = State()

class DepositStates(StatesGroup):
    """Состояние для пополнения баланса"""
    waiting_for_stars_amount = State()

class DynamicOrderStates(StatesGroup):
    """Состояние для динамического заказа (много полей, например, голосования, бусты, кастомные комментарии)"""
    waiting_for_field = State()
    waiting_for_continue = State()  # для подтверждения предупреждений
