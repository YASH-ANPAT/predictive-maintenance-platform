import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  Clock3,
  Gauge,
  RefreshCw,
  RotateCw,
  Thermometer,
  Wrench,
} from "lucide-react";
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

import { getTelemetryHistory } from "../api/client";

export default function Telemetry() {
  const [telemetry, setTelemetry] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const loadTelemetry = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }

      setError("");

      const response = await getTelemetryHistory(1);

      const records = Array.isArray(response)
        ? response
        : response?.value || [];

      setTelemetry(
        [...records].sort(
          (a, b) =>
            new Date(a.recorded_at) -
            new Date(b.recorded_at)
        )
      );
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Unable to load telemetry data."
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadTelemetry();
  }, []);

  const latest = useMemo(
    () => telemetry[telemetry.length - 1] || null,
    [telemetry]
  );

  const chartData = useMemo(
    () =>
      telemetry.map((item) => ({
        ...item,
        time: new Date(item.recorded_at).toLocaleTimeString(
          "en-IN",
          {
            hour: "2-digit",
            minute: "2-digit",
          }
        ),
      })),
    [telemetry]
  );

  if (loading) {
    return (
      <main className="page-state">
        <div>
          <h1>Loading Telemetry</h1>
          <p>Fetching machine sensor history...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="page-state">
        <div>
          <h1>Telemetry Error</h1>
          <p>{error}</p>

          <button
            className="telemetry-refresh-button"
            onClick={() => loadTelemetry()}
          >
            <RefreshCw size={16} />
            Retry
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="telemetry-page">

      {/* HEADER */}

      <header className="telemetry-page-header">

        <div>
          <p className="section-label">
            SENSOR MONITORING
          </p>

          <h1>Telemetry</h1>

          <p className="telemetry-page-subtitle">
            Real-time and historical operating data from
            the selected machine.
          </p>
        </div>

        <button
          className="telemetry-refresh-button"
          onClick={() => loadTelemetry(true)}
          disabled={refreshing}
        >
          <RefreshCw
            size={16}
            className={refreshing ? "spin" : ""}
          />
          {refreshing ? "Refreshing..." : "Refresh Data"}
        </button>

      </header>


      {/* MACHINE STATUS */}

      <section className="telemetry-machine-bar">

        <div className="telemetry-machine-icon">
          <Activity size={24} />
        </div>

        <div>
          <span>MONITORED EQUIPMENT</span>
          <strong>Hydraulic Production Unit</strong>
        </div>

        <div className="telemetry-machine-code">
          PMP-H001 · Machine Type M
        </div>

        <div className="telemetry-online">
          <span />
          Live telemetry
        </div>

      </section>


      {/* LATEST VALUES */}

      <section className="telemetry-section">

        <div className="telemetry-section-heading">
          <div>
            <p className="section-label">
              LATEST READING
            </p>

            <h2>Current Sensor Values</h2>
          </div>

          {latest && (
            <span className="telemetry-updated">
              <Clock3 size={14} />
              {new Date(
                latest.recorded_at
              ).toLocaleString("en-IN", {
                day: "2-digit",
                month: "short",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          )}
        </div>


        <div className="telemetry-value-grid">

          <TelemetryValue
            icon={<Thermometer size={19} />}
            label="Air Temperature"
            value={latest?.air_temperature}
            unit="K"
            tone="blue"
          />

          <TelemetryValue
            icon={<Thermometer size={19} />}
            label="Process Temperature"
            value={latest?.process_temperature}
            unit="K"
            tone="red"
          />

          <TelemetryValue
            icon={<RotateCw size={19} />}
            label="Rotational Speed"
            value={latest?.rotational_speed}
            unit="rpm"
            tone="purple"
          />

          <TelemetryValue
            icon={<Gauge size={19} />}
            label="Torque"
            value={latest?.torque}
            unit="Nm"
            tone="orange"
          />

          <TelemetryValue
            icon={<Wrench size={19} />}
            label="Tool Wear"
            value={latest?.tool_wear}
            unit="min"
            tone="cyan"
          />

        </div>

      </section>


      {/* TEMPERATURE CHART */}

      <section className="telemetry-chart-panel">

        <div className="telemetry-section-heading">

          <div>
            <p className="section-label">
              TEMPERATURE
            </p>

            <h2>Temperature Trend</h2>
          </div>

          <span className="telemetry-record-count">
            {telemetry.length} observations
          </span>

        </div>

        <div className="telemetry-chart">
          <ResponsiveContainer width="100%" height={350}>
            <LineChart
              data={chartData}
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
                tick={{ fontSize: 12 }}
              />

              <Tooltip />

              <Legend />

              <Line
                type="monotone"
                dataKey="air_temperature"
                name="Air Temperature (K)"
                stroke="#2563eb"
                strokeWidth={2.5}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />

              <Line
                type="monotone"
                dataKey="process_temperature"
                name="Process Temperature (K)"
                stroke="#dc2626"
                strokeWidth={2.5}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

      </section>


      {/* OPERATING CONDITIONS */}

      <section className="telemetry-chart-panel">

        <div className="telemetry-section-heading">

          <div>
            <p className="section-label">
              MACHINE PARAMETERS
            </p>

            <h2>Operating Conditions</h2>
          </div>

          <span className="telemetry-record-count">
            Live machine parameters
          </span>

        </div>

        <div className="telemetry-chart">
          <ResponsiveContainer width="100%" height={350}>
            <LineChart
              data={chartData}
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
                tick={{ fontSize: 12 }}
              />

              <Tooltip />

              <Legend />

              <Line
                type="monotone"
                dataKey="rotational_speed"
                name="Speed (rpm)"
                stroke="#7c3aed"
                strokeWidth={2.5}
                dot={{ r: 4 }}
              />

              <Line
                type="monotone"
                dataKey="tool_wear"
                name="Tool Wear (min)"
                stroke="#0891b2"
                strokeWidth={2.5}
                dot={{ r: 4 }}
              />

              <Line
                type="monotone"
                dataKey="torque"
                name="Torque (Nm)"
                stroke="#ea580c"
                strokeWidth={2.5}
                dot={{ r: 4 }}
              />

            </LineChart>
          </ResponsiveContainer>
        </div>

      </section>

      {/* RAW TELEMETRY */}

      <section className="telemetry-table-panel">

        <div className="telemetry-section-heading">

          <div>
            <p className="section-label">
              SENSOR HISTORY
            </p>

            <h2>Telemetry Records</h2>
          </div>

          <span className="telemetry-record-count">
            {telemetry.length} records
          </span>

        </div>


        <div className="telemetry-table-wrapper">

          <table className="telemetry-table">

            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Air Temp.</th>
                <th>Process Temp.</th>
                <th>Speed</th>
                <th>Torque</th>
                <th>Tool Wear</th>
              </tr>
            </thead>

            <tbody>

              {[...telemetry]
                .reverse()
                .map((item) => (

                  <tr key={item.id}>

                    <td>
                      <strong>
                        {new Date(
                          item.recorded_at
                        ).toLocaleString("en-IN", {
                          day: "2-digit",
                          month: "short",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </strong>
                    </td>

                    <td>
                      {item.air_temperature} K
                    </td>

                    <td>
                      {item.process_temperature} K
                    </td>

                    <td>
                      {item.rotational_speed} rpm
                    </td>

                    <td>
                      {item.torque} Nm
                    </td>

                    <td>
                      {item.tool_wear} min
                    </td>

                  </tr>

                ))}

            </tbody>

          </table>

        </div>

      </section>

    </main>
  );
}


function TelemetryValue({
  icon,
  label,
  value,
  unit,
  tone,
}) {
  return (
    <div className={`telemetry-value-card ${tone}`}>

      <div className="telemetry-value-icon">
        {icon}
      </div>

      <span>{label}</span>

      <strong>
        {value ?? "--"}
        <small>{unit}</small>
      </strong>

    </div>
  );
}




