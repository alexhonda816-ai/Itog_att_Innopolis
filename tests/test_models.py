import unittest
from models import Product, Client, Order

class TestModels(unittest.TestCase):
    def test_client_creation(self):
        """Тестируем создание клиента и проверку валидности данных."""
        client = Client(name="Иван Иванов", email="ivan@example.com", phone="+79123456789", address="Омск")
        self.assertEqual(client.name, "Иван Иванов")
        self.assertTrue(client.validate())

    def test_client_invalid_email(self):
        """Проверяем реакцию на неправильный email."""
        with self.assertRaises(ValueError):
            invalid_client = Client(name="Петр Петров", email="invalid_email", phone="+79011234567", address="Москва")
            invalid_client.validate()

    def test_client_invalid_phone(self):
        """Проверяем реакцию на неправильный телефон."""
        with self.assertRaises(ValueError):
            invalid_client = Client(name="Анна Иванова", email="anna@example.ru", phone="abc", address="Санкт-Петербург")
            invalid_client.validate()

    def test_product_creation(self):
        """Проверяем создание продукта."""
        product = Product(name="Ноутбук", price=9999.99)
        self.assertEqual(product.name, "Ноутбук")
        self.assertEqual(product.price, 9999.99)

    # Не проходит тест- по стоимости
    def test_order_total_cost(self):
        """Проверяем расчет итоговой суммы заказа."""
        p1 = Product(name="Мышь", price=1500)
        p2 = Product(name="Клавиатура", price=4500)
        order = Order(id=1,client_id=1, products=[p1, p2], order_date="2020-01-01")
        self.assertEqual(order.total_cost, 6000)

if __name__ == '__main__':
    unittest.main()