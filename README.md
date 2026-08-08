# Predictive Equipment Maintenance Platform

A production-oriented predictive maintenance platform combining machine learning, equipment telemetry, PostgreSQL persistence, and a FastAPI REST API.

## Overview

The platform receives equipment telemetry, transforms the latest telemetry into the exact feature contract expected by the trained model, performs equipment failure prediction, stores the prediction, and generates a maintenance recommendation.

The machine-learning workflow uses the AI4I 2020 Predictive Maintenance Dataset and evaluates multiple classification algorithms before selecting XGBoost as the final production model.

## Key Features

- Equipment CRUD management
- Equipment machine-type validation
- Telemetry ingestion and retrieval
- Latest telemetry retrieval
- Predictive equipment failure detection
- Failure probability scoring
- Configurable failure threshold
- Maintenance recommendations
- Prediction persistence
- Latest prediction retrieval
- Prediction history
- PostgreSQL integration
- SQLAlchemy ORM
- Alembic migrations
- Pydantic validation
- Production ML feature contract
- Cached ML model loading
- Backend feature-contract tests
- ML model comparison
- Cross-validation analysis
- Feature importance analysis
- SHAP explainability analysis

## Machine Learning

### Dataset

The ML workflow uses the AI4I 2020 Predictive Maintenance Dataset.

Dataset location:

`ml/datasets/ai4i2020.csv`

### Models Evaluated

Four classification algorithms were evaluated:

1. Logistic Regression
2. Decision Tree
3. Random Forest
4. XGBoost

Model selection considered Accuracy, Precision, Recall, and F1 Score. Because predictive maintenance focuses on detecting equipment failures, Recall and F1 Score were considered more important than Accuracy alone.

### Model Comparison

| Model | Accuracy | Precision | Recall | F1 Score |
|---|---:|---:|---:|---:|
| Logistic Regression | 96.85% | 66.67% | 14.71% | 24.10% |
| Decision Tree | 97.85% | 72.73% | 58.82% | 65.04% |
| Random Forest | 98.00% | 73.33% | 64.71% | 68.75% |
| **XGBoost** | **98.40%** | **75.00%** | **79.41%** | **77.14%** |

XGBoost achieved the highest Accuracy, Recall, and F1 Score in the evaluated comparison and was selected as the final production model.

### Production Feature Contract

The production inference pipeline expects:

- Type
- Air temperature [K]
- Process temperature [K]
- Rotational speed [rpm]
- Torque [Nm]
- Tool wear [min]

Supported machine types:

- `L`
- `M`
- `H`

The backend converts telemetry records into the exact feature structure expected by the trained model pipeline before inference.

## ML Workflow

```text
AI4I 2020 Dataset
        |
        v
Exploratory Data Analysis
        |
        v
Model Training
        |
        +---- Logistic Regression
        |
        +---- Decision Tree
        |
        +---- Random Forest
        |
        +---- XGBoost
        |
        v
Model Comparison
        |
        v
XGBoost Selected
        |
        v
Production Training Pipeline
        |
        v
trained_model.pkl
        |
        v
FastAPI Model Loader
        |
        v
Telemetry Feature Engineering
        |
        v
Failure Probability
        |
        v
Prediction + Maintenance Recommendation
