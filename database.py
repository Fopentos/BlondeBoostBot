import sqlite3
from datetime import datetime

DB_PATH = "blondeboost.db"

def init_db():
    """Инициализация базы данных: создание таблиц users и orders"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        rub_balance REAL DEFAULT 0.0,
        full_name TEXT,
        username TEXT,
        registered_at TIMESTAMP
    )''')
    # Таблица заказов
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        tw_order_id INTEGER,
        service_id INTEGER,
        service_name TEXT,
        link TEXT,
        quantity INTEGER,
        price_rub REAL,
        status TEXT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        twiboost_response TEXT
    )''')
    conn.commit()
    conn.close()

def get_user(user_id: int):
    """Получить данные пользователя по user_id"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, rub_balance, full_name, username, registered_at FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"user_id": row[0], "rub_balance": row[1], "full_name": row[2], "username": row[3], "registered_at": row[4]}
    return None

def create_user(user_id: int, full_name: str = "", username: str = ""):
    """Создать нового пользователя, если его нет"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, full_name, username, registered_at, rub_balance) VALUES (?, ?, ?, ?, 0.0)",
              (user_id, full_name, username, datetime.now()))
    conn.commit()
    conn.close()

def add_balance_rub(user_id: int, rub_amount: float):
    """Увеличить рублёвый баланс пользователя"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE users SET rub_balance = rub_balance + ? WHERE user_id = ?", (rub_amount, user_id))
    conn.commit()
    conn.close()

def deduct_balance_rub(user_id: int, rub_amount: float) -> bool:
    """Списать рубли с баланса, если достаточно средств. Вернёт True при успехе."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT rub_balance FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row and row[0] >= rub_amount:
        c.execute("UPDATE users SET rub_balance = rub_balance - ? WHERE user_id = ?", (rub_amount, user_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def add_order(user_id: int, tw_order_id: int, service_id: int, service_name: str, link: str, quantity: int, price_rub: float, status: str = "pending"):
    """Добавить новый заказ в базу"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.now()
    c.execute('''INSERT INTO orders 
        (user_id, tw_order_id, service_id, service_name, link, quantity, price_rub, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_id, tw_order_id, service_id, service_name, link, quantity, price_rub, status, now, now))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id

def update_order_status(order_id: int, status: str, twiboost_response: str = None):
    """Обновить статус заказа и, опционально, ответ от Twiboost"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ?, updated_at = ?, twiboost_response = ? WHERE order_id = ?",
              (status, datetime.now(), twiboost_response, order_id))
    conn.commit()
    conn.close()

def get_user_orders(user_id: int, limit=10):
    """Получить последние limit заказов пользователя"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT order_id, service_name, quantity, price_rub, status, created_at 
                 FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT ?''', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return rows

def get_order_by_id(order_id: int):
    """Получить полную информацию о заказе по его ID"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_all_users(limit=100):
    """Получить список всех пользователей (для админ-панели)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, rub_balance, full_name, username, registered_at FROM users ORDER BY rub_balance DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_orders(limit=100):
    """Получить список всех заказов (для админ-панели)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT order_id, user_id, service_name, quantity, price_rub, status, created_at 
                 FROM orders ORDER BY created_at DESC LIMIT ?''', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows