"""This module contains the PointList Class, which helps
handling point sequences (paths or polygons) easier."""

from typing import List
from src.geometry.structures.Point import Point


class PointList:
    """Simple class representing point sequences."""
    @staticmethod
    def from_string(string_pl: str) -> 'PointList':
        """
        Converts a specific (x1_y1__x2_y2__ ..) format string to
        PointList and returns it.
        """
        points = []
        for p in string_pl.strip('\n').strip('  ').split('  '):
            xy = p.split(' ')
            points.append(
                Point(
                    float(xy[0].replace(',', '.')),
                    float(xy[1].replace(',', '.'))
                )
            )
        return PointList(points)

    def __init__(self, pt_list: List[Point] = None):
        if pt_list is None:
            pt_list = []
        self.points: List = pt_list

    def convert_to_str(self) -> str:
        """Converts the PointList to a (x1_y1__x2_y2__ ..) format string"""
        ret = ""
        for p in self.points:
            ret += str(p.x) + ' ' + str(p.y) + '  '
        ret = ret.rstrip()
        return ret

    def __len__(self):
        return len(self.points)

    def __getitem__(self, item):
        return self.points[item]

    def __iter__(self):
        return (p for p in self.points)

    def __str__(self):
        if len(self.points) == 0:
            return 'Empty PointList'
        ret = '['
        for p in self.points:
            ret += f'({p.x}; {p.y}), '
        ret.rstrip(',')
        ret += ']'
        return ret

    @classmethod
    def join(cls, p1: 'PointList', p2: 'PointList') -> 'PointList':
        """Concatenates two PointLists by omitting the first point of the second one."""
        return PointList(p1.points + p2.points[1:])

