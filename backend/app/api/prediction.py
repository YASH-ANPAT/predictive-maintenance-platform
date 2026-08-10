from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.equipment import get_equipment_by_id
from app.crud.prediction import (
    create_prediction,
    get_all_predictions,
    get_latest_prediction,
    get_prediction_by_id,
    get_prediction_history,
)
from app.database.database import get_db
from app.schemas.prediction import PredictionCreate, PredictionResponse

from app.crud.telemetry import get_latest_telemetry
from app.ml.predict import run_prediction
from app.ml.explainability import (
    get_global_feature_importance,
    get_local_shap_explanation,
)
from app.crud.telemetry import get_telemetry_by_id

router = APIRouter(prefix="/prediction", tags=["Prediction"])


def _get_existing_equipment(db: Session, equipment_id: int) -> None:
    """Raise a 404 error when an equipment item does not exist."""
    if get_equipment_by_id(db, equipment_id) is None:
        raise HTTPException(status_code=404, detail="Equipment not found")


@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def create_new_prediction(
    prediction: PredictionCreate,
    db: Session = Depends(get_db),
) -> PredictionResponse:
    """Record a new failure prediction for existing equipment."""
    _get_existing_equipment(db, prediction.equipment_id)
    return create_prediction(db, prediction)


@router.get("/", response_model=list[PredictionResponse])
def get_all_predictions_endpoint(
    db: Session = Depends(get_db),
) -> list[PredictionResponse]:
    """List every recorded prediction."""
    return get_all_predictions(db)


@router.get("/explainability/feature-importance")
def get_feature_importance():
    """Return global feature importance from the deployed ML model."""
    return {
        "features": get_global_feature_importance(),
    }


@router.get("/explainability/{prediction_id}")
def get_prediction_explanation(
    prediction_id: int,
    db: Session = Depends(get_db),
):
    """Explain the model contribution for one recorded prediction."""

    prediction = get_prediction_by_id(db, prediction_id)

    if prediction is None:
        raise HTTPException(
            status_code=404,
            detail="Prediction not found",
        )

    if prediction.telemetry_id is None:
        raise HTTPException(
            status_code=422,
            detail="This prediction is not linked to telemetry and cannot be explained.",
        )

    telemetry = get_telemetry_by_id(
        db,
        prediction.telemetry_id,
    )

    if telemetry is None:
        raise HTTPException(
            status_code=404,
            detail="Telemetry associated with this prediction was not found.",
        )

    explanation = get_local_shap_explanation(
        telemetry,
    )

    return {
        "prediction_id": prediction.id,
        "telemetry_id": prediction.telemetry_id,
        "failure_probability": prediction.failure_probability,
        "predicted_failure": prediction.predicted_failure,
        "model_version": prediction.model_version,
        "explanation": explanation,
    }


@router.get("/{prediction_id}", response_model=PredictionResponse)
def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
) -> PredictionResponse:
    """Retrieve one prediction by ID."""
    prediction = get_prediction_by_id(db, prediction_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return prediction


@router.get("/latest/{equipment_id}", response_model=PredictionResponse)
def get_latest_equipment_prediction(
    equipment_id: int,
    db: Session = Depends(get_db),
) -> PredictionResponse:
    """Retrieve the latest prediction for an existing equipment item."""
    _get_existing_equipment(db, equipment_id)
    prediction = get_latest_prediction(db, equipment_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail="No predictions found for equipment")
    return prediction


@router.get("/history/{equipment_id}", response_model=list[PredictionResponse])
def get_equipment_prediction_history(
    equipment_id: int,
    db: Session = Depends(get_db),
) -> list[PredictionResponse]:
    """Retrieve the full prediction history for an existing equipment item."""
    _get_existing_equipment(db, equipment_id)
    return get_prediction_history(db, equipment_id)


@router.post(
    "/run/{equipment_id}",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_equipment_prediction(
    equipment_id: int,
    db: Session = Depends(get_db),
) -> PredictionResponse:
    """
    Run the ML model for the latest telemetry of an equipment,
    save the prediction, and return it.
    """

    # Validate equipment
    _get_existing_equipment(db, equipment_id)

    # Get latest telemetry
    latest_telemetry = get_latest_telemetry(db, equipment_id)

    if latest_telemetry is None:
        raise HTTPException(
            status_code=404,
            detail="No telemetry found for this equipment",
        )

    # Run ML inference
    result = run_prediction(latest_telemetry)

    # Create prediction schema
    prediction = PredictionCreate(
        equipment_id=equipment_id,
        telemetry_id=latest_telemetry.id,
        failure_probability=result["failure_probability"],
        predicted_failure=result["predicted_failure"],
        model_version="v1.0",
        recommendation=result["recommendation"],
    )

    # Save to database
    return create_prediction(db, prediction)



