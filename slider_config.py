from dataclasses import dataclass
from typing import Callable
from PyQt5.QtCore import Qt


@dataclass
class SliderConfig:
    row: int
    label_text: str
    min_value: int
    max_value: int
    initial_value: int
    tick_interval: int
    callback_function: Callable[[int], None]
    update_label_function: Callable[[int], str]
    orientation: Qt.Orientation = Qt.Horizontal
