import { NavLink } from "react-router-dom";
import {
  Activity,
  BarChart3,
  Cpu,
  LayoutDashboard,
  Settings,
  Wrench,
} from "lucide-react";

const navigation = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Equipment",
    path: "/equipment",
    icon: Cpu,
  },
  {
    label: "Telemetry",
    path: "/telemetry",
    icon: Activity,
  },
  {
    label: "Predictions",
    path: "/predictions",
    icon: BarChart3,
  },
  {
    label: "Maintenance",
    path: "/maintenance",
    icon: Wrench,
  },
];

export default function Layout({ children }) {
  return (
    <div className="app-shell">

      <aside className="sidebar">

        <div className="sidebar-brand">
          <div className="brand-icon">
            <Activity size={24} />
          </div>

          <div>
            <strong>Predictive</strong>
            <span>Maintenance</span>
          </div>
        </div>

        <p className="sidebar-section-title">
          OPERATIONS
        </p>

        <nav className="sidebar-nav">
          {navigation.map(({ label, path, icon: Icon }) => (
            <NavLink
              key={path}
              to={path}
              className={({ isActive }) =>
                `sidebar-link ${
                  isActive ? "active" : ""
                }`
              }
            >
              <Icon size={19} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="system-status">
            <span />
            <div>
              <strong>System Online</strong>
              <small>API Connected</small>
            </div>
          </div>

          <small className="version">
            Predictive Maintenance Platform
            <br />
            v1.0.0
          </small>
        </div>

      </aside>

      <main className="app-main">
        {children}
      </main>

    </div>
  );
}
