import subprocess
import os
import time
from Utilities.Logging import log


def get_division_from_json(R, jsname, filepath):
    arguments = [str(R), jsname, filepath]

    if os.path.exists(filepath):
        os.remove(filepath)

    process = ["libs/dangerzone"]
    process.extend(arguments)

    log("Calculate division of [{}], w: [{}]\n".format(jsname, filepath), "PLANAR_DIV")
    start = time.time()

    planar_div_executable = subprocess.Popen(process)
    planar_div_executable.wait()

    log("Time needed: {}\n".format(time.time()-start), "PLANAR_DIV")

    with open(filepath) as f:
        faces = f.readlines()

    for f in faces:
        f = f.rstrip("  \n")

    return faces
