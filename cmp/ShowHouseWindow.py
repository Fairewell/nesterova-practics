from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGridLayout,
    QFrame,
    QScrollArea,
    QSizePolicy,
    QTableWidgetItem,
    QTableWidget
)
from PyQt5.QtGui import QFont
import requests
from datetime import datetime

class HouseWidget(QWidget):
    def __init__(self, name, bookings_count, price, bookings):
        super().__init__()
        self.name = name
        self.bookings_count = bookings_count
        self.price = price
        self.bookings = bookings  # Список броней для этого дома
        self.init_ui()

    def init_ui(self):
        # Создаем фрейм как контейнер для виджетов
        frame = QFrame(self)
        frame.setStyleSheet(
            """
            QFrame {
                padding: 10px;
                margin: 10px;
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            """
        )
        layout = QVBoxLayout(frame)
        # Название дома
        name_label = QLabel(self.name)
        name_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(name_label)
        # Количество броней
        bookings_label = QLabel(f"Открыто броней: {self.bookings_count}")
        bookings_label.setFont(QFont("Arial", 10))
        layout.addWidget(bookings_label)
        # Цена
        price_label = QLabel(f"Цена за ночь: {self.price} руб.")
        price_label.setFont(QFont("Arial", 10))
        layout.addWidget(price_label)
        # Заголовок для списка броней
        bookings_header = QLabel("Брони:")
        bookings_header.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(bookings_header)
        # Таблица для бронирований
        bookings_table = QTableWidget()
        bookings_table.setColumnCount(4)
        bookings_table.setHorizontalHeaderLabels(
            ["ФИО клиента", "Дата заезда", "Дней", "Цена"]
        )
        bookings_table.setRowCount(len(self.bookings))
        bookings_table.setEditTriggers(QTableWidget.NoEditTriggers)
        bookings_table.setSelectionBehavior(QTableWidget.SelectRows)
        bookings_table.setSelectionMode(QTableWidget.SingleSelection)
        bookings_table.verticalHeader().setVisible(False)
        bookings_table.setStyleSheet(
            """
            QTableWidget {
                background-color: #ffffff;
                border: none;
                font-size: 10pt;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #ddd;
            }
            """
        )
        for row, booking in enumerate(self.bookings):
            bookings_table.setItem(
                row, 0, QTableWidgetItem(booking["customer_name"])
            )
            bookings_table.setItem(
                row, 1, QTableWidgetItem(booking["check_in_date"])
            )
            bookings_table.setItem(row, 2, QTableWidgetItem(str(booking["duration_days"])))
            bookings_table.setItem(row, 3, QTableWidgetItem(str(booking["total_price"])))
        bookings_table.resizeColumnsToContents()
        bookings_table.setAlternatingRowColors(True)
        bookings_table.setStyleSheet("alternate-background-color: #f2f2f2;")
        layout.addWidget(bookings_table)

        # Устанавливаем макет для основного виджета
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(frame)

        # Устанавливаем ширину виджета
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(200)  # Минимальная ширина
        self.setMaximumWidth(400)  # Максимальная ширина (можно настроить в зависимости от ваших нужд)

    def resizeEvent(self, event):
        # Устанавливаем ширину карточки в 20% от ширины родительского виджета
        parent_width = self.parent().width()
        new_width = int(parent_width * 0.35)  # 20% от ширины родителя
        self.setFixedWidth(new_width)
        super().resizeEvent(event)


class HousesDisplay(QWidget):
    def __init__(self, main_window):
        super().__init__()  # Исправлено на __init__
        self.main_window = main_window
        self.init_ui()
        self.load_houses()

    def go_back(self):
        self.main_window.show_main_screen()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        # Добавляем Scroll Area для прокрутки списка домов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.grid_layout = QGridLayout(scroll_content)
        scroll.setWidget(scroll_content)
        self.layout.addWidget(scroll)

    def load_houses(self):
        # Запрос списка домов из CouchDB
        houses_response = requests.get(
            f"{self.main_window.COUCHDB_URL}/{self.main_window.NAME}/_all_docs?include_docs=true"
        )
        bookings_response = requests.get(
            f"{self.main_window.COUCHDB_URL}/{self.main_window.NAME}/_all_docs?include_docs=true"
        )
        print(f"{self.main_window.COUCHDB_URL}/{self.main_window.NAME}/_all_docs?include_docs=true")
        if houses_response.status_code == 200 and bookings_response.status_code == 200:
            houses_data = houses_response.json()
            bookings_data = bookings_response.json()
            # Сбор всех броней
            all_bookings = []
            for row in bookings_data["rows"]:
                if (
                    "doc" in row
                    and "type" in row["doc"]
                    and row["doc"]["type"] == "booking"
                ):
                    booking = row["doc"]
                    # Добавляем поле для продолжительности (если его нет, можно добавить расчет)
                    if "check_in_date" in booking and "check_out_date" in booking:
                        check_in = datetime.strptime(booking["check_in_date"], "%Y-%m-%d")
                        check_out = datetime.strptime(booking["check_out_date"], "%Y-%m-%d")
                        duration = (check_out - check_in).days
                        booking["duration_days"] = duration
                    all_bookings.append(booking)
            row_idx = 0
            col_idx = 0
            columns = 3  # Количество колонок
            for house_row in houses_data["rows"]:
                if house_row["doc"].get("type") == "house":
                    house = house_row["doc"]
                    house_id = house["_id"]
                    house_name = house.get("name", "Без названия")
                    price = house.get("price_per_night", "N/A")
                    # Фильтрация броней для текущего дома
                    house_bookings = [
                        b for b in all_bookings if b.get("house_id") == house_id
                    ]
                    # Сортировка броней по дате заезда
                    house_bookings.sort(
                        key=lambda x: datetime.strptime(x["check_in_date"], "%Y-%m-%d")
                    )
                    bookings_count = len(house_bookings)
                    # Создание HouseWidget с переданными бронями
                    house_widget = HouseWidget(
                        name=house_name,
                        bookings_count=bookings_count,
                        price=price,
                        bookings=house_bookings,
                    )
                    self.grid_layout.addWidget(house_widget, row_idx, col_idx)
                    col_idx += 1
                    if col_idx >= columns:
                        col_idx = 0
                        row_idx += 1
        else:
            # Обработка ошибок
            error_message = "Не удалось загрузить данные."
            if houses_response.status_code != 200:
                error_message += " Ошибка загрузки домов."
            if bookings_response.status_code != 200:
                print(f'WARN: \n{bookings_response}')
                error_message += " Ошибка загрузки броней."
            label = QLabel(error_message)
            label.setStyleSheet("color: red;")
            self.layout.addWidget(label)