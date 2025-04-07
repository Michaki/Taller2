import axios from "axios";

const BASE_URL = "http://localhost:8000";

export const sensorAPI = {
  async getAggregatedData() {
    const res = await axios.get(`${BASE_URL}/switch/aggregated`);
    return res.data;
  },
  async getAlertLogs(currentPage: number, pageSize: number, filter: string) {
    const res = await axios.get(`${BASE_URL}/switch/alerts`, {
      params: { page: currentPage, page_size: pageSize, search: filter },
    });
    return res.data;
  },
  async getTopology() {
    const res = await axios.get(`${BASE_URL}/switch/topology`);
    return res.data;
  },
};
