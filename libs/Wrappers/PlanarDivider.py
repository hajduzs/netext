import subprocess
import os
import time
from Utilities.Logging import log

from ctypes import *
lib = cdll.LoadLibrary('libs/libpartition.so')

lib.divide.argtypes = [c_int, c_float, c_char_p, c_char_p]
lib.divide.restype = c_int


def get_division_from_json(R, jsname, filepath):

    CR = 48 # circle resoulution
    result = 0

    if not os.path.exists(filepath):

        log("Calculate division of [{}], w: [{}]\n".format(jsname, filepath), "PLANAR_DIV")
        start = time.time()

        result = lib.divide(CR, R, jsname.encode(), filepath.encode())

        log("Time needed: {} result: {}\n".format(time.time()-start, result), "PLANAR_DIV")

    if result != 0:
        return None

    with open(filepath) as f:
        faces = f.readlines()

    for f in faces:
        f = f.rstrip("  \n")

    return faces
