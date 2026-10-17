| Puzzle (N cubes) | Encoding | Device | Qubits | Two-qubit gates (after transpiling) | Depth | Shots | P(correct tower) | Random-guess baseline | qBraid job ID |
|---|---|---|---|---|---|---|---|---|---|
| 4 (front/back only, warm-up) | one-hot 3/cube, W-state + XY mixer, p=2 | aws:aws:sim:sv1 | 12 | 300 | 215 | 1000 | 30.6% | 0.098% (bitstring) / 4.9% (one-hot) | aws:aws:sim:sv1-60f2-qjob-6ad384c338127b44c71b9a46 |
| 4 | compact 3 qubits/cube, constrained QAOA p=1 | aws:aws:sim:sv1 | 12 | 550 | 522 | 1000 | 1.7% | 0.049% (bitstring) / 0.15% (valid) | aws:aws:sim:sv1-60f2-qjob-6ad384d338127b44c71b9a53 |
| 4 | compact 3 qubits/cube, constrained QAOA p=4 | aws:aws:sim:sv1 | 12 | 2188 | 2040 | 1000 | 8.7% | 0.049% (bitstring) / 0.15% (valid) | aws:aws:sim:sv1-60f2-qjob-6ad3850138127b44c71b9a5a |
| 4 | compact 3 qubits/cube, constrained QAOA p=8 | aws:aws:sim:sv1 | 12 | 4372 | 4064 | 1000 | 42.1% | 0.049% (bitstring) / 0.15% (valid) | aws:aws:sim:sv1-60f2-qjob-6ad3853638127b44c71b9a74 |
| 4 | compact 3 qubits/cube, constrained QAOA p=12 | aws:aws:sim:sv1 | 12 | 6556 | 6088 | 1000 | 73.3% | 0.049% (bitstring) / 0.15% (valid) | aws:aws:sim:sv1-60f2-qjob-6ad3857838127b44c71b9a82 |
| 4 | compact 3 qubits/cube, constrained QAOA p=10 | aws:aws:sim:sv1 | 12 | 5464 | 5076 | 2000 | 58.8% | 0.049% (bitstring) / 0.15% (valid) | aws:aws:sim:sv1-60f2-qjob-6ad385c138127b44c71b9a96 |
| 5 | compact 3 qubits/cube, constrained QAOA p=10 | aws:aws:sim:sv1 | 15 | 9285 | 8591 | 2000 | 9.5% | 0.0061% (bitstring) / 0.026% (valid) | aws:aws:sim:sv1-60f2-qjob-6ad3860638127b44c71b9aa4 |
| 6 | compact 3 qubits/cube, constrained QAOA p=10 | aws:aws:sim:sv1 | 18 | 13446 | 12001 | 2000 | 9.4% | 0.00076% (bitstring) / 0.0043% (valid) | aws:aws:sim:sv1-60f2-qjob-6ad3866a38127b44c71b9aba |
| 7 | compact 3 qubits/cube, constrained QAOA p=10 | aws:aws:sim:sv1 | 21 | 16627 | 14235 | 2000 | 3.3% | 9.5e-05% (bitstring) / 0.00071% (valid) | aws:aws:sim:sv1-60f2-qjob-6ad386e638127b44c71b9ae7 |
| 8 | compact 3 qubits/cube, constrained QAOA p=10 | aws:aws:sim:sv1 | 24 | 21128 | 17443 | 2000 | 3.3% | 1.2e-05% (bitstring) / 0.00012% (valid) | aws:aws:sim:sv1-60f2-qjob-6ad3876738127b44c71b9b23 |
