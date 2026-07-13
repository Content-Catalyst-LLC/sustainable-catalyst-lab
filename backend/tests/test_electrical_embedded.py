from __future__ import annotations

import math

from app.electrical_embedded import METHODS, public_methods, run_method


def test_catalog_and_version() -> None:
    catalog = public_methods()
    assert catalog["version"] == "0.10.0"
    assert len(catalog["methods"]) >= 12
    assert catalog["curatedOnly"] is True


def test_ohms_law() -> None:
    result = run_method("electrical.ohms-law", {"voltage": 12, "resistance": 6})
    assert result["outputs"]["current"] == 2
    assert result["outputs"]["power"] == 24


def test_parallel_resistors() -> None:
    result = run_method("electrical.resistors-parallel", {"resistances": [100, 100]})
    assert result["outputs"]["equivalentResistance"] == 50


def test_series_rlc_at_resonance() -> None:
    inductance = 0.01
    capacitance = 1e-6
    frequency = 1 / (2 * math.pi * math.sqrt(inductance * capacitance))
    result = run_method("electrical.series-rlc", {"resistance": 10, "inductance": inductance, "capacitance": capacitance, "frequency": frequency, "voltage": 1})
    assert abs(result["outputs"]["phaseDegrees"]) < 1e-8
    assert abs(result["outputs"]["currentRms"] - 0.1) < 1e-10


def test_adc_quantization() -> None:
    result = run_method("embedded.adc-quantization", {"bits": 10, "reference": 3.3, "inputVoltage": 1.65})
    assert result["outputs"]["levels"] == 1024
    assert 511 <= result["outputs"]["code"] <= 512


def test_uart_error() -> None:
    result = run_method("embedded.uart-baud", {"clock": 16_000_000, "targetBaud": 9600, "oversampling": 16})
    assert abs(result["outputs"]["errorPercent"]) < 1
