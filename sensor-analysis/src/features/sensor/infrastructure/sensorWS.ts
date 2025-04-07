// src/features/sensor/infrastructure/sensorWS.ts
export type TopologyUpdateCallback = (msg: {
  switch_id: string;
  state: string;
}) => void;

const WEBSOCKET_URL = `ws://localhost:8000`;

class SensorWebSocket {
  private socket: WebSocket | null = null;
  private callbacks: TopologyUpdateCallback[] = [];

  connect() {
    if (this.socket) return;
    const url = WEBSOCKET_URL + `/ws/alerts`;
    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log("WebSocket connected");
      // Optionally send a subscription message here if needed.
      // this.socket.send(JSON.stringify({ subscribe: "alert" }));
    };

    this.socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.event === "topology_update" && msg.data) {
          this.callbacks.forEach((cb) => cb(msg.data));
        }
      } catch (error) {
        console.error("Error parsing WS message", error);
      }
    };

    this.socket.onerror = (error) => {
      console.error("WebSocket error", error);
    };

    this.socket.onclose = () => {
      console.log("WebSocket closed");
      this.socket = null;
    };
  }

  subscribe(callback: TopologyUpdateCallback) {
    if (!this.socket) {
      this.connect();
    }
    this.callbacks.push(callback);
  }

  // Optionally, you can add an unsubscribe method.
  unsubscribe(callback: TopologyUpdateCallback) {
    this.callbacks = this.callbacks.filter((cb) => cb !== callback);
  }
}

export const sensorWS = new SensorWebSocket();
