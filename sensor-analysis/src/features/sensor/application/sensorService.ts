import { sensorAPI } from "../infrastructure/sensorAPI";

export const sensorService = {
  async getAlertLogs() {
    return await sensorAPI.getAlertLogs();
  },
  async getTopology() {
    return await sensorAPI.getTopology();
  },
  async getAggregatedSensorData() {
    return await sensorAPI.getAggregatedData();
  },
};
