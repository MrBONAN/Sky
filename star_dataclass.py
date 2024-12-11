from dataclasses import dataclass
from math import asin, atan2
from typing import NamedTuple


class Vector(NamedTuple):
    """
    Вектор в 3D пространстве.
    """
    x: float
    y: float
    z: float

    def extract_coords(self) -> tuple[float, float, float]:
        return self.x, self.y, self.z


@dataclass
class Star:
    """
    Звезда с вектором положения, магнитудой и спектральным классом.
    """
    location_vec: Vector
    magnitude: float
    spectral_class: str

    def get_vector(self) -> Vector:
        return self.location_vec

    def get_angles(self) -> tuple[float, float]:
        """
        Возвращает прямое восхождение и склонение.
        """
        vector = self.location_vec
        x,y,z = vector.extract_coords()
        right_ascension = atan2(y, x)
        declination = asin(z)
        return right_ascension, declination

    def get_magnitude(self) -> float:
        return self.magnitude

    def get_spectral_class(self) -> str:
        return self.spectral_class
