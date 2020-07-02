from typing import List, Iterable


class Point:
    def __init__(self, x: float = 0, y: float = 0):
        self.x: float = x
        self.y: float = y

    def __getitem__(self, item: int):
        if item == 0:
            return self.x
        if item == 1:
            return self.y
        raise Exception(f'A point has 2 coordinates, not {item}')

    def __str__(self):
        return f'Point({self.x}; {self.y})'


class PointList:
    def __init__(self, string_pl: str = None):
        if string_pl is not None:
            self.points = None # TODO
        else:
            self.points = []

    def convert_to_str(self):
        pass

    def pointify(self):
        pass


# TODO: the great refactor
