from typing import List
from src.geometry.pathfinder.path import PathPlanner
from src.geometry.operations_2d import point_to_line_signed, nor_vector, point_to_point
from shapely.geometry.polygon import Polygon
from shapely.geometry.linestring import LineString
from shapely.ops import split

from src.geometry.structures.PointList import PointList
from src.geometry.structures.Point import Point

import logging


# TODO TEST: should return 2 polygon sets (north and south side)
def cut_polygons(pa, pb, polygons: List[Polygon]):
    line = LineString([pa, pb])
    n = nor_vector(pa, pb)

    side_pos, side_neg = [], []
    for poly in polygons:
        pieces = split(poly, line)
        for piece in pieces:
            p = piece.representative_point()
            if point_to_line_signed(Point(p.x, p.y), pa, n) < 0:
                side_neg.append(piece)
            else:
                side_pos.append(piece)

    # test_plot(pa, pb, side_pos, side_neg)
    return side_neg, side_pos


# TODO: should return shapely polygons corresponding to ids form the dzl
def get_polygons_from_dzl(dzl, ids):
    polygons = []
    for i in ids:
        polygons.append(Polygon(dzl[i].polygon.convert_to_str()))
    return polygons


def get_str_polygons_from_dzl(dzl, ids):
    polygons = []
    for i in ids:
        polygons.append(dzl[i].polygon.convert_to_str())
    return polygons


def join_paths(p1: str, p2: str) -> PointList:
    pl1 = PointList.from_string(p1)
    pl2 = PointList.from_string(p2)
    return PointList.join(pl1, pl2)


def stringify_points(points):
    ret = ""
    for p in points:
        ret += str(p[0]) + " " + str(p[1]) + "  "
    ret = ret.rstrip()
    return ret


def stringify_polygons(polygons: List[Polygon]):
    str_polygons = []
    for poly in polygons:
        str_polygons.append(stringify_points(list(poly.exterior.coords)[:-1]))
    return str_polygons


def get_detour(pa, pb, r, polygons):
    pp = PathPlanner()
    pp.setR(r)
    for p in polygons:
        pp.addDangerZone(p)
    ids_to_avoid = [i for i in range(0, len(polygons))]
    pp.calculate_r_detour(pa, pb, ids_to_avoid)
    if pp.getCost() == -1:
        logging.critical(f'Path not found. {pa} -- {pb}  polygons: {polygons}')
        raise Exception("Path not found! (short edge) Aborting")
    return pp.getPath(), pp.getCost()


def get_detour_fast(pa, pb, ids_to_avoid, pp):
    pp.calculate_r_detour(pa, pb, ids_to_avoid)
    if pp.getCost() == -1:
        logging.critical(f'Path not found. {pa} -- {pb}  ids: {ids_to_avoid}')
        raise Exception("Path not found! (regular edge) Aborting")
    return pp.getPath(), pp.getCost()


def calculate_path(pa, pb, r, dzl, ids, default_pp):
    o_path, o_cost = get_detour_fast(pa, pb, ids, default_pp)
    # it ha been: get_detour(pa, pb, r, get_str_polygons_from_dzl(dzl, ids))

    if point_to_point(pa, pb) < 4 * r:
        n_polygons, s_polygons = cut_polygons(pa, pb, get_polygons_from_dzl(dzl, ids))
        n_path, n_cost = get_detour(pa, pb, r, stringify_polygons(n_polygons))
        s_path, s_cost = get_detour(pb, pa, r, stringify_polygons(s_polygons))

        if n_cost + s_cost < o_cost:
            return n_cost + s_cost, join_paths(n_path, s_path)

        return o_cost, o_path

    return o_cost, o_path
