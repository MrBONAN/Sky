import unittest
from StarParser import StarParser


class StarParserTests(unittest.TestCase):
    database_path = "../stars/stars/dbf/bright.dbf"
    def test_database_parser(self):
        stars = StarParser.read_database(self.database_path)
        self.assertEqual(3581, len(stars))
        for star in stars:
            vec = star.get_vector()
            norm = (vec[0]**2 + vec[1]**2 + vec[2]**2)**0.5
            self.assertAlmostEqual(1, norm,
                                   msg=f"Звезда находится не на единичной окружности: "
                                                f"({vec[0]}, {vec[1]}, {vec[2]}),длина вектора: {norm}",
                                   delta=0.01)


if __name__ == '__main__':
    unittest.main()
