# Group-State Matrix (GSM) Rubik's Cube Model

Author: Aijaz Bhat

This package contains the current reproducible code for the Group-State Matrix (GSM) representation and shallow exact-search prototype for a standard 3x3x3 Rubik's Cube.

## Contents

- `model/gsm_rubiks.py` — core cubie-level GSM state model, legal moves, permutation matrices, orientation updates, validity checks, and self-tests.
- `model/gsm_solver_prototype.py` — exact bidirectional search prototype for states within 6 half-turn metric (HTM) moves of the solved state.
- `tests/validation_suite.py` — randomized legality/inverse tests and dense-vs-indexed matrix benchmark.
- `benchmarks/benchmark_gsm.py` — search, move-application, and dense-vs-sparse benchmarks.

## State model

The cube state is represented as

`S = (P_C, O_C, P_E, O_E)`

with 8 corner permutations, 8 corner orientations, 12 edge permutations, and 12 edge orientations.

Legal-state constraints are checked by `verify_state()`:

- corner-twist sum = 0 mod 3
- edge-flip sum = 0 mod 2
- corner and edge permutation parities agree

## Move model

Each basic face turn is represented by an indexed permutation plus orientation offsets. A 20x20 block permutation matrix can be generated for the 8 corners + 12 edges with `piece_permutation_matrix(face)`.

The update has the affine form

`p' = P p`

`o' = P o + delta (mod 3 / mod 2)`.

## Exact-search scope

The bundled solver is an exact shallow-search prototype. It precomputes all states up to radius 3 from the goal and then performs a bidirectional search for scrambles whose exact distance is at most 6 HTM moves.

It is intentionally **not** presented as a full-depth optimal solver.

## Reproducibility

Validated in the supplied runtime with:

- Python syntax compilation for all four scripts
- core self-tests: all six face turns have order 4; opposite faces commute; inverse sequence returns to solved; permutation-matrix row/column checks
- 10,000 randomized legal-state tests
- 1,000 randomized sequence/inverse tests
- exact-search checks at distances 1 through 6 HTM

Example commands from this directory:

```bash
python model/gsm_rubiks.py
python model/gsm_solver_prototype.py
python tests/validation_suite.py
python benchmarks/benchmark_gsm.py
```

The benchmark script uses NumPy for the dense matrix comparison.
