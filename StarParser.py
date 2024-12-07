from dbfread import DBF
from StarDataclass import Star,Vector
from datetime import timedelta
from math import radians, degrees, cos, sin, atan2, asin, pi

class StarParser:
    @classmethod
    def read_database(cls, database_path="stars/stars/dbf/bright.dbf") -> list[Star]:
        stars = []
        for line in DBF(database_path):
            right_ascension = line["ALF"]
            declination = line["DEL"]
            magnitude = line["M"]
            spectral_class = line["SP"]
            star_vector = cls._calculate_star_vector(right_ascension, declination)
            stars.append(Star(star_vector, float(magnitude), spectral_class))
        return stars

    @classmethod
    def _calculate_star_vector(cls, right_ascension:str, declination:str) -> 'Vector':
        ra_hours, ra_minutes, ra_seconds = map(float, right_ascension.split(":"))
        right_ascension_angle = ra_hours * 15 + ra_minutes / 4 + ra_seconds / (4 * 60)
        dec_hours, dec_minutes, dec_seconds = map(float, declination.split(":"))
        declination_angle = abs(dec_hours) + dec_minutes / 60 + dec_seconds / (60 * 60)
        if dec_hours < 0: declination_angle *= -1

        ra_rad = right_ascension_angle / 360 * 2 * pi
        dec_rad = declination_angle / 90 * pi / 2

        x = cos(dec_rad) * cos(ra_rad)
        y = cos(dec_rad) * sin(ra_rad)
        z = sin(dec_rad)
        return Vector(x, y, z)


class StarPositionUpdater:
    SIDEREAL_DAY_SECONDS = 86164.091

    @classmethod
    def update_positions(cls, stars: list[Star], delta_time: timedelta) -> \
    list[Star]:
        """
        Обновляет положения звёзд с учётом времени.

        :param stars: Список объектов Star.
        :param delta_time: Изменение времени (timedelta).
        :return: Список обновленных объектов Star.
        """
        delta_seconds = delta_time.total_seconds()
        rotation_angle = (
                                     delta_seconds / cls.SIDEREAL_DAY_SECONDS) * 360  # Угловое смещение в градусах

        updated_stars = []
        for star in stars:
            x, y, z = star.get_vector().extract_coords()
            ra, dec = cls._vector_to_ra_dec(x, y, z)

            updated_ra = (degrees(ra) + rotation_angle) % 360
            updated_ra_rad = radians(updated_ra)

            updated_vector = cls._calculate_star_vector(updated_ra_rad, dec)
            updated_stars.append(
                Star(updated_vector, star.get_magnitude(), star.get_spectral_class())
            )

        return updated_stars

    @staticmethod
    def _vector_to_ra_dec(x: float, y: float, z: float) -> tuple[float, float]:
        """
        Преобразует декартовы координаты в экваториальные (RA, Dec).
        """
        ra = atan2(y, x)  # Прямое восхождение
        if ra < 0:
            ra += 2 * pi  # нормировка до полож
        dec = asin(z)  # Склонение
        return ra, dec

    @staticmethod
    def _calculate_star_vector(ra: float, dec: float) -> Vector:
        """
        Преобразует экваториальные координаты (RA, Dec) обратно в декартовы.
        """
        x = cos(dec) * cos(ra)
        y = cos(dec) * sin(ra)
        z = sin(dec)
        return Vector(x, y, z)

