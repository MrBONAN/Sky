from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QDialog, QDoubleSpinBox
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


class MainWindow(QMainWindow):
    """
    Главное окно приложения "Звездное Небо".
    """
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Звездное Небо")
        self.setGeometry(100, 100, 1200, 900)

        _central_widget = QWidget()
        self.setCentralWidget(_central_widget)

        _main_layout = QVBoxLayout()
        _central_widget.setLayout(_main_layout)

        self._sky_widget = SkyWidget(self)
        _main_layout.addWidget(self._sky_widget, stretch=1)

        _time_layout = QHBoxLayout()
        _main_layout.addLayout(_time_layout)

        _current_date_text = self._sky_widget.get_current_date_text()

        self._time_label = QLabel(f"Время: {_current_date_text}")
        self._change_date_button = QPushButton("Изменить дату")
        self._change_date_button.clicked.connect(self.change_date)

        _time_layout.addWidget(self._time_label)
        _time_layout.addWidget(self._change_date_button)

        _controls_layout = QGridLayout()
        _main_layout.addLayout(_controls_layout)
        self._add_sliders(_controls_layout)

        _magnitude_layout = QHBoxLayout()
        _min_mag_label = QLabel("Мин. звёздная величина:")
        self._min_mag_spin = QDoubleSpinBox()
        self._min_mag_spin.setRange(-1.0, 6.0)
        self._min_mag_spin.setValue(-0.1)
        self._min_mag_spin.setSingleStep(0.1)
        self._min_mag_spin.valueChanged.connect(self.update_magnitude_range)

        _magnitude_layout.addWidget(_min_mag_label)
        _magnitude_layout.addWidget(self._min_mag_spin)

        _max_mag_label = QLabel("Макс. звёздная величина:")
        self._max_mag_spin = QDoubleSpinBox()
        self._max_mag_spin.setRange(1.0, 7.0)
        self._max_mag_spin.setValue(6.0)
        self._max_mag_spin.setSingleStep(0.1)
        self._max_mag_spin.valueChanged.connect(self.update_magnitude_range)

        _magnitude_layout.addWidget(_max_mag_label)
        _magnitude_layout.addWidget(self._max_mag_spin)

        _main_layout.addLayout(_magnitude_layout)

        self._sky_widget.headLatitudeChanged.connect(self.update_head_latitude_slider)
        self._sky_widget.headLongitudeChanged.connect(self.update_head_longitude_slider)

    def _add_sliders(self, controls_layout: QGridLayout) -> None:
        """
        Добавляет слайдеры в интерфейс.
        """
        _slider_config_latitude = SliderConfig(
            row=0,
            label_text="Широта вида (°):",
            min_value=LATITUDE_RANGE[0],
            max_value=LATITUDE_RANGE[1],
            initial_value=INITIAL_LATITUDE,
            tick_interval=30,
            update_label_function=lambda value: f"{value}°",
            callback_function=self._sky_widget.set_latitude
        )
        SliderGenerator.create_slider(layout=controls_layout,
                                      config=_slider_config_latitude)

        _slider_config_longitude = SliderConfig(
            row=1,
            label_text="Долгота вида (°):",
            min_value=LONGITUDE_RANGE[0],
            max_value=LONGITUDE_RANGE[1],
            initial_value=INITIAL_LONGITUDE,
            tick_interval=30,
            update_label_function=lambda value: f"{value}°",
            callback_function=self._sky_widget.set_longitude
        )
        SliderGenerator.create_slider(layout=controls_layout,
                                      config=_slider_config_longitude)

        _slider_config_fov = SliderConfig(
            row=2,
            label_text="Зум (%):",
            min_value=FOV_RANGE[0],
            max_value=FOV_RANGE[1],
            initial_value=INITIAL_FOV,
            tick_interval=5,
            update_label_function=lambda value: f"{value}%",
            callback_function=self._sky_widget.update_zoom
        )
        SliderGenerator.create_slider(layout=controls_layout,
                                      config=_slider_config_fov)

        _slider_config_head_latitude = SliderConfig(
            row=3,
            label_text="Наклон головы вверх/вниз (°):",
            min_value=HEAD_LATITUDE_RANGE[0],
            max_value=HEAD_LATITUDE_RANGE[1],
            initial_value=INITIAL_HEAD_LATITUDE,
            tick_interval=10,
            update_label_function=lambda value: f"{value}°",
            callback_function=self._sky_widget.set_head_latitude
        )
        _, self._head_latitude_slider, _ = SliderGenerator.create_slider(
            layout=controls_layout, config=_slider_config_head_latitude)

        _slider_config_head_longitude = SliderConfig(
            row=4,
            label_text="Наклон головы влево/вправо (°):",
            min_value=HEAD_LONGITUDE_RANGE[0],
            max_value=HEAD_LONGITUDE_RANGE[1],
            initial_value=INITIAL_HEAD_LONGITUDE,
            tick_interval=30,
            update_label_function=lambda value: f"{value}°",
            callback_function=self._sky_widget.set_head_longitude
        )
        _, self._head_longitude_slider, _ = SliderGenerator.create_slider(
            layout=controls_layout, config=_slider_config_head_longitude)

    def update_magnitude_range(self):
        """
        Обновляет интервал видимой звёздной величины в sky_widget.
        """
        _min_mag = self._min_mag_spin.value()
        _max_mag = self._max_mag_spin.value()

        if _min_mag > _max_mag:
            QMessageBox.warning(self, "Неверный диапазон",
                                "Минимальная величина должна быть меньше максимальной.")
            return

        self._sky_widget.set_magnitude_range(_min_mag, _max_mag)

    def update_head_latitude_slider(self, value: float):
        self._head_latitude_slider.blockSignals(True)
        self._head_latitude_slider.setValue(int(value))
        self._head_latitude_slider.blockSignals(False)

    def update_head_longitude_slider(self, value: float):
        self._head_longitude_slider.blockSignals(True)
        self._head_longitude_slider.setValue(int(value))
        self._head_longitude_slider.blockSignals(False)

    def change_date(self):
        _current_date_text = self._time_label.text().split(": ", 1)[1]
        _date_dialog = DateChangeDialog(current_time=_current_date_text,
                                        parent=self)

        if _date_dialog.exec_() == QDialog.Accepted:
            _new_date_text = _date_dialog.get_new_time()
            self.set_new_date(_new_date_text)

    def set_new_date(self, date_text: str):
        try:
            _new_date = datetime.strptime(date_text, DATE_FORMAT)

            self._sky_widget.update_date(_new_date)

            self._time_label.setText(f"Время: {date_text}")
        except ValueError:
            QMessageBox.warning(self, "Ошибка",
                                "Неверный формат даты. Используйте YYYY/MM/DD HH:MM.")
