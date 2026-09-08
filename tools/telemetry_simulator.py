import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "ml" / "datasets" / "ai4i2020.csv"

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
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    required = FEATURES + ["Machine failure"]
    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    return df


def get_bounds(df):
    return {
        feature: (
            float(df[feature].min()),
            float(df[feature].max()),
        )
        for feature in FEATURES
    }


def build_degrading_rows(df, count):
    """
    Build a controlled degradation trajectory from normal
    operation toward high-risk operation.
    """
    bounds = get_bounds(df)

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

        noise = np.array(
            [
                rng.normal(0.0, 0.08),
                rng.normal(0.0, 0.08),
                rng.normal(0.0, 4.0),
                rng.normal(0.0, 0.25),
                rng.normal(0.0, 1.0),
            ]
        )

        point += noise

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
    """Generate stable telemetry around normal operating conditions."""
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
            value += rng.normal(0.0, span * 0.015)
            value = max(low, min(high, value))

            row[feature] = value

        rows.append(row)

    return pd.DataFrame(rows)


def build_high_risk_rows(df, count):
    """Generate telemetry around failure-class operating conditions."""
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
            value += rng.normal(0.0, span * 0.01)
            value = max(low, min(high, value))

            row[feature] = value

        rows.append(row)

    return pd.DataFrame(rows)


def to_payload(row, equipment_id):
    payload = {
        "equipment_id": equipment_id,
    }

    for dataset_field, api_field in API_FIELDS.items():
        value = row[dataset_field]

        if api_field in {"rotational_speed", "tool_wear"}:
            value = int(round(value))
        else:
            value = round(float(value), 2)

        payload[api_field] = value

    return payload


def send_telemetry(session, api_url, payload):
    response = session.post(
        f"{api_url}/telemetry/",
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def run_prediction(session, api_url, equipment_id):
    response = session.post(
        f"{api_url}/prediction/run/{equipment_id}",
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def run(mode, count, interval, api_url, equipment_id, continuous):
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

    api_url = api_url.rstrip("/")

    print()
    print("Predictive Maintenance Telemetry Simulator")
    print("--------------------------------------------")
    print(f"Mode:         {mode}")
    print(f"Equipment ID: {equipment_id}")
    print(f"API:          {api_url}")
    print(f"Interval:     {interval}s")
    print(f"Continuous:   {continuous}")
    if not continuous:
        print(f"Records:      {count}")
    print()
    print("Press Ctrl+C to stop.")
    print()

    session = requests.Session()
    cycle = 0

    try:
        while True:
            for _, row in rows.iterrows():
                cycle += 1
                payload = to_payload(row, equipment_id)

                try:
                    telemetry_result = send_telemetry(
                        session,
                        api_url,
                        payload,
                    )

                    prediction_result = run_prediction(
                        session,
                        api_url,
                        equipment_id,
                    )

                    print(
                        f"[{cycle:04d}] "
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
                    print(
                        f"ERROR during telemetry/prediction cycle: {error}"
                    )
                    raise

                if not continuous and cycle >= count:
                    return

                time.sleep(interval)

            if not continuous:
                return

            # Rebuild the same trajectory so continuous mode
            # does not run out of rows.
            if mode == "degrading":
                rows = build_degrading_rows(df, count)
            elif mode == "normal":
                rows = build_normal_rows(df, count)
            else:
                rows = build_high_risk_rows(df, count)

    except KeyboardInterrupt:
        print()
        print("Simulator stopped.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Synthetic telemetry simulator for the "
            "predictive maintenance platform."
        )
    )

    parser.add_argument(
        "--mode",
        choices=["normal", "degrading", "high-risk"],
        default="degrading",
    )

    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of records per cycle.",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        help="Seconds between telemetry cycles.",
    )

    parser.add_argument(
        "--api-url",
        default="http://127.0.0.1:8000",
        help="FastAPI base URL.",
    )

    parser.add_argument(
        "--equipment-id",
        type=int,
        default=1,
        help="Equipment ID to simulate.",
    )

    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Continue generating telemetry until stopped with Ctrl+C.",
    )

    args = parser.parse_args()

    if args.count <= 0:
        raise ValueError("--count must be greater than zero.")

    if args.interval < 0:
        raise ValueError("--interval cannot be negative.")

    if args.equipment_id <= 0:
        raise ValueError("--equipment-id must be greater than zero.")

    run(
        mode=args.mode,
        count=args.count,
        interval=args.interval,
        api_url=args.api_url,
        equipment_id=args.equipment_id,
        continuous=args.continuous,
    )


if __name__ == "__main__":
    main()
