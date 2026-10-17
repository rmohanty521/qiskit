"""Instant Insanity with a compact 3-qubits-per-cube encoding.

Everything the solution notebook needs lives here, in small functions a
judge can read. The notebook imports this module from the repo root:

    from src.insanity import ...

Encoding
--------
Each cube has 6 valid choices: an ordered pair (front/back pair, left/right
pair) of two different opposite-face pairs. The third pair is hidden on the
top and bottom. CHOICES lists them in the same order as the starter notebook:

    code 0: (0, 1)   code 1: (0, 2)   code 2: (1, 0)
    code 3: (1, 2)   code 4: (2, 0)   code 5: (2, 1)

Cube c stores its code in qubits 3c, 3c+1, 3c+2 as a 3-bit binary number
(qubit 3c is the lowest bit). Codes 6 and 7 are not used. Our circuits start
in, and never leave, the 6 valid codes, so they need no penalty term.
"""

import itertools

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import HGate
from qiskit.quantum_info import SparsePauliOp

CHOICES = list(itertools.permutations(range(3), 2))  # (front/back pair, left/right pair)
N_CODES = len(CHOICES)  # 6 valid codes out of the 8 that 3 qubits can hold


# ---------------------------------------------------------------- the puzzle

def letters_of(cubes):
    """The colours used by a puzzle, sorted."""
    return sorted({ch for cube in cubes for pair in cube for ch in pair})


def orientations(cube):
    """The 24 ways a cube can sit, as (front, back, left, right) colours. From the starter."""
    views = []
    for a, b in itertools.permutations(range(3), 2):
        for fa in (0, 1):
            for fb in (0, 1):
                fb_pair, lr_pair = cube[a], cube[b]
                views.append((fb_pair[fa], fb_pair[1 - fa], lr_pair[fb], lr_pair[1 - fb]))
    return views


def solves(tower):
    """True when each of the four sides shows N different colours. From the starter."""
    return all(len({view[side] for view in tower}) == len(tower) for side in range(4))


def classical_cost(cubes, codes):
    """Our cost for one code per cube: sum over both side pairs and every colour
    of (degree - 2)^2. Zero exactly when the front/back picks and the left/right
    picks are both 2-factors, which is exactly a solved tower."""
    total = 0
    for side in (0, 1):
        deg = dict.fromkeys(letters_of(cubes), 0)
        for cube, k in zip(cubes, codes):
            for ch in cube[CHOICES[k][side]]:
                deg[ch] += 1
        total += sum((d - 2) ** 2 for d in deg.values())
    return total


def cost_table(cubes):
    """classical_cost for all 6^N code assignments, as an array with one axis per
    cube (axis c is cube c's code). Built with numpy so N = 8 takes a second."""
    n = len(cubes)
    cols = letters_of(cubes)
    total = np.zeros((N_CODES,) * n, dtype=np.int64)
    for side in (0, 1):
        for colour in cols:
            deg = np.zeros((N_CODES,) * n, dtype=np.int64)
            for c, cube in enumerate(cubes):
                per_code = np.array([cube[CHOICES[k][side]].count(colour) for k in range(N_CODES)])
                shape = [1] * n
                shape[c] = N_CODES
                deg = deg + per_code.reshape(shape)
            total += (deg - 2) ** 2
    return total


# ---------------------------------------------------------------- bits <-> codes

def codes_to_bitstring(codes):
    """Qiskit-order bitstring (qubit 0 is the RIGHTMOST character)."""
    bits = []
    for k in codes:                       # cube 0 first, lowest bit first
        bits += [(k >> i) & 1 for i in range(3)]
    return "".join(str(b) for b in reversed(bits))


def bitstring_to_codes(key):
    """Inverse of codes_to_bitstring. Returns None if any cube holds code 6 or 7."""
    bits = [int(ch) for ch in reversed(key)]   # bits[q] is qubit q
    codes = []
    for c in range(len(bits) // 3):
        k = bits[3 * c] + 2 * bits[3 * c + 1] + 4 * bits[3 * c + 2]
        if k >= N_CODES:
            return None
        codes.append(k)
    return codes


def tower_of(cubes, codes):
    """Turn one code per cube into an explicit tower of (front, left, back, right)
    colours, using the starter's tower_from, so solves() can check it."""
    from resources.helpers import tower_from
    return tower_from(cubes, [CHOICES[k] for k in codes])


def is_solved_key(cubes, key):
    """The independent classical check we apply to EVERY measured bitstring."""
    codes = bitstring_to_codes(key)
    if codes is None:
        return False
    if classical_cost(cubes, codes) != 0:   # not two 2-factors: no tower to build
        return False
    return solves(tower_of(cubes, codes))


# ---------------------------------------------------------------- the Hamiltonian

def code_projector(c, k, n_qubits):
    """|k><k| on cube c's three qubits, as a sum of Z strings: prod over bits of (1 +/- Z)/2."""
    op = SparsePauliOp("I" * n_qubits)
    for i in range(3):
        q = 3 * c + i
        sign = -1 if (k >> i) & 1 else 1      # bit 1 -> (1 - Z)/2, bit 0 -> (1 + Z)/2
        op = op @ SparsePauliOp.from_sparse_list([("", [], 0.5), ("Z", [q], 0.5 * sign)], n_qubits)
    return op


def compact_hamiltonian(cubes):
    """H = sum over the two side pairs and every colour of (d - 2)^2, where d is the
    colour's degree written with code projectors. Built from the puzzle's structure
    (no enumeration), so it has polynomially many terms in N."""
    n = 3 * len(cubes)
    one = SparsePauliOp("I" * n)
    proj = [[code_projector(c, k, n) for k in range(N_CODES)] for c in range(len(cubes))]
    H = 0 * one
    for side in (0, 1):
        for colour in letters_of(cubes):
            d = -2 * one
            for c, cube in enumerate(cubes):
                for k in range(N_CODES):
                    count = cube[CHOICES[k][side]].count(colour)
                    if count:
                        d = d + count * proj[c][k]
            d = d.simplify()
            H = (H + (d @ d)).simplify()
    return H.simplify()


# ---------------------------------------------------------------- the circuit

THETA = 2 * np.arcsin(np.sqrt(1 / 3))   # RY angle that puts 1/3 of the weight on bit 2 = 1


def prep_cube(qc, c):
    """Equal superposition of the 6 valid codes on cube c's qubits.
    Codes 0-3 have bit2 = 0 (4 of 6), codes 4-5 have bit2 = 1 and bit1 = 0 (2 of 6)."""
    q0, q1, q2 = 3 * c, 3 * c + 1, 3 * c + 2
    qc.ry(THETA, q2)                                      # P(bit2 = 1) = 1/3
    qc.append(HGate().control(1, ctrl_state=0), [q2, q1])  # bit1 free only when bit2 = 0
    qc.h(q0)                                              # bit0 always free


def unprep_cube(qc, c):
    q0, q1, q2 = 3 * c, 3 * c + 1, 3 * c + 2
    qc.h(q0)
    qc.append(HGate().control(1, ctrl_state=0), [q2, q1])
    qc.ry(-THETA, q2)


def mixer_cube(qc, c, beta):
    """exp(-i beta |u><u|) on cube c, where |u> is the equal superposition of its
    6 valid codes. It only ever mixes valid codes with valid codes.
    Built as: undo the prep, add phase -beta to |000>, redo the prep."""
    q = [3 * c, 3 * c + 1, 3 * c + 2]
    unprep_cube(qc, c)
    qc.x(q)
    qc.mcp(-beta, q[:2], q[2])            # phase on |111> after the X's = |000> before
    qc.x(q)
    prep_cube(qc, c)


def cost_layer(qc, H, gamma):
    """exp(-i gamma H) for a Hamiltonian of Z strings of ANY length.
    A Z string on qubits q1..qm is a CNOT ladder onto qm, one RZ, and the ladder undone."""
    for label, coeff in zip(H.paulis.to_labels(), H.coeffs):
        qubits = [q for q, op in enumerate(reversed(label)) if op == "Z"]
        if not qubits:
            continue                       # the identity term is a global phase
        for a, b in zip(qubits, qubits[1:]):
            qc.cx(a, b)
        qc.rz(2 * gamma * coeff.real, qubits[-1])
        for a, b in reversed(list(zip(qubits, qubits[1:]))):
            qc.cx(a, b)


def qaoa_circuit(cubes, H, gammas, betas):
    """Constrained QAOA on the compact encoding: valid-code start, then p rounds of
    cost layer + per-cube mixer."""
    n = len(cubes)
    qc = QuantumCircuit(3 * n)
    for c in range(n):
        prep_cube(qc, c)
    for g, b in zip(gammas, betas):
        cost_layer(qc, H, g)
        for c in range(n):
            mixer_cube(qc, c, b)
    return qc


# ---------------------------------------------------------------- fast exact simulation

class ValidSpaceQAOA:
    """Exact QAOA simulation restricted to the 6^N valid code assignments.

    The circuit never leaves the valid codes, so its state lives in a space of
    6^N amplitudes, not 8^N. That makes N = 8 (1.7 million amplitudes) quick enough
    to tune angles on a laptop. We check it against Qiskit's Statevector of the
    real circuit in the notebook.
    """

    def __init__(self, cubes):
        self.n = len(cubes)
        self.costs = cost_table(cubes).astype(float)
        self.solution = self.costs == 0
        self.dim = self.costs.size

    def state(self, gammas, betas):
        n = self.n
        psi = np.full((N_CODES,) * n, 1 / np.sqrt(self.dim), dtype=complex)
        u = np.full(N_CODES, 1 / np.sqrt(N_CODES))
        for g, b in zip(gammas, betas):
            psi = psi * np.exp(-1j * g * self.costs)
            mix = np.eye(N_CODES) + (np.exp(-1j * b) - 1) * np.outer(u, u)
            for c in range(n):
                psi = np.moveaxis(np.tensordot(mix, psi, axes=([1], [c])), 0, c)
        return psi

    def stats(self, gammas, betas):
        probs = np.abs(self.state(gammas, betas)) ** 2
        return float((probs * self.costs).sum()), float(probs[self.solution].sum())


def two_qubit_gates_and_depth(qc):
    """The challenge's counting rule: transpile to rz, sx, x, cx and count cx."""
    from qiskit import transpile
    t = transpile(qc, basis_gates=["rz", "sx", "x", "cx"], optimization_level=1, seed_transpiler=7)
    return t.count_ops().get("cx", 0), t.depth()


# ---------------------------------------------------------------- bonus puzzles (copied from the starter)

def make_puzzle(n, seed):
    """N cubes, N colours, a planted answer: two random cycles through all colours.
    Copied unchanged from the starter notebook."""
    import random
    rng = random.Random(seed)
    letters = "".join(chr(ord("A") + i) for i in range(n))
    cycles = []
    for _ in range(2):
        order = rng.sample(letters, n)
        lines = [order[i] + order[(i + 1) % n] for i in range(n)]
        rng.shuffle(lines)
        cycles.append(lines)
    cubes = []
    for i in range(n):
        third = rng.choice(letters) + rng.choice(letters)
        pairs = ["".join(rng.sample(pair, 2)) for pair in (cycles[0][i], cycles[1][i], third)]
        rng.shuffle(pairs)
        cubes.append(pairs)
    return cubes


def count_answers(cubes):
    """How many of the 6**n cases solve the puzzle. Copied unchanged from the starter."""
    letters = sorted({ch for cube in cubes for pair in cube for ch in pair})
    total = 0
    for choice in itertools.product(CHOICES, repeat=len(cubes)):
        for side in (0, 1):
            deg = dict.fromkeys(letters, 0)
            for cube, pick in zip(cubes, choice):
                for ch in cube[pick[side]]:
                    deg[ch] += 1
            if any(d != 2 for d in deg.values()):
                break
        else:
            total += 1
    return total


BONUS_SEEDS = {5: 16, 6: 86, 7: 68, 8: 4}   # each gives exactly one tower (2 graph-level cases)


# ---------------------------------------------------------------- tuning the angles

def _interp(x):
    """INTERP warm start: stretch a p-layer schedule to p + 1 layers."""
    x = np.asarray(x, dtype=float)
    q = len(x)
    return np.interp(np.linspace(0, 1, q + 1), np.linspace(0, 1, q), x)


def tune(sim, p_max, maxiter, previous=None, start=(0.26, 5.55), log=print):
    """Grow the circuit one layer at a time. At each depth p, minimise the AVERAGE
    COST (the solutions are never used), starting from
      * the depth p-1 angles stretched to p layers (INTERP), and
      * if given, the depth-p angles tuned on the next smaller puzzle (transfer).
    Returns a list of dicts, one per depth: p, average cost E, P(correct) P, gammas, betas.
    The p = 1 start (0.26, 5.55) is the best point of a 61 x 61 grid on the N = 4 puzzle."""
    from scipy.optimize import minimize
    out, gam, bet = [], [start[0]], [start[1]]
    for p in range(1, p_max + 1):
        f = lambda x: sim.stats(x[:p], x[p:])[0]
        starts = [np.array(start)] if p == 1 else [np.concatenate([_interp(gam), _interp(bet)])]
        if previous is not None and len(previous) >= p:
            starts.append(np.concatenate([previous[p - 1]["g"], previous[p - 1]["b"]]))
        best = None
        for x0 in starts:
            r = minimize(f, x0, method="COBYLA", options={"maxiter": maxiter, "rhobeg": 0.1})
            if best is None or r.fun < best.fun:
                best = r
        gam, bet = list(best.x[:p]), list(best.x[p:])
        e, s = sim.stats(gam, bet)
        out.append(dict(p=p, E=e, P=s, g=gam, b=bet))
        if log:
            log(f"  p={p:2d}: average cost {e:6.3f}, P(correct) {s:7.2%}")
    return out


def sample_counts(sim, gammas, betas, shots, seed):
    """Draw shots from the EXACT output distribution (no circuit simulator needed).
    Used only for the large bonus circuits when no qBraid device is available,
    and labelled 'exact sim (local)' in every table."""
    probs = (np.abs(sim.state(gammas, betas)) ** 2).ravel()
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(probs), size=shots, p=probs / probs.sum())
    counts = {}
    for i in idx:
        codes = list(np.unravel_index(i, (N_CODES,) * sim.n))
        key = codes_to_bitstring([int(k) for k in codes])
        counts[key] = counts.get(key, 0) + 1
    return counts
