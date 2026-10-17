# Handoff: where this work stands (paused 10:15 AM ET, Sat Oct 17 2026)

Deadline: **3:00 PM ET today**. Don't push after that.

Challenge: https://github.com/qBraid/uconn-fall-fest-2026-challenge. Read its `GRADING.md` (deliverables and rubric) and `AGENTS.md` (rules for AI agents).

## The approach

- **Compact encoding:** 3 qubits per cube hold a code 0–5 for the cube's 6 valid choices (front/back pair, left/right pair) = `itertools.permutations(range(3), 2)`. Qubit `3c` is cube c's lowest bit. Qiskit puts qubit 0 RIGHTMOST in count keys. Codes 6 and 7 are unused. N=4 needs 12 qubits instead of the starter's 24.
- **Cost:** for each of the two side pairs and each colour, `(degree - 2)^2`. It is zero exactly when both pick-sets are 2-factors, which is exactly a solved tower.
- **Hamiltonian:** built from code projectors, so it has higher-order Z terms (up to 6 Z's for N=4).
- **Constrained QAOA:**
  - Start: equal superposition of the 6 valid codes per cube (`prep_cube`: RY on bit 2, open-controlled H on bit 1, H on bit 0).
  - Mixer per cube: `exp(-i β |u><u|)`. It never leaves valid codes, so no penalty terms are needed.
  - Cost layer: CNOT ladder + RZ per Z string.
- **Tuning:** minimize the expected cost. This doesn't use knowledge of the answer. Layers grow one at a time with INTERP initialisation, and angles transfer from N-1. Tuning uses `ValidSpaceQAOA`, an exact simulator over the 6^N valid states.

## Verified so far

- H matches the classical cost on all 1,296 valid states (gap 0).
- Exactly 2 zero-cost assignments, and both pass `solves(tower_of(...))`.
- `ValidSpaceQAOA` matches Qiskit `Statevector` (about 1e-16).
- 0 invalid shots in every Aer run.

## Results so far (local Aer, NOT yet SV1)

See `results/results.md`. N=4, compact encoding, 1,000 shots:

| p (layers) | Two-qubit gates | P(correct tower) |
|---|---|---|
| 1 | 550 | 1.1% |
| 4 | 2,188 | 8.5% |
| 8 | 4,372 | 39.3% |
| 12 | 6,556 | 70.4% |

Random baseline: 0.049% for a random bitstring, 0.15% for a random valid choice.

Warm-up (12-qubit front/back QAOA, p=2): 28.2%.

Bonus at p=10:

| N | Qubits | Two-qubit gates | P(correct tower) | Valid-choice baseline |
|---|---|---|---|---|
| 5 | 15 | 9.3k | 10.2% | 0.026% |
| 6 | 18 | 13.4k | 8.7% | 0.0043% |

N=7 and N=8 aren't in the table yet. Aer took 13 minutes for N=8, so the plan is to sample from the exact `ValidSpaceQAOA` distribution and label the device honestly.

Note: the table's N=4 p=10 row is formatted inconsistently (baseline written as a decimal, not %). Clean it up.

## Files

- `src/insanity.py`: all core logic (encoding, cost, Hamiltonian, circuit, fast simulator, `make_puzzle`/`count_answers`, `tune`, `sample_counts`).
- `src/tune_angles.py`: precomputes `results/angles.json`.
- `build_notebook.py`: GENERATES `solution.ipynb`. Edit this, then rebuild.
- `solution.ipynb`: built, **not yet executed and has no outputs**.
- `build_slides.py` → `slides.pptx`: a draft, **not reviewed**.
- `resources/`: the starter's helpers (required).
- `results/`: charts, angles, table, `jobs.json`.

## To do, in order

1. Run the notebook top to bottom, with the qBraid key set or in qBraid Lab, so the SV1 jobs submit:
   `jupyter nbconvert --to notebook --execute --inplace solution.ipynb`.
   Fix any errors (in `build_notebook.py`, then rebuild). Make sure it's saved WITH outputs. Job IDs are printed and saved to `results/jobs.json`. About 5–9 SV1 jobs at roughly 0.4+ credits each. Bonus SV1 runs sit behind the `BONUS_ON_QBRAID` flag: N=8 is about 21k two-qubit gates on 24 qubits and may take minutes, at 7.5 credits per minute.
2. Write `README.md` (about 1 page): team names, level (warm-up + core + bonus), how to run, the results table with the exact `GRADING.md` columns and real job IDs, and an AI-use note (Claude Code wrote the encoding, code and docs; checked by the exhaustive H-vs-cost comparison, brute-force agreement, simulator-vs-Statevector and `solves` on every tower).
3. Review and fix `slides.pptx` (at most 8 slides: problem, encoding, algorithm, checks, results, bonus, takeaways, next step).
4. Optional: `BRIEFING.md` with a 5-minute talk split across speakers and likely judge questions.
5. Commit and push before 3:00 PM ET. Delete `HANDOFF.md`, or leave it.

## Honesty points for judges

- No speedup claim. Brute force solves N=4 in under 1 second.
- At a fixed number of layers, success falls as N grows. Two-qubit gates per layer grow from about 550 to 2,100 between N=4 and N=8.
- The Hamiltonian is built from the puzzle's structure, not by enumerating answers. Enumeration is used only to *check* it.
