import os

# Токен вашего Telegram бота (из @BotFather)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# API ключ Twiboost (из личного кабинета)
TWIBOOST_API_KEY = os.getenv("TWIBOOST_API_KEY")
TWIBOOST_API_URL = "https://twiboost.com/api/v2"

# Ваш Telegram ID (для доступа к админ-панели)
# Узнать свой ID можно через бота @userinfobot или в профиле бота.
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Курс: 1 Star = 1.25 рубля
STAR_TO_RUB = 1.25

# Глобальная наценка (коэффициент) – 5.0 = 400%
DEFAULT_MARKUP_FACTOR = 5.0

# Индивидуальные наценки по ID услуги (цена_клиента = rate * factor)
# Сейчас все услуги используют глобальный коэффициент 5.0
MARKUP_BY_SERVICE = {
    # все услуги теперь 5.0
}
