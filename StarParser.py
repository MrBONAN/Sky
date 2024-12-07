from dbfread import DBF
from StarDataclass import Star, Vector
from datetime import timedelta
from math import radians, degrees, cos, sin, atan2, asin, pi


class StarParser:
    @classmethod
    def read_database(cls,
                      database_path: str = "stars/stars/dbf/bright.dbf") -> \
            list[Star]:
        """
        Читает базу данных звезд и возвращает список объектов Star.

        :param database_path: Путь к файлу базы данных.
        :return: Список звезд.
        """
        stars = []
        for line in DBF(database_path):
            right_ascension = line["ALF"]
            declination = line["DEL"]
            magnitude = line["M"]
            spectral_class = line["SP"]
            star_vector = cls.calculate_vector_from_ra_dec(right_ascension,
                                                           declination)
            stars.append(
                Star(location_vec=star_vector, magnitude=float(magnitude),
                     spectral_class=spectral_class))
        return stars

    @classmethod
    def calculate_vector_from_ra_dec(cls, right_ascension: str,
                                     declination: str) -> Vector:
        """
        Преобразует прямое восхождение и склонение в вектор.

        :param right_ascension: Прямое восхождение в формате "HH:MM:SS".
        :param declination: Склонение в формате "±DD:MM:SS".
        :return: Вектор положения звезды.
        """
        ra_rad, dec_rad = cls.parse_ra_dec(right_ascension, declination)
        return cls.vector_from_angles(ra_rad, dec_rad)

    @classmethod
    def parse_ra_dec(cls, right_ascension: str, declination: str) -> tuple[
        float, float]:
        """
        Парсит строки прямого восхождения и склонения и возвращает их в радианах.

        :param right_ascension: Прямое восхождение в формате "HH:MM:SS".
        :param declination: Склонение в формате "±DD:MM:SS".
        :return: Кортеж из прямого восхождения и склонения в радианах.
        """
        ra_hours, ra_minutes, ra_seconds = map(float,
                                               right_ascension.split(":"))
        right_ascension_angle = ra_hours * 15 + ra_minutes / 4 + ra_seconds / (
                4 * 60)
        ra_rad = radians(right_ascension_angle)

        dec_sign = -1 if declination.startswith('-') else 1
        dec_hours, dec_minutes, dec_seconds = map(float, declination.lstrip(
            '+-').split(":"))
        declination_angle = dec_sign * (
                abs(dec_hours) + dec_minutes / 60 + dec_seconds / 3600)
        dec_rad = radians(declination_angle)

        return ra_rad, dec_rad

    @staticmethod
    def vector_from_angles(ra_rad: float, dec_rad: float) -> Vector:
        """
        Преобразует углы в радианах в вектор для точки на единичной сфере.

        :param ra_rad: Прямое восхождение в радианах.
        :param dec_rad: Склонение в радианах.
        :return: Вектор положения звезды.
        """
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

        :param stars: Список звезд (объектов класса Star).
        :param delta_time: Изменение времени (timedelta).
        :return: Список обновленных объектов Star.
        """
        delta_seconds = delta_time.total_seconds()
        rotation_angle = cls.calculate_rotation_angle(delta_seconds)

        updated_stars = []
        for star in stars:
            updated_vector = cls.update_star_vector(star.get_vector(),
                                                    rotation_angle)
            updated_stars.append(Star(location_vec=updated_vector,
                                      magnitude=star.get_magnitude(),
                                      spectral_class=star.get_spectral_class()))

        return updated_stars

    @classmethod
    def calculate_rotation_angle(cls, delta_seconds: float) -> float:
        """
        Вычисляет угловое смещение на основе прошедшего времени.

        :param delta_seconds: Прошедшее время в секундах.
        :return: Угловое смещение в градусах.
        """
        return (
                delta_seconds / cls.SIDEREAL_DAY_SECONDS) * 360  # Угловое смещение в градусах

    @classmethod
    def update_star_vector(cls, vector: Vector,
                           rotation_angle: float) -> Vector:
        """
        Обновляет вектор звезды на основе углового смещения.

        :param vector: Текущий вектор звезды.
        :param rotation_angle: Угловое смещение в градусах.
        :return: Обновленный вектор звезды.
        """
        ra, dec = cls.vector_to_ra_dec(vector)
        updated_ra = (degrees(ra) + rotation_angle) % 360
        updated_ra_rad = radians(updated_ra)
        return cls.vector_from_angles(updated_ra_rad, dec)

    @staticmethod
    def vector_to_ra_dec(vector: Vector) -> tuple[float, float]:
        """
        Преобразует декартовы координаты в экваториальные (RA, Dec).

        :param vector: Вектор положения звезды.
        :return: Кортеж из прямого восхождения и склонения в радианах.
        """
        x, y, z = vector.extract_coords()
        ra = atan2(y, x)  # Прямое восхождение
        if ra < 0:
            ra += 2 * pi  # Нормировка до положительных значений
        dec = asin(z)  # Склонение
        return ra, dec

    @staticmethod
    def vector_from_angles(ra_rad: float, dec_rad: float) -> Vector:
        """
        Преобразует экваториальные координаты (RA, Dec) обратно в декартовы.

        :param ra_rad: Прямое восхождение в радианах.
        :param dec_rad: Склонение в радианах.
        :return: Вектор положения звезды.
        """
        x = cos(dec_rad) * cos(ra_rad)
        y = cos(dec_rad) * sin(ra_rad)
        z = sin(dec_rad)
        return Vector(x, y, z)
