from typing import List
from libs.Wrappers.PathPlanner import PathPlanner
from Utilities.Geometry2D import point_to_line_signed, normal_vector, point_to_point
from shapely.geometry.polygon import Polygon
from shapely.geometry.linestring import LineString
from shapely.ops import split
from algorithms.helper_functions import sample_point, destringify_points, stringify_points

from matplotlib import pyplot as plt
from descartes import PolygonPatch


def test_plot(pa, pb, np, sp):
    fig, ax = plt.subplots()
    if False:
        ax.set_xlim(70, 230)
        ax.set_ylim(40, 160)
    else:
        ax.set_xlim(-2, 8)
        ax.set_ylim(-2, 8)

    lc = (pa[0], pb[0]), (pa[1], pb[1])
    l = plt.Line2D(*lc, color='black', linewidth=2)
    ax.add_artist(l)
    for z in np:
        ax.add_patch(PolygonPatch(z, fc="blue", ec="blue", alpha=0.4, zorder=3))
    for z in sp:
        ax.add_patch(PolygonPatch(z, fc="red", ec="red", alpha=0.4, zorder=3))
    plt.show()


def test_cut_polygons():
    p = Polygon([(0,0),(2,0),(2,2),(4,2),(4,0),(6,0),(6,4),(0,4)])
    a = 0, 0
    b = 7, 6
    cut_polygons(a, b, [p])


# TODO TEST: should return 2 polygon sets (north and south side)
def cut_polygons(pa, pb, polygons: List[Polygon]):
    line = LineString([pa, pb])
    n = normal_vector(pa, pb)

    side_pos, side_neg = [], []
    for poly in polygons:
        pieces = split(poly, line)
        for piece in pieces:
            p = sample_point(piece)
            if point_to_line_signed((p.x, p.y), pa, n) < 0:
                side_neg.append(piece)
            else:
                side_pos.append(piece)

    # test_plot(pa, pb, side_pos, side_neg)
    return side_neg, side_pos


# TODO: should return shapely polygons corresponding to ids form the dzl
def get_polygons_from_dzl(dzl, ids):
    polygons = []
    for i in ids:
        polygons.append(Polygon(destringify_points(dzl[i].string_poly)))
    return polygons


def get_str_polygons_from_dzl(dzl, ids):
    polygons = []
    for i in ids:
        polygons.append(dzl[i].string_poly)
    return polygons


def join_paths(p1: str, p2: str) -> str:
    pl1 = destringify_points(p1)
    pl2 = destringify_points(p2)
    return stringify_points(pl1 + pl2[1:])


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
    return pp.getPath(), pp.getCost()


def calculate_path(pa, pb, r, dzl, ids):
    o_path, o_cost = get_detour(pa, pb, r, get_str_polygons_from_dzl(dzl, ids))

    if point_to_point(pa, pb) < 4 * r:
        n_polygons, s_polygons = cut_polygons(pa, pb, get_polygons_from_dzl(dzl, ids))
        n_path, n_cost = get_detour(pa, pb, r, stringify_polygons(n_polygons))
        s_path, s_cost = get_detour(pb, pa, r, stringify_polygons(s_polygons))

        if n_cost + s_cost < o_cost:
            return n_cost + s_cost, join_paths(n_path, s_path)

        return o_cost, o_path

    return o_cost, o_path
