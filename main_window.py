from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QDialog
)

from slider_generator import SliderGenerator
from slider_config import SliderConfig
from sky_widget import SkyWidget
from date_change_dialog_handler import DateChangeDialog
from settings import (
    INITIAL_LATITUDE, INITIAL_LONGITUDE, INITIAL_FOV,
    LATITUDE_RANGE, LONGITUDE_RANGE, FOV_RANGE,
    INITIAL_HEAD_LATITUDE, INITIAL_HEAD_LONGITUDE,
    HEAD_LATITUDE_RANGE, HEAD_LONGITUDE_RANGE,
    DATE_FORMAT
)
from datetime import datetime


class AngleConfig:
    """
    Конфигурация для угловых параметров.
    """

    def __init__(self, value: float, min_value: float, max_value: float):
        self.value = value
        self.min_value = min_value
        self.max_value = max_value


class MainWindow(QMainWindow):
    """
    Главное окно приложения "Звездное Небо".
    """

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Звездное Небо")
        self.setGeometry(100, 100, 1200, 900)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.sky_widget = SkyWidget(self)
        main_layout.addWidget(self.sky_widget, stretch=1)

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

        self.sky_widget.headLatitudeChanged.connect(
            self.update_head_latitude_slider)
        self.sky_widget.headLongitudeChanged.connect(
            self.update_head_longitude_slider)

    def add_sliders(self, controls_layout: QGridLayout) -> None:
        """
        Добавляет слайдеры в интерфейс.

        :param controls_layout: Сетка для размещения слайдеров.
        """
        slider_config_latitude = SliderConfig(
            row=0,
            label_text="Широта вида (°):",
            min_value=LATITUDE_RANGE[0],
            max_value=LATITUDE_RANGE[1],
            initial_value=INITIAL_LATITUDE,
            tick_interval=30,
            update_label_function=lambda value: f"{value}°",
            callback_function=self.sky_widget.set_latitude
        )
        SliderGenerator.create_slider(layout=controls_layout,
                                      config=slider_config_latitude)

        slider_config_longitude = SliderConfig(
            row=1,
            label_text="Долгота вида (°):",
            min_value=LONGITUDE_RANGE[0],
            max_value=LONGITUDE_RANGE[1],
            initial_value=INITIAL_LONGITUDE,
            tick_interval=30,
            update_label_function=lambda value: f"{value}°",
            callback_function=self.sky_widget.set_longitude
        )
        SliderGenerator.create_slider(layout=controls_layout,
                                      config=slider_config_longitude)

        slider_config_fov = SliderConfig(
            row=2,
            label_text="Зум (%):",
            min_value=FOV_RANGE[0],
            max_value=FOV_RANGE[1],
            initial_value=INITIAL_FOV,
            tick_interval=5,
            update_label_function=lambda value: f"{value}%",
            callback_function=self.sky_widget.update_zoom
        )
        SliderGenerator.create_slider(layout=controls_layout,
                                      config=slider_config_fov)

        slider_config_head_latitude = SliderConfig(
            row=3,
            label_text="Наклон головы вверх/вниз (°):",
            min_value=HEAD_LATITUDE_RANGE[0],
            max_value=HEAD_LATITUDE_RANGE[1],
            initial_value=INITIAL_HEAD_LATITUDE,
            tick_interval=10,
            update_label_function=lambda value: f"{value}°",
            callback_function=self.sky_widget.set_head_latitude
        )
        _, self.head_latitude_slider, _ = SliderGenerator.create_slider(
            layout=controls_layout, config=slider_config_head_latitude)

        slider_config_head_longitude = SliderConfig(
            row=4,
            label_text="Наклон головы влево/вправо (°):",
            min_value=HEAD_LONGITUDE_RANGE[0],
            max_value=HEAD_LONGITUDE_RANGE[1],
            initial_value=INITIAL_HEAD_LONGITUDE,
            tick_interval=30,
            update_label_function=lambda value: f"{value}°",
            callback_function=self.sky_widget.set_head_longitude
        )
        _, self.head_longitude_slider, _ = SliderGenerator.create_slider(
            layout=controls_layout, config=slider_config_head_longitude)

    def update_head_latitude_slider(self, value: float):
        """
        Обновляет слайдер наклона головы вверх/вниз.

        :param value: Новое значение наклона.
        """
        self.head_latitude_slider.blockSignals(True)
        self.head_latitude_slider.setValue(int(value))
        self.head_latitude_slider.blockSignals(False)

    def update_head_longitude_slider(self, value: float):
        """
        Обновляет слайдер наклона головы влево/вправо.

        :param value: Новое значение наклона.
        """
        self.head_longitude_slider.blockSignals(True)
        self.head_longitude_slider.setValue(int(value))
        self.head_longitude_slider.blockSignals(False)

    def change_date(self):
        """
        Открывает диалог для изменения даты.
        """
        current_date_text = self.time_label.text().split(": ")[1]
        date_dialog = DateChangeDialog(current_time=current_date_text,
                                       parent=self)

        if date_dialog.exec_() == QDialog.Accepted:
            new_date_text = date_dialog.get_new_time()
            self.set_new_date(new_date_text)

    def set_new_date(self, date_text: str):
        """
        Устанавливает новую дату, если формат верен.

        :param date_text: Новая дата в строковом формате.
        """
        try:
            new_date = datetime.strptime(date_text, DATE_FORMAT)
            self.sky_widget.update_date(new_date)
            self.time_label.setText(f"Время: {date_text}")
        except ValueError:
            QMessageBox.warning(self, "Ошибка",
                                "Неверный формат даты. Используйте YYYY/MM/DD/HH/MM.")
