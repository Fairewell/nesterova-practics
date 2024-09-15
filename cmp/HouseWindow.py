from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
import requests


class AddHouseWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.name_label = QLabel("Введите название дома:")
        self.name_input = QLineEdit()
        self.rooms_label = QLabel("Количество комнат:")
        self.rooms_input = QLineEdit()
        self.price_label = QLabel("Цена за ночь:")
        self.price_input = QLineEdit()
        self.add_house_button = QPushButton("Добавить дом в систему")
        self.add_house_button.clicked.connect(self.add_house)

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.rooms_label)
        layout.addWidget(self.rooms_input)
        layout.addWidget(self.price_label)
        layout.addWidget(self.price_input)
        layout.addWidget(self.add_house_button)

        self.setLayout(layout)

    def add_house(self):
        name = self.name_input.text()
        rooms = self.rooms_input.text()
        price_per_night = self.price_input.text()
        if not name or not rooms.isdigit() or not price_per_night.isdigit():
            QMessageBox.warning(
                self, "Ошибка ввода", "Пожалуйста, введите корректные данные."
            )
            return

        house_id = f'house:{name.replace(" ", "_")}'
        house_data = {
            "_id": house_id,
            "type": "house",
            "name": name,
            "rooms": int(rooms),
            "price_per_night": int(price_per_night),
            "bookings": [],
        }

        add_URL = f"{self.main_window.COUCHDB_URL}/{self.main_window.NAME}/{house_id}"
        response = requests.put(add_URL, json=house_data)
        if response.status_code in (201, 202, 200):
            QMessageBox.information(
                self, "Операция успешна", f"Дом успешно добавлен с ID: {house_id}"
            )
            self.main_window.central_widget.setCurrentWidget(
                self.main_window.main_screen
            )  # Вернуться на главный экран
        else:
            QMessageBox.warning(
                self, "Ошибка", "Не удалось добавить дом в базу данных."
            )
