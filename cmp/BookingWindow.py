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
from PyQt5.QtCore import QDate  # Импортируем QDate для работы с датами

CALENDAR_STYLE_SHEET = """
            QDateEdit {
                font-size: 14px;  /* Увеличиваем размер шрифта */
                border: 1px solid #ccc;  /* Устанавливаем рамку */
                border-radius: 5px;  /* Закругляем углы */
                padding: 5px;  /* Добавляем отступы */
            }
            QDateEdit::drop-down {
                border: none;  /* Убираем рамку у выпадающего списка */
            }
        """


class AddBookingWindow(QWidget):
    cost = 0

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

        # Устанавливаем стартовую дату (например, текущая дата)
        self.check_in_input.setDate(QDate.currentDate())

        # Применяем стиль
        self.check_in_input.setStyleSheet(CALENDAR_STYLE_SHEET)
        self.check_in_input.setCalendarPopup(
            True
        )  # Включаем всплывающее окно календаря
        self.check_out_label = QLabel("Дата выезда:")
        self.check_out_input = QDateEdit()
        self.check_out_input.setDate(QDate.currentDate().addDays(1))
        self.check_out_input.setStyleSheet(CALENDAR_STYLE_SHEET)
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
            self.cost = selected_house["price_per_night"]
            number_of_rooms = selected_house["rooms"]
            # Добавляем комнаты в выпадающее меню
            for room_number in range(1, number_of_rooms + 1):
                self.room_combo.addItem(f"Комната {room_number}", room_number)

    def add_booking(self):
        customer_name = self.customer_name_input.text()
        selected_house_id = self.house_combo.currentData()
        selected_room = self.room_combo.currentData()
        check_in_date = self.check_in_input.date()
        check_out_date = self.check_out_input.date()

        if not customer_name or not selected_house_id or selected_room is None:
            QMessageBox.warning(self, "Ошибка ввода", "Пожалуйста, заполните все поля.")
            return

        # Вычисляем количество дней и общую стоимость
        days = (check_out_date.toPyDate() - check_in_date.toPyDate()).days
        if days <= 0:
            QMessageBox.warning(
                self, "Ошибка ввода", "Дата выезда должна быть позже даты заезда."
            )
            return

        total_cost = days * self.cost  # Общая стоимость

        # Логика добавления бронирования
        booking_id = f'booking:{customer_name.replace(" ", "_")}_{check_in_date.toString("yyyy-MM-dd")}'
        booking_data = {
            "_id": booking_id,
            "type": "booking",
            "house_id": selected_house_id,
            "customer_name": customer_name,
            "room_number": selected_room,
            "check_in_date": check_in_date.toString("yyyy-MM-dd"),
            "check_out_date": check_out_date.toString("yyyy-MM-dd"),
            "total_price": total_cost,  # Добавляем общую стоимость
        }

        add_URL = f"{self.main_window.COUCHDB_URL}/{self.main_window.NAME}/{booking_id}"
        response = requests.put(add_URL, json=booking_data)
        if response.status_code in (201, 202, 200):
            QMessageBox.information(
                self, "Операция успешна", f"Бронь успешно добавлена с ID: {booking_id}"
            )
            self.main_window.central_widget.setCurrentWidget(
                self.main_window.main_screen
            )  # Вернуться на главный экран
        else:
            QMessageBox.warning(
                self, "Ошибка", "Не удалось добавить дом в базу данных."
            )
        self.close()  # Закрываем окно добавления брони
