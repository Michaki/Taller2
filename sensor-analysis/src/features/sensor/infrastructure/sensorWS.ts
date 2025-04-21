// src/features/sensor/infrastructure/sensorWS.ts

// Callback types for WS events
type TopologyUpdateCallback = (msg: { switch_id: string; state: string }) => void;
export type AggregatedUpdateCallback = (data: {
  state_summary: { healthy: number; warning: number; unhealthy: number };
  alert_count: number;
  timestamps: string[];
  avg_bandwidth_trend: number[];
  overall_metrics: { avg_latency: number; avg_packet_loss: number; avg_bandwidth: number };
}) => void;

const WEBSOCKET_BASE_URL = `ws://localhost:8000`;

class SensorWebSocket {
  // Alias for backward compatibility with existing topology page
  subscribe = this.subscribeTopology.bind(this);
  unsubscribe = this.unsubscribeTopology.bind(this);

  private sockets: Record<string, WebSocket | null> = {
    topology: null,
    dashboard: null
  };
  private topologyCallbacks: TopologyUpdateCallback[] = [];
  private aggregatedCallbacks: AggregatedUpdateCallback[] = [];

  private connect(channel: 'topology' | 'dashboard') {
    if (this.sockets[channel]) return;
    const path = channel === 'topology' ? '/ws/alerts' : '/ws/dashboard';
    const socket = new WebSocket(`${WEBSOCKET_BASE_URL}${path}`);
    this.sockets[channel] = socket;

    socket.onopen = () => console.log(`${channel} WS connected`);
    socket.onmessage = event => {
      try {
        const msg = JSON.parse(event.data);
        if (channel === 'topology' && msg.event === 'topology_update') {
          this.topologyCallbacks.forEach(cb => cb(msg.data));
        } else if (channel === 'dashboard' && msg.event === 'aggregated') {
          this.aggregatedCallbacks.forEach(cb => cb(msg.data));
        }
      } catch (err) {
        console.error(`Error parsing ${channel} WS message`, err);
      }
    };  
    socket.onerror = err => console.error(`${channel} WS error`, err);
    socket.onclose = () => {
      console.log(`${channel} WS closed`);
      this.sockets[channel] = null;
    };
  }

  /** Subscribe to topology_update events (alias: subscribe) */
  subscribeTopology(cb: TopologyUpdateCallback) {
    this.connect('topology');
    this.topologyCallbacks.push(cb);
  }

  unsubscribeTopology(cb: TopologyUpdateCallback) {
    this.topologyCallbacks = this.topologyCallbacks.filter(fn => fn !== cb);
  }

  /** Subscribe to aggregated metrics (alias: subscribeAggregated) */
  subscribeAggregated(cb: AggregatedUpdateCallback) {
    this.connect('dashboard');
    this.aggregatedCallbacks.push(cb);
  }

  unsubscribeAggregated(cb: AggregatedUpdateCallback) {
    this.aggregatedCallbacks = this.aggregatedCallbacks.filter(fn => fn !== cb);
  }
}

export const sensorWS = new SensorWebSocket();
