# MainWindow.py

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel, QPushButton, QDialog, QLineEdit
)
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt

from SliderGenerator import SliderGenerator
from SkyWidget import SkyWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Визуализация Полной Сферы с Меридианами, Параллелями и Точкой")
        self.setGeometry(100, 100, 1200, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.sky_widget = SkyWidget(self)
        main_layout.addWidget(self.sky_widget, stretch=1)

        # Добавляем информационное поле "Время" и кнопку "Изменить дату"
        time_layout = QHBoxLayout()
        main_layout.addLayout(time_layout)

        current_date_text = self.sky_widget.get_current_date_text()
        self.time_label = QLabel(f"Время: {current_date_text}")
        self.change_date_button = QPushButton("Изменить дату")
        self.change_date_button.clicked.connect(self.change_date)

        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.change_date_button)

        controls_layout = QGridLayout()
        main_layout.addLayout(controls_layout)
        self.add_sliders(controls_layout)

        # Подключаем сигналы из SkyWidget к слотам для обновления ползунков
        self.sky_widget.headLatitudeChanged.connect(self.update_head_latitude_slider)
        self.sky_widget.headLongitudeChanged.connect(self.update_head_longitude_slider)

    def add_sliders(self, controls_layout: QGridLayout) -> None:
        # Слайдер для изменения широты вида
        SliderGenerator.create_slider(
            layout=controls_layout,
            row=0,
            label_text="Широта вида (°):",
            min_value=-90,
            max_value=90,
            initial_value=57,  # примерная широта Екатеринбурга
            tick_interval=30,
            update_label_function=lambda value: f"{value}°",
            callback_function=self.sky_widget.set_latitude
        )

        # Слайдер для изменения долготы вида
        SliderGenerator.create_slider(
            layout=controls_layout,
            row=1,
            label_text="Долгота вида (°):",
            min_value=-180,
            max_value=180,
            initial_value=61,  # Примерная долгота Екатеринбурга
            tick_interval=30,
            update_label_function=lambda value: f"{value}°",
            callback_function=self.sky_widget.set_longitude
        )

        # Слайдер для зума
        SliderGenerator.create_slider(
            layout=controls_layout,
            row=2,
            label_text="Зум (%):",
            min_value=10,
            max_value=90,
            initial_value=45,
            tick_interval=5,
            update_label_function=lambda value: f"{value}%",
            callback_function=self.sky_widget.update_zoom
        )

        # Слайдер для наклона головы вверх/вниз
        _, self.head_latitude_slider, _ = SliderGenerator.create_slider(
            layout=controls_layout,
            row=3,
            label_text="Наклон головы вверх/вниз (°):",
            min_value=-90,
            max_value=90,
            initial_value=0,
            tick_interval=10,
            update_label_function=lambda value: f"{value}°",
            callback_function=self.sky_widget.set_head_latitude
        )

        # Слайдер для наклона головы влево/вправо
        _, self.head_longitude_slider, _ = SliderGenerator.create_slider(
            layout=controls_layout,
            row=4,
            label_text="Наклон головы влево/вправо (°):",
            min_value=-180,
            max_value=180,
            initial_value=0,
            tick_interval=30,
            update_label_function=lambda value: f"{value}°",
            callback_function=self.sky_widget.set_head_longitude
        )

    def update_head_latitude_slider(self, value):
        # Блокируем сигналы, чтобы избежать рекурсии
        self.head_latitude_slider.blockSignals(True)
        self.head_latitude_slider.setValue(int(value))
        self.head_latitude_slider.blockSignals(False)

    def update_head_longitude_slider(self, value):
        # Блокируем сигналы, чтобы избежать рекурсии
        self.head_longitude_slider.blockSignals(True)
        self.head_longitude_slider.setValue(int(value))
        self.head_longitude_slider.blockSignals(False)

    def change_date(self):
        current_date_text = self.time_label.text().split(": ")[1]  # Извлекаем текущую дату из лейбла
        date_dialog = QDialog(self)
        date_dialog.setWindowTitle("Укажите новую дату")
        layout = QVBoxLayout()
        date_dialog.setLayout(layout)

        date_input = QLineEdit()
        date_input.setText(current_date_text)
        layout.addWidget(date_input)

        # Добавляем кнопки
        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)

        ok_button = QPushButton("Ок")
        cancel_button = QPushButton("Отмена")
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        ok_button.clicked.connect(lambda: self.set_new_date(date_dialog, date_input.text()))
        cancel_button.clicked.connect(date_dialog.reject)

        date_dialog.exec_()

    def set_new_date(self, dialog, date_text):
        # Проверяем формат даты YYYY/MM/DD/HH/MM
        from datetime import datetime

        try:
            new_date = datetime.strptime(date_text, "%Y/%m/%d/%H/%M")
            # Обновляем дату в приложении
            self.sky_widget.update_date(new_date)
            # Обновляем информационное поле времени
            self.time_label.setText(f"Время: {date_text}")

            dialog.accept()
        except ValueError:
            # Неверный формат даты, показываем сообщение об ошибке
            QMessageBox.warning(self, "Ошибка", "Неверный формат даты. Используйте YYYY/MM/DD/HH/MM.")
