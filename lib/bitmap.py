from lib.utils import bitwise_or_reduce


class BitMap:
    def __init__(self, items):
        # index to coords
        i2c = {i: v for i, v in enumerate(list(items))}
        self.i2c = i2c
        self.c2i = {v: k for k, v in i2c.items()}

        # bitmask to coords
        b2c = {1 << k: v for k, v in i2c.items()}
        self.b2c = b2c
        self.c2b = {v: k for k, v in b2c.items()}

    def pack(self, items):
        return bitwise_or_reduce([self.c2b[i] for i in items])

    def unpack(self, val):
        return [v for k, v in self.b2c.items() if val & k]

    def get_idx(self, coord):
        return self.c2i[coord]

    def get_coord(self, idx):
        return self.i2c[idx]
