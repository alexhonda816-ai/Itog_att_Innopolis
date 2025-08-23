import re

class BaseModel:
    def to_dict(self):
        """Преобразует атрибуты объекта в словарь."""
        return vars(self)

class Client(BaseModel):
    def __init__(self, name, email, phone, address, id=None):
        self.id = id
        self.name = name
        self._email = email  # Использование приватного атрибута для хранения почты
        self.phone = phone
        self.address = address

    @property
    def email(self):
        """Получает значение email."""
        return self._email

    @email.setter
    def email(self, value):
        """Устанавливает email с предварительной валидацией формата адреса электронной почты."""
        if not re.match(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Некорректный формат email")
        self._email = value

    def validate(self):
        """Проверяет правильность заполнения полей (почта и телефон)."""
        errors = []
        if not re.match(r"[^\s@]+@[^\s@]+\.[^\s@]+", self.email):
            errors.append(f"Некорректный формат email: {self.email}")
        if not re.match(r"^\+?\d+$", self.phone):
            errors.append(f"Некорректный формат телефона: {self.phone}")
        if errors:
            raise ValueError("\n".join(errors))
        return True

class Product(BaseModel):
    def __init__(self, name, price, id=None):
        self.id = id
        self.name = name
        self.price = price


class Order(BaseModel):
    def __init__(self, id, client_id, products, order_date, _total_cost=None, client_name="", items=""):
        self.id = id
        self.client_id = client_id
        self.products = products
        self.order_date = order_date
        self._total_cost = _total_cost  # Скрытое поле для итоговой стоимости
        self.client_name = client_name  # Имя клиента
        self.items = items              # Форматированный список товаров

    @property
    def total_cost(self):
        return self._total_cost
