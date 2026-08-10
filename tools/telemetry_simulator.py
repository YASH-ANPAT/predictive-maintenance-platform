import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "ml" / "datasets" / "ai4i2020.csv"

API_BASE_URL = "http://127.0.0.1:8000"
EQUIPMENT_ID = 1

FEATURES = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]

API_FIELDS = {
    "Air temperature [K]": "air_temperature",
    "Process temperature [K]": "process_temperature",
    "Rotational speed [rpm]": "rotational_speed",
    "Torque [Nm]": "torque",
    "Tool wear [min]": "tool_wear",
}


def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    required = FEATURES + ["Machine failure"]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {missing}"
        )

    return df


def get_bounds(df):
    return {
        feature: (
            float(df[feature].min()),
            float(df[feature].max()),
        )
        for feature in FEATURES
    }


def get_operating_targets(df):
    normal = df[df["Machine failure"] == 0]
    failure = df[df["Machine failure"] == 1]

    if normal.empty or failure.empty:
        raise ValueError(
            "Dataset must contain both normal and failure records."
        )

    normal_target = normal[FEATURES].median()
    failure_target = failure[FEATURES].median()

    return normal_target, failure_target


def build_degrading_rows(df, count):
    """
    Build a controlled synthetic degradation trajectory based on
    operating points empirically verified against the production model.

    The trajectory progresses from normal operation to high-risk
    operation while remaining inside the dataset feature ranges.
    """

    bounds = get_bounds(df)

    # Operating points verified directly against the production XGBoost model.
    # Columns:
    # Air temperature, Process temperature, Rotational speed,
    # Torque, Tool wear
    anchors = np.array(
        [
            [300.0, 310.0, 1500.0, 40.0, 100.0],
            [300.5, 310.2, 1400.0, 50.0, 160.0],
            [301.0, 310.5, 1350.0, 55.0, 180.0],
            [301.5, 311.0, 1320.0, 60.0, 200.0],
            [302.0, 311.5, 1280.0, 65.0, 210.0],
            [302.5, 312.0, 1300.0, 68.0, 220.0],
        ],
        dtype=float,
    )

    rng = np.random.default_rng(42)

    # Generate evenly spaced positions across the verified trajectory.
    positions = np.linspace(0, len(anchors) - 1, count)

    rows = []

    for position in positions:
        lower = int(np.floor(position))
        upper = min(lower + 1, len(anchors) - 1)
        fraction = position - lower

        point = (
            anchors[lower]
            + (anchors[upper] - anchors[lower]) * fraction
        )

        # Small deterministic sensor variation.
        noise = np.array(
            [
                rng.normal(0.0, 0.08),   # Air temperature
                rng.normal(0.0, 0.08),   # Process temperature
                rng.normal(0.0, 4.0),    # Rotational speed
                rng.normal(0.0, 0.25),   # Torque
                rng.normal(0.0, 1.0),    # Tool wear
            ]
        )

        point = point + noise

        row = {}

        for index, feature in enumerate(FEATURES):
            low, high = bounds[feature]

            row[feature] = max(
                low,
                min(high, float(point[index])),
            )

        rows.append(row)

    return pd.DataFrame(rows)


def build_normal_rows(df, count):
    """
    Generate stable synthetic operating telemetry around the
    median normal operating condition.
    """

    normal = df[df["Machine failure"] == 0]

    if normal.empty:
        raise ValueError("No normal records found.")

    bounds = get_bounds(df)
    baseline = normal[FEATURES].median()

    rng = np.random.default_rng(10)

    rows = []

    for _ in range(count):
        row = {}

        for feature in FEATURES:
            low, high = bounds[feature]
            span = high - low

            value = float(baseline[feature])

            value += rng.normal(
                loc=0.0,
                scale=span * 0.015,
            )

            value = max(low, min(high, value))

            row[feature] = value

        rows.append(row)

    return pd.DataFrame(rows)


def build_high_risk_rows(df, count):
    """
    Generate synthetic telemetry around the median failure-class
    operating condition.
    """

    failures = df[df["Machine failure"] == 1]

    if failures.empty:
        raise ValueError("No failure records found.")

    bounds = get_bounds(df)
    baseline = failures[FEATURES].median()

    rng = np.random.default_rng(20)

    rows = []

    for _ in range(count):
        row = {}

        for feature in FEATURES:
            low, high = bounds[feature]
            span = high - low

            value = float(baseline[feature])

            value += rng.normal(
                loc=0.0,
                scale=span * 0.01,
            )

            value = max(low, min(high, value))

            row[feature] = value

        rows.append(row)

    return pd.DataFrame(rows)


def to_payload(row):
    payload = {
        "equipment_id": EQUIPMENT_ID,
    }

    for dataset_field, api_field in API_FIELDS.items():
        value = row[dataset_field]

        if api_field == "rotational_speed":
            value = int(round(value))

        elif api_field == "tool_wear":
            value = int(round(value))

        else:
            value = round(float(value), 2)

        payload[api_field] = value

    return payload


def send_telemetry(payload):
    response = requests.post(
        f"{API_BASE_URL}/telemetry/",
        json=payload,
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def run_prediction():
    response = requests.post(
        f"{API_BASE_URL}/prediction/run/{EQUIPMENT_ID}",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def run_prediction():
    response = requests.post(
        f"{API_BASE_URL}/prediction/run/{EQUIPMENT_ID}",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()

def run(mode, count, interval):
    df = load_dataset()

    if mode == "normal":
        rows = build_normal_rows(df, count)

    elif mode == "degrading":
        rows = build_degrading_rows(df, count)

    elif mode == "high-risk":
        rows = build_high_risk_rows(df, count)

    else:
        raise ValueError(
            "Mode must be: normal, degrading, or high-risk"
        )

    print()
    print("Predictive Maintenance Telemetry Simulator")
    print("--------------------------------------------")
    print(f"Mode:         {mode}")
    print(f"Equipment ID: {EQUIPMENT_ID}")
    print(f"Records:      {count}")
    print(f"Interval:     {interval}s")
    print()

    for index, (_, row) in enumerate(
        rows.iterrows(),
        start=1,
    ):
        payload = to_payload(row)

        try:
            telemetry_result = send_telemetry(payload)
            prediction_result = run_prediction()

            print(
                f"[{index:02d}/{count}] "
                f"Telemetry={telemetry_result['id']} | "
                f"Temp={payload['air_temperature']} K | "
                f"Process={payload['process_temperature']} K | "
                f"Speed={payload['rotational_speed']} rpm | "
                f"Torque={payload['torque']} Nm | "
                f"Wear={payload['tool_wear']} min | "
                f"Probability={prediction_result['failure_probability']:.2%} | "
                f"Failure={prediction_result['predicted_failure']} | "
                f"Risk={prediction_result['risk_level']}"
            )

        except requests.RequestException as error:
            print()
            print(f"ERROR during telemetry/prediction cycle: {error}")
            raise

        if index < count:
            time.sleep(interval)
def main():
    parser = argparse.ArgumentParser(
        description=(
            "Synthetic telemetry simulator for the "
            "predictive maintenance platform."
        )
    )

    parser.add_argument(
        "--mode",
        choices=[
            "normal",
            "degrading",
            "high-risk",
        ],
        default="degrading",
    )

    parser.add_argument(
        "--count",
        type=int,
        default=10,
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
    )

    args = parser.parse_args()

    if args.count <= 0:
        raise ValueError(
            "--count must be greater than zero."
        )

    if args.interval < 0:
        raise ValueError(
            "--interval cannot be negative."
        )

    run(
        mode=args.mode,
        count=args.count,
        interval=args.interval,
    )


if __name__ == "__main__":
    main()

