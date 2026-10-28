"""Measure both problems and save the numbers and figures used in the README.

    python benchmark.py
"""
from __future__ import annotations

import json
import random
import statistics as st
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

from search import puzzle, snake  # noqa: E402

ROOT = Path(__file__).resolve().parent
MEDIA = ROOT / "media"


def bench_puzzle(n=100, seed=1):
    rng = random.Random(seed)
    starts = [puzzle.random_state(rng) for _ in range(n)]
    out = {}
    optimal = {}
    for method in ("astar", "greedy"):
        for h in ("manhattan", "misplaced"):
            moves, expanded, secs = [], [], []
            for i, s in enumerate(starts):
                t = time.perf_counter()
                r = puzzle.solve(s, method, h)
                secs.append(time.perf_counter() - t)
                moves.append(r.moves)
                expanded.append(r.expanded)
                if method == "astar" and h == "manhattan":
                    optimal[i] = r.moves
            out[f"{method}-{h}"] = {"moves": moves, "expanded": expanded, "secs": secs}
    table = {}
    for k, v in out.items():
        table[k] = {
            "mean_moves": round(st.mean(v["moves"]), 2),
            "optimal_rate": round(sum(m == optimal[i] for i, m in enumerate(v["moves"])) / n, 3),
            "mean_expanded": round(st.mean(v["expanded"]), 1),
            "median_ms": round(1000 * st.median(v["secs"]), 2),
        }
    return table


def bench_snake(n=200):
    table = {}
    for c in ("greedy", "astar"):
        games = [snake.play(c, seed) for seed in range(n)]
        scores = [g.score for g in games]
        table[c] = {
            "mean_food": round(st.mean(scores), 2),
            "median_food": st.median(scores),
            "max_food": max(scores),
            "died_before_5_food": round(sum(s < 5 for s in scores) / n, 3),
        }
    return table


def plot_puzzle(table):
    keys = list(table)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    ax[0].bar(keys, [table[k]["mean_expanded"] for k in keys], color=["#2a7ab9", "#7fb3d5", "#e4572e", "#f2a07b"])
    ax[0].set_yscale("log")
    ax[0].set_title("Nodes expanded (mean, log scale)")
    ax[1].bar(keys, [table[k]["mean_moves"] for k in keys], color=["#2a7ab9", "#7fb3d5", "#e4572e", "#f2a07b"])
    ax[1].set_title("Solution length in moves (mean)")
    for a in ax:
        a.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(MEDIA / "puzzle_benchmark.png", dpi=120)
    plt.close(fig)


def snake_gif(seed=3, cell=18, max_frames=400):
    g = snake.Game(seed=seed)
    frames = []
    while g.alive and len(frames) < max_frames:
        im = Image.new("RGB", (g.width * cell, g.height * cell), (12, 18, 28))
        d = ImageDraw.Draw(im)
        for x, y in g.hurdles:
            d.rectangle([x * cell, y * cell, (x + 1) * cell - 1, (y + 1) * cell - 1], fill=(60, 90, 200))
        fx, fy = g.food
        d.ellipse([fx * cell + 2, fy * cell + 2, (fx + 1) * cell - 3, (fy + 1) * cell - 3], fill=(80, 200, 110))
        path = snake.astar_path(g, g.snake[0], g.food, g.snake[:-1]) or []
        for x, y in path[1:-1]:
            d.rectangle([x * cell + 7, y * cell + 7, x * cell + 10, y * cell + 10], fill=(110, 110, 130))
        for i, (x, y) in enumerate(g.snake):
            col = (255, 140, 60) if i == 0 else (230, 110, 50)
            d.rectangle([x * cell + 1, y * cell + 1, (x + 1) * cell - 2, (y + 1) * cell - 2], fill=col)
        frames.append(im)
        g.step(snake.astar_move(g))
    frames[0].save(MEDIA / "snake_astar.gif", save_all=True, append_images=frames[1:], duration=60, loop=0)
    return g.score


if __name__ == "__main__":
    MEDIA.mkdir(exist_ok=True)
    p = bench_puzzle()
    s = bench_snake()
    plot_puzzle(p)
    gif_score = snake_gif()
    json.dump({"puzzle": p, "snake": s, "gif_score": gif_score}, open(MEDIA / "metrics.json", "w"), indent=2)
    print(json.dumps({"puzzle": p, "snake": s}, indent=2))
