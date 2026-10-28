"""8-puzzle solved with A* and greedy best-first search.

Ported from my C++ course assignment (MS RIME, NUST, 2023). Same goal state
(0 is the blank, top-left) and the same two heuristics.
"""
from __future__ import annotations

import heapq
import itertools
import random
from dataclasses import dataclass

N = 3
GOAL = tuple(range(N * N))  # (0, 1, 2, 3, 4, 5, 6, 7, 8)
_GOAL_POS = {tile: divmod(i, N) for i, tile in enumerate(GOAL)}


def misplaced(state: tuple) -> int:
    """Number of tiles (blank excluded) not in their goal cell."""
    return sum(1 for i, t in enumerate(state) if t != 0 and t != GOAL[i])


def manhattan(state: tuple) -> int:
    """Sum of row + column distances of every tile from its goal cell."""
    h = 0
    for i, t in enumerate(state):
        if t:
            r, c = divmod(i, N)
            gr, gc = _GOAL_POS[t]
            h += abs(r - gr) + abs(c - gc)
    return h


HEURISTICS = {"manhattan": manhattan, "misplaced": misplaced}


def neighbours(state: tuple):
    """Yield every state reachable by sliding one tile into the blank."""
    z = state.index(0)
    r, c = divmod(z, N)
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < N and 0 <= nc < N:
            j = nr * N + nc
            s = list(state)
            s[z], s[j] = s[j], s[z]
            yield tuple(s)


def is_solvable(state: tuple) -> bool:
    """On a 3x3 board a state can reach GOAL iff its inversion count is even."""
    tiles = [t for t in state if t]
    inv = sum(1 for a, b in itertools.combinations(tiles, 2) if a > b)
    return inv % 2 == 0


@dataclass
class Result:
    path: list  # states from start to goal, inclusive
    expanded: int  # nodes popped from the frontier and expanded

    @property
    def moves(self) -> int:
        return len(self.path) - 1


def solve(start: tuple, method: str = "astar", heuristic: str = "manhattan") -> Result | None:
    """A* orders the frontier by g + h, greedy best-first by h only."""
    if not is_solvable(start):
        return None
    h = HEURISTICS[heuristic]
    use_g = method == "astar"
    tie = itertools.count()
    frontier = [(h(start), next(tie), start)]
    parent = {start: None}
    g = {start: 0}
    closed = set()
    expanded = 0
    while frontier:
        _, _, s = heapq.heappop(frontier)
        if s in closed:
            continue
        if s == GOAL:
            path = []
            while s is not None:
                path.append(s)
                s = parent[s]
            return Result(path[::-1], expanded)
        closed.add(s)
        expanded += 1
        for nxt in neighbours(s):
            ng = g[s] + 1
            if nxt in closed or ng >= g.get(nxt, float("inf")):
                continue
            g[nxt] = ng
            parent[nxt] = s
            f = ng + h(nxt) if use_g else h(nxt)
            heapq.heappush(frontier, (f, next(tie), nxt))
    return None


def random_state(rng: random.Random, scramble: int = 60) -> tuple:
    """Random solvable state: a random walk from the goal."""
    s = GOAL
    prev = None
    for _ in range(scramble):
        options = [n for n in neighbours(s) if n != prev]
        prev, s = s, rng.choice(options)
    return s


def show(state: tuple) -> str:
    return "\n".join(" ".join(str(t) if t else "." for t in state[r * N:(r + 1) * N]) for r in range(N))
