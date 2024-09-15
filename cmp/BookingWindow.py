from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QPushButton,
    QMessageBox,
)
import requests


class AddBookingWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.houses = []  # Список домов
        self.init_ui()
        self.load_houses()

    def init_ui(self):
        layout = QVBoxLayout()

        self.customer_name_label = QLabel("Имя клиента:")
        self.customer_name_input = QLineEdit()

        self.house_label = QLabel("Выберите дом:")
        self.house_combo = QComboBox()
        self.house_combo.currentIndexChanged.connect(self.update_rooms)

        self.room_label = QLabel("Выберите комнату:")
        self.room_combo = QComboBox()

        self.check_in_label = QLabel("Дата заезда:")
        self.check_in_input = QDateEdit()
        self.check_in_input.setCalendarPopup(
            True
        )  # Включаем всплывающее окно календаря

        self.check_out_label = QLabel("Дата выезда:")
        self.check_out_input = QDateEdit()
        self.check_out_input.setCalendarPopup(
            True
        )  # Включаем всплывающее окно календаря

        self.add_booking_button = QPushButton("Добавить бронь")
        self.add_booking_button.clicked.connect(self.add_booking)

        layout.addWidget(self.customer_name_label)
        layout.addWidget(self.customer_name_input)
        layout.addWidget(self.house_label)
        layout.addWidget(self.house_combo)
        layout.addWidget(self.room_label)
        layout.addWidget(self.room_combo)
        layout.addWidget(self.check_in_label)
        layout.addWidget(self.check_in_input)
        layout.addWidget(self.check_out_label)
        layout.addWidget(self.check_out_input)
        layout.addWidget(self.add_booking_button)

        self.setLayout(layout)

    def load_houses(self):
        # Запрос списка домов из CouchDB
        response = requests.get(
            f"{self.main_window.COUCHDB_URL}/{self.main_window.NAME}/_all_docs?include_docs=true"
        )
        if response.status_code == 200:
            houses_data = response.json()
            for row in houses_data["rows"]:
                if row["doc"]["type"] == "house":
                    self.houses.append(row["doc"])
                    self.house_combo.addItem(
                        row["doc"]["name"], row["doc"]["_id"]
                    )  # Добавляем имя дома и его ID в combo box

    def update_rooms(self):
        # Обновление списка комнат на основе выбранного дома
        self.room_combo.clear()  # Очистка предыдущих значений
        selected_house_id = (
            self.house_combo.currentData()
        )  # Получаем ID выбранного дома

        # Ищем выбранный дом в списке домов
        selected_house = next(
            (house for house in self.houses if house["_id"] == selected_house_id), None
        )
        if selected_house:
            number_of_rooms = selected_house["rooms"]
            # Добавляем комнаты в выпадающее меню
            for room_number in range(1, number_of_rooms + 1):
                self.room_combo.addItem(f"Комната {room_number}", room_number)

    def add_booking(self):
        customer_name = self.customer_name_input.text()
        selected_house_id = self.house_combo.currentData()
        selected_room = self.room_combo.currentData()
        check_in_date = self.check_in_input.date().toString(
            "yyyy-MM-dd"
        )  # Получаем дату заезда в нужном формате
        check_out_date = self.check_out_input.date().toString(
            "yyyy-MM-dd"
        )  # Получаем дату выезда в нужном формате

        if not customer_name or not selected_house_id or selected_room is None:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните все поля.")
            return

        # Логика добавления бронирования
        booking_data = {
            "house_id": selected_house_id,
            "customer_name": customer_name,
            "room_number": selected_room,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
        }

        # Здесь вы можете добавить код для сохранения бронирования в CouchDB
        # Например, отправка запроса на добавление бронирования

        QMessageBox.information(self, "Успех", "Бронь успешно добавлена!")
        self.close()  # Закрываем окно добавления брони
