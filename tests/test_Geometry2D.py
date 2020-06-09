from unittest import TestCase
from Utilities.Geometry2D import *
from math import pi


class Test(TestCase):
    def test_angle_between(self):
        self.assertEqual(angle_between((0, 0), (0, 0)), 0)
        self.assertEqual(angle_between((0, 0), (1, 0)), 0)
        self.assertEqual(angle_between((0, 0), (1, 1)), pi / 4)
        self.assertEqual(angle_between((0, 0), (0, 1)), pi / 2)
        self.assertEqual(angle_between((0, 0), (-1, 1)), pi * 3 / 4)
        self.assertEqual(angle_between((0, 0), (-1, 0)), pi)
        self.assertEqual(angle_between((0, 0), (-1, -1)), pi * 5 / 4)
        self.assertEqual(angle_between((0, 0), (0, -1)), pi * 3 / 2)
        self.assertEqual(angle_between((0, 0), (1, -1)), pi * 7 / 4)

    def test_direction_vector(self):
        self.assertEqual(direction_vector((0, 0), (0, 1)), (0, 1))
        self.assertEqual(direction_vector((1, 1), (1, 2)), (0, 1))
        self.assertEqual(direction_vector((3, 1), (2, 4)), (-1, 3))
