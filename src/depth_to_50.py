"""How many QAOA layers does each puzzle need to reach 50% success?

Run from the repo root, one puzzle size per process:
    python -m src.depth_to_50 6

It continues the layer-by-layer growth that tune() uses (INTERP start, COBYLA on the
AVERAGE cost, never the answer) from the saved p = 10 angles in results/angles.json,
adding one layer at a time until P(correct) >= 50%, the layer cap, or the time limit.
Every layer is saved to results/depth_to_50_N<n>.json as it finishes, so a run that is
stopped early still records how far it got.
"""

import json
import sys
import time

import numpy as np
from scipy.optimize import minimize

from src.insanity import BONUS_SEEDS, ValidSpaceQAOA, _interp, make_puzzle

CUBES = [["GR", "BR", "GY"], ["GY", "RB", "BY"], ["BR", "RG", "RY"], ["YR", "RG", "BG"]]
TARGET = 0.5
P_CAP = 60
MAXITER = {4: 500, 5: 400, 6: 300, 7: 150, 8: 60}    # same optimizer budgets as tune_angles.py
TIME_LIMIT = {4: 3600, 5: 3600, 6: 3600, 7: 7200, 8: 7200}   # seconds


def main(n):
    cubes = CUBES if n == 4 else make_puzzle(n, BONUS_SEEDS[n])
    sim = ValidSpaceQAOA(cubes)
    saved = json.load(open("results/angles.json"))[str(n)]
    rows = [dict(p=r["p"], E=r["E"], P=r["P"], g=r["g"], b=r["b"]) for r in saved]
    gam, bet = rows[-1]["g"], rows[-1]["b"]
    path = f"results/depth_to_50_N{n}.json"
    start = time.perf_counter()
    while rows[-1]["P"] < TARGET and len(rows) < P_CAP and time.perf_counter() - start < TIME_LIMIT[n]:
        p = len(rows) + 1
        x0 = np.concatenate([_interp(gam), _interp(bet)])
        r = minimize(lambda x: sim.stats(x[:p], x[p:])[0], x0, method="COBYLA",
                     options={"maxiter": MAXITER[n], "rhobeg": 0.1})
        gam, bet = list(r.x[:p]), list(r.x[p:])
        e, s = sim.stats(gam, bet)
        rows.append(dict(p=p, E=e, P=s, g=gam, b=bet))
        print(f"N={n} p={p:2d}: average cost {e:6.3f}, P(correct) {s:7.2%}  "
              f"({time.perf_counter() - start:.0f} s)", flush=True)
        save(path, n, rows, start)
    save(path, n, rows, start)
    reached = first_reaching(rows)
    print(f"N={n}: reached {TARGET:.0%} at p = {reached}" if reached else
          f"N={n}: stopped at p = {len(rows)} with P = {rows[-1]['P']:.2%}", flush=True)


def first_reaching(rows):
    return next((x["p"] for x in rows if x["P"] >= TARGET), None)


def save(path, n, rows, start):
    json.dump({"n": n, "target": TARGET, "reached_at_p": first_reaching(rows), "maxiter": MAXITER[n],
               "seconds": time.perf_counter() - start, "rows": rows}, open(path, "w"), indent=1)


if __name__ == "__main__":
    main(int(sys.argv[1]))
