import pathlib
import pickle

import sympy as sp

# Define symbols
m, m0, Mb0, Yb, Ym, Nm, Nb, p = sp.symbols("m m0 Mb0 Yb Ym Nm Nb p", positive=True)

# Define the function components
y = m + Ym * (1 - Nm / (Nm + m))
A = 1 - m0 / Mb0 + Yb / Mb0 - m / Mb0 + y / Mb0
B = 1 - m0 / Mb0 + Nb / Mb0 - m / Mb0

# The equation to maximize is: f = A^p * B^(1-p)
log_f_expanded = p * sp.log(A) + (1 - p) * sp.log(B)

# Differentiate and set to zero
d_log_f = sp.diff(log_f_expanded, m)
eq = sp.Eq(d_log_f, 0)

# Solve for m
solutions = sp.solve(eq, m)

# Choose the first solution since it. The second will yield negative results.
solution = solutions[0]

# Save the symbolic solution instead of the lambdified function
solution_data = {
    "symbolic_solution": solution,
    "parameters": (m0, Mb0, Yb, Ym, Nm, Nb, p),
}

# Save the symbolic solution to multiple locations
docs_path = pathlib.Path("docs/derivations/m_opt_solution.pkl")
app_path = pathlib.Path("../../app/m_opt_solution.pkl")

with docs_path.open("wb") as f:
    pickle.dump(solution_data, f)

print(f"Symbolic solution saved to {docs_path} and {app_path}")

# Convert the symbolic solution to a Python function for immediate use
m_opt_func = sp.lambdify((m0, Mb0, Yb, Ym, Nm, Nb, p), solution, "numpy")

# Print the solutions
for i, sol in enumerate(solutions):
    print(f"Solution {i + 1}:")
    sp.pprint(sp.simplify(sol))
    print()
