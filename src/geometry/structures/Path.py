"""This module contains a Path class representing paths, derived from PointList."""


from src.geometry.structures.PointList import PointList


class Path(PointList):
    """Simple class representing a Path derived from PointList."""

    def __str__(self):
        if len(self.points) == 0:
            return 'Empty Path'
        return super().__str__()
