import "../App.css";
import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  RefreshCw,
  ShieldCheck,
  Wrench,
} from "lucide-react";

import {
  getEquipment,
  getPredictionHistory,
  getLatestPrediction,
  getTelemetryHistory,
  runPrediction,
} from "../api/client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function formatDateTime(value) {
  if (!value) return "â€”";

  return new Date(value).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function MetricCard({ label, value, unit }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>
        {value ?? "â€”"}
        {unit && value !== null && value !== undefined ? (
          <small> {unit}</small>
        ) : null}
      </strong>
    </div>
  );
}

export default function Dashboard() {
  const EQUIPMENT_ID = 1;

  const [equipment, setEquipment] = useState(null);
  const [telemetry, setTelemetry] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);

  const [loading, setLoading] = useState(true);
  const [runningPrediction, setRunningPrediction] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadDashboard = async () => {
    try {
      setError("");

      const [
        equipmentData,
        telemetryData,
        predictionData,
        predictionHistoryData,
      ] = await Promise.all([
        getEquipment(EQUIPMENT_ID),
        getTelemetryHistory(EQUIPMENT_ID),
        getLatestPrediction(EQUIPMENT_ID),
        getPredictionHistory(EQUIPMENT_ID),
      ]);

      setEquipment(equipmentData);
      setTelemetry(Array.isArray(telemetryData) ? telemetryData : []);
      setPrediction(predictionData);
      setHistory(
        Array.isArray(predictionHistoryData)
          ? predictionHistoryData
          : [],
      );
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
          "Unable to load dashboard data.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const sortedTelemetry = useMemo(() => {
    return [...telemetry].sort(
      (a, b) =>
        new Date(a.recorded_at) -
        new Date(b.recorded_at),
    );
  }, [telemetry]);

  const latestTelemetry =
    sortedTelemetry.length > 0
      ? sortedTelemetry[sortedTelemetry.length - 1]
      : null;

  const chartData = sortedTelemetry.map((item) => ({
    time: new Date(item.recorded_at).toLocaleTimeString(
      "en-IN",
      {
        hour: "2-digit",
        minute: "2-digit",
      },
    ),
    temperature: Number(item.process_temperature),
    speed: Number(item.rotational_speed),
    torque: Number(item.torque),
    toolWear: Number(item.tool_wear),
  }));

  const riskPercentage = prediction
    ? prediction.failure_probability * 100
    : 0;

  const riskLevel = prediction?.predicted_failure
    ? "HIGH RISK"
    : "NORMAL";

  const handleRunPrediction = async () => {
    try {
      setRunningPrediction(true);
      setMessage("");
      setError("");

      const result = await runPrediction(EQUIPMENT_ID);

      setPrediction(result);

      const updatedHistory =
        await getPredictionHistory(EQUIPMENT_ID);

      setHistory(
        Array.isArray(updatedHistory)
          ? updatedHistory
          : [],
      );

      setMessage("Prediction completed successfully.");
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
          "Prediction failed.",
      );
    } finally {
      setRunningPrediction(false);
    }
  };

  if (loading) {
    return (
      <div className="page-state">
        <div>
          <h1>Loading Dashboard</h1>
          <p>
            Connecting to predictive maintenance
            services...
          </p>
        </div>
      </div>
    );
  }

  if (error && !equipment) {
    return (
      <div className="page-state">
        <div>
          <h1>Dashboard Error</h1>
          <p>{error}</p>
          <button onClick={loadDashboard}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">

      {/* HEADER */}

      <header className="topbar">
        <div>
          <p className="eyebrow">
            PREDICTIVE MAINTENANCE PLATFORM
          </p>

          <h1>Equipment Monitoring Dashboard</h1>

          <p className="subtitle">
            Machine health monitoring and ML-powered
            failure prediction.
          </p>
        </div>

        <div className="api-status">
          <span />
          API Connected
        </div>
      </header>

      {error && (
        <p className="error-message">{error}</p>
      )}

      {/* EQUIPMENT */}

      <section className="equipment-card">
        <div>
          <p className="section-label">
            EQUIPMENT
          </p>

          <h2>
            {equipment?.name || "Unknown Equipment"}
          </h2>

          <p>
            {equipment?.equipment_code} Â·{" "}
            {equipment?.machine_type
              ? `Machine Type ${equipment.machine_type}`
              : ""}
          </p>
        </div>

        <div className="equipment-status">
          <span />
          {equipment?.status || "Unknown"}
        </div>
      </section>

      {/* TELEMETRY METRICS */}

      <section className="metrics-grid">

        <MetricCard
          label="Air Temperature"
          value={latestTelemetry?.air_temperature}
          unit="K"
        />

        <MetricCard
          label="Process Temperature"
          value={latestTelemetry?.process_temperature}
          unit="K"
        />

        <MetricCard
          label="Rotational Speed"
          value={latestTelemetry?.rotational_speed}
          unit="rpm"
        />

        <MetricCard
          label="Torque"
          value={latestTelemetry?.torque}
          unit="Nm"
        />

        <MetricCard
          label="Tool Wear"
          value={latestTelemetry?.tool_wear}
          unit="min"
        />

      </section>

      {/* TELEMETRY CHART */}

      <section className="panel">

        <div className="panel-heading">
          <div>
            <p className="section-label">
              TELEMETRY
            </p>

            <h2>
              Equipment Sensor History
            </h2>
          </div>

          <span>
            {telemetry.length} records
          </span>
        </div>

        <div className="chart-container">

          {chartData.length > 0 ? (
            <ResponsiveContainer
              width="100%"
              height={320}
            >
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />

                <XAxis dataKey="time" />

                <YAxis />

                <Tooltip />

                <Legend />

                <Line
                  type="monotone"
                  dataKey="temperature"
                  name="Process Temp (K)"
                  stroke="#2563eb"
                  strokeWidth={2}
                />

                <Line
                  type="monotone"
                  dataKey="speed"
                  name="Speed (rpm)"
                  stroke="#16a34a"
                  strokeWidth={2}
                />

                <Line
                  type="monotone"
                  dataKey="torque"
                  name="Torque (Nm)"
                  stroke="#dc2626"
                  strokeWidth={2}
                />

                <Line
                  type="monotone"
                  dataKey="toolWear"
                  name="Tool Wear (min)"
                  stroke="#9333ea"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="page-state">
              <p>No telemetry available.</p>
            </div>
          )}

        </div>
      </section>

      {/* RISK + HISTORY */}

      <section className="bottom-grid">

        {/* RISK */}

        <div className="panel risk-panel">

          <div className="panel-heading">

            <div>
              <p className="section-label">
                LATEST PREDICTION
              </p>

              <h2>Failure Risk</h2>
            </div>

            {prediction?.predicted_failure ? (
              <AlertTriangle
                size={22}
                className="risk-icon"
              />
            ) : (
              <ShieldCheck
                size={22}
                className="safe-icon"
              />
            )}

          </div>

          {prediction ? (
            <>
              <div className="risk-layout">

                <div>

                  <div className="risk-score">
                    {riskPercentage.toFixed(2)}
                    <small>%</small>
                  </div>

                  <div
                    className={
                      prediction.predicted_failure
                        ? "risk-status danger"
                        : "risk-status safe"
                    }
                  >
                    {riskLevel}
                  </div>

                </div>

                <div className="risk-meter">

                  <div className="meter-label">
                    <span>
                      Failure probability
                    </span>

                    <strong>
                      {riskPercentage.toFixed(2)}%
                    </strong>
                  </div>

                  <div className="meter-track">
                    <div
                      className={
                        prediction.predicted_failure
                          ? "meter-fill danger-fill"
                          : "meter-fill safe-fill"
                      }
                      style={{
                        width: `${Math.min(
                          riskPercentage,
                          100,
                        )}%`,
                      }}
                    />
                  </div>

                  <p>
                    Model prediction based on latest
                    machine telemetry.
                  </p>

                </div>

              </div>

              <div className="recommendation">

                <div className="recommendation-icon">
                  <Wrench size={18} />
                </div>

                <div>
                  <span>
                    MAINTENANCE RECOMMENDATION
                  </span>

                  <p>
                    {prediction.recommendation}
                  </p>
                </div>

              </div>

              <button
                className="prediction-button"
                onClick={handleRunPrediction}
                disabled={runningPrediction}
              >
                {runningPrediction ? (
                  <>
                    <RefreshCw
                      size={16}
                      className="spin"
                    />
                    Running Prediction...
                  </>
                ) : (
                  <>
                    <Activity size={16} />
                    Run New Prediction
                  </>
                )}
              </button>

              {message && (
                <p className="success-message">
                  <CheckCircle2 size={15} />
                  {message}
                </p>
              )}
            </>
          ) : (
            <p>No prediction available.</p>
          )}

        </div>

        {/* HISTORY */}

        <div className="panel">

          <div className="panel-heading">

            <div>
              <p className="section-label">
                PREDICTION HISTORY
              </p>

              <h2>Recent Predictions</h2>
            </div>

            <BarChart3 size={20} />

          </div>

          {history.length > 0 ? (
            <div className="history">

              {history.slice(0, 6).map((item) => (
                <div
                  className="history-row"
                  key={item.id}
                >

                  <div className="history-time">

                    <strong>
                      {(
                        item.failure_probability *
                        100
                      ).toFixed(2)}
                      %
                    </strong>

                    <span>
                      {formatDateTime(
                        item.prediction_time,
                      )}
                    </span>

                  </div>

                  <span
                    className={
                      item.predicted_failure
                        ? "history-danger"
                        : "history-safe"
                    }
                  >
                    {item.predicted_failure
                      ? "Failure"
                      : "Normal"}
                  </span>

                </div>
              ))}

            </div>
          ) : (
            <p>No prediction history.</p>
          )}

        </div>

      </section>

    </div>
  );
}
