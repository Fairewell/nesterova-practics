from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
)
import requests


class ViewBookingsWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        self.load_bookings()

    def init_ui(self):
        layout = QVBoxLayout()

        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(6)  # Указываем количество столбцов
        self.bookings_table.setHorizontalHeaderLabels(
            [
                "Имя клиента",
                "Дом",
                "Комната",
                "Дата заезда",
                "Дата выезда",
                "Общая стоимость",
            ]
        )

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_bookings)

        layout.addWidget(self.bookings_table)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)
        self.setWindowTitle("Просмотр броней")
        self.resize(600, 400)

    def load_bookings(self):
        # Запрос списка броней из CouchDB
        response = requests.get(
            f"{self.main_window.COUCHDB_URL}/{self.main_window.NAME}/_all_docs?include_docs=true"
        )

        if response.status_code == 200:
            bookings_data = response.json()
            self.bookings_table.setRowCount(
                0
            )  # Очистка таблицы перед добавлением новых данных

            for row in bookings_data["rows"]:
                if (
                    "doc" in row
                    and "type" in row["doc"]
                    and row["doc"]["type"] == "booking"
                ):
                    booking = row["doc"]
                    row_position = self.bookings_table.rowCount()
                    self.bookings_table.insertRow(row_position)

                    # Заполнение таблицы данными о бронях
                    self.bookings_table.setItem(
                        row_position, 0, QTableWidgetItem(booking["customer_name"])
                    )
                    self.bookings_table.setItem(
                        row_position, 1, QTableWidgetItem(booking["house_id"])
                    )  # Можно заменить на имя дома
                    self.bookings_table.setItem(
                        row_position, 2, QTableWidgetItem(str(booking["room_number"]))
                    )
                    self.bookings_table.setItem(
                        row_position, 3, QTableWidgetItem(booking["check_in_date"])
                    )
                    self.bookings_table.setItem(
                        row_position, 4, QTableWidgetItem(booking["check_out_date"])
                    )
                    self.bookings_table.setItem(
                        row_position, 5, QTableWidgetItem(str(booking["total_price"]))
                    )
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось загрузить бронь.")
