from typing import List, Iterable


class Point:
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y

    def __getitem__(self, item):
        if item == 0:
            return self.x
        if item == 1:
            return self.y
        raise Exception(f'A point has 2 coordinates, not {item}')

    def __str__(self):
        return f'Point({self.x}; {self.y})'


class PointList:
    pass

# TODO: the great refactor
