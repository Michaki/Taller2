import type { AggregatedSensorData } from "../domain/AggregatedSensorData";
import { fetchSensors } from "../infrastructure/sensorAPI";

export async function getSensorData(): Promise<AggregatedSensorData[]> {
  return fetchSensors();
}
