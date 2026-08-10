from collections.abc import Mapping
from typing import Any

import numpy as np
import pandas as pd
import shap

from app.ml.feature_engineering import telemetry_to_model_features
from app.ml.model_loader import get_model


FEATURE_DISPLAY_NAMES = {
    "cat__Type_H": "Machine Type",
    "cat__Type_L": "Machine Type",
    "cat__Type_M": "Machine Type",
    "num__Air temperature [K]": "Air Temperature",
    "num__Process temperature [K]": "Process Temperature",
    "num__Rotational speed [rpm]": "Rotational Speed",
    "num__Torque [Nm]": "Torque",
    "num__Tool wear [min]": "Tool Wear",
}


def _get_xgb_model_and_transformed_features(
    telemetry: Any,
) -> tuple[Any, pd.DataFrame, list[str]]:
    """Prepare one telemetry record for the deployed XGBoost model."""

    model = get_model()

    if not hasattr(model, "named_steps"):
        raise TypeError("Configured ML model must be a sklearn Pipeline.")

    if "preprocessor" not in model.named_steps:
        raise ValueError("ML pipeline is missing the preprocessor.")

    if "classifier" not in model.named_steps:
        raise ValueError("ML pipeline is missing the classifier.")

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]

    raw_features = telemetry_to_model_features(telemetry)
    transformed = preprocessor.transform(raw_features)

    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()

    feature_names = list(
        preprocessor.get_feature_names_out()
    )

    # SHAP passes this data into XGBoost's DMatrix, which rejects
    # feature names containing characters such as "[" and "]".
    # Keep the original names separately for our UI mapping.
    safe_feature_names = [
        f"feature_{index}"
        for index in range(len(feature_names))
    ]

    transformed_frame = pd.DataFrame(
        transformed,
        columns=safe_feature_names,
    )

    return classifier, transformed_frame, feature_names


def _aggregate_feature_values(
    values: np.ndarray,
    feature_names: list[str],
) -> dict[str, float]:
    """Aggregate one-hot machine-type contributions into one feature."""

    aggregated: dict[str, float] = {}

    for value, feature_name in zip(values, feature_names):
        display_name = FEATURE_DISPLAY_NAMES.get(
            feature_name,
            feature_name,
        )

        aggregated[display_name] = (
            aggregated.get(display_name, 0.0) + float(value)
        )

    return aggregated


def get_global_feature_importance() -> list[dict[str, Any]]:
    """
    Return global XGBoost feature importance using the deployed model.

    One-hot machine-type features are aggregated into one user-facing
    Machine Type feature.
    """

    model = get_model()

    if not hasattr(model, "named_steps"):
        raise TypeError("Configured ML model must be a sklearn Pipeline.")

    classifier = model.named_steps.get("classifier")
    preprocessor = model.named_steps.get("preprocessor")

    if classifier is None or preprocessor is None:
        raise ValueError(
            "ML pipeline must contain both preprocessor and classifier."
        )

    importances = np.asarray(
        classifier.feature_importances_,
        dtype=float,
    )

    feature_names = list(
        preprocessor.get_feature_names_out()
    )

    if len(importances) != len(feature_names):
        raise ValueError(
            "Feature importance count does not match transformed feature count."
        )

    aggregated = _aggregate_feature_values(
        importances,
        feature_names,
    )

    total = sum(aggregated.values())

    if total > 0:
        aggregated = {
            name: value / total
            for name, value in aggregated.items()
        }

    return [
        {
            "feature": name,
            "importance": value,
        }
        for name, value in sorted(
            aggregated.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    ]


def get_local_shap_explanation(
    telemetry: Any,
) -> dict[str, Any]:
    """
    Explain the deployed XGBoost model's prediction for one telemetry record.
    """

    classifier, transformed, feature_names = (
        _get_xgb_model_and_transformed_features(telemetry)
    )

    explainer = shap.TreeExplainer(classifier)

    shap_values = explainer.shap_values(
        transformed,
    )

    values = np.asarray(shap_values)

    if values.ndim == 2:
        values = values[0]

    if values.ndim != 1:
        raise ValueError(
            f"Unexpected SHAP output shape: {values.shape}"
        )

    aggregated_shap = _aggregate_feature_values(
        values,
        feature_names,
    )

    probability = float(
        classifier.predict_proba(transformed)[0][1]
    )

    return {
        "failure_probability": probability,
        "features": [
            {
                "feature": name,
                "shap_value": value,
                "direction": (
                    "increases_failure_risk"
                    if value > 0
                    else "decreases_failure_risk"
                    if value < 0
                    else "neutral"
                ),
            }
            for name, value in sorted(
                aggregated_shap.items(),
                key=lambda item: abs(item[1]),
                reverse=True,
            )
        ],
    }

