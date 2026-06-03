# service_schemas.py
from typing import Dict, List, Any

# Типы полей
FIELD_LINK = "link"
FIELD_QUANTITY = "quantity"
FIELD_POSTS_COUNT = "posts"
FIELD_SPEED = "speed"
FIELD_VOTE_OPTION = "option"
FIELD_COMMENT_TEXT = "text"
FIELD_REACTION_ID = "reaction_id"

# Схема услуги
ServiceSchema = Dict[str, Any]

SCHEMAS: Dict[str, ServiceSchema] = {}

# ------------------------------------------------------------
# 1. Просмотры постов
# ------------------------------------------------------------
SCHEMAS["просмотры на пост"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров (целое число):"}
    ],
    "instructions": "✅ Ссылка должна вести на конкретный пост. Просто скопируйте её из Telegram."
}

SCHEMAS["последних постов"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на КАНАЛ (без номера поста):", "example": "https://t.me/durov"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров на КАЖДЫЙ пост (от 100 до 100 000 000):"}
    ],
    "instructions": "⚠️ Просмотры будут добавлены на указанное количество последних постов."
}

SCHEMAS["будущих постов"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на ПОСЛЕДНИЙ пост в закрытом канале:", "example": "https://t.me/c/123456789/301"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров на КАЖДЫЙ будущий пост:"}
    ],
    "pre_check": "🤖 Перед заказом добавьте бота @DeepDiveTGbot в администраторы канала (с правом репоста).",
    "instructions": "Просмотры будут добавляться на следующие N постов."
}

SCHEMAS["с выбором скорости"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите общее количество просмотров:"}
    ],
    "instructions": "⚡️ Просмотры будут начисляться с фиксированной скоростью (1-70 в минуту)."
}

SCHEMAS["закрытых каналов (privateviewss)"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост в закрытом канале:", "example": "https://t.me/c/123456789/301"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров:"}
    ],
    "pre_check": "🤖 Добавьте бота @privateviewss_bot в администраторы канала с правом репоста. Без этого услуга не сработает!\n\n❗️ИНСТРУКЦИЯ:\n1️⃣ Добавьте @privateviewss_bot в админы закрытого канала (доступ к репосту)\n2️⃣ После добавления бота сделайте заказ\n3️⃣ Копируйте ссылку на пост из закрытого канала\n4️⃣ Разрешите репостить пост",
    "instructions": "Просмотры будут накручены на указанный пост."
}

SCHEMAS["умные просмотры"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров (от 300 до 30 000):"}
    ],
    "instructions": "🧠 Просмотры начисляются постепенно (лесенкой), имитируя живую активность."
}

SCHEMAS["telesco.pe просмотры"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на видео-сообщение (кружочек):", "example": "https://t.me/c/123456789/301?video"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров:"}
    ],
    "instructions": "Просмотры на кружочки (видеосообщения) в Telegram."
}

SCHEMAS["авто просмотры"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на КАНАЛ (без номера поста):", "example": "https://t.me/durov"},
        {"name": "posts_count", "type": FIELD_POSTS_COUNT, "prompt": "🔢 На сколько будущих постов накрутить? (целое число от 1 до 100):"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров на КАЖДЫЙ пост:"}
    ],
    "instructions": "🔄 После заказа все будущие посты в канале будут автоматически получать указанное количество просмотров. Общая сумма = количество постов × количество просмотров на пост."
}

# ------------------------------------------------------------
# 2. Просмотры историй
# ------------------------------------------------------------
SCHEMAS["просмотры историй"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на историю (или @username канала):", "example": "https://t.me/durov/s/123 или @durov"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров:"}
    ],
    "instructions": "Если указать @username канала, просмотры будут добавлены на последнюю историю."
}

# ------------------------------------------------------------
# 3. Реакции
# ------------------------------------------------------------
SCHEMAS["реакции"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество реакций (не более 150 000):"}
    ],
    "instructions": "Реакции будут добавлены под постом. Выбранный эмодзи уже зафиксирован в услуге."
}

SCHEMAS["реакции закрытых каналов"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на ПОСТ в закрытом канале:", "example": "https://t.me/c/123456789/301"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество реакций (не больше, чем подписчиков):"}
    ],
    "pre_check": "⚠️ Для накрутки реакций в закрытом канале СНАЧАЛА закажите подписчиков (кнопка ниже). Количество подписчиков должно быть ≥ количеству реакций.\n\nПосле того как подписчики добавлены, вернитесь и закажите реакции.",
    "buttons": [{"text": "🔐 Заказать подписчиков", "callback": "sub_reactions_subscribe"}],
    "instructions": "Реакции ставят те же аккаунты, которые подписаны на канал."
}

SCHEMAS["премиум реакции"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "reaction_id", "type": FIELD_REACTION_ID, "prompt": "🔢 Введите ID реакции (для кастомной – получите у @prem_reaction_bot, для обычной – 0):", "example": "12345"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество реакций:"}
    ],
    "instructions": "⭐️ Реакции с премиум-аккаунтов. Для кастомной – сначала получите ID через бота @prem_reaction_bot."
}

SCHEMAS["реакции + просмотры"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество реакций (вместе с просмотрами):"}
    ],
    "instructions": "Вместе с реакциями автоматически накручиваются просмотры поста."
}

SCHEMAS["авто реакции"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на КАНАЛ (без номера поста):", "example": "https://t.me/durov"},
        {"name": "posts_count", "type": FIELD_POSTS_COUNT, "prompt": "🔢 На сколько будущих постов накрутить? (целое число от 1 до 100):"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество реакций на КАЖДЫЙ пост:"}
    ],
    "instructions": "🔄 Автоматические реакции будут добавляться на указанное количество будущих постов. Общая сумма = количество постов × количество реакций на пост."
}

# ------------------------------------------------------------
# 4. Комментарии
# ------------------------------------------------------------
SCHEMAS["рандомные комментарии"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество комментариев:"}
    ],
    "instructions": "Комментарии будут случайными на выбранном языке."
}

SCHEMAS["кастомные комментарии"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "comment_text", "type": FIELD_COMMENT_TEXT, "prompt": "✏️ Введите текст комментария (один, будет повторён):"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество комментариев:"}
    ],
    "instructions": "Каждый оставленный комментарий будет содержать указанный вами текст."
}

SCHEMAS["ии комментарии"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество комментариев:"}
    ],
    "instructions": "🤖 ИИ прочитает ваш пост и сгенерирует релевантные комментарии."
}

# ------------------------------------------------------------
# 5. Голоса в опросах
# ------------------------------------------------------------
SCHEMAS["голоса в опросах"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на ПОСТ с опросом:", "example": "https://t.me/durov/123"},
        {"name": "option", "type": FIELD_VOTE_OPTION, "prompt": "🔢 Введите номер варианта ответа (1, 2, 3 …):"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество голосов:"}
    ],
    "instructions": "Голоса будут отданы за указанный вами вариант."
}

# ------------------------------------------------------------
# 6. Бусты
# ------------------------------------------------------------
SCHEMAS["бусты"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на КАНАЛ:", "example": "https://t.me/durov (для открытого) или пригласительная ссылка"},
        {"name": "days", "type": "days", "prompt": "📅 Выберите длительность буста:", "options": ["1 день", "7 дней", "14 дней", "30 дней", "60 дней", "90 дней", "180 дней"]},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество бустов:"}
    ],
    "pre_check": "⚠️ Для некоторых бустов гарантия не работает, если канал уже имеет бусты (старт отличен от 0).",
    "instructions": "Буст повышает уровень канала и позволяет публиковать истории."
}

# ------------------------------------------------------------
# 7. Подписчики
# ------------------------------------------------------------
SCHEMAS["подписчики"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на КАНАЛ или пригласительную ссылку:", "example": "https://t.me/durov или https://t.me/+xxxxxx"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество подписчиков:"}
    ],
    "instructions": "Подписчики будут добавлены на указанный канал."
}

SCHEMAS["подписчики + автопросмотры"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите пригласительную ссылку (рекомендуется):", "example": "https://t.me/+xxxxxx"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество подписчиков:"}
    ],
    "instructions": "Подписчики будут автоматически просматривать новые посты."
}

SCHEMAS["онлайн подписчики"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите пригласительную ссылку (только для новых каналов/групп):", "example": "https://t.me/+xxxxxx"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество подписчиков:"}
    ],
    "instructions": "Подписчики будут постоянно онлайн (24/7) в течение указанного срока."
}

SCHEMAS["живые подписчики"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на КАНАЛ или пригласительную ссылку:", "example": "https://t.me/durov"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество подписчиков:"}
    ],
    "pre_check": "🤖 Добавьте бота @sub_checker_ro_bot в администраторы канала с правом «Добавление подписчиков» для отслеживания.",
    "instructions": "Реальные люди, пришедшие с рекламы. Могут отписываться."
}

# ------------------------------------------------------------
# 8. Старты бота
# ------------------------------------------------------------
SCHEMAS["старты бота"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на БОТА (можно реферальную):", "example": "https://t.me/bot или https://t.me/bot?start=123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество стартов:"}
    ],
    "instructions": "Бот будет запущен указанное количество раз. Если ссылка реферальная – рефералы засчитаются."
}

SCHEMAS["старты бота + активность"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на БОТА:", "example": "https://t.me/bot"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество стартов (с активностью):"}
    ],
    "instructions": "Пользователи будут повторно запускать бота через несколько дней."
}

SCHEMAS["премиум старты бота"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на БОТА:", "example": "https://t.me/bot"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество стартов (Premium аккаунты):"}
    ],
    "instructions": "Старты с премиум-аккаунтов, повышает вес бота в поиске."
}

SCHEMAS["рефералы для ботов"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите РЕФЕРАЛЬНУЮ ссылку на бота (формат t.me/bot?start=xxx):", "example": "https://t.me/bot?start=123456"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество рефералов:"}
    ],
    "instructions": "Рефералы нажимают /start и выполняют необходимые действия."
}

# ------------------------------------------------------------
# 9. Репосты
# ------------------------------------------------------------
SCHEMAS["репосты"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на ПОСТ или ИСТОРИЮ:", "example": "https://t.me/durov/123 или https://t.me/durov/s/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество репостов:"}
    ],
    "instructions": "Репосты отображаются в статистике канала."
}

# ------------------------------------------------------------
# Функция определения схемы по ID и названию
# ------------------------------------------------------------
def get_schema_for_service(service_id: int, service_name: str) -> ServiceSchema | None:
    lower_name = service_name.lower()
    
    # Специальный случай для закрытых просмотров со скоростью (ID 3740, 4704-4710)
    if service_id in [3740] + list(range(4704, 4711)):
        return SCHEMAS["закрытых каналов (privateviewss)"]
    
    # Просмотры постов
    if "просмотры на пост" in lower_name:
        if "последних" in lower_name:
            return SCHEMAS["последних постов"]
        if "будущих" in lower_name:
            return SCHEMAS["будущих постов"]
        if "в минуту" in lower_name:
            return SCHEMAS["с выбором скорости"]
        if "закрытых каналов" in lower_name:
            return SCHEMAS["закрытых каналов (privateviewss)"]
        if "умные" in lower_name or "лесенкой" in lower_name:
            return SCHEMAS["умные просмотры"]
        if "telesco.pe" in lower_name:
            return SCHEMAS["telesco.pe просмотры"]
        if "авто" in lower_name:
            return SCHEMAS["авто просмотры"]
        return SCHEMAS["просмотры на пост"]
    
    # Просмотры историй
    if "просмотры на историю" in lower_name or "просмотры историй" in lower_name:
        return SCHEMAS["просмотры историй"]
    
    # Реакции
    if "реакц" in lower_name:
        if "закрытых каналов" in lower_name or "закрытом канале" in lower_name:
            return SCHEMAS["реакции закрытых каналов"]
        if "премиум" in lower_name or "premium" in lower_name:
            return SCHEMAS["премиум реакции"]
        if "+ просмотры" in lower_name:
            return SCHEMAS["реакции + просмотры"]
        if "авто" in lower_name:
            return SCHEMAS["авто реакции"]
        return SCHEMAS["реакции"]
    
    # Подписчики
    if "подписчик" in lower_name:
        if "авто просмотры" in lower_name:
            return SCHEMAS["подписчики + автопросмотры"]
        if "24/7" in lower_name or "онлайн" in lower_name:
            return SCHEMAS["онлайн подписчики"]
        if "живые" in lower_name:
            return SCHEMAS["живые подписчики"]
        return SCHEMAS["подписчики"]
    
    # Комментарии
    if "комментар" in lower_name:
        if "кастомные" in lower_name:
            return SCHEMAS["кастомные комментарии"]
        if "ии" in lower_name or "искусствен" in lower_name:
            return SCHEMAS["ии комментарии"]
        if "рандомные" in lower_name:
            return SCHEMAS["рандомные комментарии"]
        return SCHEMAS["рандомные комментарии"]
    
    # Голоса
    if "голоса" in lower_name or "опрос" in lower_name:
        return SCHEMAS["голоса в опросах"]
    
    # Бусты
    if "буст" in lower_name:
        return SCHEMAS["бусты"]
    
    # Старты бота
    if "старты бота" in lower_name:
        if "активность" in lower_name:
            return SCHEMAS["старты бота + активность"]
        if "премиум" in lower_name or "premium" in lower_name:
            return SCHEMAS["премиум старты бота"]
        return SCHEMAS["старты бота"]
    if "рефералы" in lower_name:
        return SCHEMAS["рефералы для ботов"]
    
    # Репосты
    if "репост" in lower_name:
        return SCHEMAS["репосты"]
    
    return None