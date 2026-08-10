from typing import Literal


RiskLevel = Literal[
    "CRITICAL",
    "HIGH",
    "MODERATE",
    "LOW",
    "NORMAL",
]


def get_risk_level(failure_probability: float) -> RiskLevel:
    """
    Convert model failure probability into the project's
    five-level maintenance risk classification.

    These thresholds are a decision policy applied after ML inference.
    They are not additional ML model outputs.
    """
    if not 0 <= failure_probability <= 1:
        raise ValueError("failure_probability must be between 0 and 1")

    if failure_probability >= 0.80:
        return "CRITICAL"

    if failure_probability >= 0.60:
        return "HIGH"

    if failure_probability >= 0.40:
        return "MODERATE"

    if failure_probability >= 0.20:
        return "LOW"

    return "NORMAL"


def generate_maintenance_recommendation(
    failure_probability: float,
) -> str:
    """
    Generate risk-based maintenance guidance from failure probability.
    """
    risk_level = get_risk_level(failure_probability)

    if risk_level == "CRITICAL":
        return "Immediate maintenance inspection recommended."

    if risk_level == "HIGH":
        return "Schedule maintenance inspection soon and monitor equipment closely."

    if risk_level == "MODERATE":
        return "Inspect equipment condition and monitor telemetry for increasing risk."

    if risk_level == "LOW":
        return "Plan preventive maintenance and continue routine monitoring."

    return "No immediate maintenance action required. Continue routine monitoring."
