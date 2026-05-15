import aiohttp
from config import TWIBOOST_API_KEY, TWIBOOST_API_URL

async def api_request(params: dict):
    """Универсальный GET запрос к API Twiboost"""
    params["key"] = TWIBOOST_API_KEY
    async with aiohttp.ClientSession() as session:
        async with session.get(TWIBOOST_API_URL, params=params) as resp:
            return await resp.json()

async def get_services():
    """Получить список всех услуг"""
    return await api_request({"action": "services"})

async def get_balance():
    """Получить баланс аккаунта в Twiboost"""
    return await api_request({"action": "balance"})

async def add_order(service_id: int, link: str, quantity: int):
    """Создать заказ в Twiboost"""
    params = {
        "action": "add",
        "service": service_id,
        "link": link,
        "quantity": quantity
    }
    return await api_request(params)

async def get_order_status(order_id: int):
    """Получить статус заказа из Twiboost"""
    params = {"action": "status", "order": order_id}
    return await api_request(params)