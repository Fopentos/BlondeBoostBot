from aiogram.fsm.state import State, StatesGroup

class OrderStates(StatesGroup):
    """Состояния для процесса оформления заказа"""
    waiting_for_link = State()      # ожидание ввода ссылки
    waiting_for_quantity = State()  # ожидание ввода количества
    confirm = State()               # подтверждение заказа

class DepositStates(StatesGroup):
    """Состояние для пополнения баланса"""
    waiting_for_stars_amount = State()  # ожидание ввода суммы в Stars