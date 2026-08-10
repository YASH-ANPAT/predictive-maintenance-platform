import { useEffect, useState } from "react";
import {
  Activity,
  CalendarDays,
  Cpu,
  Factory,
  Gauge,
  RotateCw,
  Thermometer,
  Wrench,
} from "lucide-react";

import {
  getEquipment,
  getTelemetryHistory,
} from "../api/client";

export default function Equipment() {
  const [equipment, setEquipment] = useState(null);
  const [telemetry, setTelemetry] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadEquipment = async () => {
      try {
        setLoading(true);
        setError("");

        const [equipmentData, telemetryData] = await Promise.all([
          getEquipment(1),
          getTelemetryHistory(1),
        ]);

        setEquipment(equipmentData);

        const records = Array.isArray(telemetryData)
          ? telemetryData
          : telemetryData?.value || [];

        setTelemetry(records);
      } catch (err) {
        setError(
          err?.response?.data?.detail ||
            err?.message ||
            "Unable to load equipment information."
        );
      } finally {
        setLoading(false);
      }
    };

    loadEquipment();
  }, []);

  if (loading) {
    return (
      <main className="page-state">
        <div>
          <h1>Loading Equipment</h1>
          <p>Fetching machine information...</p>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="page-state">
        <div>
          <h1>Equipment Error</h1>
          <p>{error}</p>
        </div>
      </main>
    );
  }

  const latest = telemetry[0] || null;

  return (
    <main className="equipment-page-v2">

      {/* HEADER */}

      <header className="equipment-page-header">
        <div>
          <p className="section-label">EQUIPMENT MANAGEMENT</p>
          <h1>Equipment Overview</h1>
          <p className="equipment-page-subtitle">
            Machine identity, operating conditions, and current health data.
          </p>
        </div>

        <div className="equipment-live-badge">
          <span />
          System Online
        </div>
      </header>


      {/* MACHINE HERO */}

      <section className="equipment-hero">

        <div className="equipment-hero-icon">
          <Cpu size={38} />
        </div>

        <div className="equipment-hero-content">

          <p className="section-label">SELECTED EQUIPMENT</p>

          <h2>{equipment.name}</h2>

          <p className="equipment-identity">
            {equipment.equipment_code}
            <span>·</span>
            {equipment.category}
            <span>·</span>
            Machine Type {equipment.machine_type}
          </p>

          <div className="equipment-meta-row">

            <div>
              <Factory size={15} />
              <span>{equipment.manufacturer}</span>
            </div>

            <div>
              <Cpu size={15} />
              <span>Model {equipment.model_number}</span>
            </div>

          </div>

        </div>

        <div className="equipment-active-badge">
          <span />
          {equipment.status}
        </div>

      </section>


      {/* CURRENT HEALTH */}

      <section className="equipment-section">

        <div className="equipment-section-heading">
          <div>
            <p className="section-label">CURRENT TELEMETRY</p>
            <h2>Equipment Health</h2>
          </div>

          <span className="telemetry-count">
            {telemetry.length} records
          </span>
        </div>


        <div className="equipment-metrics">

          <div className="equipment-metric-card blue">
            <div className="equipment-metric-icon">
              <Thermometer size={19} />
            </div>

            <span>Air Temperature</span>

            <strong>
              {latest ? latest.air_temperature : "--"}
              <small> K</small>
            </strong>
          </div>


          <div className="equipment-metric-card red">
            <div className="equipment-metric-icon">
              <Thermometer size={19} />
            </div>

            <span>Process Temperature</span>

            <strong>
              {latest ? latest.process_temperature : "--"}
              <small> K</small>
            </strong>
          </div>


          <div className="equipment-metric-card purple">
            <div className="equipment-metric-icon">
              <RotateCw size={19} />
            </div>

            <span>Rotational Speed</span>

            <strong>
              {latest ? latest.rotational_speed : "--"}
              <small> rpm</small>
            </strong>
          </div>


          <div className="equipment-metric-card orange">
            <div className="equipment-metric-icon">
              <Gauge size={19} />
            </div>

            <span>Torque</span>

            <strong>
              {latest ? latest.torque : "--"}
              <small> Nm</small>
            </strong>
          </div>


          <div className="equipment-metric-card cyan">
            <div className="equipment-metric-icon">
              <Wrench size={19} />
            </div>

            <span>Tool Wear</span>

            <strong>
              {latest ? latest.tool_wear : "--"}
              <small> min</small>
            </strong>
          </div>

        </div>

      </section>


      {/* DETAILS */}

      <section className="equipment-details-grid">

        <div className="equipment-info-panel">

          <div className="equipment-section-heading">
            <div>
              <p className="section-label">MACHINE PROFILE</p>
              <h2>Equipment Details</h2>
            </div>
          </div>

          <div className="equipment-detail-list">

            <div>
              <span>Equipment Code</span>
              <strong>{equipment.equipment_code}</strong>
            </div>

            <div>
              <span>Machine Type</span>
              <strong>{equipment.machine_type}</strong>
            </div>

            <div>
              <span>Category</span>
              <strong>{equipment.category}</strong>
            </div>

            <div>
              <span>Manufacturer</span>
              <strong>{equipment.manufacturer}</strong>
            </div>

            <div>
              <span>Model Number</span>
              <strong>{equipment.model_number}</strong>
            </div>

            <div>
              <span>Status</span>
              <strong className="detail-status">
                <span />
                {equipment.status}
              </strong>
            </div>

          </div>

        </div>


        <div className="equipment-info-panel">

          <div className="equipment-section-heading">
            <div>
              <p className="section-label">SYSTEM INFORMATION</p>
              <h2>Lifecycle</h2>
            </div>
          </div>

          <div className="lifecycle-list">

            <div className="lifecycle-item">
              <div className="lifecycle-icon">
                <CalendarDays size={18} />
              </div>

              <div>
                <span>Installation Date</span>
                <strong>
                  {equipment.installation_date
                    ? new Date(
                        equipment.installation_date
                      ).toLocaleDateString("en-IN")
                    : "Not recorded"}
                </strong>
              </div>
            </div>


            <div className="lifecycle-item">
              <div className="lifecycle-icon">
                <Activity size={18} />
              </div>

              <div>
                <span>Last Telemetry</span>
                <strong>
                  {latest
                    ? new Date(
                        latest.recorded_at
                      ).toLocaleString("en-IN", {
                        day: "2-digit",
                        month: "short",
                        hour: "2-digit",
                        minute: "2-digit",
                      })
                    : "No telemetry"}
                </strong>
              </div>
            </div>


            <div className="lifecycle-item">
              <div className="lifecycle-icon">
                <Cpu size={18} />
              </div>

              <div>
                <span>Last Updated</span>
                <strong>
                  {new Date(
                    equipment.updated_at
                  ).toLocaleString("en-IN", {
                    day: "2-digit",
                    month: "short",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </strong>
              </div>
            </div>

          </div>

        </div>

      </section>

    </main>
  );
}
