from typing import Any, TypedDict

import pandas as pd

from app.ml.feature_engineering import telemetry_to_model_features
from app.ml.model_loader import get_model
from app.services.prediction_service import (
    generate_maintenance_recommendation,
    get_risk_level,
)


DEFAULT_FAILURE_THRESHOLD = 0.5


class PredictionResult(TypedDict):
    """Prediction result returned by the framework-independent inference layer."""

    failure_probability: float
    predicted_failure: bool
    risk_level: str
    recommendation: str


def _extract_failure_probability(
    model: Any,
    model_features: pd.DataFrame,
) -> float:
    """Run model inference and normalize the output to a probability."""

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(model_features)
        return float(probabilities[0][1])

    raw_prediction = model.predict(model_features)
    return float(raw_prediction[0])


def run_prediction(
    latest_telemetry: Any,
    threshold: float = DEFAULT_FAILURE_THRESHOLD,
) -> PredictionResult:
    """
    Run failure prediction for latest telemetry without depending on FastAPI.
    """

    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")

    model = get_model()

    model_features = telemetry_to_model_features(
        latest_telemetry
    )

    failure_probability = _extract_failure_probability(
        model,
        model_features,
    )

    failure_probability = max(
        0.0,
        min(1.0, failure_probability),
    )

    predicted_failure = failure_probability >= threshold

    risk_level = get_risk_level(
        failure_probability
    )

    return {
        "failure_probability": failure_probability,
        "predicted_failure": predicted_failure,
        "risk_level": risk_level,
        "recommendation": generate_maintenance_recommendation(
            failure_probability=failure_probability,
        ),
    }

