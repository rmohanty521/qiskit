"""Time two classical solvers on the same puzzles, for a fair comparison with QAOA.

Run from the repo root:   python -m src.classical_timing
Saves results/classical_times.json.

* brute force: the starter's count_answers, which checks all 6^N choice tuples;
* graph method: list the front/back picks that are 2-factors (3^N candidates), then
  pair two that never use the same pair of a cube. This is the classical version of
  the same trick our encoding is built on.
Each time is the best of 5 runs.
"""

import itertools
import json
import time

from src.insanity import BONUS_SEEDS, count_answers, letters_of, make_puzzle

CUBES = [["GR", "BR", "GY"], ["GY", "RB", "BY"], ["BR", "RG", "RY"], ["YR", "RG", "BG"]]


def graph_method(cubes):
    """All (front/back, left/right) pick lists that solve the puzzle, via 2-factors."""
    colours = letters_of(cubes)

    def two_factor(picks):
        degree = dict.fromkeys(colours, 0)
        for cube, p in zip(cubes, picks):
            for ch in cube[p]:
                degree[ch] += 1
        return all(d == 2 for d in degree.values())

    factors = [p for p in itertools.product(range(3), repeat=len(cubes)) if two_factor(p)]
    return [(a, b) for a in factors for b in factors if all(x != y for x, y in zip(a, b))]


def best_time(f, *args, repeats=5):
    best = float("inf")
    for _ in range(repeats):
        start = time.perf_counter()
        f(*args)
        best = min(best, time.perf_counter() - start)
    return best


def main(path="results/classical_times.json"):
    out = []
    for n in range(4, 9):
        cubes = CUBES if n == 4 else make_puzzle(n, BONUS_SEEDS[n])
        assert count_answers(cubes) == len(graph_method(cubes)) == 2
        row = dict(n=n, brute_s=best_time(count_answers, cubes), graph_s=best_time(graph_method, cubes))
        print(f"N={n}: brute force {row['brute_s'] * 1000:8.1f} ms | graph method {row['graph_s'] * 1000:6.2f} ms")
        out.append(row)
    json.dump(out, open(path, "w"), indent=1)


if __name__ == "__main__":
    main()
