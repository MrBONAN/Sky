from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout
)

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

        controls_layout = QGridLayout()
        main_layout.addLayout(controls_layout)
        self.add_sliders(controls_layout)

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
            initial_value=61,  # Примерная долгота екатеринбурга
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
            update_label_function=lambda value: f"{value}°",
            callback_function=self.sky_widget.update_zoom
        )

        # Слайдер для изменения широты вида
        SliderGenerator.create_slider(
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

        # Слайдер для изменения долготы вида
        SliderGenerator.create_slider(
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
