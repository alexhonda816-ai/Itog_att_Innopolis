import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import db


def get_orders_df():
    """Загружает заказы из базы данных в DataFrame."""
    orders_data = db.get_all_orders()
    if not orders_data:
        return pd.DataFrame()

    # Собираем данные из объектов Order
    data = [{
        'id': order.id,
        'client_name': order.client_name,
        'order_date': order.order_date,
        'total_cost': order.total_cost
    } for order in orders_data]

    df = pd.DataFrame(data)
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

def get_top_clients(n=5):
    """Возвращает топ-N клиентов по общему объему покупок."""
    df = get_orders_df()
    if df.empty:
        return pd.Series(dtype=str)

    # grouped = df.groupby('client_name').sum()['total_cost']
    grouped = df.groupby('client_name')['total_cost'].sum()
    return grouped.nlargest(n)


def plot_order_dynamics():

    """Строит график динамики заказов по месяцам."""
    df = get_orders_df()
    if df.empty:
        return None

    # Преобразуем столбец с датами в формат datetime
    df['order_date'] = pd.to_datetime(df['order_date'])
    daily_rev = df.groupby(df['order_date'].dt.date)['total_cost'].sum().reset_index()

    # Настраиваем внешний вид графика
    sns.set(style="whitegrid")
    plt.figure(figsize=(10, 6))

    # Строим динамику продаж
    sns.barplot(x='order_date', y='total_cost', data=daily_rev, palette='viridis')

    # Оформляем график
    plt.title('Динамика продаж по дням')
    plt.xlabel('Дата')
    plt.ylabel('Суммарная выручка (Руб)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    # 250827

    return plt.gcf()

def plot_client_geography_graph():
    """Визуализирует сеть городов, где живут ваши клиенты."""
    clients = db.get_all_clients()
    if len(clients) < 2:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Недостаточно клиентов для построения графа.", ha='center')
        return fig

    G = nx.Graph()
    cities = {}
    for client in clients:
        city = extract_city(client.address)
        if city not in cities:
            cities[city] = []
        cities[city].append(client.name)

    # Построение графа
    for city, names in cities.items():
        G.add_node(city)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                G.add_edge(names[i], names[j], weight=1)

    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_color="skyblue", alpha=0.8)
    nx.draw_networkx_edges(G, pos, edge_color="gray", alpha=0.5)
    nx.draw_networkx_labels(G, pos, font_size=10, font_family="sans-serif")
    plt.axis("off")
    return plt.gcf()

def extract_city(address, depth=0, max_depth=3):
    """Извлекает город из адреса."""
    if not address or depth >= max_depth:
        return "Неизвестно"
    parts = address.strip().split(',')
    first_part = parts[0].strip()

    # Сначала проверяем стандартную схему, когда "г." или "город" стоят ДО названия города
    if "г." in first_part or "город" in first_part.lower() or "гор." in first_part.lower():
        # Проверяем, не является ли "г." или "город" частью первого элемента
        sub_parts = first_part.split()
        if len(sub_parts) > 1 and sub_parts[-1].lower() in ["г.", "город", "гор."]:
            return sub_parts[:-1][-1]  # Возвращаем предпоследнюю часть (название города)
        else:
            return "Неизвестно"
    elif first_part.isalpha():  # Если городской блок указан явно
        return first_part
    elif depth < max_depth:
        return extract_city(','.join(parts[1:]), depth + 1)
    else:
        return "Неизвестно"

def sort_orders(orders, by='total_cost', reverse=True):
    """Сортирует заказы по указанному полю."""
    if not orders:
        return []
    sorted_orders = sorted(orders, key=lambda x: getattr(x, by), reverse=reverse)
    return sorted_orders

