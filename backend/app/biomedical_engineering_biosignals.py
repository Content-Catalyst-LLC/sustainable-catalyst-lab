from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

VERSION = "0.23.0"
CONTRACT_PATH = (
    Path(__file__).resolve().parents[1]
    / "contracts"
    / "biomedical-engineering-biosignals-v0230.json"
)


class BiosignalError(ValueError):
    """Raised when biosignal calculation input is invalid."""


def catalog() -> dict[str, Any]:
    return json.loads(
        CONTRACT_PATH.read_text(encoding="utf-8")
    )


def _finite(value: Any, label: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise BiosignalError(
            f"{label} must be numerical."
        ) from exc

    if not math.isfinite(number):
        raise BiosignalError(
            f"{label} must be finite."
        )

    return number


def _positive(value: Any, label: str) -> float:
    number = _finite(value, label)

    if number <= 0:
        raise BiosignalError(
            f"{label} must be greater than zero."
        )

    return number


def _values(value: Any, label: str, minimum: int = 1) -> list[float]:
    if not isinstance(value, list):
        raise BiosignalError(
            f"{label} must be an array."
        )

    numbers = [
        _finite(item, f"{label}[{index}]")
        for index, item in enumerate(value)
    ]

    if len(numbers) < minimum:
        raise BiosignalError(
            f"{label} requires at least {minimum} values."
        )

    return numbers


def _mean(values: list[float]) -> float:
    return sum(values) / len(values)


def _sd(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0

    average = _mean(values)

    return math.sqrt(
        sum(
            (value - average) ** 2
            for value in values
        )
        / (len(values) - 1)
    )


def _rms(values: list[float]) -> float:
    return math.sqrt(
        _mean([value * value for value in values])
    )


def _paired(
    left: Any,
    right: Any,
    left_label: str,
    right_label: str,
) -> tuple[list[float], list[float]]:
    a = _values(left, left_label)
    b = _values(right, right_label)

    if len(a) != len(b):
        raise BiosignalError(
            f"{left_label} and {right_label} must have equal length."
        )

    return a, b


def execute(method_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
    definitions = {
        item["id"]: item
        for item in catalog()["methods"]
    }

    if method_id not in definitions:
        raise BiosignalError(
            f"Unknown biosignal method: {method_id}"
        )

    method = definitions[method_id]
    operation = method["operation"]
    i = inputs or {}

    if operation == "sampling_interval_ms":
        result = 1000 / _positive(i.get("sampleRateHz"), "sampleRateHz")
    elif operation == "nyquist_frequency":
        result = _positive(i.get("sampleRateHz"), "sampleRateHz") / 2
    elif operation == "sample_count":
        result = round(_finite(i.get("durationSeconds"), "durationSeconds") * _positive(i.get("sampleRateHz"), "sampleRateHz"))
    elif operation == "duration_from_samples":
        result = _finite(i.get("sampleCount"), "sampleCount") / _positive(i.get("sampleRateHz"), "sampleRateHz")
    elif operation == "adc_levels":
        bits = int(_positive(i.get("bits"), "bits"))
        result = 2 ** bits
    elif operation == "quantization_step":
        bits = int(_positive(i.get("bits"), "bits"))
        result = _positive(i.get("inputRange"), "inputRange") / ((2 ** bits) - 1)
    elif operation == "heart_rate_from_rr":
        result = 60 / _positive(i.get("rrSeconds"), "rrSeconds")
    elif operation == "rr_from_heart_rate":
        result = 60 / _positive(i.get("heartRateBpm"), "heartRateBpm")
    elif operation == "qtc_bazett":
        result = _finite(i.get("qtSeconds"), "qtSeconds") / math.sqrt(_positive(i.get("rrSeconds"), "rrSeconds"))
    elif operation == "qtc_fridericia":
        result = _finite(i.get("qtSeconds"), "qtSeconds") / (_positive(i.get("rrSeconds"), "rrSeconds") ** (1 / 3))
    elif operation == "ecg_axis_angle":
        result = math.degrees(math.atan2(_finite(i.get("yComponent"), "yComponent"), _finite(i.get("xComponent"), "xComponent")))
    elif operation == "hrv_rmssd":
        values = _values(i.get("rrIntervalsMs"), "rrIntervalsMs", 2)
        result = math.sqrt(_mean([(values[index] - values[index - 1]) ** 2 for index in range(1, len(values))]))
    elif operation == "hrv_sdnn":
        result = _sd(_values(i.get("rrIntervalsMs"), "rrIntervalsMs", 2))
    elif operation == "pulse_rate_from_interval":
        result = 60 / _positive(i.get("pulseIntervalSeconds"), "pulseIntervalSeconds")
    elif operation == "perfusion_index":
        result = _finite(i.get("acAmplitude"), "acAmplitude") / _positive(i.get("dcLevel"), "dcLevel") * 100
    elif operation == "spo2_ratio_estimate":
        ratio = (
            _finite(i.get("acRed"), "acRed")
            / _positive(i.get("dcRed"), "dcRed")
        ) / (
            _positive(i.get("acInfrared"), "acInfrared")
            / _positive(i.get("dcInfrared"), "dcInfrared")
        )
        result = max(0.0, min(100.0, 110 - 25 * ratio))
    elif operation == "pulse_transit_time":
        result = _finite(i.get("distalTimeSeconds"), "distalTimeSeconds") - _finite(i.get("proximalTimeSeconds"), "proximalTimeSeconds")
    elif operation == "pulse_wave_velocity":
        result = _finite(i.get("distanceMeters"), "distanceMeters") / _positive(i.get("transitTimeSeconds"), "transitTimeSeconds")
    elif operation == "respiratory_rate":
        result = 60 / _positive(i.get("breathIntervalSeconds"), "breathIntervalSeconds")
    elif operation == "minute_ventilation":
        result = _finite(i.get("tidalVolumeLiters"), "tidalVolumeLiters") * _finite(i.get("respiratoryRate"), "respiratoryRate")
    elif operation == "ie_ratio":
        result = _finite(i.get("inspirationSeconds"), "inspirationSeconds") / _positive(i.get("expirationSeconds"), "expirationSeconds")
    elif operation == "inspiratory_duty_cycle":
        inspiration = _finite(i.get("inspirationSeconds"), "inspirationSeconds")
        expiration = _finite(i.get("expirationSeconds"), "expirationSeconds")
        denominator = inspiration + expiration
        if denominator <= 0:
            raise BiosignalError("The respiratory cycle duration must be greater than zero.")
        result = inspiration / denominator * 100
    elif operation == "apnea_burden":
        result = _finite(i.get("apneaSeconds"), "apneaSeconds") / _positive(i.get("recordingSeconds"), "recordingSeconds") * 100
    elif operation == "integrated_respiratory_volume":
        result = _finite(i.get("meanFlowLitersPerSecond"), "meanFlowLitersPerSecond") * _finite(i.get("durationSeconds"), "durationSeconds")
    elif operation == "emg_rms":
        result = _rms(_values(i.get("samples"), "samples"))
    elif operation == "emg_mav":
        result = _mean([abs(value) for value in _values(i.get("samples"), "samples")])
    elif operation == "integrated_emg":
        result = sum(abs(value) for value in _values(i.get("samples"), "samples")) * _finite(i.get("sampleIntervalSeconds"), "sampleIntervalSeconds")
    elif operation == "emg_waveform_length":
        values = _values(i.get("samples"), "samples", 2)
        result = sum(abs(values[index] - values[index - 1]) for index in range(1, len(values)))
    elif operation == "zero_crossing_rate":
        values = _values(i.get("samples"), "samples", 2)
        crossings = sum(1 for index in range(1, len(values)) if (values[index - 1] < 0 <= values[index]) or (values[index - 1] >= 0 > values[index]))
        result = crossings / (len(values) - 1) * _positive(i.get("sampleRateHz"), "sampleRateHz")
    elif operation == "peak_to_peak":
        values = _values(i.get("samples"), "samples")
        result = max(values) - min(values)
    elif operation == "crest_factor":
        values = _values(i.get("samples"), "samples")
        root_mean_square = _rms(values)
        result = max(abs(value) for value in values) / root_mean_square if root_mean_square else 0.0
    elif operation == "absolute_band_power":
        frequencies, powers = _paired(i.get("frequenciesHz"), i.get("powerValues"), "frequenciesHz", "powerValues")
        low = _finite(i.get("lowHz"), "lowHz")
        high = _finite(i.get("highHz"), "highHz")
        width = _positive(i.get("binWidthHz"), "binWidthHz")
        result = sum(power for frequency, power in zip(frequencies, powers) if low <= frequency <= high) * width
    elif operation == "relative_band_power":
        result = _finite(i.get("bandPower"), "bandPower") / _positive(i.get("totalPower"), "totalPower") * 100
    elif operation == "alpha_beta_ratio":
        result = _finite(i.get("alphaPower"), "alphaPower") / _positive(i.get("betaPower"), "betaPower")
    elif operation == "theta_beta_ratio":
        result = _finite(i.get("thetaPower"), "thetaPower") / _positive(i.get("betaPower"), "betaPower")
    elif operation == "spectral_centroid":
        frequencies, powers = _paired(i.get("frequenciesHz"), i.get("powerValues"), "frequenciesHz", "powerValues")
        total = sum(powers)
        if total <= 0:
            raise BiosignalError("powerValues must contain positive total power.")
        result = sum(frequency * power for frequency, power in zip(frequencies, powers)) / total
    elif operation == "spectral_entropy":
        powers = _values(i.get("powerValues"), "powerValues", 2)
        total = sum(powers)
        if total <= 0:
            raise BiosignalError("powerValues must contain positive total power.")
        probabilities = [power / total for power in powers if power > 0]
        result = -sum(probability * math.log2(probability) for probability in probabilities) / math.log2(len(powers))
    elif operation == "dominant_frequency":
        frequencies, powers = _paired(i.get("frequenciesHz"), i.get("powerValues"), "frequenciesHz", "powerValues")
        result = frequencies[max(range(len(powers)), key=powers.__getitem__)]
    elif operation == "hemispheric_asymmetry":
        left = _finite(i.get("leftPower"), "leftPower")
        right = _finite(i.get("rightPower"), "rightPower")
        denominator = right + left
        if denominator == 0:
            raise BiosignalError("leftPower and rightPower cannot both be zero.")
        result = (right - left) / denominator * 100
    elif operation == "rc_cutoff":
        result = 1 / (2 * math.pi * _positive(i.get("resistanceOhms"), "resistanceOhms") * _positive(i.get("capacitanceFarads"), "capacitanceFarads"))
    elif operation == "moving_average_latest":
        values = _values(i.get("samples"), "samples")
        window = int(_positive(i.get("windowSize"), "windowSize"))
        if window > len(values):
            raise BiosignalError("windowSize cannot exceed the sample count.")
        result = _mean(values[-window:])
    elif operation == "exponential_smoothing_alpha":
        interval = _finite(i.get("sampleIntervalSeconds"), "sampleIntervalSeconds")
        constant = _positive(i.get("timeConstantSeconds"), "timeConstantSeconds")
        result = interval / (constant + interval)
    elif operation == "snr_db":
        result = 20 * math.log10(_positive(i.get("signalRms"), "signalRms") / _positive(i.get("noiseRms"), "noiseRms"))
    elif operation == "missing_sample_percent":
        result = _finite(i.get("missingCount"), "missingCount") / _positive(i.get("totalCount"), "totalCount") * 100
    elif operation == "clipping_percent":
        result = _finite(i.get("clippedCount"), "clippedCount") / _positive(i.get("totalCount"), "totalCount") * 100
    elif operation == "pearson_correlation":
        x_values, y_values = _paired(i.get("xValues"), i.get("yValues"), "xValues", "yValues")
        x_mean = _mean(x_values)
        y_mean = _mean(y_values)
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
        denominator = math.sqrt(sum((x - x_mean) ** 2 for x in x_values) * sum((y - y_mean) ** 2 for y in y_values))
        if denominator == 0:
            raise BiosignalError("Correlation requires non-constant arrays.")
        result = numerator / denominator
    elif operation == "signal_quality_index":
        result = max(0.0, min(100.0, 50 + 2 * _finite(i.get("snrDb"), "snrDb") - 2 * _finite(i.get("missingPercent"), "missingPercent") - 3 * _finite(i.get("clippingPercent"), "clippingPercent")))
    else:
        raise BiosignalError(
            f"Unsupported biosignal operation: {operation}"
        )

    return {
        "schema": "sc-lab-biomedical-biosignal-result/1.0",
        "version": VERSION,
        "method": method,
        "inputs": inputs,
        "value": result,
        "unit": method["output"]["unit"],
    }


def analyze_signal(
    samples: list[Any],
    sample_rate_hz: Any,
) -> dict[str, Any]:
    values = _values(samples, "samples", 2)
    sample_rate = _positive(sample_rate_hz, "sampleRateHz")
    average = _mean(values)
    root_mean_square = _rms(values)
    crossings = sum(
        1
        for index in range(1, len(values))
        if (
            (values[index - 1] < 0 <= values[index])
            or (values[index - 1] >= 0 > values[index])
        )
    )

    return {
        "schema": "sc-lab-biosignal-waveform-analysis/1.0",
        "version": VERSION,
        "sampleCount": len(values),
        "sampleRateHz": sample_rate,
        "durationSeconds": (len(values) - 1) / sample_rate,
        "mean": average,
        "standardDeviation": _sd(values),
        "rms": root_mean_square,
        "minimum": min(values),
        "maximum": max(values),
        "peakToPeak": max(values) - min(values),
        "zeroCrossingCount": crossings,
        "zeroCrossingRate": crossings / (len(values) - 1) * sample_rate,
        "crestFactor": (
            max(abs(value) for value in values) / root_mean_square
            if root_mean_square
            else 0.0
        ),
    }


def batch_execute(rows: list[dict[str, Any]]) -> dict[str, Any]:
    results: list[dict[str, Any]] = []

    for index, row in enumerate(rows):
        try:
            result = execute(
                str(row.get("methodId") or ""),
                row.get("inputs") or {},
            )
            results.append(
                {
                    "row": index + 1,
                    "ok": True,
                    "result": result,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "row": index + 1,
                    "ok": False,
                    "error": str(exc),
                }
            )

    return {
        "schema": "sc-lab-biomedical-biosignal-batch/1.0",
        "version": VERSION,
        "rowCount": len(rows),
        "successCount": sum(1 for item in results if item["ok"]),
        "errorCount": sum(1 for item in results if not item["ok"]),
        "results": results,
    }
