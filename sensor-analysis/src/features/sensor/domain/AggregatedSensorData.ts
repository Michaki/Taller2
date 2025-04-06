export interface AggregatedSwitchData {
  id: string;
  timestamp: string;
  parent_switch_id: string;
  count: number;
  avg_bandwidth: number;
  avg_packet_loss: number;
  avg_latency: number;
  status: "healthy" | "warning" | "unhealthy";
  alert: boolean;
  raw_data: any[];
}
