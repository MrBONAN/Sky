import unittest
from StarParser import StarParser


class StarParserTests(unittest.TestCase):
    database_path = "../stars/stars/dbf/bright.dbf"
    def test_database_parser(self):
        stars = StarParser.read_database(self.database_path)
        self.assertEqual(3581, len(stars))
        for star in stars:
            x,y,z = star.get_vector().extract_coords()
            norm = (x**2 + y**2 + z**2)**0.5
            self.assertAlmostEqual(1, norm,
                                   msg=f"Звезда находится не на единичной окружности: "
                                                f"({x}, {y}, {z}),длина вектора: {norm}",
                                   delta=0.01)


if __name__ == '__main__':
    unittest.main()
