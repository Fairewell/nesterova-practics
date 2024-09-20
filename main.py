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
    QMenuBar,
    QAction,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QFile
from dotenv import load_dotenv

from cmp.BookingWindow import AddBookingWindow
from cmp.HouseWindow import AddHouseWindow
from cmp.ShowHouseWindow import HousesDisplay
from cmp.ShowBookingWindow import ViewBookingsWindow
from cmp.AuthorizationWindow import AuthWindow


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
        self.setWindowTitle("База отдыха ")
        self.setGeometry(300, 300, 900, 600)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.auth_window = AuthWindow(self)
        self.central_widget.addWidget(self.auth_window)

        self.main_screen = QWidget()
        self.central_widget.addWidget(self.main_screen)
        self.init_main_screen()
        self.init_menu()  # Добавьте этот вызов
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

    def init_menu(self):
        """Создание верхнего меню для навигации."""
        menubar = self.menuBar()

        # Создаём основное меню
        nav_menu = menubar.addMenu("Навигация")

        # Создаём действия меню
        main_action = QAction("Главная", self)
        bookings_action = QAction("Мои бронирования", self)
        houses_action = QAction("Все дома", self)
        add_house_action = QAction("Добавить дом", self)
        add_booking_action = QAction("Добавить бронь", self)
        logout_action = QAction("Выйти", self)

        # Добавляем действия в меню
        nav_menu.addAction(main_action)
        nav_menu.addAction(bookings_action)
        nav_menu.addAction(houses_action)
        nav_menu.addSeparator()
        nav_menu.addAction(add_house_action)
        nav_menu.addAction(add_booking_action)
        nav_menu.addSeparator()
        nav_menu.addAction(logout_action)

        # Подключаем слоты для действий
        main_action.triggered.connect(self.show_main_screen)
        bookings_action.triggered.connect(self.show_bookings)
        houses_action.triggered.connect(self.show_houses)
        add_house_action.triggered.connect(self.show_add_house)
        add_booking_action.triggered.connect(self.show_add_booking)
        logout_action.triggered.connect(self.logout)
    
    def logout(self):
        """Выйти из аккаунта и показать окно авторизации."""
        self.central_widget.setCurrentWidget(self.auth_window)
        # Можно добавить дополнительную логику очистки сессии и т.д.

    def show_main_screen(self):
        self.central_widget.setCurrentWidget(self.main_screen)

    def show_bookings(self):
        # Здесь можно добавить логику для отображения всех броней
        self.booking_display = ViewBookingsWindow(self)
        self.central_widget.addWidget(self.booking_display)
        self.central_widget.setCurrentWidget(self.booking_display)

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
    # font = QFont("Montserrat", 10, 400)
    # app.setFont(font)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
