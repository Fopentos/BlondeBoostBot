# service_mapping.py
# Explicit service_id → subcategory mapping for BlondeBoostBot.
# Source: Twiboost API services list (Telegram / Telegram Premium network).
#
# Usage:
#   from service_mapping import SUBCATEGORY_SERVICE_IDS, SERVICE_TO_SUBCATEGORY
#
# SUBCATEGORY_SERVICE_IDS  — dict[str, frozenset[int]]  subcategory → set of IDs
# SERVICE_TO_SUBCATEGORY   — dict[int, str]             service_id  → subcategory

from __future__ import annotations


# ─────────────────────────────────────────────────────────────────────────────
# 1. VIEWS (Просмотры)
# ─────────────────────────────────────────────────────────────────────────────

# 1a. views_single — просмотры на один конкретный пост
_VIEWS_SINGLE = frozenset({
    1612, 1614, 1615, 1616, 1617, 1618, 1619, 1620, 1621, 1622, 1623,
    1993, 2031, 2477,
    2745, 2746, 2747, 2748, 2749, 2750, 2751, 2752, 2753, 2754, 2755, 2756, 2757,
    2900, 3133, 3324,
    4210, 4211, 4212, 4213, 4214, 4215, 4216, 4217,
    4447, 4703,
    5162, 5163,
})

# 1b. views_multi — просмотры на последние N постов (ссылка на канал)
_VIEWS_MULTI = frozenset({
    1695, 1696, 1697, 1698, 1699, 1700, 1701,
    2251, 2252,
    4732, 4733, 4734, 4735, 4736, 4737, 4738,
})

# 1c. views_speed — просмотры с выбором скорости (N в минуту)
_VIEWS_SPEED = frozenset({
    4405, 4406, 4407, 4408, 4409, 4410, 4411,
})

# 1d. views_private — просмотры для закрытых каналов
_VIEWS_PRIVATE = frozenset({
    3740, 4704, 4705, 4706, 4707, 4708, 4709, 4710,
})

# 1e. views_smart — умные просмотры / лесенкой
_VIEWS_SMART = frozenset({
    4340, 4347, 4702,
})

# 1f. views_telesco — просмотры Telesco.pe (кружочки)
_VIEWS_TELESCO = frozenset({
    2769, 2770, 2771, 2772, 2773, 2774, 2775, 2776,
})

# 1g. views_auto — авто-просмотры на будущие посты
_VIEWS_AUTO = frozenset({
    3302, 4087, 4337, 4455, 4711, 5132, 5160, 5161, 5164, 5165,
})

# 1h. views_stories — просмотры историй
_VIEWS_STORIES = frozenset({
    966, 1543, 2250, 3239,
})

# 1i. views_premium — Premium просмотры [NEW]
_VIEWS_PREMIUM = frozenset({
    2563, 2609, 2633, 2690,
    3141, 3165,
    3341, 3342, 3343, 3344, 3345,
    3450, 3551, 3783,
    4726, 4727, 4728, 4729, 4730,
})


# ─────────────────────────────────────────────────────────────────────────────
# 2. REACTIONS (Реакции)
# ─────────────────────────────────────────────────────────────────────────────

# 2a. reactions_normal — обычные реакции на посты
_REACTIONS_NORMAL = frozenset({
    2817, 2818, 2819, 2820, 2821, 2822, 2823, 2824, 2825, 2826, 2827, 2828, 2829,
    2830, 2831, 2832, 2833, 2834, 2835, 2836, 2837, 2838, 2839, 2840, 2841, 2842,
    2843, 2844, 2845, 2846, 2847, 2848, 2849, 2850, 2851, 2852, 2853, 2854, 2855,
    2856, 2857, 2858, 2859, 2860, 2861, 2862, 2863, 2864, 2865, 2866, 2867, 2868,
    2869, 2870, 2871, 2872, 2873, 2874, 2875, 2876, 2877, 2878, 2879, 2880, 2881,
    2882, 2883, 2884, 2885, 2886, 2887, 2888, 2890, 2891,
    4029, 4030, 4031,
    4032, 4033, 4034, 4035, 4036, 4037, 4038, 4039, 4040, 4041, 4042, 4043, 4044,
    4045, 4046, 4047, 4048,
    4506, 4507,
    4689, 4690, 4691, 4692, 4693, 4694, 4695,
})

# 2b. reactions_private — реакции для закрытых каналов
_REACTIONS_PRIVATE = frozenset({
    4336, 4351, 4353,
})

# 2c. reactions_subscribe — подписчики для реакций в закрытом канале
_REACTIONS_SUBSCRIBE = frozenset({
    4335,
})

# 2d. reactions_premium — Premium реакции
_REACTIONS_PREMIUM = frozenset({
    4188, 4474, 4475, 4476, 4477, 4478,
})

# 2e. reactions_plus — реакции + просмотры (пустой набор, услуги добавляются при необходимости)
_REACTIONS_PLUS: frozenset[int] = frozenset()

# 2f. reactions_auto — авто-реакции на будущие посты
_REACTIONS_AUTO = frozenset({
    3303, 3304,
})

# 2g. reactions_stories — реакции на истории [NEW]
_REACTIONS_STORIES = frozenset({
    2035, 3171, 3240, 3795, 3796,
})


# ─────────────────────────────────────────────────────────────────────────────
# 3. SUBSCRIBERS (Подписчики)
# ─────────────────────────────────────────────────────────────────────────────

# 3a. subs_normal — обычные подписчики
_SUBS_NORMAL = frozenset({
    1292,
    2016, 2086, 2226, 2227, 2466, 2474, 2475, 2478, 2496,
    2560, 2561, 2562, 2700, 2740, 2742, 2743, 2744,
    2980,
    3036, 3054, 3091, 3092, 3093, 3267, 3288, 3289, 3337, 3346, 3359,
    3422, 3423, 3456, 3457, 3459, 3465, 3467,
    3765, 3771, 3835, 3836, 3837, 3958,
    4003, 4049, 4050, 4051, 4244, 4256, 4257, 4284,
    4419, 4420, 4421, 4422, 4423, 4424, 4448,
    4699, 4700, 4701, 4767,
    4946, 4947, 4948, 4949, 4950, 4961,
    5176, 5177, 5178, 5179, 5180, 5181, 5182, 5183,
    5184, 5185, 5186, 5187, 5188, 5189,
    5190, 5191, 5192, 5193, 5194, 5195, 5196, 5197,
    5198, 5199, 5200, 5201, 5202, 5203, 5204, 5205,
    5206, 5207, 5208, 5209, 5210, 5211, 5212, 5213, 5214,
    5215, 5216, 5217, 5218, 5219, 5220,
})

# 3b. subs_autoview — подписчики + авто-просмотры
_SUBS_AUTOVIEW = frozenset({
    4933, 4934, 4935, 4951, 4952, 4953, 4954, 4955, 4956, 4957, 4958,
})

# 3c. subs_online — 24/7 онлайн-подписчики
_SUBS_ONLINE = frozenset({
    4483, 4486, 4487, 4488, 4489, 4500,
    5106, 5107, 5108,
})

# 3d. subs_live — живые подписчики с рекламы (также дублируется в live_subs)
_SUBS_LIVE = frozenset({
    3948, 3949, 3950, 3951, 3952, 3953, 3954, 3955, 3956,
})

# 3e. subs_premium — Premium подписчики [NEW]
_SUBS_PREMIUM = frozenset({
    2605, 2606, 2621, 2622, 2631, 2652, 2653, 2667, 2675,
    2966,
    3033, 3138, 3140, 3150, 3152, 3153, 3173,
    3327, 3328, 3329, 3427, 3429, 3430,
    3434, 3435, 3461, 3462, 3463, 3464,
    3570,
    3983, 3984, 3985, 3986,
    4061,
    4140, 4141, 4142, 4143, 4144, 4145, 4146, 4147, 4148,
    4177, 4178, 4180,
    4404,
    4606, 4607, 4608, 4609, 4610, 4611, 4612,
    4626, 4627, 4628, 4629, 4630, 4631, 4632, 4633, 4634, 4635,
    4656, 4658, 4659,
    4936, 4938, 4939, 4940, 4941, 4942, 4943, 4944, 4945,
    5110, 5111, 5112, 5113, 5114, 5115,
})


# ─────────────────────────────────────────────────────────────────────────────
# 4. BOOSTS (Бусты)
# ─────────────────────────────────────────────────────────────────────────────

# 4a. boosts_open — бусты для открытых каналов
_BOOSTS_OPEN = frozenset({
    1269, 1270, 2970, 3148, 3911, 3912, 4255, 4328, 4556, 4575, 4654,
})

# 4b. boosts_closed — бусты для закрытых каналов
_BOOSTS_CLOSED = frozenset({
    1256, 2191, 3752, 4329,
})

# 4c. boosts_ru — бусты с RU аккаунтов
_BOOSTS_RU = frozenset({
    3684, 4640, 4641, 4642, 4643, 4644, 4645, 4646,
})


# ─────────────────────────────────────────────────────────────────────────────
# 5. BOT STARTS (Старты бота)
# ─────────────────────────────────────────────────────────────────────────────

# 5a. starts_normal — обычные старты бота
_STARTS_NORMAL = frozenset({
    2228, 2229, 2230, 2231, 2233, 2234, 2235, 2236, 2237,
    2664, 2665,
    3576, 3579, 3580, 3581, 3582, 3583, 3584, 3585, 3588, 3589, 3590, 3591, 3593, 3594,
    3721, 3722,
    3785, 3913, 3914, 3915, 3916, 3917, 3918, 3919, 3920, 3921, 3922, 3923, 3924, 3925,
    4379, 4463, 4604,
    5033,
})

# 5b. starts_activity — старты бота + активность (без Premium)
_STARTS_ACTIVITY = frozenset({
    3820,
    3991, 3992, 3994, 3995, 3997, 3998,
    4052, 4053, 4054, 4055, 4056, 4057,
    4330,
    5034, 5035, 5036, 5037, 5038, 5039, 5040, 5041, 5042,
})

# 5c. starts_premium — Premium старты бота (включая активность с Premium)
_STARTS_PREMIUM = frozenset({
    1266, 2017, 2061, 2614, 2668, 2669,
    3051,
    3144, 3145, 3167, 3172,
    3290, 3395, 3405, 3406, 3407, 3409, 3410,
    3786, 3797,
    3987, 3988, 3989, 3990,
    3999, 4000, 4005, 4006, 4007,
    4062, 4063, 4064, 4068, 4150, 4283,
    4479, 4481, 4482, 4616,
    4636, 4637, 4638, 4639,
    4717, 4718, 4719, 4720, 4721,
    4910, 4911, 4912, 4913, 4914, 4915, 4916, 4917, 4918, 4919,
    4920, 4921, 4922, 4923, 4924, 4925, 4926, 4927, 4928, 4929,
})

# 5d. starts_referral — рефералы для ботов
_STARTS_REFERRAL = frozenset({
    2200, 2224, 2494, 2973,
})


# ─────────────────────────────────────────────────────────────────────────────
# 6. COMMENTS (Комментарии)
# ─────────────────────────────────────────────────────────────────────────────

_COMMENTS_RANDOM = frozenset({
    3375, 3377, 3378, 3379, 3380, 3381, 3382, 3383, 3577,
})

_COMMENTS_CUSTOM = frozenset({
    3376, 4208, 4932,
})

_COMMENTS_AI = frozenset({
    3266,
})


# ─────────────────────────────────────────────────────────────────────────────
# 7. POLLS (Голоса)
# ─────────────────────────────────────────────────────────────────────────────

_POLLS_NORMAL = frozenset({
    965, 2812, 3119, 3120,
})


# ─────────────────────────────────────────────────────────────────────────────
# 8. REPOSTS (Репосты)
# ─────────────────────────────────────────────────────────────────────────────

_REPOSTS_POSTS = frozenset({
    1527,
})

_REPOSTS_STORIES = frozenset({
    3241,
})

_REPOSTS_GEO = frozenset({
    4464, 4465, 4466, 4467, 4468, 4469, 4470, 4471, 4472, 4473,
})

# reposts_premium — Premium репосты [NEW]
_REPOSTS_PREMIUM = frozenset({
    2691, 3452,
})


# ─────────────────────────────────────────────────────────────────────────────
# 9. LIVE (Живые)
# ─────────────────────────────────────────────────────────────────────────────

# live_subs shares the same IDs as subs_live (different category path, same services)
_LIVE_SUBS = _SUBS_LIVE


# ─────────────────────────────────────────────────────────────────────────────
# Public maps
# ─────────────────────────────────────────────────────────────────────────────

SUBCATEGORY_SERVICE_IDS: dict[str, frozenset[int]] = {
    # Views
    "views_single":    _VIEWS_SINGLE,
    "views_multi":     _VIEWS_MULTI,
    "views_speed":     _VIEWS_SPEED,
    "views_private":   _VIEWS_PRIVATE,
    "views_smart":     _VIEWS_SMART,
    "views_telesco":   _VIEWS_TELESCO,
    "views_auto":      _VIEWS_AUTO,
    "views_stories":   _VIEWS_STORIES,
    "views_premium":   _VIEWS_PREMIUM,     # NEW
    # Reactions
    "reactions_normal":    _REACTIONS_NORMAL,
    "reactions_private":   _REACTIONS_PRIVATE,
    "reactions_subscribe": _REACTIONS_SUBSCRIBE,
    "reactions_premium":   _REACTIONS_PREMIUM,
    "reactions_plus":      _REACTIONS_PLUS,
    "reactions_auto":      _REACTIONS_AUTO,
    "reactions_stories":   _REACTIONS_STORIES,  # NEW
    # Subscribers
    "subs_normal":   _SUBS_NORMAL,
    "subs_autoview": _SUBS_AUTOVIEW,
    "subs_online":   _SUBS_ONLINE,
    "subs_live":     _SUBS_LIVE,
    "subs_premium":  _SUBS_PREMIUM,     # NEW
    # Boosts
    "boosts_open":   _BOOSTS_OPEN,
    "boosts_closed": _BOOSTS_CLOSED,
    "boosts_ru":     _BOOSTS_RU,
    # Bot starts
    "starts_normal":    _STARTS_NORMAL,
    "starts_activity":  _STARTS_ACTIVITY,
    "starts_premium":   _STARTS_PREMIUM,
    "starts_referral":  _STARTS_REFERRAL,
    # Comments
    "comments_random": _COMMENTS_RANDOM,
    "comments_custom": _COMMENTS_CUSTOM,
    "comments_ai":     _COMMENTS_AI,
    # Polls
    "polls_normal": _POLLS_NORMAL,
    # Reposts
    "reposts_posts":   _REPOSTS_POSTS,
    "reposts_stories": _REPOSTS_STORIES,
    "reposts_geo":     _REPOSTS_GEO,
    "reposts_premium": _REPOSTS_PREMIUM,  # NEW
    # Live
    "live_subs": _LIVE_SUBS,
}

# Reverse map: service_id → subcategory (for O(1) lookup by ID)
SERVICE_TO_SUBCATEGORY: dict[int, str] = {
    service_id: subcat
    for subcat, ids in SUBCATEGORY_SERVICE_IDS.items()
    for service_id in ids
}
