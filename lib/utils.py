import numpy as np

from lib.globals import ROWS, COLS


def rand_letters(n=1):
    raw_freq = {
        "a": 8.167,
        "b": 1.492,
        "c": 2.782,
        "d": 4.253,
        "e": 12.702,
        "f": 2.228,
        "g": 2.015,
        "h": 6.094,
        "i": 6.966,
        "j": 0.153,
        "k": 0.772,
        "l": 4.025,
        "m": 2.406,
        "n": 6.749,
        "o": 7.507,
        "p": 1.929,
        "q": 0.095,
        "r": 5.987,
        "s": 6.327,
        "t": 9.056,
        "u": 2.758,
        "v": 0.978,
        "w": 2.360,
        "x": 0.150,
        "y": 1.974,
        "z": 0.074
    }
    raw_freq = {k.upper(): v for k, v in raw_freq.items()}

    p = np.array([v for k, v in raw_freq.items()])
    p /= np.sum(p)

    return np.random.choice(list(raw_freq.keys()), size=n, p=p)


def options(i: int, j: int):
    for m in [-1, 0, 1]:
        for n in [-1, 0, 1]:
            if m == 0 and n == 0:
                continue
            i2 = m + i
            j2 = n + j
            if not 0 <= i2 < ROWS:
                continue
            if not 0 <= j2 < COLS:
                continue
            yield i2, j2


def to_idx(r, c):
    return r * COLS + c


def fr_idx(i):
    return i // COLS, i % COLS


