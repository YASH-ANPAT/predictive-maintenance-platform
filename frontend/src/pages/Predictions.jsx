import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  RefreshCw,
  ShieldCheck,
  TrendingUp,
  Wrench,
} from "lucide-react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import {
  getLatestPrediction,
  getPredictionHistory,
  getTelemetryHistory,
  runPrediction,
  getFeatureImportance,
  getPredictionExplainability,
} from "../api/client";

const EQUIPMENT_ID = 1;

export default function Predictions() {
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);
  const [telemetry, setTelemetry] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [featureImportance, setFeatureImportance] = useState([]);
  const [shapExplanation, setShapExplanation] = useState(null);
  const [explainabilityLoading, setExplainabilityLoading] = useState(true);
  const [explainabilityError, setExplainabilityError] = useState("");

  const loadPredictions = async () => {
    try {
      setError("");

      const [latest, historyData, telemetryData] =
        await Promise.all([
          getLatestPrediction(EQUIPMENT_ID),
          getPredictionHistory(EQUIPMENT_ID),
          getTelemetryHistory(EQUIPMENT_ID),
        ]);

      setPrediction(latest);

      const records = Array.isArray(historyData)
        ? historyData
        : historyData?.value || [];

      setHistory(records);

      const telemetryRecords = Array.isArray(telemetryData)
        ? telemetryData
        : telemetryData?.value || [];

      setTelemetry(telemetryRecords);
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
        err?.message ||
        "Unable to load prediction data."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPredictions();
  }, []);
  useEffect(() => {
    const loadExplainability = async () => {
      try {
        setExplainabilityLoading(true);
        setExplainabilityError("");

        const globalData = await getFeatureImportance();

        const globalFeatures = Array.isArray(globalData)
          ? globalData
          : globalData?.features || [];

        setFeatureImportance(globalFeatures);

        const latestPrediction =
          await getLatestPrediction(EQUIPMENT_ID);

        if (!latestPrediction?.id) {
          setShapExplanation(null);
          return;
        }

        const localData =
          await getPredictionExplainability(
            latestPrediction.id
          );

        setShapExplanation(localData);
      } catch (err) {
        console.error(
          "Explainability loading failed:",
          err
        );

        setExplainabilityError(
          err?.response?.data?.detail ||
          err?.message ||
          "Unable to load model explainability."
        );
      } finally {
        setExplainabilityLoading(false);
      }
    };

    loadExplainability();
  }, []);

  const handleRunPrediction = async () => {
    try {
      setRunning(true);
      setError("");
      setMessage("");

      const result = await runPrediction(EQUIPMENT_ID);

      setPrediction(result);

      await loadPredictions();

      setMessage("New prediction generated successfully.");
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
        err?.message ||
        "Unable to run prediction."
      );
    } finally {
      setRunning(false);
    }
  };

  const riskPercentage = prediction
    ? prediction.failure_probability * 100
    : 0;

  const riskLevel = prediction?.predicted_failure
    ? "HIGH RISK"
    : "NORMAL";

  const riskClass = prediction?.predicted_failure
    ? "danger"
    : "safe";

  const sortedHistory = useMemo(
    () =>
      [...history].sort(
        (a, b) =>
          new Date(b.prediction_time) -
          new Date(a.prediction_time)
      ),
    [history]
  );

  const failureCount = history.filter(
    (item) => item.predicted_failure
  ).length;

  const normalCount = history.filter(
    (item) => !item.predicted_failure
  ).length;

  const predictionChartData = useMemo(() => {
    return history
      .filter((predictionItem) => predictionItem.telemetry_id)
      .map((predictionItem) => {
        const sourceTelemetry = telemetry.find(
          (item) =>
            item.id === predictionItem.telemetry_id
        );

        if (!sourceTelemetry) {
          return null;
        }

        return {
          timestamp: sourceTelemetry.recorded_at,
          time: new Date(
            sourceTelemetry.recorded_at
          ).toLocaleTimeString("en-IN", {
            hour: "2-digit",
            minute: "2-digit",
          }),
          failure_probability:
            predictionItem.failure_probability * 100,
          risk_level: predictionItem.risk_level,
          telemetry_id: predictionItem.telemetry_id,
        };
      })
      .filter(Boolean)
      .sort(
        (a, b) =>
          new Date(a.timestamp) -
          new Date(b.timestamp)
      );
  }, [history, telemetry]);

  if (loading) {
    return (
      <main className="page-state">
        <div>
          <h1>Loading Predictions</h1>
          <p>Fetching machine-learning prediction history...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="predictions-page">

      {/* HEADER */}

      <header className="predictions-header">
        <div>
          <p className="section-label">
            MACHINE LEARNING
          </p>

          <h1>Predictions</h1>

          <p className="predictions-subtitle">
            Failure-risk predictions generated from the
            latest machine telemetry.
          </p>
        </div>

        <button
          className="prediction-run-button"
          onClick={handleRunPrediction}
          disabled={running}
        >
          <RefreshCw
            size={16}
            className={running ? "spin" : ""}
          />

          {running
            ? "Running Prediction..."
            : "Run New Prediction"}
        </button>
      </header>


      {/* ERROR */}

      {error && (
        <div className="prediction-alert error">
          <AlertTriangle size={17} />
          <span>{error}</span>
        </div>
      )}


      {/* SUCCESS */}

      {message && (
        <div className="prediction-alert success">
          <CheckCircle2 size={17} />
          <span>{message}</span>
        </div>
      )}


      {/* MACHINE BAR */}

      <section className="prediction-machine-bar">

        <div className="prediction-machine-icon">
          <Activity size={23} />
        </div>

        <div>
          <span>MONITORED EQUIPMENT</span>
          <strong>Hydraulic Production Unit</strong>
        </div>

        <div className="prediction-machine-code">
          PMP-H001 · Machine Type M
        </div>

        <div className="prediction-model">
          Model <strong>{prediction?.model_version || "v1.0"}</strong>
        </div>

      </section>


      {prediction ? (
        <>
          {/* MAIN RISK CARD */}

          <section className="prediction-hero">

            <div className="prediction-hero-header">
              <div>
                <p className="section-label">
                  LATEST PREDICTION
                </p>

                <h2>Failure Risk Assessment</h2>
              </div>

              {prediction.predicted_failure ? (
                <AlertTriangle
                  size={25}
                  className="prediction-danger-icon"
                />
              ) : (
                <ShieldCheck
                  size={25}
                  className="prediction-safe-icon"
                />
              )}
            </div>


            <div className="prediction-risk-layout">

              <div className="prediction-score-block">

                <span className="prediction-score-label">
                  FAILURE PROBABILITY
                </span>

                <div className="prediction-score">
                  {riskPercentage.toFixed(2)}
                  <small>%</small>
                </div>

                <div className={`prediction-status ${riskClass}`}>
                  {prediction.predicted_failure
                    ? "FAILURE PREDICTED"
                    : "NORMAL"}
                </div>

              </div>


              <div className="prediction-meter-section">

                <div className="prediction-meter-header">
                  <span>Risk probability</span>
                  <strong>
                    {riskPercentage.toFixed(2)}%
                  </strong>
                </div>

                <div className="prediction-meter">
                  <div
                    className={`prediction-meter-fill ${riskClass}`}
                    style={{
                      width: `${Math.min(
                        riskPercentage,
                        100
                      )}%`,
                    }}
                  />
                </div>

                <div className="prediction-meter-scale">
                  <span>0%</span>
                  <span>50%</span>
                  <span>100%</span>
                </div>

                <p>
                  The probability is produced by the
                  deployed XGBoost failure-classification
                  pipeline using the latest telemetry.
                </p>

              </div>

            </div>


            {/* RECOMMENDATION */}

            <div className="prediction-recommendation">

              <div className="prediction-recommendation-icon">
                <Wrench size={19} />
              </div>

              <div>
                <span>MAINTENANCE RECOMMENDATION</span>
                <p>
                  {prediction.recommendation}
                </p>
              </div>

            </div>

          </section>


          {/* SUMMARY CARDS */}

          <section className="prediction-summary-grid">

            <div className="prediction-summary-card">
              <div className="summary-icon blue">
                <TrendingUp size={19} />
              </div>

              <span>Total Predictions</span>

              <strong>{history.length}</strong>
            </div>


            <div className="prediction-summary-card">
              <div className="summary-icon red">
                <AlertTriangle size={19} />
              </div>

              <span>Failure Predictions</span>

              <strong>{failureCount}</strong>
            </div>


            <div className="prediction-summary-card">
              <div className="summary-icon green">
                <ShieldCheck size={19} />
              </div>

              <span>Normal Predictions</span>

              <strong>{normalCount}</strong>
            </div>


            <div className="prediction-summary-card">
              <div className="summary-icon purple">
                <Clock3 size={19} />
              </div>

              <span>Latest Prediction</span>

              <strong className="summary-time">
                {new Date(
                  prediction.prediction_time
                ).toLocaleString("en-IN", {
                  day: "2-digit",
                  month: "short",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </strong>
            </div>

          </section>


          {/* HISTORY */}

          <section className="prediction-history-panel">

            <div className="prediction-section-heading">
              <div>
                <p className="section-label">
                  PREDICTION HISTORY
                </p>

                <h2>Recent Model Predictions</h2>
              </div>

              <span>
                {history.length} records
              </span>
            </div>


            {sortedHistory.length > 0 ? (
              <div className="prediction-history-table-wrapper">

                <table className="prediction-history-table">

                  <thead>
                    <tr>
                      <th>Timestamp</th>
                      <th>Probability</th>
                      <th>Status</th>
                      <th>Model</th>
                      <th>Recommendation</th>
                    </tr>
                  </thead>

                  <tbody>

                    {sortedHistory
                      .slice(0, 10)
                      .map((item) => {

                        const percentage =
                          item.failure_probability * 100;

                        return (
                          <tr key={item.id}>

                            <td>
                              <strong>
                                {new Date(
                                  item.prediction_time
                                ).toLocaleString(
                                  "en-IN",
                                  {
                                    day: "2-digit",
                                    month: "short",
                                    year: "numeric",
                                    hour: "2-digit",
                                    minute: "2-digit",
                                  }
                                )}
                              </strong>
                            </td>

                            <td>
                              <strong>
                                {percentage.toFixed(2)}%
                              </strong>
                            </td>

                            <td>
                              <span
                                className={
                                  item.predicted_failure
                                    ? "history-status danger"
                                    : "history-status safe"
                                }
                              >
                                {item.predicted_failure
                                  ? "Failure"
                                  : "Normal"}
                              </span>
                            </td>

                            <td>
                              {item.model_version}
                            </td>

                            <td className="recommendation-cell">
                              {item.recommendation}
                            </td>

                          </tr>
                        );
                      })}

                  </tbody>

                </table>

              </div>
            ) : (
              <div className="prediction-empty">
                No prediction history available.
              </div>
            )}

          </section>

          {/* FAILURE PROBABILITY TREND */}

          <section className="telemetry-chart-panel">

            <div className="telemetry-section-heading">

              <div>
                <p className="section-label">
                  MACHINE LEARNING
                </p>

                <h2>Failure Probability Trend</h2>

                <p className="telemetry-chart-description">
                  Failure probability for the telemetry
                  records used during ML prediction.
                </p>
              </div>

              <span className="telemetry-record-count">
                {predictionChartData.length} predictions
              </span>

            </div>

            {predictionChartData.length > 0 ? (

              <div className="telemetry-chart">

                <ResponsiveContainer
                  width="100%"
                  height={350}
                >

                  <LineChart
                    data={predictionChartData}
                    margin={{
                      top: 10,
                      right: 20,
                      left: 5,
                      bottom: 10,
                    }}
                  >

                    <CartesianGrid
                      strokeDasharray="3 3"
                      vertical={false}
                    />

                    <XAxis
                      dataKey="time"
                      tick={{ fontSize: 12 }}
                    />

                    <YAxis
                      domain={[0, 100]}
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value) =>
                        `${value}%`
                      }
                    />

                    <Tooltip
                      formatter={(value) => [
                        `${Number(value).toFixed(2)}%`,
                        "Failure Probability",
                      ]}
                      labelFormatter={(label, payload) => {
                        const point = payload?.[0]?.payload;

                        if (!point) {
                          return `Telemetry: ${label}`;
                        }

                        return `Telemetry: ${new Date(
                          point.timestamp
                        ).toLocaleString("en-IN", {
                          day: "2-digit",
                          month: "short",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}`;
                      }}
                    />

                    <Line
                      type="monotone"
                      dataKey="failure_probability"
                      name="Failure Probability"
                      stroke="#dc2626"
                      strokeWidth={3}
                      dot={{ r: 5 }}
                      activeDot={{ r: 7 }}
                    />

                  </LineChart>

                </ResponsiveContainer>

              </div>

            ) : (

              <div className="prediction-chart-empty">

                <Activity size={22} />

                <strong>
                  No telemetry-linked predictions yet
                </strong>

                <span>
                  Run a prediction to create a
                  telemetry-linked result.
                </span>

              </div>

            )}

          </section>

          {/* MODEL EXPLAINABILITY */}

          <section className="prediction-explainability">

            <div className="telemetry-section-heading">

              <div>
                <p className="section-label">
                  MODEL EXPLAINABILITY
                </p>

                <h2>
                  Why did the model make this prediction?
                </h2>

                <p className="telemetry-chart-description">
                  Global feature importance shows how the trained model
                  uses features overall. Local SHAP values show how each
                  feature contributed to this specific prediction.
                </p>
              </div>

            </div>

            {explainabilityLoading ? (

              <div className="prediction-chart-empty">
                <Activity size={22} />
                <strong>
                  Loading model explanation...
                </strong>
              </div>

            ) : explainabilityError ? (

              <div className="prediction-chart-empty">
                <AlertTriangle size={22} />
                <strong>
                  Explainability unavailable
                </strong>
                <span>
                  {explainabilityError}
                </span>
              </div>

            ) : (

              <div className="prediction-explainability-grid">

                <div className="prediction-explainability-card">

                  <div className="prediction-explainability-card-header">

                    <div>
                      <p className="section-label">
                        GLOBAL
                      </p>

                      <h3>
                        Feature Importance
                      </h3>
                    </div>

                    <TrendingUp size={20} />

                  </div>

                  <div className="explainability-feature-list">

                    {featureImportance.map((item) => (

                      <div
                        className="explainability-feature-row"
                        key={item.feature}
                      >

                        <div className="explainability-feature-label">

                          <span>
                            {item.feature}
                          </span>

                          <strong>
                            {(item.importance * 100).toFixed(2)}%
                          </strong>

                        </div>

                        <div className="explainability-bar">

                          <div
                            className="explainability-bar-fill"
                            style={{
                              width: `${Math.min(
                                item.importance * 100,
                                100
                              )}%`,
                            }}
                          />

                        </div>

                      </div>

                    ))}

                  </div>

                </div>


                <div className="prediction-explainability-card">

                  <div className="prediction-explainability-card-header">

                    <div>
                      <p className="section-label">
                        LOCAL
                      </p>

                      <h3>
                        Prediction Drivers
                      </h3>
                    </div>

                    <Activity size={20} />

                  </div>

                  {shapExplanation?.explanation?.features?.length > 0 ? (

                    <div className="explainability-shap-list">

                      {shapExplanation.explanation.features.map(
                        (item) => (

                          <div
                            className="explainability-shap-row"
                            key={item.feature}
                          >

                            <div>

                              <strong>
                                {item.feature}
                              </strong>

                              <span
                                className={
                                  item.direction ===
                                    "increases_failure_risk"
                                    ? "shap-positive"
                                    : item.direction ===
                                      "decreases_failure_risk"
                                      ? "shap-negative"
                                      : "shap-neutral"
                                }
                              >

                                {item.direction ===
                                  "increases_failure_risk"
                                  ? "↑ Increases failure risk"
                                  : item.direction ===
                                    "decreases_failure_risk"
                                    ? "↓ Decreases failure risk"
                                    : "→ Neutral"}

                              </span>

                            </div>

                            <strong>
                              {item.shap_value > 0 ? "+" : ""}
                              {Number(
                                item.shap_value
                              ).toFixed(3)}
                            </strong>

                          </div>

                        )
                      )}

                    </div>

                  ) : (

                    <div className="prediction-chart-empty">

                      <span>
                        No local explanation available.
                      </span>

                    </div>

                  )}

                </div>

              </div>

            )}

            <div className="prediction-explainability-note">

              <ShieldCheck size={18} />

              <span>
                Model contribution only — these explanations indicate
                which input features influenced the prediction. They do
                not identify a failed component or provide a
                component-level diagnosis.
              </span>

            </div>

          </section>

        </>
      ) : (
        <section className="prediction-empty">
          No prediction is currently available.
        </section>
      )}

    </main>
  );
}



