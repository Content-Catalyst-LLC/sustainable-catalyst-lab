from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

VERSION = "0.23.2"
CONTRACT_PATH = (
    Path(__file__).resolve().parents[1]
    / "contracts"
    / "biosignal-visualization-comparison-v0232.json"
)


class BiosignalVisualizationError(ValueError):
    """Raised when visualization/comparison input is invalid."""


def contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise BiosignalVisualizationError(f"{label} must be numerical.") from exc
    if not math.isfinite(number):
        raise BiosignalVisualizationError(f"{label} must be finite.")
    return number


def _positive(value: Any, label: str) -> float:
    number = _finite(value, label)
    if number <= 0:
        raise BiosignalVisualizationError(f"{label} must be greater than zero.")
    return number


def _values(value: Any, label: str, minimum: int = 1) -> list[float]:
    if not isinstance(value, list):
        raise BiosignalVisualizationError(f"{label} must be an array.")
    result = [_finite(item, f"{label}[{index}]") for index, item in enumerate(value)]
    if len(result) < minimum:
        raise BiosignalVisualizationError(f"{label} requires at least {minimum} values.")
    return result


def _paired(left: Any, right: Any) -> tuple[list[float], list[float]]:
    a = _values(left, "reference", 2)
    b = _values(right, "comparison", 2)
    if len(a) != len(b):
        raise BiosignalVisualizationError("reference and comparison must have equal length.")
    return a, b


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _sd(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    average = _mean(values)
    return math.sqrt(sum((value - average) ** 2 for value in values) / (len(values) - 1))


def _rms(values: list[float]) -> float:
    return math.sqrt(_mean([value * value for value in values]))


def descriptive_features(samples: Any, sample_rate_hz: Any = 1) -> dict[str, Any]:
    values = _values(samples, "samples", 2)
    rate = _positive(sample_rate_hz, "sampleRateHz")
    average = _mean(values)
    root_mean_square = _rms(values)
    crossings = sum(
        1 for index in range(1, len(values))
        if (values[index - 1] < 0 <= values[index]) or (values[index - 1] >= 0 > values[index])
    )
    return {
        "sampleCount": len(values),
        "sampleRateHz": rate,
        "durationSeconds": (len(values) - 1) / rate,
        "mean": average,
        "standardDeviation": _sd(values),
        "rms": root_mean_square,
        "minimum": min(values),
        "maximum": max(values),
        "peakToPeak": max(values) - min(values),
        "zeroCrossingCount": crossings,
        "zeroCrossingRate": crossings / (len(values) - 1) * rate,
        "crestFactor": max(abs(value) for value in values) / root_mean_square if root_mean_square else 0.0,
    }


def min_max_normalize(samples: Any) -> list[float]:
    values = _values(samples, "samples")
    minimum = min(values)
    span = max(values) - minimum
    if span == 0:
        return [0.0 for _ in values]
    return [(value - minimum) / span for value in values]


def z_score_normalize(samples: Any) -> list[float]:
    values = _values(samples, "samples", 2)
    average = _mean(values)
    deviation = _sd(values)
    if deviation == 0:
        return [0.0 for _ in values]
    return [(value - average) / deviation for value in values]


def moving_average(samples: Any, window_size: Any) -> list[float]:
    values = _values(samples, "samples")
    window = int(_positive(window_size, "windowSize"))
    if window > len(values):
        raise BiosignalVisualizationError("windowSize cannot exceed the sample count.")
    return [_mean(values[max(0, index - window + 1):index + 1]) for index in range(len(values))]


def linear_resample(samples: Any, source_rate_hz: Any, target_rate_hz: Any) -> list[float]:
    values = _values(samples, "samples", 2)
    source_rate = _positive(source_rate_hz, "sourceRateHz")
    target_rate = _positive(target_rate_hz, "targetRateHz")
    duration = (len(values) - 1) / source_rate
    target_count = max(2, int(round(duration * target_rate)) + 1)
    result: list[float] = []
    for index in range(target_count):
        position = (index / target_rate) * source_rate
        left = min(len(values) - 1, int(math.floor(position)))
        right = min(len(values) - 1, left + 1)
        fraction = position - left
        result.append(values[left] + (values[right] - values[left]) * fraction)
    return result


def pearson_correlation(reference: Any, comparison: Any) -> float:
    a, b = _paired(reference, comparison)
    a_mean = _mean(a)
    b_mean = _mean(b)
    numerator = sum((x - a_mean) * (y - b_mean) for x, y in zip(a, b))
    denominator = math.sqrt(
        sum((x - a_mean) ** 2 for x in a)
        * sum((y - b_mean) ** 2 for y in b)
    )
    if denominator == 0:
        raise BiosignalVisualizationError("Correlation requires non-constant arrays.")
    return numerator / denominator


def mean_absolute_error(reference: Any, comparison: Any) -> float:
    a, b = _paired(reference, comparison)
    return _mean([abs(x - y) for x, y in zip(a, b)])


def root_mean_square_error(reference: Any, comparison: Any) -> float:
    a, b = _paired(reference, comparison)
    return math.sqrt(_mean([(x - y) ** 2 for x, y in zip(a, b)]))


def normalized_rmse(reference: Any, comparison: Any) -> float:
    a, b = _paired(reference, comparison)
    span = max(a) - min(a)
    if span == 0:
        raise BiosignalVisualizationError("Normalized RMSE requires a non-zero reference range.")
    return root_mean_square_error(a, b) / span


def shift_series(reference: Any, comparison: Any, lag_samples: Any) -> dict[str, Any]:
    a, b = _paired(reference, comparison)
    lag = int(_finite(lag_samples, "lagSamples"))
    if abs(lag) >= len(a) - 1:
        raise BiosignalVisualizationError("Absolute lag must leave at least two overlapping samples.")
    if lag > 0:
        aligned_a, aligned_b = a[lag:], b[:-lag]
    elif lag < 0:
        aligned_a, aligned_b = a[:lag], b[-lag:]
    else:
        aligned_a, aligned_b = a, b
    return {"lagSamples": lag, "reference": aligned_a, "comparison": aligned_b, "overlapCount": len(aligned_a)}


def best_lag_correlation(reference: Any, comparison: Any, max_lag_samples: Any) -> dict[str, Any]:
    a, b = _paired(reference, comparison)
    maximum = int(_finite(max_lag_samples, "maxLagSamples"))
    maximum = min(abs(maximum), len(a) - 2)
    results: list[dict[str, Any]] = []
    for lag in range(-maximum, maximum + 1):
        aligned = shift_series(a, b, lag)
        try:
            correlation = pearson_correlation(aligned["reference"], aligned["comparison"])
        except BiosignalVisualizationError:
            correlation = 0.0
        results.append({"lagSamples": lag, "correlation": correlation, "overlapCount": aligned["overlapCount"]})
    best = max(results, key=lambda item: (abs(item["correlation"]), -abs(item["lagSamples"])))
    return {"bestLagSamples": best["lagSamples"], "bestCorrelation": best["correlation"], "overlapCount": best["overlapCount"], "scan": results}


def event_rate(event_count: Any, duration_seconds: Any) -> float:
    return _finite(event_count, "eventCount") * 60 / _positive(duration_seconds, "durationSeconds")


def interval_summary(intervals: Any) -> dict[str, Any]:
    if not isinstance(intervals, list) or not intervals:
        raise BiosignalVisualizationError("intervals must contain at least one interval.")
    durations: list[float] = []
    starts: list[float] = []
    ends: list[float] = []
    for index, interval in enumerate(intervals):
        if not isinstance(interval, dict):
            raise BiosignalVisualizationError(f"intervals[{index}] must be an object.")
        start = _finite(interval.get("startSeconds"), f"intervals[{index}].startSeconds")
        end = _finite(interval.get("endSeconds"), f"intervals[{index}].endSeconds")
        if end < start:
            raise BiosignalVisualizationError(f"intervals[{index}] ends before it starts.")
        starts.append(start); ends.append(end); durations.append(end - start)
    span = max(ends) - min(starts)
    return {
        "intervalCount": len(intervals),
        "totalDurationSeconds": sum(durations),
        "meanDurationSeconds": _mean(durations),
        "minimumDurationSeconds": min(durations),
        "maximumDurationSeconds": max(durations),
        "coveredSpanSeconds": span,
        "burdenPercent": sum(durations) / span * 100 if span > 0 else 0.0,
    }


def annotation_coverage(annotations: Any, window_start_seconds: Any, window_end_seconds: Any) -> dict[str, Any]:
    if not isinstance(annotations, list):
        raise BiosignalVisualizationError("annotations must be an array.")
    start = _finite(window_start_seconds, "windowStartSeconds")
    end = _finite(window_end_seconds, "windowEndSeconds")
    if end <= start:
        raise BiosignalVisualizationError("windowEndSeconds must exceed windowStartSeconds.")
    clipped: list[tuple[float, float]] = []
    type_counts: dict[str, int] = {}
    for index, annotation in enumerate(annotations):
        if not isinstance(annotation, dict):
            raise BiosignalVisualizationError(f"annotations[{index}] must be an object.")
        a_start = _finite(annotation.get("startSeconds"), f"annotations[{index}].startSeconds")
        a_end = _finite(annotation.get("endSeconds", a_start), f"annotations[{index}].endSeconds")
        if a_end < a_start:
            raise BiosignalVisualizationError(f"annotations[{index}] ends before it starts.")
        clipped_start = max(start, a_start)
        clipped_end = min(end, a_end)
        if clipped_end > clipped_start:
            clipped.append((clipped_start, clipped_end))
        annotation_type = str(annotation.get("type") or "note")
        type_counts[annotation_type] = type_counts.get(annotation_type, 0) + 1
    clipped.sort()
    merged: list[list[float]] = []
    for interval_start, interval_end in clipped:
        if not merged or interval_start > merged[-1][1]:
            merged.append([interval_start, interval_end])
        else:
            merged[-1][1] = max(merged[-1][1], interval_end)
    covered = sum(interval_end - interval_start for interval_start, interval_end in merged)
    return {
        "annotationCount": len(annotations),
        "coveredSeconds": covered,
        "coveragePercent": covered / (end - start) * 100,
        "typeCounts": type_counts,
        "mergedIntervals": [{"startSeconds": item[0], "endSeconds": item[1]} for item in merged],
    }


def common_time_window(run_a: Any, run_b: Any) -> dict[str, Any]:
    if not isinstance(run_a, dict) or not isinstance(run_b, dict):
        raise BiosignalVisualizationError("runA and runB must be objects.")
    a_start = _finite(run_a.get("startSeconds", 0), "runA.startSeconds")
    b_start = _finite(run_b.get("startSeconds", 0), "runB.startSeconds")
    a_duration = _positive(run_a.get("durationSeconds"), "runA.durationSeconds")
    b_duration = _positive(run_b.get("durationSeconds"), "runB.durationSeconds")
    start = max(a_start, b_start)
    end = min(a_start + a_duration, b_start + b_duration)
    return {"startSeconds": start, "endSeconds": end, "durationSeconds": max(0.0, end - start), "overlap": end > start}


def compare_runs(reference: Any, comparison: Any, sample_rate_hz: Any = 1) -> dict[str, Any]:
    a, b = _paired(reference, comparison)
    return {
        "sampleCount": len(a),
        "sampleRateHz": _positive(sample_rate_hz, "sampleRateHz"),
        "correlation": pearson_correlation(a, b),
        "meanAbsoluteError": mean_absolute_error(a, b),
        "rootMeanSquareError": root_mean_square_error(a, b),
        "normalizedRootMeanSquareError": normalized_rmse(a, b),
        "referenceFeatures": descriptive_features(a, sample_rate_hz),
        "comparisonFeatures": descriptive_features(b, sample_rate_hz),
    }


def execute(method_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
    operation = method_id
    i = inputs or {}
    if operation == "descriptive-features": value = descriptive_features(i.get("samples"), i.get("sampleRateHz", 1))
    elif operation == "min-max-normalize": value = min_max_normalize(i.get("samples"))
    elif operation == "z-score-normalize": value = z_score_normalize(i.get("samples"))
    elif operation == "moving-average": value = moving_average(i.get("samples"), i.get("windowSize"))
    elif operation == "linear-resample": value = linear_resample(i.get("samples"), i.get("sourceRateHz"), i.get("targetRateHz"))
    elif operation == "pearson-correlation": value = pearson_correlation(i.get("reference"), i.get("comparison"))
    elif operation == "mean-absolute-error": value = mean_absolute_error(i.get("reference"), i.get("comparison"))
    elif operation == "root-mean-square-error": value = root_mean_square_error(i.get("reference"), i.get("comparison"))
    elif operation == "normalized-rmse": value = normalized_rmse(i.get("reference"), i.get("comparison"))
    elif operation == "shift-series": value = shift_series(i.get("reference"), i.get("comparison"), i.get("lagSamples"))
    elif operation == "best-lag-correlation": value = best_lag_correlation(i.get("reference"), i.get("comparison"), i.get("maxLagSamples"))
    elif operation == "event-rate": value = event_rate(i.get("eventCount"), i.get("durationSeconds"))
    elif operation == "interval-summary": value = interval_summary(i.get("intervals"))
    elif operation == "annotation-coverage": value = annotation_coverage(i.get("annotations"), i.get("windowStartSeconds"), i.get("windowEndSeconds"))
    elif operation == "common-time-window": value = common_time_window(i.get("runA"), i.get("runB"))
    elif operation == "compare-runs": value = compare_runs(i.get("reference"), i.get("comparison"), i.get("sampleRateHz", 1))
    else: raise BiosignalVisualizationError(f"Unknown visualization analysis method: {method_id}")
    return {"schema":"sc-lab-biosignal-visualization-result/1.0","version":VERSION,"methodId":method_id,"inputs":inputs,"value":value}
