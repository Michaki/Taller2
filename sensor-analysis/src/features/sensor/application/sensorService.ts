import { sensorAPI } from "../infrastructure/sensorAPI";

export const sensorService = {
  async getAlertLogs(currentPage: number, pageSize: number, filter: string) {
    return await sensorAPI.getAlertLogs(currentPage, pageSize, filter);
  },
  async getTopology() {
    return await sensorAPI.getTopology();
  },
  async getAggregatedSensorData() {
    return await sensorAPI.getAggregatedData();
  },
};
