from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)


class DateChangeDialog(QDialog):
    def __init__(self, current_time: str, parent=None):
        super(DateChangeDialog, self).__init__(parent)
        self.setWindowTitle("Укажите новую дату")
        self.setModal(True)

        self.current_time = current_time

        # Основной вертикальный макет
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Информационное сообщение
        info_label = QLabel("Введите новую дату в формате YYYY/MM/DD/HH/MM:")
        main_layout.addWidget(info_label)

        # Поле ввода даты
        self.time_input = QLineEdit()
        self.time_input.setText(self.current_time)
        main_layout.addWidget(self.time_input)

        # Горизонтальный макет для кнопок
        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        # Кнопка "ОК"
        ok_button = QPushButton("ОК")
        ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_button)

        # Кнопка "Отмена"
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

    def get_new_time(self) -> str:
        return self.time_input.text()

    def accept(self):
        if self.validate_time_format(self.time_input.text()):
            super().accept()
        else:
            QMessageBox.warning(self, "Неверный формат", "Пожалуйста, введите дату в формате YYYY/MM/DD/HH/MM.")

    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """Проверяет, соответствует ли строка формату YYYY/MM/DD/HH/MM."""
        try:
            parts = time_str.split('/')
            if len(parts) != 5:
                return False
            year, month, day, hour, minute = map(int, parts)
            if not (1 <= month <= 12):
                return False
            if not (1 <= day <= 31):
                return False
            if not (0 <= hour < 24):
                return False
            if not (0 <= minute < 60):
                return False
            return True
        except ValueError:
            return False
