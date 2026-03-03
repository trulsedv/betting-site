"""Plot expected rate of return as a function of the stake and optimum stake."""

import pathlib
import pickle  # noqa: S403

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

# Load the symbolic solution
with pathlib.Path("app/algorithms/m_opt_solution.pkl").open("rb") as f:
    solution_data = pickle.load(f)  # noqa: S301

# Create the function from the symbolic solution
m_opt_func = sp.lambdify(solution_data["parameters"], solution_data["symbolic_solution"], "numpy")


# Substitute numerical values
params = {
    "m0": 5.0,
    "Mb0": 1000.0,
    "Yb": 6.0,
    "Ym": 1000.0,
    "Nm": 1000.0,
    "Nb": 0.0,
    "p": 0.51,
}

solution_num = m_opt_func(params["m0"], params["Mb0"], params["Yb"], params["Ym"], params["Nm"], params["Nb"], params["p"])
print(f"Numerical value of the solution: {solution_num}")


# Define the function to plot
def calculate_r(params: dict, m_val: float) -> float:
    """Compute $1+r$ for a given stake value."""
    y_val = m_val + params["Ym"] * (1 - params["Nm"] / (params["Nm"] + m_val))
    a_val = 1 - params["m0"] / params["Mb0"] + params["Yb"] / params["Mb0"] - m_val / params["Mb0"] + y_val / params["Mb0"]
    b_val = 1 - params["m0"] / params["Mb0"] + params["Nb"] / params["Mb0"] - m_val / params["Mb0"]
    f_val = a_val ** params["p"] * b_val ** (1 - params["p"])
    return f_val


# Range of m values
m_values = np.linspace(0.0, 100.0, 400)

# Calculate 1 + r for each m
r_values = [calculate_r(params, m_val) for m_val in m_values]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(m_values, r_values, label="$1+r$", color="blue")
if "solution_num" in locals():
    plt.axvline(x=float(solution_num), color="red", linestyle="--", label=f"Optimal $m$ = {float(solution_num):.2f}")
plt.xlabel("$m$", fontsize=12)
plt.ylabel("$1+r$", fontsize=12)
plt.title("Plot of $1+r$ vs $m$", fontsize=14)
plt.grid(visible=True)
plt.legend(fontsize=12)
plt.show()
