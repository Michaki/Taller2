import axios from "axios";
import type { AggregatedSwitchData } from "../domain/AggregatedSensorData";

export async function fetchSwitches(): Promise<AggregatedSwitchData[]> {
  const res = await axios.get("http://localhost:8000/switches/aggregated");
  return res.data.records.map((record: any) => ({
    id: record._id,
    ...record._source,
  }));
}
