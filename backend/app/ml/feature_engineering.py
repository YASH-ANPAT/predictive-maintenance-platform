from collections.abc import Mapping
from typing import Any

import numpy as np

FEATURE_NAMES = (
    "temperature",
    "vibration",
    "pressure",
    "rpm",
    "voltage",
    "current",
    "load",
    "humidity",
)


def _get_telemetry_value(telemetry: Any, field_name: str) -> Any:
    """Read one telemetry value from an ORM object or mapping."""
    if isinstance(telemetry, Mapping):
        return telemetry.get(field_name)
    return getattr(telemetry, field_name, None)


def telemetry_to_feature_dict(telemetry: Any) -> dict[str, float]:
    """Convert latest telemetry into an ordered feature dictionary."""
    features: dict[str, float] = {}
    missing_fields: list[str] = []

    for field_name in FEATURE_NAMES:
        value = _get_telemetry_value(telemetry, field_name)
        if value is None:
            missing_fields.append(field_name)
            continue
        features[field_name] = float(value)

    if missing_fields:
        missing = ", ".join(missing_fields)
        raise ValueError(f"Telemetry is missing required feature fields: {missing}")

    return features


def telemetry_to_model_features(telemetry: Any) -> np.ndarray:
    """Convert latest telemetry into a two-dimensional model feature array."""
    feature_dict = telemetry_to_feature_dict(telemetry)
    return np.asarray(
        [[feature_dict[field_name] for field_name in FEATURE_NAMES]],
        dtype=float,
    )
