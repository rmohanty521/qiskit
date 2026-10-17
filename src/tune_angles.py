"""Tune QAOA angles for the bonus puzzles and save them to results/angles.json.

Run from the repo root:   python -m src.tune_angles
It takes about an hour on a laptop (N = 8 is the slow part), which is why the
notebook loads the saved angles by default (RETUNE = False).
"""

import json
import os
import time

from src.insanity import BONUS_SEEDS, ValidSpaceQAOA, make_puzzle, tune

CUBES = [["GR", "BR", "GY"], ["GY", "RB", "BY"], ["BR", "RG", "RY"], ["YR", "RG", "BG"]]
P_MAX = 10
MAXITER = {4: 500, 5: 400, 6: 300, 7: 150, 8: 60}   # fewer optimizer steps where each step is slow


def main(path="results/angles.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out, previous = {}, None
    if os.path.exists(path):                   # resume: keep every N already tuned to P_MAX layers
        out = {k: v for k, v in json.load(open(path)).items() if len(v) == P_MAX}
    for n in [4, 5, 6, 7, 8]:
        if str(n) in out:
            previous = out[str(n)]
            print(f"N = {n}: already tuned, kept")
            continue
        cubes = CUBES if n == 4 else make_puzzle(n, BONUS_SEEDS[n])
        start = time.perf_counter()
        print(f"N = {n}")
        previous = tune(ValidSpaceQAOA(cubes), P_MAX, MAXITER[n], previous)
        out[str(n)] = previous
        print(f"  {time.perf_counter() - start:.0f} s")
        with open(path, "w") as fh:
            json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
