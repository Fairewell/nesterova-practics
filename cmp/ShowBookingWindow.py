from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableView,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSortFilterProxyModel
import requests

class ViewBookingsWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        self.load_bookings()

    def init_ui(self):
        layout = QVBoxLayout()
        # Инициализация модели данных
        self.model = QStandardItemModel()
        self.model.setColumnCount(6)
        self.model.setHorizontalHeaderLabels([
            "Имя клиента",
            "Дом",
            "Комната",
            "Дата заезда",
            "Дата выезда",
            "Общая стоимость",
        ])
        # Создание прокси-модели для сортировки и фильтрации
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        
        # Настройка QTableView
        self.bookings_view = QTableView()
        self.bookings_view.setModel(self.proxy_model)
        self.bookings_view.setSortingEnabled(True)  # Включаем сортировку
        self.bookings_view.horizontalHeader().setStretchLastSection(True)
        self.bookings_view.setSelectionBehavior(QTableView.SelectRows)
        self.bookings_view.setEditTriggers(QTableView.NoEditTriggers)

        # Настройка ширины столбцов (опционально)
        for i in range(6):
            self.bookings_view.horizontalHeader().setSectionResizeMode(i, self.bookings_view.horizontalHeader().ResizeToContents)

        # Кнопка обновления
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_bookings)

        # Добавление виджетов в макет
        layout.addWidget(self.bookings_view)
        layout.addWidget(self.refresh_button)
        self.setLayout(layout)
        self.setWindowTitle("Просмотр броней")
        self.resize(800, 600)

    def load_bookings(self):
        # Запрос списка броней из CouchDB
        try:
            response = requests.get(
                f"{self.main_window.COUCHDB_URL}/{self.main_window.NAME}/_all_docs?include_docs=true"
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить бронь.\n{e}")
            return

        bookings_data = response.json()
        self.model.removeRows(0, self.model.rowCount())  # Очистка таблицы
        for row in bookings_data.get("rows", []):
            doc = row.get("doc", {})
            if doc.get("type") == "booking":
                customer_name = doc.get("customer_name", "")
                house_id = doc.get("house_id", "")
                room_number = doc.get("room_number", "")
                check_in_date = doc.get("check_in_date", "")
                check_out_date = doc.get("check_out_date", "")
                total_price = doc.get("total_price", "")
                # Создание элементов модели
                items = [
                    QStandardItem(customer_name),
                    QStandardItem(house_id),
                    QStandardItem(str(room_number)),
                    QStandardItem(check_in_date),
                    QStandardItem(check_out_date),
                    QStandardItem(f"{total_price:.2f}" if isinstance(total_price, (int, float)) else str(total_price)),
                ]
                # Установка типа данных для корректной сортировки
                try:
                    room_number_value = int(room_number)
                except ValueError:
                    room_number_value = 0
                try:
                    total_price_value = float(total_price)
                except ValueError:
                    total_price_value = 0.0
                items[2].setData(room_number_value, Qt.EditRole)
                items[5].setData(total_price_value, Qt.EditRole)
                self.model.appendRow(items)
        # Автоматическая сортировка по первому столбцу (опционально)
        self.bookings_view.sortByColumn(0, Qt.AscendingOrder)