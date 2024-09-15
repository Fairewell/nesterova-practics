from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGridLayout,
    QFrame,
    QPushButton,
)
from PyQt5.QtGui import QPixmap
import requests


class HouseWidget(QWidget):
    def __init__(self, name, bookings_count, price):
        super().__init__()
        self.init_ui(name, bookings_count, price)

    def init_ui(self, name, bookings_count, price):
        # Создаем фрейм как контейнер для виджетов
        frame = QFrame(self)
        frame.setStyleSheet(
            """
            QFrame {
                padding: 4px;
                margin: 4px;
                background-color: #f0f0f0;
                border-radius: 8px;
            }
            """
        )

        layout = QVBoxLayout(frame)

        # Название дома
        self.name_label = QLabel(name)

        # Количество броней
        self.bookings_label = QLabel(f"Открытых броней: {bookings_count}")

        # Цена
        self.price_label = QLabel(f"Цена за ночь: {price} руб.")

        # Добавление элементов в макет
        layout.addWidget(self.name_label)
        layout.addWidget(self.bookings_label)
        layout.addWidget(self.price_label)

        # Устанавливаем макет для основного виджета
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(frame)


class HousesDisplay(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        self.load_houses()

    def go_back(self):
        self.main_window.show_main_screen()

    def init_ui(self):
        layout = QGridLayout()
        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)
        self.setLayout(layout)

    def load_houses(self):
        # Запрос списка домов из CouchDB
        response = requests.get(
            f"{self.main_window.COUCHDB_URL}/{self.main_window.NAME}/_all_docs?include_docs=true"
        )
        if response.status_code == 200:
            houses_data = response.json()
            row = 0
            col = 0
            for row_data in houses_data["rows"]:
                if row_data["doc"]["type"] == "house":
                    name = row_data["doc"]["name"]
                    bookings_count = len(row_data["doc"]["bookings"])
                    price = row_data["doc"]["price_per_night"]
                    icon_path = (
                        "path/to/your/icon.png"  # Замените на путь к вашей иконке
                    )

                    house_widget = HouseWidget(name, bookings_count, price)
                    self.layout.addWidget(house_widget, row, col)

                    col += 1
                    if col >= 3:  # Переход на следующую строку после 3 домов
                        col = 0
                        row += 1
