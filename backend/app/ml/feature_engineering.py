from collections.abc import Mapping
from typing import Any

import pandas as pd


MODEL_FEATURE_NAMES = (
    "Type",
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
)


TELEMETRY_TO_MODEL_FEATURES = {
    "air_temperature": "Air temperature [K]",
    "process_temperature": "Process temperature [K]",
    "rotational_speed": "Rotational speed [rpm]",
    "torque": "Torque [Nm]",
    "tool_wear": "Tool wear [min]",
}


def _get_telemetry_value(telemetry: Any, field_name: str) -> Any:
    """Read one telemetry value from an ORM object or mapping."""
    if isinstance(telemetry, Mapping):
        return telemetry.get(field_name)

    return getattr(telemetry, field_name, None)


def _get_machine_type(telemetry: Any) -> str | None:
    """Read machine type from the telemetry record's related equipment."""
    equipment = _get_telemetry_value(telemetry, "equipment")

    if equipment is None:
        raise ValueError("Telemetry must include related equipment")

    machine_type = _get_telemetry_value(equipment, "machine_type")

    if machine_type is None:
        raise ValueError("Equipment is missing required machine_type")

    return str(machine_type)


def telemetry_to_feature_dict(telemetry: Any) -> dict[str, str | float]:
    """Convert backend telemetry into the final model feature contract."""
    machine_type = _get_machine_type(telemetry)

    if machine_type not in {"L", "M", "H"}:
        raise ValueError("Telemetry equipment machine_type must be one of: L, M, H")

    features: dict[str, str | float] = {
        "Type": machine_type,
    }

    missing_fields: list[str] = []

    for field_name, model_feature_name in TELEMETRY_TO_MODEL_FEATURES.items():
        value = _get_telemetry_value(telemetry, field_name)

        if value is None:
            missing_fields.append(field_name)
            continue

        features[model_feature_name] = float(value)

    if missing_fields:
        missing = ", ".join(missing_fields)
        raise ValueError(
            f"Telemetry is missing required feature fields: {missing}"
        )

    return {
        feature_name: features[feature_name]
        for feature_name in MODEL_FEATURE_NAMES
    }


def telemetry_to_model_features(telemetry: Any) -> pd.DataFrame:
    """Convert telemetry into the named DataFrame expected by the model pipeline."""
    feature_dict = telemetry_to_feature_dict(telemetry)

    return pd.DataFrame(
        [feature_dict],
        columns=MODEL_FEATURE_NAMES,
    )