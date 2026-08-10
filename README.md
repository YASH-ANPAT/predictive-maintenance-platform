# Predictive Equipment Maintenance Platform

A full-stack predictive maintenance platform that combines machine learning, equipment telemetry, PostgreSQL persistence, explainable AI, and a React dashboard to identify potential equipment failures and support maintenance decisions.

The system uses an XGBoost classification pipeline trained on the AI4I 2020 Predictive Maintenance Dataset and exposes the trained model through a FastAPI backend.

---

## Overview

The platform follows an end-to-end predictive maintenance workflow:

1. Equipment is registered in the system.
2. Telemetry records are stored against equipment.
3. The latest telemetry is transformed into the exact feature contract expected by the ML pipeline.
4. The trained XGBoost model predicts equipment failure probability.
5. The prediction is persisted in PostgreSQL.
6. A maintenance recommendation is generated based on the prediction.
7. SHAP-based explanations identify the telemetry features contributing to the prediction.
8. The React frontend presents prediction results, history, telemetry trends, and model explainability.

---

## Key Features

### Equipment & Telemetry

- Equipment CRUD management
- Equipment machine-type validation
- Telemetry ingestion
- Telemetry history
- Latest telemetry retrieval
- Equipment status tracking

### Predictive Maintenance

- Equipment failure prediction
- Failure probability scoring
- Configurable risk threshold
- Maintenance recommendations
- Prediction persistence
- Latest prediction retrieval
- Prediction history
- Telemetry-linked predictions

### Explainable AI

- Global feature importance
- Local SHAP explanations
- Positive and negative feature contributions
- Prediction-driver visualization
- Feature-level failure-risk interpretation

### Backend

- FastAPI REST API
- PostgreSQL
- SQLAlchemy ORM
- Alembic migrations
- Pydantic validation
- Cached ML model loading
- Production ML feature contract
- Backend feature-contract tests
- CORS configuration

### Frontend

- React
- Vite
- React Router
- Axios API integration
- Recharts visualizations
- Responsive prediction dashboard
- Telemetry visualization
- Prediction history
- Failure probability trend
- ML explainability dashboard

---

# System Architecture

```text
                    ┌──────────────────────┐
                    │     React Frontend   │
                    │   Vite + Recharts    │
                    └──────────┬───────────┘
                               │
                               │ REST API
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │                      │
                    │ Equipment API         │
                    │ Telemetry API         │
                    │ Prediction API        │
                    │ Maintenance API       │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
                 ▼             ▼             ▼
        ┌──────────────┐ ┌────────────┐ ┌──────────────┐
        │ PostgreSQL   │ │ ML Pipeline│ │ Explainability│
        │              │ │            │ │              │
        │ Equipment    │ │ XGBoost    │ │ SHAP         │
        │ Telemetry    │ │ Prediction │ │ Feature      │
        │ Predictions  │ │            │ │ Importance   │
        │ Maintenance  │ │            │ │              │
        └──────────────┘ └────────────┘ └──────────────┘