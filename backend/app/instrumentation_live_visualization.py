from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

VERSION = "0.25.2"
ENGINE_VERSION = "0.25.0"
PRODUCTION_VERSION = "0.25.1"
CONTRACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "contracts"
    / "instrumentation-live-visualization-v0252.json"
)


class LiveVisualizationError(ValueError):
    """Raised when live visualization input is invalid."""


def contract() -> dict[str, Any]:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise LiveVisualizationError(f"{label} must be numerical.") from exc
    if not math.isfinite(number):
        raise LiveVisualizationError(f"{label} must be finite.")
    return number


def _positive(value: Any, label: str) -> float:
    number = _finite(value, label)
    if number <= 0:
        raise LiveVisualizationError(f"{label} must be greater than zero.")
    return number


def _records(value: Any, label: str = "records") -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise LiveVisualizationError(f"{label} must be an array.")
    result: list[dict[str, Any]] = []
    for index, record in enumerate(value):
        if not isinstance(record, dict):
            raise LiveVisualizationError(f"{label}[{index}] must be an object.")
        normalized = dict(record)
        normalized["timestamp"] = _finite(record.get("timestamp"), f"{label}[{index}].timestamp")
        if "value" in record:
            normalized["value"] = _finite(record.get("value"), f"{label}[{index}].value")
        result.append(normalized)
    return result


def _values(value: Any, label: str = "values") -> list[float]:
    if not isinstance(value, list) or not value:
        raise LiveVisualizationError(f"{label} must be a non-empty array.")
    return [_finite(item, f"{label}[{index}]") for index, item in enumerate(value)]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _sd(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    average = _mean(values)
    return math.sqrt(
        sum((value - average) ** 2 for value in values)
        / (len(values) - 1)
    )


def append_ring_buffer(
    existing: Any,
    incoming: Any,
    maximum_points: Any,
) -> list[dict[str, Any]]:
    prior = _records(existing, "existing")
    added = _records(incoming, "incoming")
    maximum = int(_positive(maximum_points, "maximumPoints"))
    combined = sorted(prior + added, key=lambda item: item["timestamp"])
    return combined[-maximum:]


def trim_time_window(
    points: Any,
    window_start: Any,
    window_end: Any,
) -> list[dict[str, Any]]:
    records = _records(points, "points")
    start = _finite(window_start, "windowStart")
    end = _finite(window_end, "windowEnd")
    if end < start:
        raise LiveVisualizationError("windowEnd must be at least windowStart.")
    return [record for record in records if start <= record["timestamp"] <= end]


def channel_summary(values: Any) -> dict[str, Any]:
    numbers = _values(values)
    return {
        "count": len(numbers),
        "mean": _mean(numbers),
        "standardDeviation": _sd(numbers),
        "minimum": min(numbers),
        "maximum": max(numbers),
        "range": max(numbers) - min(numbers),
        "latest": numbers[-1],
    }


def latest_channel_values(records: Any) -> dict[str, dict[str, Any]]:
    normalized = _records(records)
    latest: dict[str, dict[str, Any]] = {}
    for record in normalized:
        channel = str(record.get("channel") or "")
        if not channel:
            continue
        if channel not in latest or record["timestamp"] >= latest[channel]["timestamp"]:
            latest[channel] = record
    return latest


def threshold_status(
    value: Any,
    warning_low: Any,
    warning_high: Any,
    action_low: Any,
    action_high: Any,
) -> str:
    number = _finite(value, "value")
    wl = _finite(warning_low, "warningLow")
    wh = _finite(warning_high, "warningHigh")
    al = _finite(action_low, "actionLow")
    ah = _finite(action_high, "actionHigh")
    if not (al <= wl <= wh <= ah):
        raise LiveVisualizationError(
            "Thresholds must satisfy actionLow <= warningLow <= warningHigh <= actionHigh."
        )
    if number < al or number > ah:
        return "action"
    if number < wl or number > wh:
        return "warning"
    return "normal"


def detect_threshold_events(records: Any, thresholds: Any) -> list[dict[str, Any]]:
    normalized = _records(records)
    if not isinstance(thresholds, dict):
        raise LiveVisualizationError("thresholds must be an object.")
    events: list[dict[str, Any]] = []
    previous_status: dict[str, str] = {}
    for record in normalized:
        channel = str(record.get("channel") or "")
        definition = thresholds.get(channel)
        if not channel or not isinstance(definition, dict):
            continue
        status = threshold_status(
            record.get("value"),
            definition.get("warningLow"),
            definition.get("warningHigh"),
            definition.get("actionLow"),
            definition.get("actionHigh"),
        )
        if status != "normal" and status != previous_status.get(channel):
            events.append(
                {
                    "type": status,
                    "channel": channel,
                    "timestamp": record["timestamp"],
                    "value": record["value"],
                    "message": f"{channel} entered {status} range.",
                }
            )
        previous_status[channel] = status
    return events


def detect_gap_events(records: Any, maximum_gap_seconds: Any) -> list[dict[str, Any]]:
    normalized = sorted(_records(records), key=lambda item: (str(item.get("channel") or ""), item["timestamp"]))
    maximum = _positive(maximum_gap_seconds, "maximumGapSeconds")
    previous: dict[str, float] = {}
    events: list[dict[str, Any]] = []
    for record in normalized:
        channel = str(record.get("channel") or "")
        if not channel:
            continue
        if channel in previous:
            gap = record["timestamp"] - previous[channel]
            if gap > maximum:
                events.append(
                    {
                        "type": "gap",
                        "channel": channel,
                        "timestamp": record["timestamp"],
                        "gapSeconds": gap,
                    }
                )
        previous[channel] = record["timestamp"]
    return events


def rolling_mean_series(values: Any, window_size: Any) -> list[float]:
    numbers = _values(values)
    window = int(_positive(window_size, "windowSize"))
    return [
        _mean(numbers[max(0, index - window + 1): index + 1])
        for index in range(len(numbers))
    ]


def rolling_sd_series(values: Any, window_size: Any) -> list[float]:
    numbers = _values(values)
    window = int(_positive(window_size, "windowSize"))
    return [
        _sd(numbers[max(0, index - window + 1): index + 1])
        for index in range(len(numbers))
    ]


def exponential_smoothing_series(values: Any, alpha: Any) -> list[float]:
    numbers = _values(values)
    weight = _finite(alpha, "alpha")
    if not 0 < weight <= 1:
        raise LiveVisualizationError("alpha must be greater than zero and at most one.")
    smoothed = [numbers[0]]
    for value in numbers[1:]:
        smoothed.append(weight * value + (1 - weight) * smoothed[-1])
    return smoothed


def min_max_downsample(points: Any, bucket_count: Any) -> list[dict[str, Any]]:
    records = sorted(_records(points, "points"), key=lambda item: item["timestamp"])
    buckets = int(_positive(bucket_count, "bucketCount"))
    if buckets >= len(records):
        return records
    output: list[dict[str, Any]] = []
    for bucket in range(buckets):
        start = math.floor(bucket * len(records) / buckets)
        end = math.floor((bucket + 1) * len(records) / buckets)
        group = records[start:max(start + 1, end)]
        minimum = min(group, key=lambda item: item["value"])
        maximum = max(group, key=lambda item: item["value"])
        for item in sorted({id(minimum): minimum, id(maximum): maximum}.values(), key=lambda entry: entry["timestamp"]):
            output.append(item)
    return output


def align_channels(
    reference: Any,
    comparison: Any,
    tolerance_seconds: Any,
) -> list[dict[str, Any]]:
    left = sorted(_records(reference, "reference"), key=lambda item: item["timestamp"])
    right = sorted(_records(comparison, "comparison"), key=lambda item: item["timestamp"])
    tolerance = _positive(tolerance_seconds, "toleranceSeconds")
    matches: list[dict[str, Any]] = []
    used: set[int] = set()
    for reference_point in left:
        candidates = [
            (abs(point["timestamp"] - reference_point["timestamp"]), index, point)
            for index, point in enumerate(right)
            if index not in used
            and abs(point["timestamp"] - reference_point["timestamp"]) <= tolerance
        ]
        if not candidates:
            continue
        _, index, point = min(candidates, key=lambda item: item[0])
        used.add(index)
        matches.append(
            {
                "timestamp": reference_point["timestamp"],
                "referenceValue": reference_point["value"],
                "comparisonValue": point["value"],
                "timeDeltaSeconds": point["timestamp"] - reference_point["timestamp"],
            }
        )
    return matches


def common_time_window(series: Any) -> dict[str, float | None]:
    if not isinstance(series, list) or not series:
        raise LiveVisualizationError("series must be a non-empty array.")
    normalized = [_records(item, f"series[{index}]") for index, item in enumerate(series)]
    if any(not item for item in normalized):
        return {"start": None, "end": None, "durationSeconds": 0.0}
    start = max(min(point["timestamp"] for point in item) for item in normalized)
    end = min(max(point["timestamp"] for point in item) for item in normalized)
    return {
        "start": start,
        "end": end,
        "durationSeconds": max(0.0, end - start),
    }


def event_rate(event_count: Any, duration_seconds: Any) -> float:
    return _finite(event_count, "eventCount") * 60 / _positive(duration_seconds, "durationSeconds")


def connection_uptime(online_seconds: Any, total_seconds: Any) -> float:
    total = _positive(total_seconds, "totalSeconds")
    online = _finite(online_seconds, "onlineSeconds")
    return max(0.0, min(100.0, online / total * 100))


def dashboard_summary(records: Any, events: Any, connection_state: Any) -> dict[str, Any]:
    normalized = _records(records)
    if not isinstance(events, list):
        raise LiveVisualizationError("events must be an array.")
    by_channel: dict[str, list[float]] = {}
    for record in normalized:
        channel = str(record.get("channel") or "")
        if channel:
            by_channel.setdefault(channel, []).append(record["value"])
    return {
        "recordCount": len(normalized),
        "channelCount": len(by_channel),
        "eventCount": len(events),
        "connectionState": str(connection_state),
        "latest": latest_channel_values(normalized),
        "channels": {
            channel: channel_summary(values)
            for channel, values in by_channel.items()
        },
        "eventTypeCounts": {
            event_type: sum(1 for event in events if event.get("type") == event_type)
            for event_type in sorted({str(event.get("type") or "") for event in events})
            if event_type
        },
    }


def execute(method_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
    i = inputs or {}
    dispatch = {
        "append-ring-buffer": lambda: append_ring_buffer(i.get("existing", []), i.get("incoming", []), i.get("maximumPoints")),
        "trim-time-window": lambda: trim_time_window(i.get("points", []), i.get("windowStart"), i.get("windowEnd")),
        "channel-summary": lambda: channel_summary(i.get("values")),
        "latest-channel-values": lambda: latest_channel_values(i.get("records", [])),
        "threshold-status": lambda: threshold_status(i.get("value"), i.get("warningLow"), i.get("warningHigh"), i.get("actionLow"), i.get("actionHigh")),
        "detect-threshold-events": lambda: detect_threshold_events(i.get("records", []), i.get("thresholds", {})),
        "detect-gap-events": lambda: detect_gap_events(i.get("records", []), i.get("maximumGapSeconds")),
        "rolling-mean-series": lambda: rolling_mean_series(i.get("values"), i.get("windowSize")),
        "rolling-sd-series": lambda: rolling_sd_series(i.get("values"), i.get("windowSize")),
        "exponential-smoothing-series": lambda: exponential_smoothing_series(i.get("values"), i.get("alpha")),
        "min-max-downsample": lambda: min_max_downsample(i.get("points", []), i.get("bucketCount")),
        "align-channels": lambda: align_channels(i.get("reference", []), i.get("comparison", []), i.get("toleranceSeconds")),
        "common-time-window": lambda: common_time_window(i.get("series", [])),
        "event-rate": lambda: event_rate(i.get("eventCount"), i.get("durationSeconds")),
        "connection-uptime": lambda: connection_uptime(i.get("onlineSeconds"), i.get("totalSeconds")),
        "dashboard-summary": lambda: dashboard_summary(i.get("records", []), i.get("events", []), i.get("connectionState", "disconnected")),
    }
    if method_id not in dispatch:
        raise LiveVisualizationError(f"Unknown live visualization method: {method_id}")
    return {
        "schema": "sc-lab-instrumentation-live-analysis/1.0",
        "version": VERSION,
        "methodId": method_id,
        "inputs": inputs,
        "value": dispatch[method_id](),
    }


def build_snapshot(
    records: Any,
    thresholds: Any = None,
    maximum_gap_seconds: Any = 10,
    connection_state: Any = "disconnected",
) -> dict[str, Any]:
    normalized = _records(records)
    threshold_events = detect_threshold_events(normalized, thresholds or {})
    gap_events = detect_gap_events(normalized, maximum_gap_seconds) if normalized else []
    events = threshold_events + gap_events
    return {
        "schema": "sc-lab-instrumentation-live-snapshot/1.0",
        "version": VERSION,
        "createdFromRecordCount": len(normalized),
        "events": events,
        "summary": dashboard_summary(normalized, events, connection_state),
        "records": normalized,
    }
