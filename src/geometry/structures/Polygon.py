"""This module contains the polygon class representing polygons.
The class also provides support for shapely conversion."""

from src.geometry.structures.Point import Point
from src.geometry.structures.PointList import PointList
from shapely.geometry import Polygon as SP


class Polygon(PointList):
    """"""
    @staticmethod
    def from_string(string_pl: str):
        points = []
        fi = string_pl.strip('\n').strip('  ').split('  ')
        if len(fi) < 3:
            raise Exception("Cannot construct Polygon from 2 or less points!")

        for p in fi:
            xy = p.split(' ')
            points.append(
                Point(
                    float(xy[0].replace(',', '.')),
                    float(xy[1].replace(',', '.'))
                )
            )
        return Polygon(points)

    def __str__(self):
        if len(self.points) == 0:
            return 'Empty Polygon'
        return super().__str__()

    def repr_point(self):
        # TODO: clean this up
        sp = SP(self)
        if sp.is_empty:
            return None
        if sp.is_valid:
            sp = sp.buffer(0)
            if sp.is_empty:
                return None
            repr = sp.representative_point()
            return Point(repr.x, repr.y)
        return None

