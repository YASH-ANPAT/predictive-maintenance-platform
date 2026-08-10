import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  headers: {
    "Content-Type": "application/json",
  },
});

export const getEquipment = async (equipmentId) => {
  const response = await api.get(`/equipment/${equipmentId}`);
  return response.data;
};

export const getTelemetryHistory = async (equipmentId) => {
  const response = await api.get(`/telemetry/equipment/${equipmentId}`);
  return response.data;
};

export const getLatestPrediction = async (equipmentId) => {
  const response = await api.get(`/prediction/latest/${equipmentId}`);
  return response.data;
};

export const getPredictionHistory = async (equipmentId) => {
  const response = await api.get(`/prediction/history/${equipmentId}`);
  return response.data;
};

export const runPrediction = async (equipmentId) => {
  const response = await api.post(`/prediction/run/${equipmentId}`);
  return response.data;
};
export const getFeatureImportance = async () => {
  const response = await api.get(
    "/prediction/explainability/feature-importance"
  );
  return response.data;
};

export const getPredictionExplainability = async (predictionId) => {
  const response = await api.get(
    `/prediction/explainability/${predictionId}`
  );
  return response.data;
};

export const getMaintenanceHistory = async () => {
  const response = await api.get("/maintenance/");
  return response.data;
};

export const getEquipmentMaintenance = async (equipmentId) => {
  const response = await api.get(
    `/maintenance/equipment/${equipmentId}`
  );
  return response.data;
};

export const checkApiHealth = async () => {
  const response = await api.get("/");
  return response.data;
};

export default api;


