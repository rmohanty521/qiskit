| Puzzle (N cubes) | Encoding | Device | Qubits | Two-qubit gates (after transpiling) | Depth | Shots | P(correct tower) | Random-guess baseline | qBraid job ID |
|---|---|---|---|---|---|---|---|---|---|
| 4 (front/back only, warm-up) | one-hot 3/cube, W-state + XY mixer, p=2 | local Aer (SV1 pending) | 12 | 300 | 215 | 1000 | 28.2% | 0.098% (bitstring) / 4.9% (one-hot) | TODO: run in qBraid Lab |
| 4 | compact 3 qubits/cube, constrained QAOA p=1 | local Aer (SV1 pending) | 12 | 550 | 522 | 1000 | 1.1% | 0.049% (bitstring) / 0.15% (valid) | TODO: run in qBraid Lab |
| 4 | compact 3 qubits/cube, constrained QAOA p=4 | local Aer (SV1 pending) | 12 | 2188 | 2040 | 1000 | 8.5% | 0.049% (bitstring) / 0.15% (valid) | TODO: run in qBraid Lab |
| 4 | compact 3 qubits/cube, constrained QAOA p=8 | local Aer (SV1 pending) | 12 | 4372 | 4064 | 1000 | 39.3% | 0.049% (bitstring) / 0.15% (valid) | TODO: run in qBraid Lab |
| 4 | compact 3 qubits/cube, constrained QAOA p=12 | local Aer (SV1 pending) | 12 | 6556 | 6088 | 1000 | 70.4% | 0.049% (bitstring) / 0.15% (valid) | TODO: run in qBraid Lab |
| 4 | compact 3 qubits/cube, constrained QAOA p=10 | local Aer (SV1 pending) | 12 | 5464 | 5076 | 2000 | 56.6% | 0.00049 (bitstring) / 0.0015 (valid) | TODO: run in qBraid Lab |
| 5 | compact 3 qubits/cube, constrained QAOA p=10 | local Aer (SV1 pending) | 15 | 9285 | 8591 | 2000 | 10.2% | 6.1e-05 (bitstring) / 0.00026 (valid) | TODO: run in qBraid Lab |
| 6 | compact 3 qubits/cube, constrained QAOA p=10 | local Aer (SV1 pending) | 18 | 13446 | 12001 | 2000 | 8.7% | 7.6e-06 (bitstring) / 4.3e-05 (valid) | TODO: run in qBraid Lab |
