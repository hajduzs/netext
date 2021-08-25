from ctypes import *

lib = cdll.LoadLibrary('src/geometry/pathfinder/siglib.so')


class PathPlanner(c_void_p):

    def __init__(self):
        # Argument types
        lib.PP_addDangerZone.argtypes = [c_void_p, c_char_p]
        lib.PP_setDangerZones.argtypes = [c_void_p, POINTER(c_int), c_int]
        lib.PP_calculatePath.argtypes = [c_void_p]
        lib.PP_getPath.argtypes = [c_void_p]
        lib.PP_getCost.argtypes = [c_void_p]
        lib.PP_getEpsilon.argtypes = [c_void_p]
        lib.PP_setR.argtypes = [c_void_p, c_float]
        lib.PP_setStartPoint.argtypes = [c_void_p, c_float, c_float]
        lib.PP_setEndPoint.argtypes = [c_void_p, c_float, c_float]

        # Return types (for functions that return something)
        lib.PP_getPath.restype = c_char_p
        lib.PP_getCost.restype = c_float
        lib.PP_getEpsilon.restype = c_float

        # Calling the original constructor from the lib
        self.obj = lib.PP_new()

    # polydata MUST be a string
    def addDangerZone(self, polydata: str):
        lib.PP_addDangerZone(self.obj, polydata.encode())

    # ids MUST be a list/tuple of integers
    def setDangerZones(self, ids):
        n = len(ids)
        p = (c_int * n)()
        for i in range(0, n):
            p[i] = c_int(ids[i])

        lib.PP_setDangerZones(self.obj, p, n)

    def calculatePath(self):
        lib.PP_calculatePath(self.obj)

    def getPath(self):
        ret = c_char_p(lib.PP_getPath(self.obj)).value.decode('utf-8').rstrip(f'  ')
        return ret

    def getCost(self):
        c = lib.PP_getCost(self.obj)
        return c

    def getEpsilon(self):
        e = lib.PP_getEpsilon(self.obj)
        return e

    def setR(self, R):
        lib.PP_setR(self.obj, c_float(R))

    def setStartPoint(self, x: float, y: float):
        lib.PP_setStartPoint(self.obj, c_float(x), c_float(y))

    def setEndPoint(self, x: float, y: float):
        lib.PP_setEndPoint(self.obj, c_float(x), c_float(y))

    def calculate_r_detour(self, pi, pg, ids):
        self.setStartPoint(pi[0], pi[1])
        self.setEndPoint(pg[0], pg[1])
        self.setDangerZones(ids)
        self.calculatePath()
