# Sudoku-Solver-using-MiniSat
Full pipeline (generate CNF -> run MiniSat -> decode -> benchmark).

Requirements:
- Python 3
- MiniSat installed

How It Works:
Each (row, column, digit) combination is mapped to a SAT variable: var = 81*(r-1) + 9*(c-1) + d
There are 729 total variables (9x9x9).
The CNF encodes: 
1. Each cell contains exactly one digit.
2. Each digit appears once per row.
3. Each digit appears once per column.
4. Each digit appears once per 3x3 block.
5. Pre-filled clues are enforced as unit clauses.

Run python sudoku_solver.py to:
1. Generate sudoku.cnf 
2. Run MiniSat 
3. Decode and print the solved grid 
4. Print timing results 
5. Log results to sudoku_benchmarks.csv

Changing the Sudoku Puzzle
Modify the clues list inside sudoku_solver.py.

Example: (1,1,5): Row 1, Column 1 is 5.

Benchmark Logging:
Each run appends to: sudoku_benchmarks.csv
Columns: CNF_time_sec, Solver_time_sec, Decoding_time_sec, Memory_MB

UNSAT: The Sudoku puzzle has no valid solution.
