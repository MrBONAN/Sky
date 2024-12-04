from dataclasses import dataclass
from math import asin, atan2

@dataclass
class Star:
    _location_vec: tuple[float, float, float]
    magnitude: float
    spectral_class: str

    def get_vector(self) -> tuple[float, float, float]:
        return self._location_vec

    def get_angles(self) -> tuple[float, float]:
        x, y, z = self._location_vec
        right_ascension = atan2(y, x)
        declination = asin(z)
        return right_ascension, declination