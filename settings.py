from dataclasses import dataclass

DATE_FORMAT = "%Y/%m/%d %H:%M"

INITIAL_LATITUDE = 57
INITIAL_LONGITUDE = 61
INITIAL_FOV = 45
INITIAL_HEAD_LATITUDE = 0
INITIAL_HEAD_LONGITUDE = 0

LATITUDE_RANGE = (-90, 90)
LONGITUDE_RANGE = (-180, 180)
FOV_RANGE = (10, 90)
HEAD_LATITUDE_RANGE = (-90, 90)
HEAD_LONGITUDE_RANGE = (-180, 180)

SIDEREAL_DAY_SECONDS = 86164.091

@dataclass
class AngleConfig:
    """
    Конфигурация для угловых параметров.
    """

    def __init__(self, value: float, min_value: float, max_value: float):
        self.value = value
        self.min_value = min_value
        self.max_value = max_value