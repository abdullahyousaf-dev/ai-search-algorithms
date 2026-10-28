import random

from search import puzzle, snake


def test_heuristics_zero_at_goal():
    assert puzzle.manhattan(puzzle.GOAL) == 0
    assert puzzle.misplaced(puzzle.GOAL) == 0


def test_manhattan_dominates_misplaced():
    rng = random.Random(0)
    for _ in range(50):
        s = puzzle.random_state(rng)
        assert puzzle.manhattan(s) >= puzzle.misplaced(s)


def test_unsolvable_detected():
    s = (0, 2, 1, 3, 4, 5, 6, 7, 8)  # one swap = odd parity
    assert not puzzle.is_solvable(s)
    assert puzzle.solve(s) is None


def test_astar_is_optimal_and_path_valid():
    rng = random.Random(1)
    for _ in range(20):
        s = puzzle.random_state(rng)
        a = puzzle.solve(s, "astar", "manhattan")
        b = puzzle.solve(s, "astar", "misplaced")
        assert a.moves == b.moves  # both heuristics are admissible
        assert a.path[0] == s and a.path[-1] == puzzle.GOAL
        for x, y in zip(a.path, a.path[1:]):
            assert y in set(puzzle.neighbours(x))


def test_greedy_never_shorter_than_astar():
    rng = random.Random(2)
    for _ in range(20):
        s = puzzle.random_state(rng)
        assert puzzle.solve(s, "greedy").moves >= puzzle.solve(s, "astar").moves


def test_snake_astar_path_avoids_walls():
    g = snake.Game(seed=4)
    path = snake.astar_path(g, g.snake[0], g.food, g.snake[:-1])
    assert path[0] == g.snake[0] and path[-1] == g.food
    for c in path[1:-1]:
        assert not g.blocked(c, g.snake[:-1])


def test_astar_snake_beats_greedy():
    a = sum(snake.play("astar", s).score for s in range(30))
    g = sum(snake.play("greedy", s).score for s in range(30))
    assert a > g
