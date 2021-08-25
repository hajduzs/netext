"""This simple class represents a point.
It is derived form Vec2."""

from src.geometry.structures.Vec2 import Vec2


class Point(Vec2):
    def __str__(self):
        return f'Point({self.x}; {self.y})'
