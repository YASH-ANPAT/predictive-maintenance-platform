from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

DATASET_PATH = PROJECT_ROOT / "ml" / "datasets" / "ai4i2020.csv"
MODEL_PATH = BACKEND_DIR / "app" / "ml" / "trained_model.pkl"


# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

df = pd.read_csv(DATASET_PATH)

print(f"Dataset loaded: {df.shape}")


# ---------------------------------------------------------
# Features and target
# ---------------------------------------------------------

X = df.drop(
    columns=[
        "UDI",
        "Product ID",
        "Machine failure",
        "TWF",
        "HDF",
        "PWF",
        "OSF",
        "RNF",
    ]
)

y = df["Machine failure"]


# ---------------------------------------------------------
# Train/test split
# ---------------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)


# ---------------------------------------------------------
# Feature contract
# ---------------------------------------------------------

categorical_features = [
    "Type"
]

numerical_features = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]


# ---------------------------------------------------------
# Preprocessor
# ---------------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features,
        ),
        (
            "num",
            SimpleImputer(strategy="median"),
            numerical_features,
        ),
    ]
)


# ---------------------------------------------------------
# Class imbalance handling
# ---------------------------------------------------------

negative = (y_train == 0).sum()
positive = (y_train == 1).sum()

scale_pos_weight = negative / positive

print(f"scale_pos_weight: {scale_pos_weight}")


# ---------------------------------------------------------
# XGBoost model
# ---------------------------------------------------------

xgboost_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            XGBClassifier(
                n_estimators=500,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.8,
                scale_pos_weight=scale_pos_weight,
                random_state=42,
                eval_metric="logloss",
            ),
        ),
    ]
)


# ---------------------------------------------------------
# Train
# ---------------------------------------------------------

print("Training XGBoost pipeline...")

xgboost_pipeline.fit(
    X_train,
    y_train,
)

print("Training complete.")


# ---------------------------------------------------------
# Evaluation
# ---------------------------------------------------------

y_pred = xgboost_pipeline.predict(X_test)

print("\n========== MODEL EVALUATION ==========")
print(f"Accuracy : {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall   : {recall_score(y_test, y_pred):.4f}")
print(f"F1 Score : {f1_score(y_test, y_pred):.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))

print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))


# ---------------------------------------------------------
# Save complete pipeline
# ---------------------------------------------------------

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

joblib.dump(
    xgboost_pipeline,
    MODEL_PATH,
)

print(f"\nModel saved to: {MODEL_PATH}")