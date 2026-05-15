from typing import Dict, List, Any

# Определяем типы полей
FIELD_LINK = "link"          # ссылка Telegram
FIELD_QUANTITY = "quantity"  # целое число
FIELD_POSTS_COUNT = "posts"  # количество будущих постов (для авто-реакций)
FIELD_VOTE_OPTION = "option" # номер варианта в опросе (int)
FIELD_COMMENT_TEXT = "text"  # текст комментария (для кастомных)

# Схема для группы услуг
ServiceSchema = Dict[str, Any]

# Ключевые слова -> схема
SCHEMAS: Dict[str, ServiceSchema] = {
    # ----- Реакции на закрытые каналы -----
    "реакция на пост в закрытом канале": {
        "fields": [
            {"name": "link", "type": FIELD_LINK, "prompt": "Введите ссылку на ПОСТ в закрытом канале:"},
            {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "Введите количество реакций:"},
        ],
        "pre_check": "⚠️ Для накрутки реакций на закрытый канал СНАЧАЛА закажите подписчиков (ID 5178 или 5220 и т.п.). Количество подписчиков должно быть ≥ количеству реакций.\n\nПосле того как подписчики добавлены, закажите реакции.",
        "instructions": "Убедитесь, что ссылка ведёт на конкретный пост, а не на канал."
    },

    # ----- Авто-реакции на будущие посты -----
    "авто реакц": {
        "fields": [
            {"name": "link", "type": FIELD_LINK, "prompt": "Введите ссылку на КАНАЛ (без номера поста):"},
            {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "Введите количество реакций на каждый будущий пост:"},
            {"name": "posts_count", "type": FIELD_POSTS_COUNT, "prompt": "На сколько будущих постов накрутить реакции? (целое число от 1 до 100):"},
        ],
        "instructions": "Авто-реакции будут добавлены на следующие N постов канала. Убедитесь, что бот @privateviewss_bot добавлен в админы (для закрытых каналов)."
    },

    # ----- Голоса в опросах (свой ответ) -----
    "голоса в опрос": {
        "fields": [
            {"name": "link", "type": FIELD_LINK, "prompt": "Введите ссылку на ПОСТ с опросом:"},
            {"name": "option", "type": FIELD_VOTE_OPTION, "prompt": "Введите номер варианта ответа (от 1 до N):"},
            {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "Введите количество голосов:"},
        ],
        "instructions": "Голоса будут отданы за указанный вариант."
    },

    # ----- Кастомные комментарии -----
    "кастомные комментар": {
        "fields": [
            {"name": "link", "type": FIELD_LINK, "prompt": "Введите ссылку на ПОСТ:"},
            {"name": "comment_text", "type": FIELD_COMMENT_TEXT, "prompt": "Введите текст комментария (на русском/английском):"},
            {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "Введите количество комментариев:"},
        ],
        "instructions": "Каждый аккаунт оставит указанный комментарий под постом."
    },

    # ----- Бусты (с выбором длительности) -----
    "бусты": {
        "fields": [
            {"name": "link", "type": FIELD_LINK, "prompt": "Введите ссылку на КАНАЛ:"},
            {"name": "days", "type": "days", "prompt": "Выберите длительность буста:", "options": ["1 день", "7 дней", "14 дней", "30 дней", "90 дней", "180 дней"]},
            {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "Введите количество бустов:"},
        ],
        "instructions": "Буст повышает уровень канала и позволяет публиковать истории. Цена зависит от длительности."
    },

    # ----- Старты бота с реферальными ссылками -----
    "старты бота": {
        "fields": [
            {"name": "link", "type": FIELD_LINK, "prompt": "Введите ссылку на БОТА (можно реферальную, например https://t.me/bot?start=123):"},
            {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "Введите количество стартов:"},
        ],
        "instructions": "Бот будет запущен указанное количество раз. Если ссылка реферальная – рефералы засчитаются."
    },
}

def get_schema_for_service(service_name: str) -> ServiceSchema | None:
    """Возвращает схему для услуги по её названию (по ключевым словам)"""
    lower_name = service_name.lower()
    for keyword, schema in SCHEMAS.items():
        if keyword in lower_name:
            return schema
    return None
