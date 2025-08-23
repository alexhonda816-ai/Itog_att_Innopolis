import tkinter as tk
from itertools import count
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from tkinter.ttk import Button
import operator

# Импортирование библиотек для визуализации
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import analysis
import db
from models import Client, Product, Order
import csv


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система учета заказов")
        self.geometry("1000x700")  # Размеры окна

        # Основной контейнер вкладок
        notebook = ttk.Notebook(self)
        notebook.pack(padx=10, pady=10, fill="both", expand=True)

        # Добавляем вкладки
        self.create_clients_tab(notebook)
        self.create_products_tab(notebook)
        self.create_orders_tab(notebook)
        self.create_analysis_tab(notebook)
        self.create_admin_tab(notebook)

    def create_clients_tab(self, notebook):
        """Вкладка 'Клиенты'"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Клиенты")

        # Форма добавления клиента
        form_frame = ttk.Labelframe(frame, text="Добавить/Изменить клиента")
        form_frame.pack(fill="x", padx=10, pady=10)

        # Поля формы
        tk.Label(form_frame, text="Имя:").grid(row=0, column=0, padx=5, pady=5)
        self.client_name = tk.Entry(form_frame, width=40)
        self.client_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        self.client_email = tk.Entry(form_frame, width=40)
        self.client_email.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Телефон:").grid(row=2, column=0, padx=5, pady=5)
        self.client_phone = tk.Entry(form_frame, width=40)
        self.client_phone.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Адрес:").grid(row=3, column=0, padx=5, pady=5)
        self.client_address = tk.Entry(form_frame, width=40)
        self.client_address.grid(row=3, column=1, padx=5, pady=5)

        # Кнопка сохранения клиента
        ttk.Button(form_frame, text="Сохранить", command=self.save_client).grid(row=4, columnspan=2, pady=10)

        # Таблица клиентов
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.client_tree = ttk.Treeview(tree_frame, columns=("id", "name", "email", "phone", "address"),
                                        show="headings")

        # Заголовки таблиц
        self.client_tree.heading("id", text="ID", command=lambda c="id": self.sort_by_column(c))
        self.client_tree.heading("name", text="Имя", command=lambda c="name": self.sort_by_column(c))
        self.client_tree.heading("email", text="Email", command=lambda c="email": self.sort_by_column(c))
        self.client_tree.heading("phone", text="Телефон", command=lambda c="phone": self.sort_by_column(c))
        self.client_tree.heading("address", text="Адрес", command=lambda c="address": self.sort_by_column(c))

        # Колонки таблицы
        self.client_tree.column("id", anchor='center', width=50)
        self.client_tree.column("name", anchor='w')
        self.client_tree.column("email", anchor='w')
        self.client_tree.column("phone", anchor='w')
        self.client_tree.column("address", anchor='w')

        self.client_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.client_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.client_tree.configure(yscrollcommand=scrollbar.set)

        # Обновляем таблицу
        self.refresh_clients_list()

    # Метод сортировки по выбранному столбцу
    def sort_by_column(self, col):
        items = [(self.client_tree.set(child, col), child) for child in self.client_tree.get_children()]
        sorted_items = sorted(items, key=operator.itemgetter(0))

        # Переставляем порядок элементов
        for index, (_, item_id) in enumerate(sorted_items):
            self.client_tree.move(item_id, '', index)

        # Инвертируем направление сортировки
        self.client_tree.heading(col, command=lambda _col=col: self.reverse_sort(_col))

    # Метод обратного порядка сортировки
    def reverse_sort(self, col):
        items = [(self.client_tree.set(child, col), child) for child in self.client_tree.get_children()]
        sorted_items = sorted(items, key=operator.itemgetter(0), reverse=True)

        # Переставляем порядок элементов обратно
        for index, (_, item_id) in enumerate(sorted_items):
            self.client_tree.move(item_id, '', index)

        # Возвращаем обычный порядок сортировки
        self.client_tree.heading(col, command=lambda _col=col: self.sort_by_column(_col))

    def save_client(self):
        """Сохраняет данные клиента"""
        try:
            client = Client(
                name=self.client_name.get(),
                email=self.client_email.get(),
                phone=self.client_phone.get(),
                address=self.client_address.get()
            )

            # Проверяем валидность введенных данных
            client.validate()

            # Сохраняем нового клиента в базу данных
            db.add_client(client)

            # Сообщаем пользователю о успешном сохранении
            messagebox.showinfo("Успех", "Клиент успешно добавлен.")

            # Обновляем список клиентов в таблице
            self.refresh_clients_list()
            self.populate_order_comboboxes()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh_clients_list(self):
        """Обновляет список клиентов в таблице"""
        # Очищаем дерево перед обновлением
        for i in self.client_tree.get_children():
            self.client_tree.delete(i)

        # Получаем всех клиентов из базы данных
        clients = db.get_all_clients()

        # Заполняем таблицу новыми клиентами
        for client in clients:
            self.client_tree.insert("", "end",
                                    values=(client.id, client.name, client.email, client.phone, client.address))

    def create_products_tab(self, notebook):
        """Вкладка 'Товары'"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Товары")

        # Форма добавления товара
        form_frame = ttk.Labelframe(frame, text="Добавить товар")
        form_frame.pack(fill="x", padx=10, pady=10)

        # Поля формы
        tk.Label(form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5)
        self.product_name = tk.Entry(form_frame, width=40)
        self.product_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Цена:").grid(row=1, column=0, padx=5, pady=5)
        self.product_price = tk.Entry(form_frame, width=40)
        self.product_price.grid(row=1, column=1, padx=5, pady=5)

        # Кнопка сохранения продукта
        ttk.Button(form_frame, text="Сохранить", command=self.save_product).grid(row=2, columnspan=2, pady=10)

        # Таблица продуктов
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.product_tree = ttk.Treeview(tree_frame, columns=("id", "name", "price"), show="headings")

        # Заголовки таблиц
        self.product_tree.heading("id", text="ID", command=lambda c="id": self.sort_products_by_column(c))
        self.product_tree.heading("name", text="Название", command=lambda c="name": self.sort_products_by_column(c))
        self.product_tree.heading("price", text="Цена", command=lambda c="price": self.sort_products_by_column(c))

        # Колонки таблицы
        self.product_tree.column("id", anchor='center', width=50)
        self.product_tree.column("name", anchor='w')
        self.product_tree.column("price", anchor='w')

        self.product_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.product_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.product_tree.configure(yscrollcommand=scrollbar.set)

        # Обновляем таблицу
        self.refresh_products_list()

    def sort_products_by_column(self, col):
        items = [(self.product_tree.set(child, col), child) for child in self.product_tree.get_children()]
        sorted_items = sorted(items, key=operator.itemgetter(0))

        # Перемещение элементов
        for index, (_, item_id) in enumerate(sorted_items):
            self.product_tree.move(item_id, '', index)

        # Изменение направления сортировки
        self.product_tree.heading(col, command=lambda _col=col: self.reverse_sort_products(_col))

    def reverse_sort_products(self, col):
        items = [(self.product_tree.set(child, col), child) for child in self.product_tree.get_children()]
        sorted_items = sorted(items, key=operator.itemgetter(0), reverse=True)

        # Перемещение элементов
        for index, (_, item_id) in enumerate(sorted_items):
            self.product_tree.move(item_id, '', index)

        # Возвращение обычного порядка сортировки
        self.product_tree.heading(col, command=lambda _col=col: self.sort_products_by_column(_col))

    def save_product(self):
        """Сохраняет новый продукт"""
        try:
            price = float(self.product_price.get())  # Преобразуем цену в число
            product = Product(name=self.product_name.get(), price=price)

            # Сохраняем новый продукт в базу данных
            db.add_product(product)

            # Сообщаем пользователю о успехе
            messagebox.showinfo("Успех", "Товар успешно добавлен.")

            # Обновляем таблицу продуктов
            self.refresh_products_list()

            #2 Обновляем список товаров после добавления
            self.update_products_list()
            self.populate_order_comboboxes()
        except ValueError:
            messagebox.showerror("Ошибка", "Цена должна быть числом.")

    def update_products_list(self): #2
        # Получить свежий список товаров из базы данных
        self.products_data = db.get_all_products()

        # Перегрузить значения в Combobox
        self.order_product['values'] = [f"{p.id}: {p.name}, Цена: {p.price:.2f} руб." for p in self.products_data]



    def refresh_products_list(self):
        """Обновляет список товаров в таблице"""
        # Очищаем дерево перед обновлением
        for i in self.product_tree.get_children():
            self.product_tree.delete(i)

        # Получаем все товары из базы данных
        products = db.get_all_products()

        # Заполняем таблицу товарами
        for product in products:
            self.product_tree.insert("", "end", values=(product.id, product.name, f'{product.price:.2f}'))


    def create_orders_tab(self, notebook):
        """Вкладка 'Заказы'"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Заказы")

        # Форма создания заказа
        form_frame = ttk.Labelframe(frame, text="Создать заказ")
        form_frame.pack(fill="x", padx=10, pady=10)

        # Выбор клиента
        tk.Label(form_frame, text="Клиент:").grid(row=0, column=0, padx=5, pady=5)
        self.order_client = ttk.Combobox(form_frame, state="readonly", width=37)
        self.order_client.grid(row=0, column=1, padx=5, pady=5)

        # Выбор товара
        tk.Label(form_frame, text="Товар:").grid(row=1, column=0, padx=5, pady=5)
        self.order_product = ttk.Combobox(form_frame, state="readonly", width=37)
        self.order_product.grid(row=1, column=1, padx=5, pady=5)

        # Кнопка добавления товара в заказ
        ttk.Button(form_frame, text="Добавить в заказ", command=self.add_product_to_order).grid(row=1, column=2, padx=5)

        # Список товаров в заказе
        self.order_products_list = tk.Listbox(frame, height=8, selectmode=tk.EXTENDED)
        self.order_products_list.pack(fill="x", padx=10, pady=10)

        # Кнопка оформления заказа
        ttk.Button(frame, text="Оформить заказ", command=self.save_order).pack(pady=10)

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.order_tree = ttk.Treeview(tree_frame, columns=("id", "client", "date", "cost", "items"), show="headings")

        # Названия столбцов с обработчиками сортировки
        self.order_tree.heading("id", text="ID", command=lambda c="id": self.sort_orders_by_column(c))
        self.order_tree.heading("client", text="Клиент", command=lambda c="client": self.sort_orders_by_column(c))
        self.order_tree.heading("date", text="Дата", command=lambda c="date": self.sort_orders_by_column(c))
        self.order_tree.heading("cost", text="Стоимость", command=lambda c="cost": self.sort_orders_by_column(c))
        # self.order_tree.heading("items", text="Количество товаров")  # Строка закомментирована ранее

        self.order_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.order_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.order_tree.configure(yscrollcommand=scrollbar.set)

        # Обновляем таблицу заказов
        self.refresh_orders_list()
        self.populate_order_comboboxes()

    def sort_orders_by_column(self, col):
        items = [(self.order_tree.set(child, col), child) for child in self.order_tree.get_children()]
        sorted_items = sorted(items, key=operator.itemgetter(0))

        # Перемещение элементов
        for index, (_, item_id) in enumerate(sorted_items):
            self.order_tree.move(item_id, '', index)

        # Обратная сортировка
        self.order_tree.heading(col, command=lambda _col=col: self.reverse_sort_orders(_col))

    def reverse_sort_orders(self, col):
        items = [(self.order_tree.set(child, col), child) for child in self.order_tree.get_children()]
        sorted_items = sorted(items, key=operator.itemgetter(0), reverse=True)

        # Перемещение элементов
        for index, (_, item_id) in enumerate(sorted_items):
            self.order_tree.move(item_id, '', index)

        # Обычная сортировка
        self.order_tree.heading(col, command=lambda _col=col: self.sort_orders_by_column(_col))

    def populate_order_comboboxes(self):
        """Заполняет выпадающие списки клиентов и товаров"""
        self.clients_data = db.get_all_clients()
        self.products_data = db.get_all_products()

        # Устанавливаем значения в выпадающих списках
        self.order_client["values"] = [f"{c.id}: {c.name}" for c in self.clients_data]
        self.order_product["values"] = [f"{p.id}: {p.name}, цена: {p.price:.2f} руб." for p in self.products_data]

    def add_product_to_order(self):
        """Добавляет выбранный товар в список текущего заказа"""
        selected_product = self.order_product.get()
        if selected_product:
            self.order_products_list.insert(tk.END, selected_product)

    def save_order(self):
        """Сохраняет созданный заказ"""
        try:
            client_str = self.order_client.get()
            if not client_str:
                raise ValueError("Выберите клиента.")

            client_id = int(client_str.split(":")[0])  # Извлекаем ID клиента

            # Выбираем товары из выбранного списка
            product_ids = []
            for idx in range(len(self.order_products_list.get(0, tk.END))):
                product_item = self.order_products_list.get(idx)
                product_id = int(product_item.split(":")[0])
                product_ids.append(product_id)

            # Если ни одного товара не выбрано
            if len(product_ids) == 0:
                raise ValueError("Нет товаров в заказе.")

            # Формируем объекты товаров
            products_in_order = [p for p in self.products_data if p.id in product_ids]

            order = Order(
                id=None,  # Тут устанавливаем None, так как id будет назначен автоматически
                client_id=client_id,
                products=products_in_order,
                order_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                _total_cost=sum([p.price for p in products_in_order])
            )
            # Сохраняем заказ в базу данных
            db.add_order(order)

            # Уведомляем пользователя
            messagebox.showinfo("Успех", "Заказ успешно сохранён.")

            # Обновляем список заказов
            self.refresh_orders_list()

            # Очищаем список товаров
            self.order_products_list.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

    def refresh_orders_list(self):
        """Обновляет список заказов в таблице"""
        # Очищаем дерево перед обновлением
        for i in self.order_tree.get_children():
            self.order_tree.delete(i)

        orders = db.get_all_orders()

        # Заполняем таблицу новыми заказами
        for order in orders:
            self.order_tree.insert("", "end",
                                   values=(order.id, order.client_name, order.order_date, f"{order.total_cost:.2f}"))

    def create_analysis_tab(self, notebook):
        """Вкладка анализа и визуализации"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Анализ и Визуализация")

        # Панель кнопок
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side="top", fill="x", padx=10, pady=10)

        # Кнопки для анализа
        ttk.Button(btn_frame, text="Топ-5 клиентов", command=self.show_top_clients).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Динамика заказов", command=self.show_order_dynamics).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="География клиентов", command=self.show_client_geography).pack(side="left", padx=5)

        # Контейнер для графика
        self.plot_canvas_frame = ttk.Frame(frame)
        self.plot_canvas_frame.pack(side="bottom", fill="both", expand=True)

    def show_top_clients(self):
        top_clients = analysis.get_top_clients()
        # Подготавливаем список строк для отображения
        formatted_clients = [f"{index}: {value:.2f}" for index, value in top_clients.items()]
        # Объединяем строки для вывода
        messagebox.showinfo("Топ клиенты", "\n".join(formatted_clients))

    def show_order_dynamics(self):

        """Показывает динамику изменения количества заказов по месяцам"""
        fig = analysis.plot_order_dynamics()
        canvas = FigureCanvasTkAgg(fig, master=self.plot_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    def show_client_geography(self):

        """Отображает географию распределения клиентов"""
        fig = analysis.plot_client_geography_graph()
        canvas = FigureCanvasTkAgg(fig, master=self.plot_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    def create_admin_tab(self, notebook):
        """Создает вкладку администрирования."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text='Администрирование')

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(padx=20, pady=20)

        # Кнопка для импорта данных из CSV
        ttk.Button(btn_frame, text="Импорт клиентов из CSV", command=self.import_from_csv).pack(pady=10)

        # Кнопка для экспорта данных в JSON
        ttk.Button(btn_frame, text="Экспорт всех данных в JSON", command=self.export_to_json).pack(pady=10)

    def import_from_csv(self):
        """Импортирует данные из CSV-файла."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                db.import_data_from_csv(file_path)
                messagebox.showinfo("Успех", "Данные успешно импортированы")
                self.refresh_clients_list()
            except Exception as e:
                messagebox.showerror("Ошибка импорта", str(e))

    def export_to_json(self):
        """Экспортирует данные в JSON-файл."""
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                db.export_data_to_json(file_path)
                messagebox.showinfo("Успех", "Данные успешно экспортированы")
            except Exception as e:
                messagebox.showerror("Ошибка экспорта", str(e))


if __name__ == "__main__":
    app = App()
    app.mainloop()

# for git
