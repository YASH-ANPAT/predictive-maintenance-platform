import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import "./App.css";

import Layout from "./Layout";
import Dashboard from "./pages/Dashboard";
import Equipment from "./pages/Equipment";
import Telemetry from "./pages/Telemetry";
import Predictions from "./pages/Predictions";
import Maintenance from "./pages/Maintenance";

function Placeholder({ title }) {
  return (
    <div className="page-state">
      <div>
        <h1>{title}</h1>
        <p>This page is under construction.</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/equipment"
            element={<Equipment />}
          />

          <Route path="/telemetry" element={<Telemetry />} />

          <Route path="/predictions" element={<Predictions />} />

          <Route
            path="/maintenance"
            element={<Maintenance />}
          />

          <Route
            path="/"
            element={
              <Navigate
                to="/dashboard"
                replace
              />
            }
          />

          <Route
            path="*"
            element={
              <Navigate
                to="/dashboard"
                replace
              />
            }
          />

        </Routes>
      </Layout>
    </BrowserRouter>
  );
}




