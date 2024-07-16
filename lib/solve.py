import lib.common_curses
from lib.grid import Grid
from lib.scoring import best_score
from lib.visitor import Visitor


# solves the voggle puzzle, guaranteed to return the optimal solution as covers[0]
# does not guarantee to enumerate all covers
def solve(g: Grid):
    covers = []
    cmax = [0]

    def step(v: Visitor):
        if v.covered:
            if v.visits_left == 0:
                cover = list(v.bits_history[1:])
                cover, s = best_score(cover)
                covers.append(([g.get_word(_) for _ in cover], s))
                cmax[0] = max(s, cmax[0])
            return
        if v.bcs + v.score < cmax[0] * v.max_visits:
            # TAB = '\t'
            # print(f'{TAB*v.visit_count}exiting', v.bcs, v.score, cmax[0], v.max_visits)
            return

        for bits in g.cell_lookup[v.next_zero]:
            if v.visited_before(bits):
                continue

            v.visit(bits)
            # TAB = '\t'
            # print(f"{TAB*v.visit_count}{v.next_zero, v.bcs, v.score, bits, g.get_word(bits)}")
            step(v)
            v.unvisit(bits)

    r = 1
    while True:
        step(Visitor(g, r))
        r += 1
        if cmax[0] > g.ubs[r]:
            break

    return covers.sorted(key=lambda _: -_[1])