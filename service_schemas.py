# service_schemas.py
from typing import Dict, Any

# Field type constants
FIELD_LINK = "link"
FIELD_QUANTITY = "quantity"
FIELD_POSTS_COUNT = "posts"
FIELD_SPEED = "speed"
FIELD_VOTE_OPTION = "option"
FIELD_COMMENT_TEXT = "text"
FIELD_REACTION_ID = "reaction_id"

ServiceSchema = Dict[str, Any]
SCHEMAS: Dict[str, ServiceSchema] = {}

# ============================================================
# CATEGORY 1: VIEWS (Просмотры)
# ============================================================

# --- 1a. views_single: Single post views ---
SCHEMAS["просмотры на пост"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на *конкретный пост*:",
            "example": "https://t.me/durov/123"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество просмотров:"
        }
    ],
    "pre_check": (
        "📊 *Просмотры на один пост*\n\n"
        "✅ Что нужно:\n"
        "• Ссылка на конкретный пост (не канал)\n"
        "• Пост должен быть в открытом канале или группе\n\n"
        "⏱ Скорость: зависит от выбранной услуги\n"
        "🔁 Гарантия: указана в названии услуги"
    )
}

# --- 1b. views_multi: Last N posts views ---
SCHEMAS["последних постов"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на *КАНАЛ* (без номера поста):",
            "example": "https://t.me/durov"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество просмотров на *КАЖДЫЙ* из последних постов:"
        }
    ],
    "pre_check": (
        "📚 *Просмотры на несколько последних постов*\n\n"
        "✅ Что нужно:\n"
        "• Ссылка на *канал*, не на конкретный пост\n"
        "• Просмотры распределятся по последним N постам\n\n"
        "⚠️ Итоговое списание = количество просмотров × количество постов\n"
        "📌 Количество постов фиксировано в каждой услуге (читайте название)"
    )
}

# --- 1c. views_speed: Views with speed control ---
SCHEMAS["с выбором скорости"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на пост:",
            "example": "https://t.me/durov/123"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите *общее* количество просмотров:"
        }
    ],
    "pre_check": (
        "⏱ *Просмотры с контролем скорости*\n\n"
        "✅ Как работает:\n"
        "• Просмотры приходят с фиксированной скоростью 1–70 в минуту\n"
        "• Имитирует органический трафик — идеально для продвижения\n"
        "• Подходит для постов, которые ещё продвигаются в рекомендациях\n\n"
        "📌 Скорость зафиксирована в выбранной услуге"
    )
}

# --- 1d. views_private: Private channel views (privateviewss bot) ---
SCHEMAS["закрытых каналов (privateviewss)"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на пост в *закрытом* канале:",
            "example": "https://t.me/c/123456789/301"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество просмотров:"
        }
    ],
    "pre_check": (
        "🔒 *Просмотры для закрытых каналов*\n\n"
        "❗️ ОБЯЗАТЕЛЬНО до заказа:\n"
        "1️⃣ Добавьте @privateviewss\\_bot в *администраторы* вашего закрытого канала\n"
        "2️⃣ Дайте боту право *репостить сообщения*\n"
        "3️⃣ Скопируйте ссылку на пост в формате https://t.me/c/XXXXXXXXX/NN\n\n"
        "⚠️ Без добавления бота в админы — услуга НЕ сработает и деньги не возвращаются"
    )
}

# --- 1e. views_smart: Smart/ladder views ---
SCHEMAS["умные просмотры"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на пост:",
            "example": "https://t.me/durov/123"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество просмотров (от 300 до 30 000):"
        }
    ],
    "pre_check": (
        "🧠 *Умные просмотры (лесенкой)*\n\n"
        "✅ Как работает:\n"
        "• Просмотры приходят постепенно — сначала медленно, затем быстрее\n"
        "• Имитируют вирусный рост публикации\n"
        "• Минимальный риск для аккаунта\n\n"
        "📊 Диапазон: 300 — 30 000 просмотров\n"
        "⏱ Скорость: 1–24 часа в зависимости от объёма"
    )
}

# --- 1f. views_telesco: Telesco.pe / video circles ---
SCHEMAS["telesco.pe просмотры"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на видео-сообщение (кружочек):",
            "example": "https://t.me/c/123456789/301"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество просмотров:"
        }
    ],
    "pre_check": (
        "📹 *Просмотры кружочков (Telesco.pe)*\n\n"
        "✅ Что нужно:\n"
        "• Ссылка на *видео-сообщение* (кружочек) в Telegram\n"
        "• Видео должно быть в открытом канале\n\n"
        "📌 Как получить ссылку:\n"
        "Откройте видео → нажмите «Поделиться» → скопируйте ссылку\n\n"
        "⚠️ Обычные ссылки на посты НЕ подойдут — нужна именно ссылка на кружочек"
    )
}

# --- 1g. views_auto: Auto-views for future posts ---
SCHEMAS["авто просмотры"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на *КАНАЛ* (без номера поста):",
            "example": "https://t.me/durov"
        },
        {
            "name": "posts_count",
            "type": FIELD_POSTS_COUNT,
            "prompt": "🔢 На сколько *будущих* постов накрутить просмотры? (от 1 до 100):"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Сколько просмотров добавлять на *каждый* пост?"
        }
    ],
    "pre_check": (
        "🔄 *Авто-просмотры для будущих постов*\n\n"
        "✅ Как работает:\n"
        "• После заказа каждый новый пост в канале автоматически получает просмотры\n"
        "• Работает на N следующих постов — указываете сами\n\n"
        "💰 Итоговая сумма = количество постов × просмотры на пост\n\n"
        "📌 Ссылка должна вести на *канал*, а не на конкретный пост"
    )
}

# ============================================================
# CATEGORY 2: STORY VIEWS (Просмотры историй) — views_single includes stories
# ============================================================
SCHEMAS["просмотры историй"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на историю *или* @username канала:",
            "example": "https://t.me/durov/s/123  или  @durov"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество просмотров истории:"
        }
    ],
    "pre_check": (
        "📖 *Просмотры историй*\n\n"
        "✅ Два варианта ссылки:\n"
        "• Ссылка на конкретную историю: https://t.me/username/s/N\n"
        "• @username канала — просмотры пойдут на *последнюю* историю\n\n"
        "⚠️ История должна быть активна (не удалена и не истекла)"
    )
}

# ============================================================
# CATEGORY 3: REACTIONS (Реакции)
# ============================================================

# --- 3a. reactions_normal: Regular reactions ---
SCHEMAS["реакции"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на пост:",
            "example": "https://t.me/durov/123"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество реакций (не более 150 000):"
        }
    ],
    "pre_check": (
        "❤️ *Обычные реакции*\n\n"
        "✅ Что нужно:\n"
        "• Ссылка на пост в открытом канале или группе\n"
        "• Выбранный эмодзи зафиксирован в названии услуги\n\n"
        "📊 Максимум: 150 000 реакций\n"
        "⏱ Старт: от 0 до 15 минут после оплаты"
    )
}

# --- 3b. reactions_private: Reactions for private channels ---
SCHEMAS["реакции закрытых каналов"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на пост в *закрытом* канале:",
            "example": "https://t.me/c/123456789/301"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество реакций (не больше числа подписчиков канала):"
        }
    ],
    "pre_check": (
        "🔒 *Реакции для закрытых каналов*\n\n"
        "⚠️ ВАЖНО: Сначала нужны подписчики!\n\n"
        "Реакции ставят те же аккаунты, которые подписаны на канал.\n"
        "Количество реакций ≤ количества подписчиков.\n\n"
        "📋 Порядок действий:\n"
        "1️⃣ Закажите подписчиков для закрытого канала (кнопка ниже)\n"
        "2️⃣ Дождитесь выполнения заказа\n"
        "3️⃣ Вернитесь и закажите реакции\n\n"
        "📌 Ссылка на пост: https://t.me/c/XXXXXXXXX/NN"
    ),
    "buttons": [{"text": "🔐 Заказать подписчиков", "callback": "sub_reactions_subscribe"}]
}

# --- 3c. reactions_subscribe: Subscribers for private channel reactions ---
SCHEMAS["подписчики для реакций в закрытом канале"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите *пригласительную ссылку* на закрытый канал:",
            "example": "https://t.me/+abcXYZ123456"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество подписчиков (рекомендуем заказать столько, сколько реакций нужно):"
        }
    ],
    "pre_check": (
        "🔐 *Подписчики для закрытых каналов (под реакции)*\n\n"
        "✅ Эти аккаунты вступят в закрытый канал и смогут ставить реакции.\n\n"
        "📌 Обязательно:\n"
        "• Только *пригласительная ссылка* формата https://t.me/+XXXXX\n"
        "• Обычная ссылка @username или https://t.me/channel НЕ подойдёт\n\n"
        "⏱ После выполнения этого заказа — закажите реакции для закрытого канала"
    )
}

# --- 3d. reactions_premium: Premium reactions ---
SCHEMAS["премиум реакции"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на пост:",
            "example": "https://t.me/durov/123"
        },
        {
            "name": "reaction_id",
            "type": FIELD_REACTION_ID,
            "prompt": (
                "⭐️ Введите ID реакции:\n"
                "• Для *кастомной* (платной) реакции — получите ID через @prem\\_reaction\\_bot\n"
                "• Для *обычной* реакции — введите *0*"
            ),
            "example": "12345  или  0"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество реакций:"
        }
    ],
    "pre_check": (
        "⭐️ *Premium реакции*\n\n"
        "Реакции ставятся с аккаунтов с Telegram Premium.\n\n"
        "📋 Как получить ID кастомной реакции:\n"
        "1️⃣ Перейдите в @prem\\_reaction\\_bot\n"
        "2️⃣ Отправьте нужный эмодзи\n"
        "3️⃣ Бот вернёт числовой ID — вставьте его в следующем шаге\n\n"
        "📌 Для обычной реакции (❤️ 👍 и т.д.) введите *0* — эмодзи уже выбран в услуге"
    )
}

# --- 3e. reactions_plus: Reactions + views combo ---
SCHEMAS["реакции + просмотры"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на пост:",
            "example": "https://t.me/durov/123"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество реакций (просмотры добавятся автоматически):"
        }
    ],
    "pre_check": (
        "➕ *Реакции + просмотры*\n\n"
        "✅ Два в одном:\n"
        "• Реакции указанного эмодзи под постом\n"
        "• Просмотры поста добавляются *автоматически* (включены в стоимость)\n\n"
        "📌 Вы вводите только количество реакций — просмотры подберутся пропорционально\n"
        "⏱ Старт: 0–15 минут"
    )
}

# --- 3f. reactions_auto: Auto-reactions for future posts ---
SCHEMAS["авто реакции"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на *КАНАЛ* (без номера поста):",
            "example": "https://t.me/durov"
        },
        {
            "name": "posts_count",
            "type": FIELD_POSTS_COUNT,
            "prompt": "🔢 На сколько *будущих* постов накрутить реакции? (от 1 до 100):"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Сколько реакций на *каждый* пост?"
        }
    ],
    "pre_check": (
        "🔄 *Авто-реакции для будущих постов*\n\n"
        "✅ Как работает:\n"
        "• Каждый новый пост в канале автоматически получает реакции\n"
        "• Эмодзи зафиксирован в выбранной услуге\n"
        "• Количество будущих постов — вы указываете сами\n\n"
        "💰 Итоговая сумма = кол-во постов × реакций на пост\n"
        "📌 Ссылка на *канал*, не на пост"
    )
}

# ============================================================
# CATEGORY 4: SUBSCRIBERS (Подписчики)
# ============================================================

# --- 4a. subs_normal: Regular subscribers ---
SCHEMAS["подписчики"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на канал или пригласительную ссылку:",
            "example": "https://t.me/durov  или  https://t.me/+xxxxxx"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество подписчиков:"
        }
    ],
    "pre_check": (
        "👥 *Обычные подписчики*\n\n"
        "✅ Принимаются оба формата ссылки:\n"
        "• Открытый канал: https://t.me/username\n"
        "• Закрытый канал: https://t.me/+XXXXX (пригласительная)\n\n"
        "⚠️ Гарантия и скорость — читайте описание конкретной услуги\n"
        "📉 Небольшое количество подписчиков может отписаться — это нормально"
    )
}

# --- 4b. subs_autoview: Subscribers with auto-views ---
SCHEMAS["подписчики + автопросмотры"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите *пригласительную* ссылку (рекомендуется):",
            "example": "https://t.me/+xxxxxx"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество подписчиков:"
        }
    ],
    "pre_check": (
        "📺 *Подписчики с авто-просмотрами*\n\n"
        "✅ Особенности:\n"
        "• Подписчики автоматически просматривают каждый новый пост в канале\n"
        "• Повышают охват публикаций без дополнительных заказов\n\n"
        "📌 Рекомендуется использовать *пригласительную ссылку*:\n"
        "Настройки канала → Пригласительные ссылки → Создать ссылку\n\n"
        "⏱ Просмотры начисляются в течение 30 минут после каждого поста"
    )
}

# --- 4c. subs_online: 24/7 online subscribers ---
SCHEMAS["онлайн подписчики"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите *пригласительную* ссылку (только для новых каналов/групп):",
            "example": "https://t.me/+xxxxxx"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество онлайн-участников:"
        }
    ],
    "pre_check": (
        "🟢 *Онлайн-подписчики 24/7*\n\n"
        "✅ Что это:\n"
        "• Аккаунты, которые постоянно отображаются как «онлайн» в вашей группе\n"
        "• Повышают доверие к каналу/группе\n\n"
        "⚠️ Важные ограничения:\n"
        "• Работает только для *групп* (не обычных каналов)\n"
        "• Рекомендуется для *новых* групп без существующих участников\n"
        "• Необходима *пригласительная ссылка* https://t.me/+XXXXX\n\n"
        "⏱ Срок работы — указан в названии услуги"
    )
}

# --- 4d. subs_live: Live subscribers from ads ---
SCHEMAS["живые подписчики"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на канал или пригласительную ссылку:",
            "example": "https://t.me/durov"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество подписчиков:"
        }
    ],
    "pre_check": (
        "📢 *Живые подписчики с рекламы*\n\n"
        "✅ Особенности:\n"
        "• Реальные люди, увидевшие рекламу вашего канала\n"
        "• Активны, могут лайкать и комментировать\n"
        "• Могут отписаться — это естественное поведение\n\n"
        "🤖 Для отслеживания результата:\n"
        "Добавьте @sub\\_checker\\_ro\\_bot в администраторы канала\n"
        "(право: добавление участников)\n\n"
        "⏱ Скорость поступления: медленнее обычных подписчиков, зато качественнее"
    )
}

# ============================================================
# CATEGORY 5: BOOSTS (Бусты)
# ============================================================

# --- 5a. boosts_open: Boosts for open channels ---
SCHEMAS["бусты открытый канал"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на *открытый* канал:",
            "example": "https://t.me/durov"
        },
        {
            "name": "days",
            "type": "days",
            "prompt": "📅 Выберите длительность буста:",
            "options": ["1 день", "7 дней", "14 дней", "30 дней", "60 дней", "90 дней", "180 дней"]
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество бустов:"
        }
    ],
    "pre_check": (
        "🚀 *Бусты для открытых каналов*\n\n"
        "✅ Что дают бусты:\n"
        "• Повышают уровень канала (Stories, эксклюзивные функции)\n"
        "• Делают канал более заметным\n\n"
        "⚠️ Важно:\n"
        "• Гарантия НЕ работает, если у канала уже есть активные бусты (старт не с 0)\n"
        "• Для открытого канала — обычная ссылка https://t.me/username"
    )
}

# --- 5b. boosts_closed: Boosts for closed/private channels ---
SCHEMAS["бусты закрытый канал"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите *пригласительную ссылку* на закрытый канал:",
            "example": "https://t.me/+abcXYZ123456"
        },
        {
            "name": "days",
            "type": "days",
            "prompt": "📅 Выберите длительность буста:",
            "options": ["1 день", "7 дней", "14 дней", "30 дней", "60 дней", "90 дней", "180 дней"]
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество бустов:"
        }
    ],
    "pre_check": (
        "🔒 *Бусты для закрытых каналов*\n\n"
        "📌 Формат ссылки:\n"
        "• Нужна *пригласительная* ссылка: https://t.me/+XXXXX\n"
        "• Обычная ссылка https://t.me/channel НЕ подойдёт\n\n"
        "✅ Как создать пригласительную ссылку:\n"
        "Настройки канала → Пригласительные ссылки → Создать\n\n"
        "⚠️ Гарантия НЕ работает при наличии уже активных бустов (старт ≠ 0)"
    )
}

# --- 5c. boosts_ru: RU-account boosts ---
SCHEMAS["бусты ru аккаунты"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на канал (открытый) или пригласительную (закрытый):",
            "example": "https://t.me/durov  или  https://t.me/+XXXXX"
        },
        {
            "name": "days",
            "type": "days",
            "prompt": "📅 Выберите длительность буста:",
            "options": ["1 день", "7 дней", "14 дней", "30 дней", "60 дней", "90 дней", "180 дней"]
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество бустов:"
        }
    ],
    "pre_check": (
        "🇷🇺 *Бусты с RU аккаунтов*\n\n"
        "✅ Особенности:\n"
        "• Бусты выставляются с российских аккаунтов Telegram\n"
        "• Подходят для каналов с русскоязычной аудиторией\n"
        "• Работают как с открытыми, так и с закрытыми каналами\n\n"
        "⚠️ Гарантия НЕ работает при наличии уже активных бустов (старт ≠ 0)\n"
        "📌 Для закрытого канала — используйте пригласительную ссылку https://t.me/+XXXXX"
    )
}

# ============================================================
# CATEGORY 6: BOT STARTS (Старты бота)
# ============================================================

# --- 6a. starts_normal: Regular bot starts ---
SCHEMAS["старты бота"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на бота (можно реферальную):",
            "example": "https://t.me/mybot  или  https://t.me/mybot?start=REF123"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество стартов:"
        }
    ],
    "pre_check": (
        "🤖 *Старты бота*\n\n"
        "✅ Как работает:\n"
        "• Пользователи переходят по ссылке и нажимают /start в боте\n"
        "• Если ссылка реферальная — рефералы засчитываются\n\n"
        "📌 Ссылка на бота:\n"
        "• Обычная: https://t.me/username\\_bot\n"
        "• Реферальная: https://t.me/username\\_bot?start=КОД\n\n"
        "⏱ Скорость и гарантия — смотрите описание конкретной услуги"
    )
}

# --- 6b. starts_activity: Starts with activity ---
SCHEMAS["старты бота + активность"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на бота:",
            "example": "https://t.me/mybot"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество стартов с активностью:"
        }
    ],
    "pre_check": (
        "🔄 *Старты бота с активностью*\n\n"
        "✅ Особенности:\n"
        "• Пользователи запускают бота и взаимодействуют с ним\n"
        "• Через несколько дней повторно запускают (симуляция возврата)\n"
        "• Повышает метрики удержания пользователей\n\n"
        "📌 Подходит для ботов с реферальными программами и геймификацией\n"
        "⏱ Скорость: медленнее обычных стартов из-за повторных посещений"
    )
}

# --- 6c. starts_premium: Premium account starts ---
SCHEMAS["премиум старты бота"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на бота:",
            "example": "https://t.me/mybot"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество стартов (с Premium аккаунтов):"
        }
    ],
    "pre_check": (
        "⭐️ *Premium старты бота*\n\n"
        "✅ Особенности:\n"
        "• Старты совершаются с аккаунтов с *Telegram Premium*\n"
        "• Повышает авторитет и рейтинг бота в поиске Telegram\n"
        "• Полезно для ботов, участвующих в рейтингах и каталогах\n\n"
        "⏱ Старт: 0–24 часа\n"
        "📌 Количество Premium аккаунтов ограничено — большие заказы выполняются дольше"
    )
}

# --- 6d. starts_referral: Bot referrals ---
SCHEMAS["рефералы для ботов"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите *реферальную* ссылку на бота (обязательно с параметром start=):",
            "example": "https://t.me/mybot?start=REF123456"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество рефералов:"
        }
    ],
    "pre_check": (
        "🔗 *Рефералы для ботов*\n\n"
        "✅ Что нужно:\n"
        "• *Реферальная* ссылка с параметром ?start= (обязательно!)\n"
        "• Обычная ссылка без параметра — рефералы НЕ засчитаются\n\n"
        "📌 Формат ссылки:\n"
        "https://t.me/username\\_bot?start=ВАШ\\_КОД\n\n"
        "⏱ Пользователи нажимают /start и выполняют действия в боте\n"
        "💡 Используйте для фарма рефералов в реферальных программах"
    )
}

# ============================================================
# CATEGORY 7: COMMENTS (Комментарии)
# ============================================================

# --- 7a. comments_random: Random comments ---
SCHEMAS["рандомные комментарии"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на пост (с открытыми комментариями):",
            "example": "https://t.me/durov/123"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество комментариев:"
        }
    ],
    "pre_check": (
        "🎲 *Рандомные комментарии*\n\n"
        "✅ Особенности:\n"
        "• Комментарии случайные на языке, указанном в услуге (RU / EN / смешанные)\n"
        "• Разные аккаунты, разный текст — выглядит естественно\n\n"
        "⚠️ Требования:\n"
        "• Пост должен быть в *открытом* канале с включёнными комментариями\n"
        "• Комментарии не должны быть отключены или ограничены\n\n"
        "📌 Ссылка на конкретный пост, не на канал"
    )
}

# --- 7b. comments_custom: Custom text comments ---
SCHEMAS["кастомные комментарии"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на пост (с открытыми комментариями):",
            "example": "https://t.me/durov/123"
        },
        {
            "name": "comment_text",
            "type": FIELD_COMMENT_TEXT,
            "prompt": "✏️ Введите текст комментария (будет повторён указанное количество раз):"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество комментариев:"
        }
    ],
    "pre_check": (
        "✏️ *Кастомные комментарии*\n\n"
        "✅ Особенности:\n"
        "• Каждый комментарий содержит *ваш текст*\n"
        "• Один текст повторяется N раз от разных аккаунтов\n\n"
        "📌 Рекомендации по тексту:\n"
        "• Короткий и нейтральный текст — выглядит естественнее\n"
        "• Избегайте спамных фраз и внешних ссылок\n\n"
        "⚠️ Пост должен быть в открытом канале с включёнными комментариями"
    )
}

# --- 7c. comments_ai: AI-generated comments ---
SCHEMAS["ии комментарии"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на пост (с открытыми комментариями):",
            "example": "https://t.me/durov/123"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество ИИ-комментариев:"
        }
    ],
    "pre_check": (
        "🤖 *ИИ-комментарии*\n\n"
        "✅ Как работает:\n"
        "• Искусственный интеллект *читает ваш пост* и генерирует релевантные комментарии\n"
        "• Каждый комментарий уникален и соответствует теме публикации\n"
        "• Выглядит максимально естественно\n\n"
        "📌 Лучше всего работает для:\n"
        "• Информационных постов\n"
        "• Новостей и обзоров\n"
        "• Постов с вопросами\n\n"
        "⚠️ Для коротких постов (1–2 слова) качество ниже"
    )
}

# ============================================================
# CATEGORY 8: POLL VOTES (Голоса в опросах)
# ============================================================

SCHEMAS["голоса в опросах"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на пост *с опросом*:",
            "example": "https://t.me/durov/123"
        },
        {
            "name": "option",
            "type": FIELD_VOTE_OPTION,
            "prompt": "🗳 Введите *номер варианта* ответа, за который голосовать (1, 2, 3 …):"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество голосов:"
        }
    ],
    "pre_check": (
        "🗳 *Голоса в опросах*\n\n"
        "✅ Инструкция:\n"
        "1️⃣ Откройте пост с опросом\n"
        "2️⃣ Посмотрите на варианты — они пронумерованы сверху вниз (1, 2, 3 …)\n"
        "3️⃣ Введите номер нужного варианта\n\n"
        "📌 Ссылка на пост с опросом (не на канал)\n\n"
        "⚠️ Опрос должен быть *активным* и не анонимным (анонимные опросы не поддерживаются некоторыми услугами)"
    )
}

# ============================================================
# CATEGORY 9: REPOSTS (Репосты)
# ============================================================

# --- 9a. reposts_posts: Regular post reposts ---
SCHEMAS["репосты постов"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на *пост* для репостов:",
            "example": "https://t.me/durov/123"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество репостов:"
        }
    ],
    "pre_check": (
        "🔄 *Репосты постов*\n\n"
        "✅ Особенности:\n"
        "• Пост пересылается (форвардится) другими аккаунтами\n"
        "• Репосты отображаются в статистике канала (Telegram Analytics)\n"
        "• Увеличивает виральность публикации\n\n"
        "📌 Ссылка на *конкретный пост*, не на канал\n"
        "⏱ Скорость: указана в описании услуги (~50–3000 репостов в сутки)"
    )
}

# --- 9b. reposts_stories: Story reposts ---
SCHEMAS["репосты историй"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на *историю*:",
            "example": "https://t.me/durov/s/123"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество репостов истории:"
        }
    ],
    "pre_check": (
        "📸 *Репосты историй*\n\n"
        "✅ Особенности:\n"
        "• История пересылается другими аккаунтами в их истории\n"
        "• Увеличивает охват истории\n\n"
        "📌 Как получить ссылку на историю:\n"
        "Откройте историю → нажмите '...' → Поделиться → Скопировать ссылку\n\n"
        "⚠️ Формат ссылки: https://t.me/username/s/НОМЕР\n"
        "История должна быть *активной* (не истекшей)"
    )
}

# --- 9c. reposts_geo: Geo-targeted reposts ---
SCHEMAS["репосты геотаргетинг"] = {
    "fields": [
        {
            "name": "link",
            "type": FIELD_LINK,
            "prompt": "📎 Введите ссылку на пост для репостов:",
            "example": "https://t.me/durov/123"
        },
        {
            "name": "quantity",
            "type": FIELD_QUANTITY,
            "prompt": "🔢 Введите количество репостов:"
        }
    ],
    "pre_check": (
        "🌍 *Геотаргетированные репосты*\n\n"
        "✅ Особенности:\n"
        "• Репосты совершаются аккаунтами из *конкретной страны* (указана в названии услуги)\n"
        "• Доступные страны: Россия, США, Германия, Италия, Турция, Израиль, Индонезия, Китай, Индия, ОАЭ\n\n"
        "📌 Идеально для:\n"
        "• Продвижения на аудиторию конкретной страны\n"
        "• Локального контента и региональных предложений\n\n"
        "⏱ Скорость: медленнее обычных репостов из-за таргетинга"
    )
}

# ============================================================
# CATEGORY 10: LIVE (Живые)
# ============================================================

SCHEMAS["живые подписчики live"] = SCHEMAS["живые подписчики"]

# ============================================================
# SCHEMA RESOLVER: maps service name/ID → schema
# ============================================================

# ============================================================
# SUBCATEGORY → SCHEMA DIRECT MAP (primary lookup)
# ============================================================
# Maps the subcategory key (stored in FSM state as category_name)
# to the exact schema. This is the reliable source of truth —
# every service inside a subcategory gets the same schema
# regardless of how its API name looks.

SUBCATEGORY_TO_SCHEMA: Dict[str, ServiceSchema] = {
    # Views
    "views_single":    SCHEMAS["просмотры на пост"],
    "views_multi":     SCHEMAS["последних постов"],
    "views_speed":     SCHEMAS["с выбором скорости"],
    "views_private":   SCHEMAS["закрытых каналов (privateviewss)"],
    "views_smart":     SCHEMAS["умные просмотры"],
    "views_telesco":   SCHEMAS["telesco.pe просмотры"],
    "views_auto":      SCHEMAS["авто просмотры"],
    # Story views
    "views_stories":   SCHEMAS["просмотры историй"],
    # Reactions
    "reactions_normal":    SCHEMAS["реакции"],
    "reactions_private":   SCHEMAS["реакции закрытых каналов"],
    "reactions_subscribe": SCHEMAS["подписчики для реакций в закрытом канале"],
    "reactions_premium":   SCHEMAS["премиум реакции"],
    "reactions_plus":      SCHEMAS["реакции + просмотры"],
    "reactions_auto":      SCHEMAS["авто реакции"],
    # Subscribers
    "subs_normal":   SCHEMAS["подписчики"],
    "subs_autoview": SCHEMAS["подписчики + автопросмотры"],
    "subs_online":   SCHEMAS["онлайн подписчики"],
    "subs_live":     SCHEMAS["живые подписчики"],
    # Boosts
    "boosts_open":   SCHEMAS["бусты открытый канал"],
    "boosts_closed": SCHEMAS["бусты закрытый канал"],
    "boosts_ru":     SCHEMAS["бусты ru аккаунты"],
    # Bot starts
    "starts_normal":    SCHEMAS["старты бота"],
    "starts_activity":  SCHEMAS["старты бота + активность"],
    "starts_premium":   SCHEMAS["премиум старты бота"],
    "starts_referral":  SCHEMAS["рефералы для ботов"],
    # Comments
    "comments_random": SCHEMAS["рандомные комментарии"],
    "comments_custom": SCHEMAS["кастомные комментарии"],
    "comments_ai":     SCHEMAS["ии комментарии"],
    # Polls
    "polls_normal": SCHEMAS["голоса в опросах"],
    # Reposts
    "reposts_posts":   SCHEMAS["репосты постов"],
    "reposts_stories": SCHEMAS["репосты историй"],
    "reposts_geo":     SCHEMAS["репосты геотаргетинг"],
    # Live
    "live_subs": SCHEMAS["живые подписчики"],
}


# Countries used in geo reposts (for detection)
_GEO_COUNTRIES = [
    "италия", "германия", "турция", "израиль",
    "индонезия", "китай", "сша", "россия", "индия", "арабские", "оаэ"
]


def get_schema_for_service(service_id: int, service_name: str) -> ServiceSchema | None:
    lower = service_name.lower()

    # --- Special case: privateviewss bot IDs ---
    if service_id in [3740] + list(range(4704, 4711)):
        return SCHEMAS["закрытых каналов (privateviewss)"]

    # ---- VIEWS ----
    if "просмотры на пост" in lower or "просмотры [" in lower:
        if "последних" in lower:
            return SCHEMAS["последних постов"]
        if "будущих" in lower:
            return SCHEMAS["будущих постов"]
        if "в минуту" in lower:
            return SCHEMAS["с выбором скорости"]
        if "закрытых каналов" in lower:
            return SCHEMAS["закрытых каналов (privateviewss)"]
        if "умные" in lower or "лесенкой" in lower:
            return SCHEMAS["умные просмотры"]
        if "telesco.pe" in lower:
            return SCHEMAS["telesco.pe просмотры"]
        if "авто" in lower:
            return SCHEMAS["авто просмотры"]
        return SCHEMAS["просмотры на пост"]

    if "просмотры на историю" in lower or "просмотры историй" in lower:
        return SCHEMAS["просмотры историй"]

    # ---- REACTIONS ----
    if "реакц" in lower or "реакция" in lower:
        if "закрытых каналов" in lower or "закрытом канале" in lower:
            return SCHEMAS["реакции закрытых каналов"]
        if "премиум" in lower or "premium" in lower:
            return SCHEMAS["премиум реакции"]
        if "+ просмотры" in lower:
            return SCHEMAS["реакции + просмотры"]
        if "авто" in lower:
            return SCHEMAS["авто реакции"]
        return SCHEMAS["реакции"]

    # ---- SUBSCRIBERS ----
    if "подписчик" in lower:
        # Subscribers for reactions in closed channels (reactions_subscribe subcategory)
        if "закрытых каналов" in lower or "для реакций" in lower:
            return SCHEMAS["подписчики для реакций в закрытом канале"]
        if "авто просмотры" in lower:
            return SCHEMAS["подписчики + автопросмотры"]
        if "24/7" in lower or "онлайн" in lower:
            return SCHEMAS["онлайн подписчики"]
        if "живые" in lower:
            return SCHEMAS["живые подписчики"]
        return SCHEMAS["подписчики"]

    # ---- COMMENTS ----
    if "комментар" in lower:
        if "кастомные" in lower:
            return SCHEMAS["кастомные комментарии"]
        if "ии" in lower or "искусствен" in lower or "ai" in lower:
            return SCHEMAS["ии комментарии"]
        return SCHEMAS["рандомные комментарии"]

    # ---- POLLS ----
    if "голоса" in lower or "опрос" in lower:
        return SCHEMAS["голоса в опросах"]

    # ---- BOOSTS ----
    if "буст" in lower:
        if "закрытых" in lower:
            return SCHEMAS["бусты закрытый канал"]
        if "ru" in lower:
            return SCHEMAS["бусты ru аккаунты"]
        return SCHEMAS["бусты открытый канал"]

    # ---- BOT STARTS ----
    if "рефералы" in lower:
        return SCHEMAS["рефералы для ботов"]
    if "старты бота" in lower:
        if "активность" in lower:
            return SCHEMAS["старты бота + активность"]
        if "премиум" in lower or "premium" in lower:
            return SCHEMAS["премиум старты бота"]
        return SCHEMAS["старты бота"]

    # ---- REPOSTS ----
    if "репост" in lower:
        if "истори" in lower:
            return SCHEMAS["репосты историй"]
        if any(country in lower for country in _GEO_COUNTRIES):
            return SCHEMAS["репосты геотаргетинг"]
        return SCHEMAS["репосты постов"]

    # ---- UNIVERSAL FALLBACK (never return None) ----
    # Any service not matched above gets a generic link + quantity schema
    return {
        "fields": [
            {
                "name": "link",
                "type": FIELD_LINK,
                "prompt": "📎 Введите ссылку:",
                "example": "https://t.me/..."
            },
            {
                "name": "quantity",
                "type": FIELD_QUANTITY,
                "prompt": "🔢 Введите количество:"
            }
        ]
    }
