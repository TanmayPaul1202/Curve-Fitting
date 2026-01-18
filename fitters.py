from __future__ import annotations

from typing import List, Dict, Any
import math
import numpy as np


def _safe_list(values: List[float]) -> np.ndarray:
    return np.array(values, dtype=float)


def _r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    # If all y are equal, define R^2 as 1.0 if perfect fit else 0.0
    if ss_tot == 0.0:
        return 1.0 if ss_res == 0.0 else 0.0
    return 1.0 - ss_res / ss_tot


def _linear_least_squares(X: np.ndarray, Y: np.ndarray) -> Dict[str, Any]:
    n = len(X)
    Sx = float(np.sum(X))
    Sy = float(np.sum(Y))
    Sxx = float(np.sum(X * X))
    Sxy = float(np.sum(X * Y))
    denom = n * Sxx - Sx * Sx
    if denom == 0.0:
        return {"error": "Singular system (denominator zero) in linear normal equations."}
    b = (n * Sxy - Sx * Sy) / denom
    a = (Sy - b * Sx) / n
    steps = [
        f"n = {n}",
        f"Σx = {Sx:.6g}",
        f"Σy = {Sy:.6g}",
        f"Σx² = {Sxx:.6g}",
        f"Σxy = {Sxy:.6g}",
        "Formulas: b = (nΣxy − (Σx)(Σy)) / (nΣx² − (Σx)²), a = (Σy − bΣx)/n",
        f"Computed: b = {b:.6g}, a = {a:.6g}",
    ]
    return {"a": a, "b": b, "steps": steps}


def linear_fit(x: List[float], y: List[float]) -> Dict[str, Any]:
    X = _safe_list(x)
    Y = _safe_list(y)
    # Compute helpful columns for manual-style solution
    xy = X * Y
    x2 = X * X
    table = [
        {"x": float(X[i]), "y": float(Y[i]), "xy": float(xy[i]), "x2": float(x2[i])}
        for i in range(len(X))
    ]

    n = len(X)
    Sx = float(np.sum(X))
    Sy = float(np.sum(Y))
    Sxy = float(np.sum(xy))
    Sx2 = float(np.sum(x2))

    sol = _linear_least_squares(X, Y)
    if "error" in sol:
        return {
            "type": "linear",
            "formula": "y = a + b x",
            "error": sol["error"],
            "steps": sol.get("steps", []),
            "question": "Fit a straight line to the given data",
            "columns": ["x", "y", "xy", "x²"],
            "table": table,
            "sums": {"n": n, "Σx": Sx, "Σy": Sy, "Σxy": Sxy, "Σx²": Sx2},
        }
    a = float(sol["a"])  # ensure JSON-serializable
    b = float(sol["b"])  # ensure JSON-serializable
    y_hat = a + b * X
    r2 = _r2_score(Y, y_hat)
    # Normal equations text
    eqs = [
        "Σy = n·a + b·Σx",
        "Σxy = a·Σx + b·Σx²",
    ]
    working = [
        "Let the best fitted straight line be y = a + b x",
        f"Substitute values: Σy={Sy:.6g} = {n}·a + {Sx:.6g}·b",
        f"and Σxy={Sxy:.6g} = {Sx:.6g}·a + {Sx2:.6g}·b",
        f"Solve → b = {b:.6g}, then a = (Σy − bΣx)/n = ({Sy:.6g} − {b:.6g}·{Sx:.6g})/{n} = {a:.6g}",
    ]

    return {
        "type": "linear",
        "formula": "y = a + b x",
        "coefficients": {"a": a, "b": b},
        "equation": f"y = {a:.6g} + {b:.6g} x",
        "r2": r2,
        "steps": sol["steps"],
        "question": "Fit a straight line to the following data",
        "columns": ["x", "y", "xy", "x²"],
        "table": table,
        "sums": {"n": n, "Σx": Sx, "Σy": Sy, "Σxy": Sxy, "Σx²": Sx2},
        "equations": eqs,
        "working": working,
    }


def quadratic_fit(x: List[float], y: List[float]) -> Dict[str, Any]:
    X = _safe_list(x)
    Y = _safe_list(y)
    n = len(X)
    Sx = float(np.sum(X))
    Sx2 = float(np.sum(X**2))
    Sx3 = float(np.sum(X**3))
    Sx4 = float(np.sum(X**4))
    Sy = float(np.sum(Y))
    Sxy = float(np.sum(X * Y))
    Sx2y = float(np.sum((X**2) * Y))

    A = np.array([
        [n, Sx, Sx2],
        [Sx, Sx2, Sx3],
        [Sx2, Sx3, Sx4],
    ], dtype=float)
    b_vec = np.array([Sy, Sxy, Sx2y], dtype=float)
    try:
        a, b, c = np.linalg.solve(A, b_vec)
    except np.linalg.LinAlgError:
        return {
            "type": "quadratic",
            "formula": "y = a + b x + c x^2",
            "error": "Singular system while solving quadratic normal equations.",
            "steps": [],
        }

    steps = [
        f"n = {n}",
        f"Σx = {Sx:.6g}",
        f"Σx² = {Sx2:.6g}",
        f"Σx³ = {Sx3:.6g}",
        f"Σx⁴ = {Sx4:.6g}",
        f"Σy = {Sy:.6g}",
        f"Σxy = {Sxy:.6g}",
        f"Σx²y = {Sx2y:.6g}",
        "Normal equations:",
        "Σy = n·a + b·Σx + c·Σx²",
        "Σxy = a·Σx + b·Σx² + c·Σx³",
        "Σx²y = a·Σx² + b·Σx³ + c·Σx⁴",
        "Solve the 3×3 system for a, b, c.",
        f"Computed: a = {a:.6g}, b = {b:.6g}, c = {c:.6g}",
    ]

    # Ensure native Python floats for JSON safety
    a = float(a)
    b = float(b)
    c = float(c)

    y_hat = a + b * X + c * (X ** 2)
    r2 = _r2_score(Y, y_hat)
    return {
        "type": "quadratic",
        "formula": "y = a + b x + c x^2",
        "coefficients": {"a": a, "b": b, "c": c},
        "equation": f"y = {a:.6g} + {b:.6g} x + {c:.6g} x^2",
        "r2": r2,
        "steps": steps,
        "question": "Fit a quadratic curve to the following data",
        "columns": ["x", "y"],
        "table": [{"x": float(X[i]), "y": float(Y[i])} for i in range(n)],
        "sums": {"n": n, "Σx": Sx, "Σx²": Sx2, "Σx³": Sx3, "Σx⁴": Sx4, "Σy": Sy, "Σxy": Sxy, "Σx²y": Sx2y},
        "equations": [
            "Σy = n·a + b·Σx + c·Σx²",
            "Σxy = a·Σx + b·Σx² + c·Σx³",
            "Σx²y = a·Σx² + b·Σx³ + c·Σx⁴",
        ],
    }


def exponential_fit(x: List[float], y: List[float]) -> Dict[str, Any]:
    X = _safe_list(x)
    Y = _safe_list(y)
    if np.any(Y <= 0):
        return {
            "type": "exponential",
            "formula": "y = a e^{b x}",
            "error": "Exponential fit requires all y > 0 (log transform).",
            "steps": ["Check: all y must be positive for ln(y)."],
        }
    lnY = np.log(Y)
    x2 = X * X
    xlny = X * lnY
    n = len(X)
    Sx = float(np.sum(X))
    Sx2 = float(np.sum(x2))
    Slny = float(np.sum(lnY))
    Sxlny = float(np.sum(xlny))
    table = [
        {"x": float(X[i]), "y": float(Y[i]), "lny": float(lnY[i]), "xlny": float(xlny[i]), "x2": float(x2[i])}
        for i in range(n)
    ]
    sol = _linear_least_squares(X, lnY)
    if "error" in sol:
        return {
            "type": "exponential",
            "formula": "y = a e^{b x}",
            "error": sol["error"],
            "steps": sol.get("steps", []),
            "question": "Fit an exponential curve to the data",
            "columns": ["x", "y", "ln(y)", "x·ln(y)", "x²"],
            "table": table,
            "sums": {"n": n, "Σx": Sx, "Σx²": Sx2, "Σln(y)": Slny, "Σx ln(y)": Sxlny},
        }
    ln_a = float(sol["a"])  # ensure JSON-serializable
    b = float(sol["b"])     # ensure JSON-serializable
    a = float(math.exp(ln_a))
    y_hat = a * np.exp(b * X)
    r2 = _r2_score(Y, y_hat)
    steps = [
        "Take logs: ln(y) = ln(a) + b x",
        f"Normal equations on ln(y) vs x:",
        "Σln(y) = n·ln(a) + b·Σx",
        "Σx ln(y) = ln(a)·Σx + b·Σx²",
        f"With values: {Slny:.6g} = {n}·ln(a) + {Sx:.6g}·b and {Sxlny:.6g} = ln(a)·{Sx:.6g} + b·{Sx2:.6g}",
        f"Solve → ln(a) = {ln_a:.6g}, b = {b:.6g}; so a = e^{{ln(a)}} = {a:.6g}",
    ]
    return {
        "type": "exponential",
        "formula": "y = a e^{b x}",
        "coefficients": {"a": a, "b": b},
        "equation": f"y = {a:.6g} e^({b:.6g} x)",
        "r2": r2,
        "steps": steps,
        "question": "Fit an exponential curve to the following data",
        "columns": ["x", "y", "ln(y)", "x·ln(y)", "x²"],
        "table": table,
        "sums": {"n": n, "Σx": Sx, "Σx²": Sx2, "Σln(y)": Slny, "Σx ln(y)": Sxlny},
        "equations": [
            "Σln(y) = n·ln(a) + b·Σx",
            "Σx ln(y) = ln(a)·Σx + b·Σx²",
        ],
    }


def logarithmic_fit(x: List[float], y: List[float]) -> Dict[str, Any]:
    X = _safe_list(x)
    Y = _safe_list(y)
    if np.any(X <= 0):
        return {
            "type": "logarithmic",
            "formula": "y = a + b ln(x)",
            "error": "Logarithmic fit requires all x > 0 (log transform).",
            "steps": ["Check: all x must be positive for ln(x)."],
        }
    lnX = np.log(X)
    u = lnX
    u2 = u * u
    uy = u * Y
    n = len(X)
    Su = float(np.sum(u))
    Su2 = float(np.sum(u2))
    Sy = float(np.sum(Y))
    Suy = float(np.sum(uy))
    table = [
        {"x": float(X[i]), "y": float(Y[i]), "lnx": float(u[i]), "u*y": float(uy[i]), "u2": float(u2[i])}
        for i in range(n)
    ]
    sol = _linear_least_squares(lnX, Y)
    if "error" in sol:
        return {
            "type": "logarithmic",
            "formula": "y = a + b ln(x)",
            "error": sol["error"],
            "steps": sol.get("steps", []),
            "question": "Fit a logarithmic curve to the data",
            "columns": ["x", "y", "ln(x)", "ln(x)·y", "(ln x)²"],
            "table": table,
            "sums": {"n": n, "Σln(x)": Su, "Σ(ln x)²": Su2, "Σy": Sy, "Σ(ln x)·y": Suy},
        }
    a = float(sol["a"])  # ensure JSON-serializable
    b = float(sol["b"])  # ensure JSON-serializable
    y_hat = a + b * lnX
    r2 = _r2_score(Y, y_hat)
    steps = [
        "Let u = ln(x), then y = a + b·u",
        "Normal equations:",
        "Σy = n·a + b·Σu",
        "Σuy = a·Σu + b·Σu²",
        f"Values: Σy={Sy:.6g}, Σu={Su:.6g}, Σu²={Su2:.6g}, Σuy={Suy:.6g}",
        f"Solve → a = {a:.6g}, b = {b:.6g}",
    ]
    return {
        "type": "logarithmic",
        "formula": "y = a + b ln(x)",
        "coefficients": {"a": a, "b": b},
        "equation": f"y = {a:.6g} + {b:.6g} ln(x)",
        "r2": r2,
        "steps": steps,
        "question": "Fit a logarithmic curve to the following data",
        "columns": ["x", "y", "ln(x)", "ln(x)·y", "(ln x)²"],
        "table": table,
        "sums": {"n": n, "Σln(x)": Su, "Σ(ln x)²": Su2, "Σy": Sy, "Σ(ln x)·y": Suy},
        "equations": [
            "Σy = n·a + b·Σln(x)",
            "Σ(ln x)·y = a·Σln(x) + b·Σ(ln x)²",
        ],
    }


def power_fit(x: List[float], y: List[float]) -> Dict[str, Any]:
    X = _safe_list(x)
    Y = _safe_list(y)
    if np.any(X <= 0) or np.any(Y <= 0):
        return {
            "type": "power",
            "formula": "y = a x^b",
            "error": "Power fit requires all x > 0 and y > 0 (log transform).",
            "steps": ["Check: all x and y must be positive for ln(x), ln(y)."],
        }
    lnX = np.log(X)
    lnY = np.log(Y)
    u = lnX
    v = lnY
    u2 = u * u
    uv = u * v
    n = len(X)
    Su = float(np.sum(u))
    Su2 = float(np.sum(u2))
    Sv = float(np.sum(v))
    Suv = float(np.sum(uv))
    table = [
        {"x": float(X[i]), "y": float(Y[i]), "lnx": float(u[i]), "lny": float(v[i]), "lnx·lny": float(uv[i]), "(lnx)²": float(u2[i])}
        for i in range(n)
    ]
    sol = _linear_least_squares(lnX, lnY)
    if "error" in sol:
        return {
            "type": "power",
            "formula": "y = a x^b",
            "error": sol["error"],
            "steps": sol.get("steps", []),
            "question": "Fit a power curve to the data",
            "columns": ["x", "y", "ln(x)", "ln(y)", "ln(x)·ln(y)", "(ln x)²"],
            "table": table,
            "sums": {"n": n, "Σln(x)": Su, "Σ(ln x)²": Su2, "Σln(y)": Sv, "Σln(x)ln(y)": Suv},
        }
    ln_a = float(sol["a"])  # ensure JSON-serializable
    b = float(sol["b"])     # ensure JSON-serializable
    a = float(math.exp(ln_a))
    y_hat = a * (X ** b)
    r2 = _r2_score(Y, y_hat)
    steps = [
        "Take logs: ln(y) = ln(a) + b·ln(x)",
        "Normal equations:",
        "Σln(y) = n·ln(a) + b·Σln(x)",
        "Σln(x)ln(y) = ln(a)·Σln(x) + b·Σ(ln x)²",
        f"Values: Σln(y)={Sv:.6g}, Σln(x)={Su:.6g}, Σ(ln x)²={Su2:.6g}, Σln(x)ln(y)={Suv:.6g}",
        f"Solve → ln(a) = {ln_a:.6g}, b = {b:.6g}; so a = e^{{ln(a)}} = {a:.6g}",
    ]
    return {
        "type": "power",
        "formula": "y = a x^b",
        "coefficients": {"a": a, "b": b},
        "equation": f"y = {a:.6g} x^{b:.6g}",
        "r2": r2,
        "steps": steps,
        "question": "Fit a power curve to the following data",
        "columns": ["x", "y", "ln(x)", "ln(y)", "ln(x)·ln(y)", "(ln x)²"],
        "table": table,
        "sums": {"n": n, "Σln(x)": Su, "Σ(ln x)²": Su2, "Σln(y)": Sv, "Σln(x)ln(y)": Suv},
        "equations": [
            "Σln(y) = n·ln(a) + b·Σln(x)",
            "Σln(x)ln(y) = ln(a)·Σln(x) + b·Σ(ln x)²",
        ],
    }



