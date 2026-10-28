"""Headless Snake on a grid with two AI controllers.

`greedy` is the controller from my original course project (tkinter game, 2023):
step along x toward the food, then along y. `astar` plans a shortest path to the
food that avoids hurdles and the snake's own body, and falls back to chasing its
tail when no safe path exists.
"""
from __future__ import annotations

import heapq
import itertools
import random
from dataclasses import dataclass, field

DIRS = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}


@dataclass
class Game:
    width: int = 20
    height: int = 20
    n_hurdles: int = 5
    seed: int = 0
    snake: list = field(default_factory=list)  # head first, (x, y) cells
    hurdles: set = field(default_factory=set)
    food: tuple = (0, 0)
    score: int = 0
    alive: bool = True
    steps: int = 0

    def __post_init__(self):
        self.rng = random.Random(self.seed)
        cx, cy = self.width // 2, self.height // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        while len(self.hurdles) < self.n_hurdles:
            c = self._random_free()
            if abs(c[0] - cx) > 3 or c[1] != cy:  # keep the start row clear
                self.hurdles.add(c)
        self.food = self._random_free()

    def _random_free(self):
        while True:
            c = (self.rng.randrange(self.width), self.rng.randrange(self.height))
            if c not in self.snake and c not in self.hurdles:
                return c

    def blocked(self, cell, body=None) -> bool:
        x, y = cell
        body = self.snake if body is None else body
        return not (0 <= x < self.width and 0 <= y < self.height) or cell in self.hurdles or cell in body

    def step(self, direction: str):
        if not self.alive:
            return
        dx, dy = DIRS[direction]
        hx, hy = self.snake[0]
        new = (hx + dx, hy + dy)
        grows = new == self.food
        body = self.snake if grows else self.snake[:-1]  # the tail moves away this step
        if self.blocked(new, body):
            self.alive = False
            return
        self.snake.insert(0, new)
        if grows:
            self.score += 1
            if len(self.snake) + len(self.hurdles) >= self.width * self.height:
                self.alive = False  # board full
                return
            self.food = self._random_free()
        else:
            self.snake.pop()
        self.steps += 1


def _direction(a, b) -> str:
    d = (b[0] - a[0], b[1] - a[1])
    return next(k for k, v in DIRS.items() if v == d)


def greedy_move(game: Game) -> str:
    """Original controller: close the x gap first, then the y gap."""
    (hx, hy), (fx, fy) = game.snake[0], game.food
    if hx < fx:
        return "Right"
    if hx > fx:
        return "Left"
    if hy < fy:
        return "Down"
    return "Up"


def astar_path(game: Game, start, goal, body) -> list | None:
    """Shortest 4-connected path from start to goal; body cells and hurdles are walls."""
    def h(c):
        return abs(c[0] - goal[0]) + abs(c[1] - goal[1])

    tie = itertools.count()
    frontier = [(h(start), next(tie), start)]
    parent = {start: None}
    g = {start: 0}
    while frontier:
        _, _, cur = heapq.heappop(frontier)
        if cur == goal:
            path = []
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            return path[::-1]
        for dx, dy in DIRS.values():
            nxt = (cur[0] + dx, cur[1] + dy)
            if nxt != goal and game.blocked(nxt, body):
                continue
            ng = g[cur] + 1
            if ng < g.get(nxt, 1 << 30):
                g[nxt] = ng
                parent[nxt] = cur
                heapq.heappush(frontier, (ng + h(nxt), next(tie), nxt))
    return None


def astar_move(game: Game) -> str:
    head = game.snake[0]
    body = game.snake[:-1]  # the tail cell frees up as the snake moves
    path = astar_path(game, head, game.food, body)
    if path and len(path) > 1:
        return _direction(head, path[1])
    # No route to the food: follow the tail to buy time until one opens up.
    path = astar_path(game, head, game.snake[-1], game.snake[:-1])
    if path and len(path) > 1:
        return _direction(head, path[1])
    # Last resort: any move that does not kill the snake right now.
    for d, (dx, dy) in DIRS.items():
        if not game.blocked((head[0] + dx, head[1] + dy), body):
            return d
    return "Up"


CONTROLLERS = {"greedy": greedy_move, "astar": astar_move}


def play(controller: str, seed: int, max_steps: int = 2000, **kw) -> Game:
    game = Game(seed=seed, **kw)
    move = CONTROLLERS[controller]
    while game.alive and game.steps < max_steps:
        game.step(move(game))
    return game
