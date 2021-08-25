class EdgeVertex:

    def __init__(self, a: int, b: int):
        if a < b:
            a, b = b, a
        self.name = f'{a}/{b}'
        self.a = a
        self.b = b

