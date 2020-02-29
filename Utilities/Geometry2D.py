from math import sqrt, acos

# Every parameter here is a two-tuple of real numbers.
# "p" is for points, "v" is for vectors.
# Return types are real numbers OR tuples (points or vectors)
# and when returning tuples, python doesnt need parentheses to know its a tuple. simple commas will do.


def direction_vector(p1, p2):
    return p1[0] - p2[0], p1[1] - p2[1]


def length(v):
    return sqrt((v[0] ** 2) + (v[1] ** 2))


def normalize(v):
    try:
        return v[0] / length(v), v[1] / length(v)
    except ZeroDivisionError:
        return float('Inf'), float('Inf')


def normal_vector(p1, p2):
    v = direction_vector(p1, p2)
    return -v[1], v[0]


def cross_product(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]


def angle_between(v1, v2):
    return acos(cross_product(v1, v2)/(length(v1)*length(v2)))


def point_to_point(p1, p2):
    return length(direction_vector(p1, p2))


def point_to_line(p, p0, n):
    return abs(cross_product(normalize(n), direction_vector(p, p0)))
