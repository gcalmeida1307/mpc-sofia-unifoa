from __future__ import annotations

from hashlib import sha1
from typing import Any


_CACHE: dict[str, dict[str, Any]] = {}


def _cpu_supports_avx() -> bool:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as cpuinfo:
            return " avx " in f" {cpuinfo.read().lower()} "
    except OSError:
        return False


def _values(series: list[dict[str, Any]]) -> list[float]:
    values = [max(0.0, float(item.get("problems", 0) or 0)) for item in series]
    # A large discontinuity normally means a collector/limit change, not behavior.
    start = 0
    for index in range(1, len(values)):
        previous = max(values[index - 1], 1.0)
        if abs(values[index] - values[index - 1]) / previous > 0.5:
            start = index
    return values[start:]


def _collecting(method: str, samples: int, required: int) -> dict[str, Any]:
    return {"method": method, "status": "collecting", "samples": samples, "required_samples": required}


def analyze_problem_series(series: list[dict[str, Any]], *, seed: int = 42) -> dict[str, Any]:
    values = _values(series)
    fingerprint = sha1(repr(values).encode()).hexdigest()
    if fingerprint in _CACHE:
        return _CACHE[fingerprint]

    result: dict[str, Any] = {
        "quality": {"usable_samples": len(values), "discarded_samples": len(series) - len(values)},
        "random_forest": _collecting("Random Forest", len(values), 20),
        "monte_carlo": _collecting("Monte Carlo", len(values), 8),
        "tensorflow": (
            _collecting("TensorFlow", len(values), 24) if _cpu_supports_avx()
            else {"method": "TensorFlow", "status": "hardware_incompatible", "samples": len(values),
                  "reason": "CPU sem instrução AVX; execução bloqueada para proteger a API"}
        ),
    }
    if len(values) >= 8:
        import numpy as np

        rng = np.random.default_rng(seed)
        deltas = np.diff(np.asarray(values, dtype=float))
        low, high = np.quantile(deltas, [0.1, 0.9])
        robust = np.clip(deltas, low, high)
        paths = np.maximum(0, values[-1] + rng.choice(robust, size=(2000, 30), replace=True).cumsum(axis=1))
        final = paths[:, -1]
        result["monte_carlo"] = {"method": "Monte Carlo", "status": "ready", "samples": len(values),
            "simulations": 2000, "horizon_minutes": 60, "p10": round(float(np.quantile(final, .1)), 1),
            "median": round(float(np.quantile(final, .5)), 1), "p90": round(float(np.quantile(final, .9)), 1)}

    if len(values) >= 20:
        import numpy as np
        from sklearn.ensemble import RandomForestRegressor

        array = np.asarray(values, dtype=float)
        x = np.asarray([[index, array[index-1], array[index-2], array[index-3]] for index in range(3, len(array))])
        y = array[3:]
        model = RandomForestRegressor(n_estimators=80, max_depth=5, min_samples_leaf=2, random_state=seed, n_jobs=1)
        model.fit(x, y)
        prediction = max(0.0, float(model.predict([[len(array), array[-1], array[-2], array[-3]]])[0]))
        score = float(model.score(x, y)) if len(y) > 1 else 0.0
        result["random_forest"] = {"method": "Random Forest", "status": "ready", "samples": len(values),
            "next_prediction": round(prediction, 1), "fit_score": round(max(-1.0, min(1.0, score)), 3),
            "trees": 80}

    if len(values) >= 24 and _cpu_supports_avx():
        import os
        os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
        import numpy as np
        try:
            import tensorflow as tf
        except ImportError:
            result["tensorflow"] = {"method":"TensorFlow","status":"dependency_unavailable","samples":len(values),
                "reason":"instale requirements-tensorflow.txt em um host com AVX"}
            _CACHE.clear(); _CACHE[fingerprint] = result
            return result

        tf.keras.utils.set_random_seed(seed)
        tf.config.threading.set_intra_op_parallelism_threads(1)
        tf.config.threading.set_inter_op_parallelism_threads(1)
        array = np.asarray(values, dtype="float32")
        scale = max(float(array.max()), 1.0)
        normalized = array / scale
        x = np.asarray([normalized[index-4:index] for index in range(4, len(array))], dtype="float32")
        y = normalized[4:]
        model = tf.keras.Sequential([tf.keras.layers.Input((4,)), tf.keras.layers.Dense(8, activation="relu"), tf.keras.layers.Dense(1)])
        model.compile(optimizer=tf.keras.optimizers.Adam(.02), loss="mse")
        history = model.fit(x, y, epochs=35, batch_size=min(8, len(x)), verbose=0)
        prediction = max(0.0, float(model.predict(normalized[-4:].reshape(1, 4), verbose=0)[0][0] * scale))
        result["tensorflow"] = {"method": "TensorFlow", "status": "ready", "samples": len(values),
            "next_prediction": round(prediction, 1), "loss": round(float(history.history["loss"][-1]), 6),
            "architecture": "MLP 4→8→1"}

    _CACHE.clear()
    _CACHE[fingerprint] = result
    return result
