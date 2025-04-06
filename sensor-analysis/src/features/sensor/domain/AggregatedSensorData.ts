import type { Sensor } from "./Sensor";

export interface AggregatedSensorData {
  id: string;
  timestamp: string;
  count: number;
  avg_temperature: number;
  avg_humidity: number;
  min_temperature: number;
  max_temperature: number;
  alert: boolean;
  raw_data: Sensor[];
}
