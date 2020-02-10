import subprocess
import os
import time
from Utilities.Logging import log

from ctypes import *
lib = cdll.LoadLibrary('libs/libpartition.so')

lib.divide.argtypes = [c_int, c_float, c_char_p, c_char_p]
lib.divide.restype = c_int


def get_division_from_json(R, jsname, filepath):

    CR = 60

    if not os.path.exists(filepath):

        log("Calculate division of [{}], w: [{}]\n".format(jsname, filepath), "PLANAR_DIV")
        start = time.time()

        result = lib.divide(60, R, jsname.encode(), filepath.encode())

        log("Time needed: {}\n".format(time.time()-start), "PLANAR_DIV")

    with open(filepath) as f:
        faces = f.readlines()

    if len(faces) == 0:
        return None

    for f in faces:
        f = f.rstrip("  \n")

    return faces
