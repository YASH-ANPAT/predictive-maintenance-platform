import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.crud.equipment import create_equipment
from app.crud.prediction import (
    create_prediction,
    get_latest_prediction,
    get_prediction_history,
)
from app.crud.telemetry import (
    create_telemetry,
    get_equipment_telemetry,
    get_telemetry_by_id,
)
from app.database.base import Base
from app.ml.feature_engineering import (
    MODEL_FEATURE_NAMES,
    telemetry_to_feature_dict,
    telemetry_to_model_features,
)
from app.ml.predict import run_prediction
from app.schemas.equipment import EquipmentCreate
from app.schemas.prediction import PredictionCreate
from app.schemas.telemetry import TelemetryCreate
from app.services.prediction_service import prepare_prediction_input


def _equipment_payload(machine_type: str = "M") -> EquipmentCreate:
    """Build a valid equipment payload."""
    return EquipmentCreate(
        equipment_code="EQ-001",
        name="Milling Machine",
        category="Industrial",
        machine_type=machine_type,
        manufacturer="ACME",
        model_number="MX-1",
        installation_date=date(2026, 1, 1),
    )


def _telemetry_payload(equipment_id: int) -> TelemetryCreate:
    """Build a valid telemetry payload using final model features."""
    return TelemetryCreate(
        equipment_id=equipment_id,
        air_temperature=298.1,
        process_temperature=308.6,
        rotational_speed=1551,
        torque=42.8,
        tool_wear=0,
    )


class FeatureContractTestCase(unittest.TestCase):
    """Backend and ML contract tests for final XGBoost features."""

    def setUp(self) -> None:
        """Create an isolated in-memory database for each test."""
        self.engine = create_engine("sqlite:///:memory:")
        testing_session_local = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db: Session = testing_session_local()

    def tearDown(self) -> None:
        """Close and drop the isolated test database."""
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_equipment_machine_type_validation(self) -> None:
        """Validate that equipment machine_type accepts only final model classes."""
        self.assertEqual(_equipment_payload("L").machine_type, "L")

        with self.assertRaises(ValidationError):
            _equipment_payload("X")

    def test_telemetry_creation_and_retrieval(self) -> None:
        """Create and retrieve telemetry with the final production contract."""
        equipment = create_equipment(self.db, _equipment_payload())
        telemetry = create_telemetry(self.db, _telemetry_payload(equipment.id))

        self.assertEqual(telemetry.air_temperature, 298.1)
        self.assertEqual(telemetry.rotational_speed, 1551)
        self.assertEqual(
            get_telemetry_by_id(self.db, telemetry.id).id,
            telemetry.id,
        )
        self.assertEqual(
            get_equipment_telemetry(self.db, equipment.id)[0].id,
            telemetry.id,
        )

    def test_feature_engineering_uses_exact_xgboost_contract(self) -> None:
        """Convert production telemetry into the exact final pipeline columns."""
        telemetry = SimpleNamespace(
            equipment=SimpleNamespace(machine_type="M"),
            air_temperature=298.1,
            process_temperature=308.6,
            rotational_speed=1551,
            torque=42.8,
            tool_wear=0,
        )

        feature_dict = telemetry_to_feature_dict(telemetry)
        feature_frame = telemetry_to_model_features(telemetry)

        self.assertEqual(tuple(feature_dict), MODEL_FEATURE_NAMES)
        self.assertEqual(tuple(feature_frame.columns), MODEL_FEATURE_NAMES)
        self.assertEqual(feature_dict["Type"], "M")
        self.assertEqual(feature_dict["Air temperature [K]"], 298.1)

    def test_missing_required_telemetry_fields_are_rejected(self) -> None:
        """Reject incomplete telemetry before model inference."""
        with self.assertRaises(ValidationError):
            TelemetryCreate(
                equipment_id=1,
                air_temperature=298.1,
                process_temperature=308.6,
                rotational_speed=1551,
                torque=42.8,
            )

        with self.assertRaisesRegex(ValueError, "tool_wear"):
            telemetry_to_feature_dict(
        {
            "equipment": {
                "machine_type": "M",
            },
            "air_temperature": 298.1,
            "process_temperature": 308.6,
            "rotational_speed": 1551,
            "torque": 42.8,
        }
    )

    def test_prediction_input_compatibility(self) -> None:
        """Prepare prediction input using equipment Type plus latest telemetry."""
        equipment = create_equipment(self.db, _equipment_payload("H"))
        telemetry = create_telemetry(
            self.db,
            _telemetry_payload(equipment.id),
        )

        prediction_input = prepare_prediction_input(
            self.db,
            equipment.id,
        )

        self.assertEqual(
            prediction_input["equipment_id"],
            equipment.id,
        )
        self.assertEqual(
            prediction_input["telemetry_id"],
            telemetry.id,
        )
        self.assertEqual(
            prediction_input["machine_type"],
            "H",
        )
        self.assertEqual(
            prediction_input["features"]["tool_wear"],
            0,
        )

    def test_run_prediction_returns_expected_contract(self) -> None:
        """Run inference with a fake pipeline without requiring trained_model.pkl."""

        test_case = self

        class FakeModel:
            def predict_proba(self, features):
                test_case.assertEqual(
                    tuple(features.columns),
                    MODEL_FEATURE_NAMES,
                )
                return [[0.2, 0.8]]

        with patch(
            "app.ml.predict.get_model",
            return_value=FakeModel(),
        ):
            result = run_prediction(
                SimpleNamespace(
                    equipment=SimpleNamespace(machine_type="L"),
                    air_temperature=298.1,
                    process_temperature=308.6,
                    rotational_speed=1551,
                    torque=42.8,
                    tool_wear=0,
                )
            )

        self.assertEqual(
            result["failure_probability"],
            0.8,
        )
        self.assertIs(
            result["predicted_failure"],
            True,
        )
        self.assertTrue(
            result["recommendation"],
        )

    def test_existing_prediction_history_behavior(self) -> None:
        """Ensure prediction latest/history CRUD behavior remains intact."""
        equipment = create_equipment(
            self.db,
            _equipment_payload(),
        )

        prediction = create_prediction(
            self.db,
            PredictionCreate(
                equipment_id=equipment.id,
                failure_probability=0.7,
                predicted_failure=True,
                model_version="v1.0",
                recommendation="Schedule preventive maintenance soon.",
            ),
        )

        self.assertEqual(
            get_latest_prediction(
                self.db,
                equipment.id,
            ).id,
            prediction.id,
        )

        self.assertEqual(
            get_prediction_history(
                self.db,
                equipment.id,
            )[0].id,
            prediction.id,
        )


if __name__ == "__main__":
    unittest.main()