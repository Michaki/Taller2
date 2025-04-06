import type { AggregatedSensorData } from "../domain/AggregatedSensorData";
import axios from "axios";

export async function fetchSensors(): Promise<AggregatedSensorData[]> {
  const res = await axios.get("http://localhost:8000/sensors/aggregated");
  return res.data.records.map((record: any) => ({
    id: record._id,
    ...record._source,
  }));
}
