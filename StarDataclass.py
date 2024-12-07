from dataclasses import dataclass
from math import asin, atan2
from typing import NamedTuple


@dataclass
class Star:
    _location_vec: 'Vector'
    _magnitude: float
    _spectral_class: str

    def get_vector(self) -> 'Vector':
        return self._location_vec

    def get_angles(self) -> tuple[float, float]:
        x, y, z = self._location_vec
        right_ascension = atan2(y, x)
        declination = asin(z)
        return right_ascension, declination

    def get_magnitude(self):
        return self._magnitude

    def get_spectral_class(self):
        return self._spectral_class


@dataclass
class Vector:
    """
    params: x
    params: y
    params: z
    """
    x: float
    y: float
    z: float


    def extract_coords(self):
        return self.x,self.y,self.z