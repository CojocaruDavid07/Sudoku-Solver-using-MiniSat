import time
import subprocess
import resource
import re
import csv
import os

def varnum(r, c, d):
    return 81 * (r - 1) + 9 * (c - 1) + d

def exactly_one(vars):
    clauses = []
    clauses.append(vars)
    for i in range(len(vars)):
        for j in range(i + 1, len(vars)):
            clauses.append([-vars[i], -vars[j]])
    return clauses

def sudoku_cnf(clues):
    clauses = []
    for r in range(1, 10):
        for c in range(1, 10):
            vars = [varnum(r, c, d) for d in range(1, 10)]
            clauses.extend(exactly_one(vars))
    for r in range(1, 10):
        for d in range(1, 10):
            vars = [varnum(r, c, d) for c in range(1, 10)]
            clauses.extend(exactly_one(vars))
    for c in range(1, 10):
        for d in range(1, 10):
            vars = [varnum(r, c, d) for r in range(1, 10)]
            clauses.extend(exactly_one(vars))
    for br in range(0, 3):
        for bc in range(0, 3):
            for d in range(1, 10):
                vars = [varnum(r, c, d) for r in range(1 + 3 * br, 4 + 3 * br)
                                            for c in range(1 + 3 * bc, 4 + 3 * bc)]
                clauses.extend(exactly_one(vars))
    for (r, c, d) in clues:
        clauses.append([varnum(r, c, d)])
    return clauses

def write_cnf_file(clauses, filename="sudoku.cnf"):
    num_vars = 9 * 9 * 9
    num_clauses = len(clauses)
    with open(filename, "w") as f:
        f.write(f"p cnf {num_vars} {num_clauses}\n")
        for clause in clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")

def decode_solution(out_file="sudoku.out"):
    with open(out_file, "r") as f:
        lines = f.readlines()
    if lines[0].strip() != "SAT":
        print("No solution found.")
        return
    assignments = list(map(int, lines[1].split()))
    grid = [[0 for _ in range(9)] for _ in range(9)]
    for v in assignments:
        if v > 0:
            v -= 1
            d = (v % 9) + 1
            c = (v // 9) % 9
            r = (v // 81)
            grid[r][c] = d
    for row in grid:
        print(" ".join(str(num) for num in row))

def get_memory_usage_mb():
    usage_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return usage_kb / 1024

clues = [
    (1, 1, 5), (1, 2, 3), (1, 5, 7),
    (2, 1, 6), (2, 4, 1), (2, 5, 9), (2, 6, 5),
    (3, 2, 9), (3, 3, 8), (3, 8, 6),
    (4, 1, 8), (4, 5, 6), (4, 9, 3),
    (5, 1, 4), (5, 4, 8), (5, 6, 3), (5, 9, 1),
    (6, 1, 7), (6, 5, 2), (6, 9, 6)
]


start_cnf = time.time()
clauses = sudoku_cnf(clues)
write_cnf_file(clauses)
end_cnf = time.time()

start_solver = time.time()
result = subprocess.run(
    ["minisat", "-verb=1", "sudoku.cnf", "sudoku.out"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)
end_solver = time.time()
solver_output = result.stdout

match = re.search(r'CPU time\s*:\s*([0-9.]+)\s*s', solver_output)
solver_time = float(match.group(1)) if match else (end_solver - start_solver)

start_decode = time.time()
decode_solution()
end_decode = time.time()

memory_usage = get_memory_usage_mb()

print("\nBenchmark Report:")
print(f"CNF generation time   : {end_cnf - start_cnf:.4f} sec")
print(f"Solver time           : {solver_time:.4f} sec")
print(f"Decoding time         : {end_decode - start_decode:.4f} sec")
print(f"Python peak memory    : {memory_usage:.2f} MB")

csv_file = "sudoku_benchmarks.csv"
file_exists = os.path.isfile(csv_file)

with open(csv_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow(["CNF_time_sec", "Solver_time_sec", "Decoding_time_sec", "Memory_MB", "Clues"])
    writer.writerow([
        round(end_cnf - start_cnf, 4),
        round(solver_time, 4),
        round(end_decode - start_decode, 4),
        round(memory_usage, 2)
        
    ])

print(f"\nResults logged to {csv_file}")
