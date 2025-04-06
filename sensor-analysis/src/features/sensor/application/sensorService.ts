import { fetchSwitches } from "../infrastructure/sensorAPI";
import type { AggregatedSwitchData } from "../domain/AggregatedSensorData";

export async function getSwitchData(): Promise<AggregatedSwitchData[]> {
  return fetchSwitches();
}
