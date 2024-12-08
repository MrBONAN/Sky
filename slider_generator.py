from PyQt5.QtWidgets import QLabel, QSlider, QGridLayout
from slider_config import SliderConfig


class SliderGenerator:
    @classmethod
    def create_slider(cls, layout: QGridLayout, config: SliderConfig) -> tuple[
        QLabel, QSlider, QLabel]:
        """
        Создаёт и настраивает слайдер с меткой и отображением значения.

        :param layout: Сетка для размещения слайдера.
        :param config: Конфигурация слайдера.
        :return: Кортеж из метки, слайдера и метки значения.
        """
        label = QLabel(config.label_text)

        slider = QSlider(config.orientation)
        slider.setMinimum(config.min_value)
        slider.setMaximum(config.max_value)
        slider.setValue(config.initial_value)
        slider.setTickInterval(config.tick_interval)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.valueChanged.connect(config.callback_function)

        value_label = QLabel()

        def wrapped_update_value_label(value):
            value_label.setText(config.update_label_function(value))

        wrapped_update_value_label(config.initial_value)
        slider.valueChanged.connect(wrapped_update_value_label)

        layout.addWidget(label, config.row, 0)
        layout.addWidget(slider, config.row, 1)
        layout.addWidget(value_label, config.row, 2)

        return label, slider, value_label
