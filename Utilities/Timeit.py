import time


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
        if msg is not None:
            Timeit.latest_msg = msg
        Timeit.latest_time = time.time()


    @staticmethod
    def time(msg: str):
        passed = time.time() - Timeit.latest_time
        print(f'FROM: {Timeit.latest_msg} TO: {msg} : {passed}')
        Timeit.latest_msg = msg
        Timeit.latest_time = time.time()
        return passed

