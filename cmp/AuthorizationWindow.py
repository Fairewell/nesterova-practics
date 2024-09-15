import requests
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)


class AuthWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

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
        username = self.login_input.text()
        password = self.password_input.text()

        # URL для получения документа
        couchdb_url = (
            f"{self.main_window.COUCHDB_URL}/{self.main_window.NAME}/auth:{username}"
        )

        # Запрос на получение документа
        response = requests.get(couchdb_url)

        if response.status_code == 200:
            user_data = response.json()
            # Проверка пароля
            if user_data.get("password") == password:
                QMessageBox.information(self, "Успех", "Вы успешно вошли!")
                self.main_window.show_main_screen()  # Переход на главный экран
                self.close()  # Закрыть окно авторизации
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")
        else:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден.")
