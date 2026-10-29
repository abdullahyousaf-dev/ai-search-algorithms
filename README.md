# AI Search Algorithms: 8-Puzzle and Snake

A* and greedy best-first search on two problems from my MS AI course (RIME, NUST,
2023), rebuilt in Python with tests and measured results.

[![tests](https://github.com/abdullahyousaf-dev/ai-search-algorithms/actions/workflows/tests.yml/badge.svg)](https://github.com/abdullahyousaf-dev/ai-search-algorithms/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

![A* snake](media/snake_astar.gif)

*The orange snake plans a path to the food with A\* (grey dots), treating hurdles
(blue) and its own body as walls.*

## Highlights

- **A\* + Manhattan** solves all 100 test boards optimally, expanding **~10× fewer nodes** than the misplaced-tiles heuristic
- **A\* Snake eats 61 food per game on average** vs 2 for the original greedy controller
- Heuristics, solvability check and controllers covered by 7 tests

## Results

**8-puzzle**, 100 random solvable boards (60-move random walks from the goal):

| Method | Mean moves | Optimal | Mean nodes expanded | Median time |
|---|---|---|---|---|
| A* + Manhattan | 21.96 | 100% | 1,618 | 5.9 ms |
| A* + misplaced | 21.96 | 100% | 15,563 | 70.3 ms |
| Greedy + Manhattan | 43.96 | 5% | 287 | 2.3 ms |
| Greedy + misplaced | 50.84 | 2% | 830 | 3.9 ms |

![8-puzzle benchmark](media/puzzle_benchmark.png)

**Snake**, 200 games per controller, 20×20 board, 5 hurdles, 2,000-step limit:

| Controller | Mean food | Median food | Best game | Died before 5 food |
|---|---|---|---|---|
| Greedy (original) | 2.07 | 0 | 14 | 79% |
| A* | 61.26 | 64.5 | 108 | 0% |

## How it works

**8-puzzle.** Ported from my C++ assignment: same goal state (blank top-left, tiles
1–8 in order) and the same two heuristics, misplaced tiles and Manhattan distance.
Both are admissible, so A* returns the shortest solution with either. Greedy
best-first orders the frontier by the heuristic alone: fewer nodes, no optimality.
Manhattan is the stronger heuristic (never smaller than misplaced), which cuts A*'s
work by about 10× for the same answer.

**Snake.** The course project was a tkinter game whose AI closed the x gap to the
food, then the y gap; that controller is kept as `greedy`. The new `astar` controller:

1. Runs A* from the head to the food, with hurdles and body cells as walls (the tail
   cell counts as free because it moves away on the next step).
2. If no path exists, follows its own tail to stay alive until one opens.
3. If that fails too, takes any move that is safe right now.

## Quick start

```bash
pip install -r requirements.txt
python -m pytest -q        # 7 tests
python benchmark.py        # rebuilds the tables, plot and GIF in media/
```

```python
from search import puzzle
r = puzzle.solve((1, 2, 5, 3, 4, 0, 6, 7, 8), "astar", "manhattan")
print(r.moves, r.expanded)
```

## Project structure

```
search/puzzle.py   8-puzzle state, heuristics, solvability check, A* / greedy search
search/snake.py    headless Snake, greedy and A* controllers
benchmark.py       experiments behind the tables above
tests/             optimality, valid paths, A* beats greedy
media/             GIF, plot and metrics.json
```

## Design notes

- Solvability is checked up front with inversion parity, so unsolvable boards return
  immediately instead of exhausting the search space.
- The greedy snake mostly dies early by turning back into its own neck or walking
  into a hurdle; the A* version never dies before 5 food in 200 games.

## Limitations & next steps

- The A* snake can still trap itself late in long games; a Hamiltonian-cycle fallback would fix that
- Next: IDA* for the 15-puzzle, where plain A* runs out of memory

## License

MIT. See [LICENSE](LICENSE).

**Keywords:** A* search, greedy best-first search, heuristics, 8-puzzle, pathfinding,
Snake game AI, Python.
