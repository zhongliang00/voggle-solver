import math

from lib.globals import ROWS, COLS
from lib.grid import Grid


# calculates the Best Case score
def score_bc(bc: list[int], visited: int, visits_left: int):
    # print('score_bc', bc, visited, visits_left)
    n = ROWS * COLS - visited.bit_count()
    s = 0
    for visit_no, bits in enumerate(bc):
        if visit_no >= visits_left:
            break
        b = min(n, bits.bit_count())
        n -= b
        s += bits.bit_count() * b * 10
    if n > 0:
        return -math.inf
    return s


# class to help track state when visiting/traversing the search space
class Visitor:
    ALL_VISITED = (1 << ROWS * COLS) - 1

    def __init__(self, grid: Grid, r: int):
        self.grid = grid
        self.max_visits = r
        self.bits_history = [0]
        self.bits_history_set = set()
        self.visited_history = [0]
        self.score_history = [0]

        # best case tracking
        self.bc = {_: None for _ in self.grid.valid_bits[:self.max_visits]}
        self.bc_history = {}
        # best case scenario
        self.bcs = score_bc(list(self.bc.keys()), self.visited, self.visits_left)

    @property
    def visited(self):
        return self.visited_history[-1]

    @property
    def score(self):
        return self.score_history[-1]

    @property
    def visit_count(self):
        return len(self.visited_history) - 1

    @property
    def visits_left(self):
        return self.max_visits - self.visit_count

    @property
    def covered(self):
        return ROWS * COLS - self.visited.bit_count() == 0

    @property
    def next_zero(self):
        x = self.ALL_VISITED - self.visited
        return (x & -x).bit_length() - 1

    def visited_before(self, bits: int):
        return int(bits) in self.bits_history_set

    def visit(self, bits: int):
        if self.visit_count >= self.max_visits:
            raise RuntimeError('reached max_visits')
        bits = int(bits)
        self.bits_history.append(bits)
        self.bits_history_set.add(bits)
        self.visited_history.append(self.visited | bits)
        broken = (self.visited_history[-1] - self.visited_history[-2]).bit_count()
        self.score_history.append(self.score_history[-1] + bits.bit_count() * broken * 10)

        if bits in self.bc:
            del self.bc[bits]
            self.bc_history[bits] = None
        self.bcs = score_bc(list(self.bc.keys()), self.visited, self.visits_left)

    def unvisit(self, bits: int):
        bits = int(bits)
        if bits != self.bits_history[-1]:
            raise RuntimeError('trying to unvisit unvisited bits')
        self.bits_history.pop()
        self.bits_history_set.remove(bits)
        self.visited_history.pop()
        self.score_history.pop()

        if bits in self.bc_history:
            del self.bc_history[bits]
            self.bc[bits] = None
        self.bcs = score_bc(list(self.bc.keys()), self.visited, self.visits_left)

    def __repr__(self):
        return f'<Visitor visited={self.visited}>'
