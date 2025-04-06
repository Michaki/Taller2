# utils/thresholds.py

BANDWIDTH_THRESHOLD = 800  # Mbps
PACKET_LOSS_THRESHOLD = 2    # Percent
LATENCY_THRESHOLD = 80       # ms

# Multipliers for aggregated data (used in stream_consumer logic)
BANDWIDTH_UNHEALTHY_MULTIPLIER = 1.2
PACKET_LOSS_UNHEALTHY_MULTIPLIER = 1.5
LATENCY_UNHEALTHY_MULTIPLIER = 1.2

def determine_status(bandwidth: float, packet_loss: float, latency: float, alert_mode: bool = False) -> str:
    """
    Determine the status of a switch (or an aggregated group) based on its metrics.
    
    When alert_mode is True, any metric exceeding its threshold returns "unhealthy".
    Otherwise (for aggregated data):
      - If any metric exceeds its base threshold, then:
           * If any metric is more severe (exceeding the threshold multiplied by a factor),
             returns "unhealthy".
           * Otherwise, returns "warning".
      - Returns "healthy" if no thresholds are exceeded.
    """
    if alert_mode:
        if bandwidth > BANDWIDTH_THRESHOLD or packet_loss > PACKET_LOSS_THRESHOLD or latency > LATENCY_THRESHOLD:
            return "unhealthy"
        return "healthy"
    else:
        if bandwidth > BANDWIDTH_THRESHOLD or packet_loss > PACKET_LOSS_THRESHOLD or latency > LATENCY_THRESHOLD:
            if (bandwidth > BANDWIDTH_THRESHOLD * BANDWIDTH_UNHEALTHY_MULTIPLIER or 
                packet_loss > PACKET_LOSS_THRESHOLD * PACKET_LOSS_UNHEALTHY_MULTIPLIER or 
                latency > LATENCY_THRESHOLD * LATENCY_UNHEALTHY_MULTIPLIER):
                return "unhealthy"
            return "warning"
        return "healthy"
