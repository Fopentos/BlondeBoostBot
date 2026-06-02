# service_schemas.py
from typing import Dict, List, Any

# Типы полей
FIELD_LINK = "link"
FIELD_QUANTITY = "quantity"
FIELD_POSTS_COUNT = "posts"
FIELD_SPEED = "speed"
FIELD_VOTE_OPTION = "option"
FIELD_COMMENT_TEXT = "text"
FIELD_REACTION_ID = "reaction_id"  # для кастомных премиум-реакций

# Схема услуги: fields – список полей, pre_check – предупреждение, instructions – пояснение
ServiceSchema = Dict[str, Any]

SCHEMAS: Dict[str, ServiceSchema] = {}

# ------------------------------------------------------------
# 1. Просмотры постов
# ------------------------------------------------------------

# 1.1. На один пост (обычные)
SCHEMAS["просмотры на пост"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров (целое число):"}
    ],
    "instructions": "✅ Ссылка должна вести на конкретный пост. Просто скопируйте её из Telegram."
}

# 1.2. На несколько последних постов
SCHEMAS["последних постов"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на КАНАЛ (без номера поста):", "example": "https://t.me/durov"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров на КАЖДЫЙ пост (от 100 до 100 000 000):"}
    ],
    "instructions": "⚠️ Просмотры будут добавлены на указанное количество последних постов (5, 10, 20 и т.д. – зависит от выбранной услуги). Указывайте количество просмотров для одного поста."
}

# 1.3. На будущие посты (закрытые каналы)
SCHEMAS["будущих постов"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на ПОСЛЕДНИЙ пост в закрытом канале:", "example": "https://t.me/c/123456789/301"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров на КАЖДЫЙ будущий пост:"}
    ],
    "pre_check": "🤖 Перед заказом добавьте бота @DeepDiveTGbot в администраторы канала (с правом репоста). Без этого просмотры не накрутятся!",
    "instructions": "Просмотры будут автоматически добавляться на следующие N постов (5, 10, 20 и т.д.). Количество постов зависит от выбранной услуги."
}

# 1.4. С выбором скорости (в минуту) – скорость фиксирована в ID
SCHEMAS["с выбором скорости"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите общее количество просмотров:"}
    ],
    "instructions": "⚡️ Просмотры будут начисляться с фиксированной скоростью (1, 2, 5, 10, 20, 50 или 70 в минуту), в зависимости от выбранной услуги."
}

# 1.5. Для закрытых каналов (через бота @privateviewss_bot)
SCHEMAS["закрытых каналов (privateviewss)"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост в закрытом канале:", "example": "https://t.me/c/123456789/301"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров:"}
    ],
    "pre_check": "🤖 Добавьте бота @privateviewss_bot в администраторы канала с правом репоста. Без этого услуга не сработает!",
    "instructions": "Просмотры будут накручены на указанный пост. Убедитесь, что бот добавлен."
}

# 1.6. Умные просмотры (лесенкой для TGStat)
SCHEMAS["умные просмотры"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров (от 300 до 30 000):"}
    ],
    "instructions": "🧠 Просмотры будут начисляться постепенно, имитируя живую активность (лесенкой). Подходит для TGStat и Telemetr."
}

# 1.7. Telesco.pe просмотры (на кружочки)
SCHEMAS["telesco.pe просмотры"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на видео-сообщение (кружочек):", "example": "https://t.me/c/123456789/301?video"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров:"}
    ],
    "instructions": "Просмотры на кружочки (видеосообщения) в Telegram. Ссылка должна вести непосредственно на видео."
}

# 1.8. Авто-просмотры на новые посты
SCHEMAS["авто просмотры"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на КАНАЛ (без номера поста):", "example": "https://t.me/durov"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров на КАЖДЫЙ новый пост:"}
    ],
    "instructions": "🔄 После заказа все будущие посты в канале будут автоматически получать указанное количество просмотров. Услуга действует до окончания накрутки."
}

# ------------------------------------------------------------
# 2. Просмотры историй
# ------------------------------------------------------------
SCHEMAS["просмотры историй"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на историю (или @username канала):", "example": "https://t.me/durov/s/123  или @durov"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество просмотров:"}
    ],
    "instructions": "Если указать @username канала, просмотры будут добавлены на последнюю историю. Если ссылку на конкретную историю – только на неё."
}

# ------------------------------------------------------------
# 3. Реакции
# ------------------------------------------------------------
# 3.1. Обычные реакции (открытые каналы)
SCHEMAS["реакции"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество реакций (не более 150 000):"}
    ],
    "instructions": "Реакции будут добавлены под постом. Выбранный эмодзи уже зафиксирован в услуге."
}

# 3.2. Реакции для закрытых каналов (с возможностью перехода к подписчикам)
SCHEMAS["реакции закрытых каналов"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на ПОСТ в закрытом канале:", "example": "https://t.me/c/123456789/301"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество реакций (не больше, чем подписчиков):"}
    ],
    "pre_check": "⚠️ Для накрутки реакций в закрытом канале СНАЧАЛА закажите подписчиков (кнопка ниже). Количество подписчиков должно быть ≥ количеству реакций.\n\nПосле того как подписчики добавлены, вернитесь и закажите реакции.",
    "buttons": [{"text": "🔐 Заказать подписчиков", "callback": "sub_reactions_subscribe"}],
    "instructions": "Реакции ставят те же аккаунты, которые подписаны на канал. Без предварительной накрутки подписчиков реакции не добавятся."
}

# 3.3. Premium реакции (включая кастомные через бота)
SCHEMAS["премиум реакции"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "reaction_id", "type": FIELD_REACTION_ID, "prompt": "🔢 Введите ID реакции (для кастомной реакции получите его у бота @prem_reaction_bot, для обычной – оставьте 0):", "example": "12345"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество реакций:"}
    ],
    "instructions": "⭐️ Реакции ставятся с премиум-аккаунтов. Для кастомной реакции сначала запустите @prem_reaction_bot, вставьте ссылку на пост, скопируйте число ID и введите его в поле."
}

# 3.4. Реакции + просмотры
SCHEMAS["реакции + просмотры"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество реакций (вместе с просмотрами):"}
    ],
    "instructions": "Вместе с реакциями автоматически накручиваются просмотры поста."
}

# 3.5. Авто-реакции на будущие посты
SCHEMAS["авто реакции"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на КАНАЛ (без номера поста):", "example": "https://t.me/durov"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество реакций на КАЖДЫЙ будущий пост:"}
    ],
    "instructions": "Автоматические реакции будут добавляться на все новые посты в канале."
}

# ------------------------------------------------------------
# 4. Комментарии
# ------------------------------------------------------------
SCHEMAS["рандомные комментарии"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество комментариев:"}
    ],
    "instructions": "Комментарии будут случайными на выбранном языке (страна фиксирована в услуге)."
}

SCHEMAS["кастомные комментарии"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "comment_text", "type": FIELD_COMMENT_TEXT, "prompt": "✏️ Введите текст комментария (один, будет повторён):"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество комментариев:"}
    ],
    "instructions": "Каждый оставленный комментарий будет содержать указанный вами текст. Не используйте ссылки, мат или запрещённые темы."
}

SCHEMAS["ии комментарии"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на пост:", "example": "https://t.me/durov/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество комментариев:"}
    ],
    "instructions": "🤖 ИИ прочитает ваш пост и сгенерирует релевантные комментарии на том же языке."
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
    "instructions": "Голоса будут отданы за указанный вами вариант. Убедитесь, что номер варианта существует."
}

# ------------------------------------------------------------
# 6. Бусты
# ------------------------------------------------------------
SCHEMAS["бусты"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на КАНАЛ:", "example": "https://t.me/durov (для открытого) или пригласительная ссылка для закрытого"},
        {"name": "days", "type": "days", "prompt": "📅 Выберите длительность буста:", "options": ["1 день", "7 дней", "14 дней", "30 дней", "60 дней", "90 дней", "180 дней"]},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество бустов:"}
    ],
    "pre_check": "⚠️ Для некоторых бустов гарантия не работает, если канал уже имеет бусты (старт отличен от 0).",
    "instructions": "Буст повышает уровень канала и позволяет публиковать истории. Длительность уже выбрана."
}

# ------------------------------------------------------------
# 7. Подписчики (общая схема)
# ------------------------------------------------------------
SCHEMAS["подписчики"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на КАНАЛ или пригласительную ссылку:", "example": "https://t.me/durov  или https://t.me/+xxxxxx"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество подписчиков:"}
    ],
    "instructions": "Подписчики будут добавлены на указанный канал. Для закрытых каналов используйте пригласительную ссылку."
}

SCHEMAS["подписчики + автопросмотры"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите пригласительную ссылку (рекомендуется):", "example": "https://t.me/+xxxxxx"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество подписчиков:"}
    ],
    "instructions": "Подписчики будут автоматически просматривать новые посты в течение гарантийного срока."
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
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на БОТА (можно реферальную):", "example": "https://t.me/bot  или https://t.me/bot?start=123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество стартов:"}
    ],
    "instructions": "Бот будет запущен указанное количество раз. Если ссылка реферальная – рефералы засчитаются."
}

SCHEMAS["старты бота + активность"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на БОТА:", "example": "https://t.me/bot"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество стартов (с активностью):"}
    ],
    "instructions": "Пользователи будут повторно запускать бота через несколько дней, создавая активность."
}

SCHEMAS["премиум старты бота"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на БОТА:", "example": "https://t.me/bot"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество стартов (Premium аккаунты):"}
    ],
    "instructions": "Старты с премиум-аккаунтов, что повышает вес бота в поиске."
}

SCHEMAS["рефералы для ботов"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите РЕФЕРАЛЬНУЮ ссылку на бота (формат t.me/bot?start=xxx):", "example": "https://t.me/bot?start=123456"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество рефералов:"}
    ],
    "instructions": "Рефералы нажимают /start и выполняют необходимые действия (зависит от бота). Работает только для ботов из списка поддержки."
}

# ------------------------------------------------------------
# 9. Репосты
# ------------------------------------------------------------
SCHEMAS["репосты"] = {
    "fields": [
        {"name": "link", "type": FIELD_LINK, "prompt": "📎 Введите ссылку на ПОСТ или ИСТОРИЮ:", "example": "https://t.me/durov/123  или https://t.me/durov/s/123"},
        {"name": "quantity", "type": FIELD_QUANTITY, "prompt": "🔢 Введите количество репостов:"}
    ],
    "instructions": "Репосты отображаются в статистике канала."
}

# ------------------------------------------------------------
# 10. Живые услуги – общая схема (но наследуют другие схемы)
# ------------------------------------------------------------
# Отдельных схем для живых не нужно, они будут обрабатываться через основные схемы, но с дополнительным пояснением.
# Однако можно добавить общую схему для живых, если потребуется, но сейчас не требуется.

# ------------------------------------------------------------
# Функция для определения схемы по ID и названию услуги
# ------------------------------------------------------------
def get_schema_for_service(service_id: int, service_name: str) -> ServiceSchema | None:
    lower_name = service_name.lower()

    # Просмотры постов
    if "просмотры на пост" in lower_name:
        if "последних" in lower_name or "5 последних" in lower_name or "10 последних" in lower_name or "20 последних" in lower_name or "50 последних" in lower_name or "100 последних" in lower_name or "200 последних" in lower_name or "500 последних" in lower_name:
            return SCHEMAS["последних постов"]
        if "будущих" in lower_name:
            return SCHEMAS["будущих постов"]
        if "в минуту" in lower_name or "1 в минуту" in lower_name or "2 в минуту" in lower_name or "5 в минуту" in lower_name or "10 в минуту" in lower_name or "20 в минуту" in lower_name or "50 в минуту" in lower_name or "70 в минуту" in lower_name:
            return SCHEMAS["с выбором скорости"]
        if "закрытых каналов" in lower_name and "privateviewss" in lower_name:
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

    # Подписчики (но это не реакции, поэтому сюда не попадут – отдельно)
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

    # Голоса в опросах
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

    # Если ничего не подошло – стандартная схема (ссылка + количество) будет использована в handlers.py
    return None