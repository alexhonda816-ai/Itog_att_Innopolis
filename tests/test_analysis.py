import unittest
from analysis import extract_city
from analysis import sort_orders

class TestExtractCity(unittest.TestCase):
    def test_extract_city_valid_addresses(self):
        cases = {
            "Москва, ул. Ленина, д. 1": "Москва",
            "Санкт-Петербург г., Невский проспект, дом 12": "Санкт-Петербург",
            "Краснодар г., ул. Пушкина, 12": "Краснодар",
            "Екатеринбург, Свердловская область, улица Карла Маркса, 10": "Екатеринбург",
            "Новосибирск, Красный проспект, 12": "Новосибирск",
            "Владивосток, Приморский край, Светланская улица, 15": "Владивосток",
        }
        for addr, expected_city in cases.items():
            result = extract_city(addr)
            self.assertEqual(result, expected_city)

    def test_extract_city_invalid_addresses(self):
        invalid_cases = [
            "",
            "ул. Ленина, д. 1",
            "Ленинградская обл.",
            "г."
        ]
        for case in invalid_cases:
            result = extract_city(case)
            self.assertEqual(result, "Неизвестно")


class MockOrder:
    def __init__(self, id, client_name, order_date, total_cost):
        self.id = id
        self.client_name = client_name
        self.order_date = order_date
        self.total_cost = total_cost

orders = [
    MockOrder(1, "Иван Иванов", "2023-01-01", 100),
    MockOrder(2, "Сергей Петров", "2023-02-01", 150),
    MockOrder(3, "Анна Смирнова", "2023-03-01", 200),
    MockOrder(4, "Михаил Кузнецов", "2023-04-01", 50),
]

class TestSortOrders(unittest.TestCase):
    def test_sort_orders_total_cost_descending(self):
        mock_orders = [
            MockOrder(1, "Иван Иванов", "2023-01-01", 100),
            MockOrder(2, "Сергей Петров", "2023-02-01", 150),
            MockOrder(3, "Анна Смирнова", "2023-03-01", 200),
            MockOrder(4, "Михаил Кузнецов", "2023-04-01", 50),
        ]
        sorted_orders = sort_orders(mock_orders, by='total_cost', reverse=True)
        expected_ids = [3, 2, 1, 4]
        actual_ids = [order.id for order in sorted_orders]
        self.assertListEqual(expected_ids, actual_ids)

    def test_sort_orders_total_cost_ascending(self):
        mock_orders = [
            MockOrder(1, "Иван Иванов", "2023-01-01", 100),
            MockOrder(2, "Сергей Петров", "2023-02-01", 150),
            MockOrder(3, "Анна Смирнова", "2023-03-01", 200),
            MockOrder(4, "Михаил Кузнецов", "2023-04-01", 50),
        ]
        sorted_orders = sort_orders(mock_orders, by='total_cost', reverse=False)
        expected_ids = [4, 1, 2, 3]
        actual_ids = [order.id for order in sorted_orders]
        self.assertListEqual(expected_ids, actual_ids)



if __name__ == '__main__':
    unittest.main()