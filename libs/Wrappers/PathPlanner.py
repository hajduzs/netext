from Utilities.Logging import log
from ctypes import *

lib = cdll.LoadLibrary('libs/siglib.so')


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
    def addDangerZone(self, polydata):
        lib.PP_addDangerZone(self.obj, polydata.encode())
        #log("Added Danger Zone: [ {} ]\n".format(polydata), "PATH_PLANNER")

    # ids MUST be a list/tuple of integers
    def setDangerZones(self, ids):
        n = len(ids)
        p = (c_int*n)()
        for i in range(0, n):
                p[i] = c_int(ids[i])

        lib.PP_setDangerZones(self.obj, p, n)
        #log("Set Danger Zones:  {} \n".format(ids), "PATH_PLANNER")

    def calculatePath(self):
        lib.PP_calculatePath(self.obj)
        #log("Called calculatepath\n", "PATH_PLANNER")

    def getPath(self):
        ret = c_char_p(lib.PP_getPath(self.obj)).value.decode('utf-8').rstrip("  \n")
        #log("Called getPath. path: [ {} ]\n".format(ret), "PATH_PLANNER")
        return ret

    def getCost(self):
        c = lib.PP_getCost(self.obj)
        #log("Called getCost. cost: [ {} ]\n".format(c), "PATH_PLANNER")
        return c

    def getEpsilon(self):
        e = lib.PP_getEpsilon(self.obj)
        #log("Called getEpsilon. eps: [ {} ]\n".format(e), "PATH_PLANNER")
        return e

    def setR(self, R):
        lib.PP_setR(self.obj, c_float(R))
        #log("Set R: {}\n".format(R), "PATH_PLANNER")

    def setStartPoint(self, x, y):
        lib.PP_setStartPoint(self.obj, c_float(x), c_float(y))
        #log("Set starting point: ({},{})\n".format(x, y), "PATH_PLANNER")
    
    def setEndPoint(self, x, y):
        lib.PP_setEndPoint(self.obj, c_float(x), c_float(y))
        #log("Set ending point: ({},{})\n".format(x, y), "PATH_PLANNER")

    def calculate_r_detour(self, pi, pg, ids):
        self.setStartPoint(pi[0], pi[1])
        self.setEndPoint(pg[0], pg[1])
        self.setDangerZones(ids)
        self.calculatePath()
