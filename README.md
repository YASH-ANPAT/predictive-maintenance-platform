Predictive Equipment Maintenance Platform — Architecture

1. System Overview

The Predictive Equipment Maintenance Platform is a full-stack predictive-maintenance application that collects equipment telemetry, runs an XGBoost failure-prediction model, stores predictions and telemetry in PostgreSQL, and presents the results through a React dashboard.

The system is organized into five main layers:

Frontend — React/Vite user interface

API Layer — FastAPI routes

Service & ML Layer — business logic, prediction orchestration, feature engineering, XGBoost inference, risk policy, and SHAP explainability

Persistence Layer — CRUD modules and PostgreSQL

Simulation Layer — telemetry simulator used to generate realistic demonstration telemetry

2. High-Level Architecture

flowchart TB

    USER([Platform User])

    subgraph FRONTEND["Frontend — React / Vite"]
        DASH["Dashboard<br/>Dashboard.jsx"]
        EQUIP_UI["Equipment UI<br/>Equipment.jsx"]
        TELE_UI["Telemetry UI<br/>Telemetry.jsx"]
        PRED_UI["Predictions UI<br/>Predictions.jsx"]
        MAINT_UI["Maintenance UI<br/>Maintenance.jsx"]
        CLIENT["API Client<br/>client.js"]
    end

    subgraph BACKEND["Backend — FastAPI"]
        MAIN["FastAPI Application<br/>main.py"]

        subgraph API["API Routes"]
            EQUIP_API["Equipment Routes<br/>equipment.py"]
            TELE_API["Telemetry Routes<br/>telemetry.py"]
            PRED_API["Prediction Routes<br/>prediction.py"]
            MAINT_API["Maintenance Routes<br/>maintenance.py"]
        end

        subgraph SERVICES["Service Layer"]
            TELE_SERVICE["Telemetry Service<br/>telemetry_service.py"]
            PRED_SERVICE["Prediction Service<br/>prediction_service.py"]
            RISK["Risk Policy<br/>risk_policy.py"]
            MAINT_SERVICE["Maintenance Service<br/>maintenance_service.py"]
        end

        subgraph ML["Prediction & ML"]
            FEATURE["Feature Engineering<br/>feature_engineering.py"]
            PREDICT["ML Inference<br/>predict.py"]
            LOADER["Model Loader<br/>model_loader.py"]
            XGB["Trained XGBoost Model"]
            SHAP["SHAP Explainability<br/>explainability.py"]
        end

        subgraph CRUD["Persistence / CRUD"]
            EQUIP_CRUD["Equipment CRUD<br/>equipment.py"]
            TELE_CRUD["Telemetry CRUD<br/>telemetry.py"]
            PRED_CRUD["Prediction CRUD<br/>prediction.py"]
            MAINT_CRUD["Maintenance CRUD<br/>maintenance.py"]
        end
    end

    subgraph SIM["Simulation"]
        SIMULATOR["Telemetry Simulator<br/>tools/telemetry_simulator.py"]
    end

    DB[(PostgreSQL)]

    USER -->|"views / manages"| DASH
    USER -->|"views"| EQUIP_UI
    USER -->|"views"| TELE_UI
    USER -->|"reviews / runs"| PRED_UI
    USER -->|"manages"| MAINT_UI

    DASH --> CLIENT
    EQUIP_UI --> CLIENT
    TELE_UI --> CLIENT
    PRED_UI --> CLIENT
    MAINT_UI --> CLIENT

    CLIENT -->|"REST / HTTP requests"| MAIN

    MAIN --> EQUIP_API
    MAIN --> TELE_API
    MAIN --> PRED_API
    MAIN --> MAINT_API

    EQUIP_API --> EQUIP_CRUD
    TELE_API --> TELE_SERVICE
    PRED_API --> PRED_SERVICE
    MAINT_API --> MAINT_SERVICE

    TELE_SERVICE --> TELE_CRUD
    PRED_SERVICE --> PRED_CRUD
    PRED_SERVICE --> FEATURE
    PRED_SERVICE --> PREDICT
    PRED_SERVICE --> RISK
    MAINT_SERVICE --> MAINT_CRUD

    PREDICT --> FEATURE
    PREDICT --> LOADER
    LOADER --> XGB

    SHAP --> FEATURE
    SHAP --> LOADER
    SHAP --> XGB

    EQUIP_CRUD --> DB
    TELE_CRUD --> DB
    PRED_CRUD --> DB
    MAINT_CRUD --> DB

    SIMULATOR -->|"POST telemetry"| TELE_API
    SIMULATOR -->|"POST run prediction"| PRED_API

3. Runtime Prediction Flow

The normal prediction workflow is:

Latest Equipment Telemetry
          │
          ▼
   Prediction API Route
          │
          ▼
   Prediction Service
          │
          ├── validates equipment
          │
          ├── gets latest telemetry
          │
          ▼
   Feature Engineering
          │
          ▼
     XGBoost Model
          │
          ▼
   Failure Probability
          │
          ▼
      Risk Policy
          │
          ▼
Maintenance Recommendation
          │
          ▼
   Prediction Record
          │
          ▼
      PostgreSQL

The prediction API runs the model using the latest telemetry, saves the resulting prediction, and returns the prediction response.

4. Telemetry Simulation Flow

The project includes tools/telemetry_simulator.py for demonstration and testing.

Telemetry Simulator
        │
        │ POST /telemetry/
        ▼
   Telemetry API
        │
        ▼
   Telemetry CRUD
        │
        ▼
    PostgreSQL
        │
        │ latest telemetry
        ▼
POST /prediction/run/{equipment_id}
        │
        ▼
 Prediction Service
        │
        ▼
   XGBoost Inference
        │
        ▼
 Failure Probability
        │
        ▼
 Risk / Recommendation
        │
        ▼
 Prediction CRUD
        │
        ▼
    PostgreSQL

The simulator supports the project demonstration modes:

normal

degrading

high-risk

The degrading mode generates a controlled telemetry trajectory so that the dashboard can demonstrate changing predicted risk.

5. Frontend Architecture

The frontend is implemented using React and Vite.

Main UI components

Component

Responsibility

Dashboard.jsx

Overall equipment and prediction overview

Equipment.jsx

Equipment information and management

Telemetry.jsx

Telemetry records and telemetry visualization

Predictions.jsx

Prediction results, history, risk, and explainability

Maintenance.jsx

Maintenance records and maintenance management

client.js

Central API client used by frontend pages

Layout.jsx

Shared application layout/navigation

The frontend communicates with the backend through the centralized API client rather than directly accessing PostgreSQL.

6. Backend Architecture

The backend uses FastAPI and separates API routing, services, ML logic, and database access.

API routes

Route module

Responsibility

equipment.py

Equipment CRUD endpoints

telemetry.py

Telemetry endpoints

prediction.py

Prediction creation, retrieval, history, inference, and explainability

maintenance.py

Maintenance record endpoints

Service layer

Service

Responsibility

telemetry_service.py

Telemetry-related service operations

prediction_service.py

Prediction orchestration and preparation of model input

risk_policy.py

Converts prediction results into risk classification/recommendation

maintenance_service.py

Maintenance history, upcoming maintenance, and overdue maintenance logic

The service layer keeps application/business logic separate from the HTTP route handlers and CRUD database operations.

7. ML Architecture

The deployed ML model is an XGBoost binary classifier trained using the AI4I 2020 Predictive Maintenance Dataset.

Model input features

The final model uses six features:

Type
Air temperature [K]
Process temperature [K]
Rotational speed [rpm]
Torque [Nm]
Tool wear [min]

The dataset identifier fields and failure-mode columns are excluded from the model input.

Training pipeline

AI4I 2020 Dataset
        │
        ▼
Feature / Target Selection
        │
        ▼
80/20 Stratified Train-Test Split
        │
        ▼
Preprocessing
   ├── Type → OneHotEncoder
   └── Numerical values → Median Imputation
        │
        ▼
XGBoost Classifier
        │
        ▼
Trained Model

The categorical machine Type is one-hot encoded. Numerical telemetry features use median imputation.

The training split is stratified to preserve the failure/non-failure class distribution.

Because machine failures are highly imbalanced in the dataset, scale_pos_weight is calculated from the training-set class counts and supplied to XGBoost.

Final XGBoost configuration

XGBClassifier(
    n_estimators=500,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    random_state=42,
    eval_metric="logloss",
)

The model is used as a snapshot/tabular classifier: each prediction is based on the latest available telemetry for an equipment item.

8. Production Feature Engineering

The backend maintains an explicit feature contract between telemetry and the trained model.

Telemetry fields
      │
      ├── air_temperature
      ├── process_temperature
      ├── rotational_speed
      ├── torque
      └── tool_wear
              │
              ▼
     Feature Engineering
              │
              ├── machine type from equipment
              ├── numeric conversion
              ├── validation
              └── exact model column ordering
              │
              ▼
      Model Feature DataFrame
              │
              ▼
          XGBoost

The backend validates that the equipment machine type is one of:

L
M
H

The resulting DataFrame follows the exact model feature order used during training.

9. Risk and Maintenance Recommendation Flow

The model produces a failure probability and prediction result.

The application then applies its risk policy to convert the prediction result into a user-facing risk level and maintenance recommendation.

XGBoost
   │
   ▼
Failure Probability
   │
   ▼
Risk Policy
   │
   ├── Risk Level
   │
   └── Maintenance Recommendation

The recommendation is guidance generated from the prediction result.

A recommendation does not automatically mean that a maintenance record was performed.

Actual maintenance records remain separate application records managed through the Maintenance UI/API.

10. SHAP Explainability

The project includes SHAP-based explainability for the trained XGBoost model.

Telemetry
    │
    ▼
Feature Engineering
    │
    ▼
Preprocessor
    │
    ▼
Transformed Features
    │
    ▼
XGBoost Classifier
    │
    ▼
SHAP
    │
    ▼
Feature Contributions

The preprocessing output contains one-hot encoded machine-type features and numerical features.

The explainability layer maps the transformed feature names back into user-friendly names such as:

Machine Type
Air Temperature
Process Temperature
Rotational Speed
Torque
Tool Wear

Machine-type one-hot contributions are aggregated into the single UI-level feature Machine Type.

SHAP values represent the contribution of features to the model output; they should not be interpreted as causal effects.

11. Persistence Architecture

The application uses SQLAlchemy CRUD modules for database persistence.

Equipment CRUD ───────┐
Telemetry CRUD ───────┤
Prediction CRUD ──────┼──► PostgreSQL
Maintenance CRUD ─────┘

The main persisted domains are:

equipment

telemetry

predictions

maintenance

Predictions also retain the relationship to the telemetry record used for the prediction.

12. End-to-End Production Flow

                    ┌───────────────────┐
                    │    Platform User  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ React / Vite UI   │
                    └─────────┬─────────┘
                              │ REST
                              ▼
                    ┌───────────────────┐
                    │    FastAPI        │
                    │      main.py      │
                    └─────────┬─────────┘
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
           Equipment      Telemetry      Prediction
              API            API            API
                                            │
                                            ▼
                                    Prediction Service
                                            │
                              ┌─────────────┴─────────────┐
                              ▼                           ▼
                       Latest Telemetry             ML Pipeline
                                                          │
                                                          ▼
                                                   XGBoost Model
                                                          │
                                                          ▼
                                                Failure Probability
                                                          │
                                                          ▼
                                                    Risk Policy
                                                          │
                                                          ▼
                                             Recommendation / Risk
                                                          │
                                                          ▼
                                                    Prediction
                                                          │
                ┌─────────────────────────────────────────┘
                ▼
         CRUD / Persistence
                │
                ▼
          PostgreSQL Database

13. Demo Flow

For a live demonstration, the intended sequence is:

1. Start with the deployed dashboard.
2. Select the equipment.
3. Run the telemetry simulator.
4. Simulator sends telemetry to the backend.
5. Backend stores telemetry.
6. Prediction endpoint runs the trained XGBoost model.
7. Prediction is stored in PostgreSQL.
8. Dashboard retrieves the latest prediction.
9. Risk level and maintenance recommendation are displayed.
10. Prediction history and SHAP explainability can be inspected.

The simulator can be used with the production API by supplying the deployed backend URL and equipment ID.

14. Technology Stack

Frontend

React

Vite

React Router

Recharts

Lucide React

Backend

Python

FastAPI

SQLAlchemy

Alembic

Pydantic

Machine Learning

Scikit-learn

XGBoost

SHAP

Pandas

Database

PostgreSQL

Deployment

Vercel — frontend

Render — backend

Aiven — PostgreSQL

15. Important Architectural Boundary

The project is a predictive-maintenance decision-support platform.

The ML model predicts the probability of machine failure from the latest telemetry. The application layer then converts that result into a risk level and maintenance recommendation.

The system does not claim that the model itself performs physical maintenance or that a recommendation automatically represents a completed maintenance action.

This separation keeps the ML prediction, application policy, and actual maintenance records as distinct responsibilities