from dbfread import DBF
from StarDataclass import Star
from math import pi, cos, sin

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
    def _calculate_star_vector(cls, right_ascension:str, declination:str) -> tuple[float, float, float]:
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
        return x, y, z

