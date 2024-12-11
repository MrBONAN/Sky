from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)


class DateChangeDialog(QDialog):
    """
    Диалог для изменения даты.
    """
    #тут было требование аннотировать, не понял что именно аннотировать
    def __init__(self, current_time: str, parent=None):
        """
        :param current_time: Строка в формате YYYY/MM/DD/HH/MM
        """
        super(DateChangeDialog, self).__init__(parent)
        self.setWindowTitle("Укажите новую дату")
        self.setModal(True)

        self.original_datetime = datetime.strptime(current_time, "%Y/%m/%d/%H/%M")

        current_date_str = self.original_datetime.strftime("%d/%m/%Y")
        current_time_str = self.original_datetime.strftime("%H:%M")

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        info_label = QLabel("Введите новую дату и время:")
        main_layout.addWidget(info_label)

        date_layout = QHBoxLayout()
        date_label = QLabel("Дата (DD/MM/YYYY):")
        self.date_input = QLineEdit()
        self.date_input.setText(current_date_str)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        main_layout.addLayout(date_layout)

        time_layout = QHBoxLayout()
        time_label = QLabel("Время (HH:MM):")
        self.time_input = QLineEdit()
        self.time_input.setText(current_time_str)
        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_input)
        main_layout.addLayout(time_layout)

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
        Возвращает введённую пользователем новую дату в формате YYYY/MM/DD/HH/MM.
        """
        return self._new_time_str

    def accept(self):
        """
        Переопределённый метод accept с валидацией формата даты/времени.
        """
        date_str = self.date_input.text().strip()
        time_str = self.time_input.text().strip()

        try:
            new_dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")

            self._new_time_str = new_dt.strftime("%Y/%m/%d/%H/%M")
            super().accept()
        except ValueError:
            QMessageBox.warning(self, "Неверный формат",
                                "Пожалуйста, введите дату в формате DD/MM/YYYY и время в формате HH:MM.")
