import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  ShieldCheck,
  Wrench,
  Activity,
  RefreshCw,
} from "lucide-react";

import {
  getEquipment,
  getLatestPrediction,
  getPredictionHistory,
  getMaintenanceHistory,
} from "../api/client";

const EQUIPMENT_ID = 1;

function getRiskMeta(probability) {
  const percentage = probability * 100;

  if (percentage >= 80) {
    return {
      level: "CRITICAL",
      className: "critical",
      action: "Immediate maintenance inspection recommended.",
      icon: AlertTriangle,
    };
  }

  if (percentage >= 60) {
    return {
      level: "HIGH",
      className: "high",
      action: "Schedule maintenance inspection soon and monitor equipment closely.",
      icon: AlertTriangle,
    };
  }

  if (percentage >= 40) {
    return {
      level: "MODERATE",
      className: "moderate",
      action: "Inspect equipment condition and monitor telemetry for increasing risk.",
      icon: Activity,
    };
  }

  if (percentage >= 20) {
    return {
      level: "LOW",
      className: "low",
      action: "Plan preventive maintenance and continue routine monitoring.",
      icon: Clock3,
    };
  }

  return {
    level: "NORMAL",
    className: "normal",
    action: "No immediate maintenance action required. Continue routine monitoring.",
    icon: ShieldCheck,
  };
}

function formatDate(value) {
  if (!value) return "—";

  return new Date(value).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatMaintenanceDate(value) {
  if (!value) return "—";

  return new Date(`${value}T00:00:00`).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

export default function Maintenance() {
  const [equipment, setEquipment] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [history, setHistory] = useState([]);
  const [maintenanceRecords, setMaintenanceRecords] = useState([]);

  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadData = async (showRefreshing = false) => {
    try {
      if (showRefreshing) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const [
        equipmentData,
        predictionData,
        historyData,
        maintenanceData,
      ] = await Promise.all([
        getEquipment(EQUIPMENT_ID),
        getLatestPrediction(EQUIPMENT_ID),
        getPredictionHistory(EQUIPMENT_ID),
        getMaintenanceHistory(),
      ]);

      setEquipment(equipmentData);
      setPrediction(predictionData);
      setHistory(historyData);

      const maintenanceRecordsData = Array.isArray(maintenanceData)
        ? maintenanceData
        : maintenanceData?.value || [];

      setMaintenanceRecords(maintenanceRecordsData);
    } catch (err) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
        "Unable to load maintenance information."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const risk = useMemo(() => {
    if (!prediction) return null;

    return getRiskMeta(prediction.failure_probability);
  }, [prediction]);

  const riskPercentage = prediction
    ? prediction.failure_probability * 100
    : 0;

  const maintenanceStatus = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return maintenanceRecords.map((record) => {
      const scheduledDate = new Date(
        `${record.scheduled_date}T00:00:00`
      );

      const isOverdue =
        record.status === "Scheduled" &&
        scheduledDate < today;

      const isUpcoming =
        record.status === "Scheduled" &&
        scheduledDate >= today;

      return {
        ...record,
        isOverdue,
        isUpcoming,
      };
    });
  }, [maintenanceRecords]);

  const overdueMaintenance = maintenanceStatus.filter(
    (record) => record.isOverdue
  );

  const upcomingMaintenance = maintenanceStatus.filter(
    (record) => record.isUpcoming
  );

  const inProgressMaintenance = maintenanceStatus.filter(
    (record) => record.status === "In Progress"
  );

  const completedMaintenance = maintenanceStatus.filter(
    (record) => record.status === "Completed"
  );

  const activeMaintenance = maintenanceStatus
    .filter(
      (record) =>
        record.status === "Scheduled" ||
        record.status === "In Progress"
    )
    .sort(
      (a, b) =>
        new Date(`${a.scheduled_date}T00:00:00`) -
        new Date(`${b.scheduled_date}T00:00:00`)
    );

  const maintenanceHistory = maintenanceStatus
    .filter(
      (record) =>
        record.status === "Completed" ||
        record.status === "Cancelled"
    )
    .sort(
      (a, b) =>
        new Date(
          `${b.completed_date || b.scheduled_date}T00:00:00`
        ) -
        new Date(
          `${a.completed_date || a.scheduled_date}T00:00:00`
        )
    );

  if (loading) {
    return (
      <div className="page-state">
        <Activity size={28} />
        <h2>Loading Maintenance Center</h2>
        <p>
          Retrieving current equipment risk and
          maintenance recommendations...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-state">
        <AlertTriangle size={30} />
        <h2>Unable to Load Maintenance Data</h2>
        <p>{error}</p>

        <button
          className="maintenance-refresh-button"
          onClick={() => loadData()}
        >
          <RefreshCw size={16} />
          Retry
        </button>
      </div>
    );
  }

  const RiskIcon = risk?.icon || ShieldCheck;

  return (
    <div className="maintenance-page">

      {/* HEADER */}

      <div className="maintenance-header">
        <div>
          <p className="section-label">
            MAINTENANCE CENTER
          </p>

          <h1>Maintenance Overview</h1>

          <p className="maintenance-subtitle">
            Risk-based maintenance guidance from the
            latest machine prediction.
          </p>
        </div>

        <button
          className="maintenance-refresh-button"
          onClick={() => loadData(true)}
          disabled={refreshing}
        >
          <RefreshCw
            size={16}
            className={refreshing ? "spin" : ""}
          />

          {refreshing ? "Refreshing..." : "Refresh Data"}
        </button>
      </div>

      {/* EQUIPMENT BAR */}

      <section className="maintenance-equipment-bar">
        <div className="maintenance-equipment-icon">
          <Wrench size={22} />
        </div>

        <div>
          <span className="maintenance-label">
            EQUIPMENT
          </span>

          <strong>
            {equipment?.name || "Unknown Equipment"}
          </strong>
        </div>

        <div className="maintenance-equipment-code">
          {equipment?.equipment_code || "—"}
        </div>

        <div className="maintenance-equipment-status">
          <span />
          {equipment?.status || "Unknown"}
        </div>
      </section>

      {/* MAIN RISK CARD */}

      {prediction && risk && (
        <section className={`maintenance-risk-card ${risk.className}`}>
          <div className="maintenance-risk-header">
            <div>
              <p className="section-label">
                CURRENT RISK ASSESSMENT
              </p>

              <h2>{risk.level}</h2>
            </div>

            <div className="maintenance-risk-icon">
              <RiskIcon size={28} />
            </div>
          </div>

          <div className="maintenance-risk-content">
            <div className="maintenance-risk-score">
              <strong>{riskPercentage.toFixed(2)}</strong>
              <span>%</span>
            </div>

            <div className="maintenance-risk-details">
              <div className="maintenance-meter-label">
                <span>Failure probability</span>

                <strong>
                  {riskPercentage.toFixed(2)}%
                </strong>
              </div>

              <div className="maintenance-meter">
                <div
                  className={`maintenance-meter-fill ${risk.className}`}
                  style={{
                    width: `${Math.min(
                      riskPercentage,
                      100
                    )}%`,
                  }}
                />
              </div>

              <p>
                Estimated by the current ML prediction
                from the latest available telemetry.
              </p>
            </div>
          </div>
        </section>
      )}

      {/* RECOMMENDATION */}

      {prediction && risk && (
        <section className="maintenance-recommendation">
          <div className="maintenance-recommendation-icon">
            <Wrench size={21} />
          </div>

          <div className="maintenance-recommendation-content">
            <span>MAINTENANCE RECOMMENDATION</span>

            <h3>{prediction.recommendation}</h3>

            <p>{risk.action}</p>
          </div>
        </section>
      )}

      {/* INFORMATION GRID */}

      <div className="maintenance-info-grid">
        <section className="maintenance-info-card">
          <div className="maintenance-card-heading">
            <Clock3 size={19} />

            <div>
              <p className="section-label">
                LAST ASSESSMENT
              </p>

              <h3>Prediction Details</h3>
            </div>
          </div>

          {prediction ? (
            <div className="maintenance-details-list">
              <div>
                <span>Prediction time</span>

                <strong>
                  {formatDate(
                    prediction.prediction_time
                  )}
                </strong>
              </div>

              <div>
                <span>Model version</span>

                <strong>
                  {prediction.model_version}
                </strong>
              </div>

              <div>
                <span>Classification</span>

                <strong>
                  {prediction.predicted_failure
                    ? "Failure predicted"
                    : "Normal"}
                </strong>
              </div>
            </div>
          ) : (
            <p>No prediction available.</p>
          )}
        </section>

        {/* RISK SCALE */}

        <section className="maintenance-info-card">
          <div className="maintenance-card-heading">
            <Activity size={19} />

            <div>
              <p className="section-label">
                RISK SCALE
              </p>

              <h3>Decision Levels</h3>
            </div>
          </div>

          <div className="risk-scale">
            <div className="risk-scale-item critical">
              <span />
              <div>
                <strong>Critical</strong>
                <small>80–100%</small>
              </div>
            </div>

            <div className="risk-scale-item high">
              <span />
              <div>
                <strong>High</strong>
                <small>60–79.99%</small>
              </div>
            </div>

            <div className="risk-scale-item moderate">
              <span />
              <div>
                <strong>Moderate</strong>
                <small>40–59.99%</small>
              </div>
            </div>

            <div className="risk-scale-item low">
              <span />
              <div>
                <strong>Low</strong>
                <small>20–39.99%</small>
              </div>
            </div>

            <div className="risk-scale-item normal">
              <span />
              <div>
                <strong>Normal</strong>
                <small>0–19.99%</small>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* RECENT PREDICTION HISTORY */}

      <section className="maintenance-history">
        <div className="maintenance-history-header">
          <div>
            <p className="section-label">
              PREDICTION HISTORY
            </p>

            <h2>Recent Risk Assessments</h2>
          </div>

          <span>{history.length} recorded</span>
        </div>

        {history.length > 0 ? (
          <div className="maintenance-history-list">
            {history.slice(0, 8).map((item) => {
              const itemRisk = getRiskMeta(
                item.failure_probability
              );

              return (
                <div
                  className="maintenance-history-row"
                  key={item.id}
                >
                  <div className="maintenance-history-time">
                    <strong>
                      {(
                        item.failure_probability * 100
                      ).toFixed(2)}%
                    </strong>

                    <span>
                      {formatDate(
                        item.prediction_time
                      )}
                    </span>
                  </div>

                  <span
                    className={`maintenance-history-risk ${itemRisk.className}`}
                  >
                    {itemRisk.level}
                  </span>

                  <span
                    className={
                      item.predicted_failure
                        ? "maintenance-history-result failure"
                        : "maintenance-history-result normal"
                    }
                  >
                    {item.predicted_failure
                      ? "Failure predicted"
                      : "Normal"}
                  </span>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="maintenance-empty">
            <CheckCircle2 size={22} />

            <p>
              No prediction history is available yet.
            </p>
          </div>
        )}
      </section>

      {/* MAINTENANCE STATUS OVERVIEW */}

      <section className="maintenance-history">
        <div className="maintenance-history-header">
          <div>
            <p className="section-label">
              MAINTENANCE OPERATIONS
            </p>

            <h2>Maintenance Status</h2>

            <p className="maintenance-subtitle">
              Current operational state of maintenance work. These records are independent of the ML failure prediction and do not represent component-level diagnosis.
            </p>
          </div>

          <span>
            {maintenanceRecords.length} records
          </span>
        </div>

        <div className="maintenance-info-grid">
          <section className="maintenance-info-card">
            <div className="maintenance-card-heading">
              <AlertTriangle size={19} />

              <div>
                <p className="section-label">OVERDUE</p>
                <h3>{overdueMaintenance.length}</h3>
              </div>
            </div>

            <p>Scheduled maintenance past its planned date.</p>
          </section>

          <section className="maintenance-info-card">
            <div className="maintenance-card-heading">
              <Clock3 size={19} />

              <div>
                <p className="section-label">UPCOMING</p>
                <h3>{upcomingMaintenance.length}</h3>
              </div>
            </div>

            <p>Scheduled maintenance that has not yet started.</p>
          </section>

          <section className="maintenance-info-card">
            <div className="maintenance-card-heading">
              <Activity size={19} />

              <div>
                <p className="section-label">IN PROGRESS</p>
                <h3>{inProgressMaintenance.length}</h3>
              </div>
            </div>

            <p>Maintenance currently marked as in progress.</p>
          </section>

          <section className="maintenance-info-card">
            <div className="maintenance-card-heading">
              <CheckCircle2 size={19} />

              <div>
                <p className="section-label">COMPLETED</p>
                <h3>{completedMaintenance.length}</h3>
              </div>
            </div>

            <p>Maintenance work successfully completed.</p>
          </section>
        </div>
      </section>

      {/* MAINTENANCE SCHEDULE */}

      <section className="maintenance-history">
        <div className="maintenance-history-header">
          <div>
            <p className="section-label">
              ACTIVE MAINTENANCE
            </p>

            <h2>Maintenance Schedule</h2>
          </div>
        </div>

        {activeMaintenance.length > 0 ? (
          <div className="maintenance-history-list">
            {activeMaintenance.map((record) => (
              <div
                className="maintenance-history-row"
                key={record.id}
              >
                <div className="maintenance-history-time">
                  <strong>
                    {record.maintenance_type}
                  </strong>

                  <span>
                    {record.description}
                  </span>
                </div>

                <span>
                  {record.technician}
                </span>

                <span
                  className={
                    record.isOverdue
                      ? "maintenance-history-risk critical"
                      : "maintenance-history-risk normal"
                  }
                >
                  {record.isOverdue
                    ? "OVERDUE"
                    : record.status.toUpperCase()}
                </span>

                <span>
                  {formatMaintenanceDate(
                    record.scheduled_date
                  )}
                </span>

                <span>
                  ₹{Number(record.cost).toLocaleString("en-IN")}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="maintenance-empty">
            <CheckCircle2 size={22} />

            <p>
              No active maintenance records are available.
            </p>
          </div>
        )}
      </section>

      {/* MAINTENANCE HISTORY */}

      <section className="maintenance-history">
        <div className="maintenance-history-header">
          <div>
            <p className="section-label">
              MAINTENANCE HISTORY
            </p>

            <h2>Completed & Cancelled</h2>
          </div>

          <span>
            {maintenanceHistory.length} recorded
          </span>
        </div>

        {maintenanceHistory.length > 0 ? (
          <div className="maintenance-history-list">
            {maintenanceHistory.map((record) => (
              <div
                className="maintenance-history-row"
                key={record.id}
              >
                <div className="maintenance-history-time">
                  <strong>
                    {record.maintenance_type}
                  </strong>

                  <span>
                    {record.description}
                  </span>
                </div>

                <span>
                  {record.technician}
                </span>

                <span>
                  {formatMaintenanceDate(
                    record.completed_date ||
                    record.scheduled_date
                  )}
                </span>

                <span>
                  ₹{Number(record.cost).toLocaleString("en-IN")}
                </span>

                <span
                  className={`maintenance-history-risk ${
                    record.status === "Completed"
                      ? "normal"
                      : "moderate"
                  }`}
                >
                  {record.status.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="maintenance-empty">
            <CheckCircle2 size={22} />

            <p>
              No maintenance history is available yet.
            </p>
          </div>
        )}
      </section>

    </div>
  );
}
