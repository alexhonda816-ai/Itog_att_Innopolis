import sqlite3
import json
import csv
from models import Client, Product, Order

DB_FILE = "shop.db"


def get_connection():
    """Возвращает соединение с базой данных."""
    return sqlite3.connect(DB_FILE)


def create_tables():
    """Создает таблицы в базе данных, если они ещё не существуют."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT NOT NULL,
                    address TEXT
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    order_date TEXT NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients(id)
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER DEFAULT 1,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                );
            """)
    except sqlite3.Error as e:
        print(f"Ошибка при создании таблиц: {e}")


def add_client(client):
    """Добавляет нового клиента в базу данных."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clients (name, email, phone, address) VALUES (?, ?, ?, ?)",
                (client.name, client.email, client.phone, client.address)
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("Клиент с таким email уже существует.")
    except sqlite3.Error as e:
        print(f"Ошибка БД: {e}")
        return None


def get_all_clients():
    """Получает список всех клиентов из базы данных."""
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM clients;")
            rows = cursor.fetchall()
            return [Client(**dict(row)) for row in rows]
    except sqlite3.Error as e:
        print(f"Ошибка БД: {e}")
        return []


def add_product(product):
    """Добавляет новый товар в базу данных."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO products (name, price) VALUES (?, ?);",
                (product.name, product.price)
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"Ошибка БД: {e}")
        return None


def get_all_products():
    """Получает список всех товаров из базы данных."""
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products;")
            rows = cursor.fetchall()
            return [Product(**dict(row)) for row in rows]
    except sqlite3.Error as e:
        print(f"Ошибка БД: {e}")
        return []


def add_order(order):
    """Добавляет новый заказ в базу данных."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (client_id, order_date) VALUES (?, ?);",
                (order.client_id, order.order_date)
            )
            order_id = cursor.lastrowid

            # Добавляем продукты в заказ
            for product in order.products:
                cursor.execute(
                    "INSERT INTO order_products (order_id, product_id) VALUES (?, ?);",
                    (order_id, product.id)
                )
            conn.commit()
            return order_id
    except sqlite3.Error as e:
        print(f"Ошибка БД: {e}")
        return None

def get_all_orders():
    """Получает список всех заказов из базы данных."""
    try:
        with get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            query = """
                SELECT o.id AS order_id, o.order_date, c.name AS client_name,
                       GROUP_CONCAT(p.name || ': ' || op.quantity) AS items,
                       SUM(p.price * op.quantity) AS total_cost
                FROM orders o
                LEFT JOIN clients c ON o.client_id = c.id
                LEFT JOIN order_products op ON o.id = op.order_id
                LEFT JOIN products p ON op.product_id = p.id
                GROUP BY o.id
                ORDER BY o.id ASC;
            """
            cursor.execute(query)
            result = cursor.fetchall()
            # Преобразуем raw-записи в объекты Order
            orders = [
                Order(
                    id=row['order_id'],
                    client_id=None,  # Так как client_id нам тут не нужен, ставим None
                    products=[],     # Мы получаем готовые товары и их цены, поэтому пустой список
                    order_date=row['order_date'],
                    _total_cost=row['total_cost'],  # Добавляем скрытый атрибут для удобства
                    client_name=row['client_name'], # Передаем дополнительно имя клиента
                    items=row['items']              # Списки товаров
                ) for row in result
            ]
            return orders
    except sqlite3.Error as e:
        print(f"Ошибка БД: {e}")
        return []

def export_data_to_json(file_path):
    """Экспортирует данные клиентов и товаров в JSON-файл."""
    data = {
        "clients": [c.__dict__ for c in get_all_clients()],
        "products": [p.__dict__ for p in get_all_products()]
    }
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Ошибка записи в файл: {e}")


def import_data_from_csv(file_path):
    """Импортирует данные клиентов из CSV-файла."""
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    client = Client(
                        name=row['name'],
                        email=row['email'],
                        phone=row['phone'],
                        address=row['address']
                    )
                    client.validate()
                    add_client(client)
                except (ValueError, KeyError) as e:
                    print(f"Ошибка в строке CSV: {row}. {e}")
    except IOError as e:
        print(f"Ошибка чтения файла: {e}")