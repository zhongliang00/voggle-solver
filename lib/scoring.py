from itertools import permutations


def _score(cover: list[int]):
    s = 0
    visited = 0
    for bits in cover:
        l = bits.bit_count()
        b = (bits - (visited & bits)).bit_count()
        s += l * b * 10
        visited |= bits
    return s / len(cover)


def best_score(cover: list[int]):
    best = 0
    best_permutation = None
    for permutation in permutations(cover):
        permutation: list[int]
        s = _score(permutation)
        if s > best:
            best = s
            best_permutation = permutation
    return best_permutation, best
