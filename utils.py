import math
from config import DEFAULT_MARKUP_FACTOR, MARKUP_BY_SERVICE, STAR_TO_RUB

def get_markup_factor(service_id: int) -> float:
    """
    Возвращает коэффициент наценки для конкретной услуги.
    Если услуга не найдена в словаре, возвращает глобальный коэффициент.
    """
    return MARKUP_BY_SERVICE.get(service_id, DEFAULT_MARKUP_FACTOR)

def calculate_price_rub(service_id: int, rate_per_1000: float) -> float:
    """
    Рассчитывает розничную цену за 1000 единиц в рублях.
    rate_per_1000 - закупочная цена Twiboost за 1000 единиц.
    """
    factor = get_markup_factor(service_id)
    return rate_per_1000 * factor

def calculate_total_rub(price_rub_per_1000: float, quantity: int) -> float:
    """
    Рассчитывает полную стоимость заказа в рублях.
    price_rub_per_1000 - цена за 1000 единиц.
    quantity - количество заказываемых единиц.
    """
    return price_rub_per_1000 * quantity / 1000.0

def safe_decode_link(encoded: str) -> str:
    """
    Декодирует ссылку после передачи в callback_data.
    Заменяет утроенные подчёркивания обратно на одинарные.
    """
    return encoded.replace("___", "_")

def stars_to_rub(stars: int) -> float:
    """Конвертирует Stars в рубли по текущему курсу."""
    return stars * STAR_TO_RUB

def rub_to_stars(rub: float) -> int:
    """Конвертирует рубли в Stars (с округлением вверх)."""
    return math.ceil(rub / STAR_TO_RUB)