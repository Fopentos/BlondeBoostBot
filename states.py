from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    waiting_for_link = State()
    waiting_for_quantity = State()
    confirm = State()


class DepositStates(StatesGroup):
    waiting_for_stars_amount = State()


class DynamicOrderStates(StatesGroup):
    waiting_for_field = State()
    waiting_for_continue = State()
