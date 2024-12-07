from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox
)


class DateChangeDialog(QDialog):
    """
    Диалог для изменения даты.
    """

    def __init__(self, current_time: str, parent=None):
        super(DateChangeDialog, self).__init__(parent)
        self.setWindowTitle("Укажите новую дату")
        self.setModal(True)

        self.current_time = current_time

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        info_label = QLabel("Введите новую дату в формате YYYY/MM/DD/HH/MM:")
        main_layout.addWidget(info_label)

        self.time_input = QLineEdit()
        self.time_input.setText(self.current_time)
        main_layout.addWidget(self.time_input)

        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)

        ok_button = QPushButton("ОК")
        ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_button)

        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

    def get_new_time(self) -> str:
        """
        Возвращает введённую пользователем новую дату.

        :return: Строка с новой датой.
        """
        return self.time_input.text()

    def accept(self):
        """
        Переопределённый метод accept с валидацией формата даты.
        """
        if self.validate_time_format(self.time_input.text()):
            super().accept()
        else:
            QMessageBox.warning(self, "Неверный формат",
                                "Пожалуйста, введите дату в формате YYYY/MM/DD/HH/MM.")

    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """
        Проверяет, соответствует ли строка формату YYYY/MM/DD/HH/MM.

        :param time_str: Строка даты.
        :return: True, если формат верный, иначе False.
        """
        try:
            datetime.strptime(time_str, "%Y/%m/%d/%H/%M")
            return True
        except ValueError:
            return False
