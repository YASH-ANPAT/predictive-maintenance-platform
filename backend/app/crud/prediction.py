from sqlalchemy.orm import Session

from app.models.prediction import Prediction
from app.schemas.prediction import PredictionCreate


def create_prediction(db: Session, prediction: PredictionCreate) -> Prediction:
    """Create and return a failure prediction record."""
    db_prediction = Prediction(**prediction.model_dump(exclude_none=True))
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction


def get_prediction_by_id(db: Session, prediction_id: int) -> Prediction | None:
    """Return a prediction record by its primary key."""
    return db.query(Prediction).filter(Prediction.id == prediction_id).first()


def get_all_predictions(db: Session) -> list[Prediction]:
    """Return all predictions, newest first."""
    return db.query(Prediction).order_by(Prediction.prediction_time.desc()).all()


def get_latest_prediction(
    db: Session,
    equipment_id: int,
) -> Prediction | None:
    """Return the most recent prediction for one equipment item."""
    return (
        db.query(Prediction)
        .filter(Prediction.equipment_id == equipment_id)
        .order_by(Prediction.prediction_time.desc())
        .first()
    )


def get_prediction_history(
    db: Session,
    equipment_id: int,
) -> list[Prediction]:
    """Return all predictions for one equipment item, newest first."""
    return (
        db.query(Prediction)
        .filter(Prediction.equipment_id == equipment_id)
        .order_by(Prediction.prediction_time.desc())
        .all()
    )
