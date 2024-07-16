import numpy as np

import lib.common_curses
from collections import defaultdict, Counter
from itertools import product

from lib.bitmap import BitMap
from lib.globals import ROWS, COLS, WORDLIST
from lib.utils import rand_letters, options


class Grid(list):
    def __init__(self, chars=None):
        if chars is None:
            chars = ''.join(rand_letters(ROWS * COLS))
        super().__init__(list(chars[i::COLS]) for i in range(ROWS))

        # precomp for get_path, {(i, j, char): [(x, y), (x, y)...]}
        neighbor_lookup = defaultdict(list)
        for i, row in enumerate(self):
            for j, c in enumerate(row):
                neighbor_lookup[(None, None, c)].append((i, j))
                for i2, j2 in options(i, j):
                    neighbor_lookup[(i, j, self[i2][j2])].append((i2, j2))
        self.nl = dict(neighbor_lookup)

        # temp bitmap
        temp_bitmap = BitMap([(r, c) for r, c in product(range(ROWS), range(COLS))])

        # find paths for each word
        word_paths_list = WORDLIST.map(
            lambda _: [(_, _2, temp_bitmap.pack(_2)) for _2 in self.get_paths(_)]
        ).flatten()

        # remove duplicates
        word_paths_list = word_paths_list.unique(key=lambda _: _[2])

        # remove all paths that are subpaths
        subpaths = set()
        for (_, _, b1), (_, _, b2) in product(word_paths_list, word_paths_list):
            if (b1 != b2) and b1 | b2 == max(b1, b2):
                subpaths.add(b2 if b1.bit_count() > b2.bit_count() else b1)
        word_paths_list = word_paths_list.nfilter(lambda _: _[2] in subpaths)

        # create the real bit map, ordered by sparsity (lsb = most sparse)
        c = Counter()
        for (_, path, _) in word_paths_list:
            c.update(path)
        self.bitmap = BitMap(c.cast(list).sorted(lambda _: _[1]).map(lambda _: _[0]))

        # write all valid paths
        word_lookup = {}
        valid_bits = []
        for (word, path, _) in word_paths_list:
            bits = self.bitmap.pack(path)
            valid_bits.append(bits)
            word_lookup[bits] = word

        self.valid_bits = np.array(valid_bits.sorted(lambda _: -_.bit_count()))
        self.bits_ranking = list(self.valid_bits).enumerate().cast(dict).reverse()
        self.word_lookup = word_lookup

        # lookup by cell (i.e. cl[0] = entries where bit 0 is 1)
        cl = []
        for i in range(ROWS * COLS):
            cl.append(self.valid_bits[self.valid_bits & (1 << i) != 0])
        self.cell_lookup = cl

        # check that solution exists
        if np.bitwise_or.reduce(self.valid_bits).bit_count() != ROWS * COLS:
            raise RuntimeError('no solution for this puzzle')

        # score upper bounds for n-rounds
        ubs = [0]
        i = ROWS * COLS
        for bits in self.valid_bits:
            n = bits.bit_count()
            ubs.append(n * min(i, n))
            i -= n
            i = max(0, i)
        c = 0
        for i, v in enumerate(ubs):
            ubs[i] = c + v
            c += v
        for i, v in enumerate(ubs):
            if i == 0:
                continue
            ubs[i] /= i
            ubs[i] *= 10
        self.ubs = ubs

    def get_word(self, bits):
        if bits in self.word_lookup:
            return self.word_lookup[bits]
        path = self.bitmap.unpack(bits)
        return ''.join([self[i][j] for i, j in path])

    def get_bits(self, word):
        paths = self.get_paths(word)
        return [self.bitmap.pack(path) for path in paths]

    def get_paths(self, word, loc=(None, None), visited=None):
        if visited is None:
            visited = set()
        if len(word) == 0:
            return [[]]
        c0, *word = word
        nl = self.nl.get(loc + (c0,), [])
        paths = []
        for nloc in nl:
            if nloc in visited:
                continue
            visited.add(nloc)
            paths.extend([[nloc] + _ for _ in self.get_paths(word, nloc, visited)])
            visited.remove(nloc)

        return paths

