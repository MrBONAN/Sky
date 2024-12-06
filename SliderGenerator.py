# SliderGenerator.py

from PyQt5.QtWidgets import QLabel, QSlider, QGridLayout
from PyQt5.QtCore import Qt
from typing import Callable


class SliderGenerator:
    @classmethod
    def create_slider(cls,
                      layout: QGridLayout,
                      row: int,
                      label_text: str,
                      min_value: int,
                      max_value: int,
                      initial_value: int,
                      tick_interval: int,
                      callback_function: Callable[[int], None],
                      update_label_function: Callable[[int], str],
                      orientation=Qt.Horizontal
                      ) -> tuple[QLabel, QSlider, QLabel]:
        label = QLabel(label_text)

        slider = QSlider(orientation)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(initial_value)
        slider.setTickInterval(tick_interval)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.valueChanged.connect(callback_function)

        value_label = QLabel()

        def wrapped_update_value_label(value):
            value_label.setText(update_label_function(value))

        wrapped_update_value_label(initial_value)
        slider.valueChanged.connect(lambda value: wrapped_update_value_label(value))

        layout.addWidget(label, row, 0)
        layout.addWidget(slider, row, 1)
        layout.addWidget(value_label, row, 2)

        return label, slider, value_label
