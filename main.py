import sys
import os
import requests
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QStackedWidget,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QFile
from dotenv import load_dotenv

from cmp.BookingWindow import AddBookingWindow
from cmp.HouseWindow import AddHouseWindow
from cmp.ShowHouseWindow import HousesDisplay


class AuthWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()
        # Применение стилей

    def init_ui(self):
        layout = QVBoxLayout()
        self.login_label = QLabel("Логин:")
        self.login_input = QLineEdit()
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.login)

        layout.addWidget(self.login_label)
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        # Здесь можно добавить логику проверки логина и пароля
        self.main_window.show_main_screen()
        self.close()


class MainWindow(QMainWindow):
    # Загрузка переменных окружения
    dotenv_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    LOGIN = os.getenv("DB_LOGIN")
    PASSWORD = os.getenv("DB_PASSWORD")
    NAME = os.getenv("DB_NAME")
    COUCHDB_URL = f"http://{LOGIN}:{PASSWORD}@localhost:5984"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление Тур Агентством")
        self.setGeometry(300, 300, 600, 400)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.auth_window = AuthWindow(self)
        self.central_widget.addWidget(self.auth_window)

        self.main_screen = QWidget()
        self.central_widget.addWidget(self.main_screen)
        self.init_main_screen()
        self.load_stylesheet("stylesheet.qss")

    def load_stylesheet(self, filename):
        """Загрузка и применение файла стилей."""
        file = QFile(filename)
        if file.open(QFile.ReadOnly):
            stylesheet = str(file.readAll(), encoding="utf-8")
            self.setStyleSheet(stylesheet)
            file.close()
        else:
            print(f"Не удалось открыть файл стилей: {filename}")

    def init_main_screen(self):
        layout = QVBoxLayout()
        self.booking_button = QPushButton("Просмотр броней")
        self.booking_button.clicked.connect(self.show_bookings)
        self.houses_button = QPushButton("Просмотр всех домов")
        self.houses_button.clicked.connect(self.show_houses)

        # Кнопки добавления
        self.add_house_button = QPushButton("Добавить дом")
        self.add_house_button.clicked.connect(self.show_add_house)
        self.add_booking_button = QPushButton("Добавить бронь")
        self.add_booking_button.clicked.connect(self.show_add_booking)

        layout.addWidget(self.booking_button)
        layout.addWidget(self.houses_button)
        layout.addWidget(self.add_house_button)
        layout.addWidget(self.add_booking_button)

        self.main_screen.setLayout(layout)

    def show_main_screen(self):
        self.central_widget.setCurrentWidget(self.main_screen)

    def show_bookings(self):
        # Здесь можно добавить логику для отображения всех броней
        QMessageBox.information(
            self, "Просмотр броней", "Здесь будет список всех броней."
        )

    def show_houses(self):
        # Здесь можно добавить логику для отображения всех домов
        self.house_display = HousesDisplay(self)
        self.central_widget.addWidget(self.house_display)
        self.central_widget.setCurrentWidget(self.house_display)

    def show_add_house(self):
        # Переход к экрану добавления дома
        self.add_house_window = AddHouseWindow(self)
        self.central_widget.addWidget(self.add_house_window)
        self.central_widget.setCurrentWidget(self.add_house_window)

    def show_add_booking(self):
        # Переход к экрану добавления брони
        self.add_booking_window = AddBookingWindow(self)
        self.central_widget.addWidget(self.add_booking_window)
        self.central_widget.setCurrentWidget(self.add_booking_window)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Установка шрифта для всего приложения
    font = QFont("Montserrat", 10, 400)
    app.setFont(font)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
