"""Module containing the custom timer context manager to log running time more easily"""

import time
from src.measurement.output import OutPut


class timer:
    """timer context manager for algorithm and other code runtime measurement.
    uses OutPut class automatically for time logging."""
    def __init__(self, name: str, logging=True):
        """Initializes timing context with a name. Set 'logging' to false if
        time need not to be logged (nor produced in output statistics)"""
        self._name = name
        self._log = logging
        self._start_time = None

    def __enter__(self):
        self._start_time = time.time()

    def __exit__(self, exc_type, exc_value, traceback):
        passed = time.time() - self._start_time
        OutPut.data(f'time_{self._name}', passed)
        OutPut.print(f'Timed {self._name} took {passed}')
        # if exc_type is not None:
        #     print("{0} with value {1} caught\nTraceback: {2}".format(exc_type, exc_value, traceback))


""" Code used a long long time ago.. 
class Timeit(object):
    instance = None
    latest_time = None
    latest_msg = None

    @staticmethod
    def get_instance():
        if Timeit.instance is None:
            Timeit.instance = Timeit()
        return Timeit.instance

    @staticmethod
    def init(msg=None):
        if msg is None:
            msg = "-"
        Timeit.latest_msg = msg
        Timeit.latest_time = time.time()

    @staticmethod
    def time(msg: str):
        passed = time.time() - Timeit.latest_time
        print(f'FROM: {Timeit.latest_msg} TO: {msg} : {passed}')
        Timeit.latest_msg = msg
        Timeit.latest_time = time.time()
        return passed
"""