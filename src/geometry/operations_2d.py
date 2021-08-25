"""2D Operations Module 

This module contains the most common 2D vector operations (like getting the length,
dot product etc.) which we use in other modules. 
"""

from math import sqrt, atan2, pi
from src.geometry.structures.Vec2 import Vec2


def length(v: Vec2) -> float:
    """Returns the length of a 2D vector"""
    return sqrt(v.x ** 2 + v.y ** 2)


def cross(v1: Vec2, v2: Vec2) -> float:
    """Returns the cross product of two vectors"""
    return v1.x * v2.x + v1.y * v2.y


def norm(v: Vec2) -> Vec2:
    """Returns the normalised (length scaled to 1) version of the input vector"""
    t = length(v)
    return Vec2(v.x / t, v.y / t)


def dir_vector(p1: Vec2, p2: Vec2) -> Vec2:
    """Returns the direction vector going from """
    return Vec2(p2.x - p1.x, p2.y - p1.y)


def nor_vector(p1: Vec2, p2: Vec2) -> Vec2:
    """Returns the normal vector between two points"""
    return Vec2(p1.y - p2.y, p2.x - p1.x)


def point_to_point(p1: Vec2, p2: Vec2):
    """Returns the absolute distance between two points"""
    return length(dir_vector(p1, p2))


def point_to_line_signed(p: Vec2, p0: Vec2, p1: Vec2):
    """Returns the signed distance between a point and a line"""
    return cross(norm(nor_vector(p0, p1)), dir_vector(p, p0))


def point_to_line_abs(p: Vec2, p0: Vec2, p1: Vec2):
    """Returns the absolute distance between a point and a line"""
    return abs(point_to_line_signed(p, p0, p1))


def angle_between(v1: Vec2, v2: Vec2):
    """Returns the angle between two points direction vector."""
    v = dir_vector(v1, v2)
    a = atan2(v.y, v.x)
    if a < 0:
        a = 2 * pi + a
    return a
