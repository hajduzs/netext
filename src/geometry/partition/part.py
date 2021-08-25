import subprocess
import os
import time
import logging
import json

from src.geometry.structures.Polygon import Polygon


def get_division_from_json(R, js_dump, filepath="tmp_faces.txt"):
    CR = 48

    jsname = "tmp_json.js"
    with open(jsname, "w") as f:
        f.write(json.dumps(js_dump))

    arguments = [str(CR), str(R), jsname, filepath]

    if not os.path.exists(filepath):

        process = ["src/geometry/partition/partitioner.x"]
        process.extend(arguments)

        logging.debug(f'Calculate division of [{jsname}], w: [{filepath}]')
        start = time.time()

        planar_div_executable = subprocess.Popen(process)
        planar_div_executable.wait()

        logging.info(f'Time needed: {time.time() - start}')

    if os.path.exists(filepath):
        with open(filepath) as f:
            faces = f.readlines()

        if len(faces) == 0:
            logging.critical('No faces calculated. Degenerate segment.')
            return None

        if len(faces) != int(faces[0]):
            logging.critical('Not all faces in file. Segfault while printing.')
            return None

        del faces[0]
        ret_poly_list = []
        for f in faces:
            ret_poly_list.append(Polygon.from_string(f.rstrip("  \n")))
        return ret_poly_list

    logging.critical("No faces calculated. File not even generated.")
    return None