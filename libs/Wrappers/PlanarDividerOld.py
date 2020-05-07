import subprocess
import os
import time
import logging


def get_division_from_json(R, jsname, filepath):
    CR = 48

    arguments = [str(CR), str(R), jsname, filepath]

    if not os.path.exists(filepath):

        process = ["libs/partitioner.x"]
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
        for f in faces:
            f = f.rstrip("  \n")
        return faces

    logging.critical("No faces calculated. File not even generated.")
    return None
