import axios from "axios";

const BASE_URL = "http://localhost:8000";

export const sensorAPI = {
  async getAggregatedData() {
    const res = await axios.get(`${BASE_URL}/switch/aggregated`);
    return res.data;
  },
  async getAlertLogs() {
    const res = await axios.get(`${BASE_URL}/switch/alerts`);
    return res.data;
  },
  async getTopology() {
    const res = await axios.get(`${BASE_URL}/switch/topology`);
    return res.data;
  },
};
