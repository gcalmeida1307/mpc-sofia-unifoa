from services.predictive_analytics import analyze_problem_series


def _series(values):
    return [{"generated_at": f"2026-08-05T12:{index:02d}:00+00:00", "problems": value} for index, value in enumerate(values)]


def test_models_wait_for_enough_clean_samples():
    result = analyze_problem_series(_series([200] * 20 + [596, 597]))
    assert result["quality"] == {"usable_samples": 2, "discarded_samples": 20}
    assert result["random_forest"]["status"] == "collecting"
    assert result["monte_carlo"]["status"] == "collecting"
    assert result["tensorflow"]["status"] in {"collecting", "hardware_incompatible"}


def test_monte_carlo_and_random_forest_produce_bounded_outputs():
    result = analyze_problem_series(_series([500 + (index % 5) * 3 for index in range(20)]))
    assert result["monte_carlo"]["status"] == "ready"
    assert result["monte_carlo"]["p10"] <= result["monte_carlo"]["median"] <= result["monte_carlo"]["p90"]
    assert result["random_forest"]["status"] == "ready"
    assert result["random_forest"]["trees"] == 80
    assert result["tensorflow"]["status"] in {"collecting", "hardware_incompatible"}


def test_tensorflow_small_model_is_enabled_after_24_samples(monkeypatch):
    monkeypatch.setattr("services.predictive_analytics._cpu_supports_avx", lambda: False)
    result = analyze_problem_series(_series([500 + (index % 6) * 2 for index in range(24)]))
    assert result["tensorflow"]["status"] == "hardware_incompatible"
    assert "AVX" in result["tensorflow"]["reason"]
