from __future__ import annotations

from flask import Flask, render_template, request, jsonify
from typing import List, Dict, Any

from fitters import (
    linear_fit,
    quadratic_fit,
    exponential_fit,
    logarithmic_fit,
    power_fit,
)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def index() -> str:
        return render_template("index.html")

    @app.route("/fit", methods=["POST"])
    def fit() -> Any:
        import traceback
        payload: Dict[str, Any] = request.get_json(force=True) or {}
        x: List[float] = payload.get("x", [])
        y: List[float] = payload.get("y", [])
        fit_types: List[str] = payload.get("types", [])

        if not isinstance(x, list) or not isinstance(y, list) or len(x) != len(y) or len(x) == 0:
            return jsonify({
                "error": "Provide equal-length non-empty arrays 'x' and 'y'."
            }), 400

        # Normalize types: if 'all' provided, expand to all kinds
        all_types = ["linear", "quadratic", "exponential", "logarithmic", "power"]
        if not fit_types or "all" in fit_types:
            fit_types = all_types
        else:
            # keep only known types, preserve order
            fit_types = [t for t in fit_types if t in all_types]
            if not fit_types:
                fit_types = all_types

        results = []
        formulas = {
            "linear": "y = a + b x",
            "quadratic": "y = a + b x + c x^2",
            "exponential": "y = a e^{b x}",
            "logarithmic": "y = a + b ln(x)",
            "power": "y = a x^b",
        }
        for t in fit_types:
            try:
                if t == "linear":
                    results.append(linear_fit(x, y))
                elif t == "quadratic":
                    results.append(quadratic_fit(x, y))
                elif t == "exponential":
                    results.append(exponential_fit(x, y))
                elif t == "logarithmic":
                    results.append(logarithmic_fit(x, y))
                elif t == "power":
                    results.append(power_fit(x, y))
            except Exception as e:
                traceback.print_exc()
                results.append({
                    "type": t,
                    "formula": formulas.get(t, ""),
                    "error": f"Server error: {e}",
                    "steps": [],
                })

        # Choose best by highest R^2 among those without fatal error
        best_type = None
        best_r2 = float("-inf")
        for res in results:
            r2 = res.get("r2")
            err = res.get("error")
            if err is None and isinstance(r2, (int, float)) and r2 > best_r2:
                best_r2 = r2
                best_type = res.get("type")

        def to_native(obj):
            try:
                import numpy as np  # local import; optional dependency here
                np_generic = np.generic
            except Exception:  # pragma: no cover
                np_generic = tuple()

            if isinstance(obj, dict):
                return {str(k): to_native(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [to_native(v) for v in obj]
            if np_generic and isinstance(obj, np_generic):
                return obj.item()
            return obj

        safe_payload = to_native({
            "results": results,
            "bestType": best_type,
        })
        return jsonify(safe_payload)

    return app


app = create_app()

if __name__ == "__main__":
    # Development server
    app.run(host="127.0.0.1", port=5000, debug=True)



