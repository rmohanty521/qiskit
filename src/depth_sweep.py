"""Layers to 50% success on MORE puzzles per size, to see the trend through puzzle-to-puzzle luck.

Run from the repo root, one puzzle per process:
    python -m src.depth_sweep 6 20        # N = 6, make_puzzle seed 20

Same procedure as the main puzzles: tune() grows p = 1..10 (INTERP, plus the N - 1 angles
from results/angles.json as a second start, average-cost objective, never the answer),
then layers are added one at a time until P(correct) >= 50%, the cap, or the time limit.
Saves results/sweep/N<n>_seed<seed>.json after every layer.
"""

import json
import os
import sys
import time

import numpy as np
from scipy.optimize import minimize

from src.depth_to_50 import MAXITER, P_CAP, TARGET, TIME_LIMIT
from src.insanity import ValidSpaceQAOA, _interp, count_answers, make_puzzle, tune


def main(n, seed):
    cubes = make_puzzle(n, seed)
    assert count_answers(cubes) == 2, "use a seed with exactly one tower"
    sim = ValidSpaceQAOA(cubes)
    previous = json.load(open("results/angles.json")).get(str(n - 1))
    os.makedirs("results/sweep", exist_ok=True)
    path = f"results/sweep/N{n}_seed{seed}.json"
    start = time.perf_counter()

    def save():
        reached = next((x["p"] for x in rows if x["P"] >= TARGET), None)
        json.dump({"n": n, "seed": seed, "target": TARGET, "reached_at_p": reached,
                   "seconds": time.perf_counter() - start, "rows": rows}, open(path, "w"), indent=1)
        return reached

    rows = tune(sim, 10, MAXITER[n], previous, log=lambda s: print(f"N={n} seed={seed}{s}", flush=True))
    gam, bet = rows[-1]["g"], rows[-1]["b"]
    save()
    while rows[-1]["P"] < TARGET and len(rows) < P_CAP and time.perf_counter() - start < TIME_LIMIT[n]:
        p = len(rows) + 1
        x0 = np.concatenate([_interp(gam), _interp(bet)])
        r = minimize(lambda x: sim.stats(x[:p], x[p:])[0], x0, method="COBYLA",
                     options={"maxiter": MAXITER[n], "rhobeg": 0.1})
        gam, bet = list(r.x[:p]), list(r.x[p:])
        e, s = sim.stats(gam, bet)
        rows.append(dict(p=p, E=e, P=s, g=gam, b=bet))
        print(f"N={n} seed={seed} p={p:2d}: average cost {e:6.3f}, P(correct) {s:7.2%}  "
              f"({time.perf_counter() - start:.0f} s)", flush=True)
        save()
    reached = save()
    print(f"N={n} seed={seed}: reached {TARGET:.0%} at p = {reached}" if reached else
          f"N={n} seed={seed}: stopped at p = {len(rows)} with P = {rows[-1]['P']:.2%}", flush=True)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
