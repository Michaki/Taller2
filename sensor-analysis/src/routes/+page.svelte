<script lang="ts">
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';
  import { sensorService } from '../features/sensor/application/sensorService';

  // Aggregated dashboard data from backend endpoint
  let aggregatedData: any = {};
  let stateSummary: { healthy?: number, warning?: number, unhealthy?: number } = {};
  let alertCount = 0;
  let timestamps: string[] = [];
  let avgBandwidthTrend: number[] = [];
  let overallMetrics: {
    avg_latency?: number;
    avg_packet_loss?: number;
    avg_bandwidth?: number;
  } = {};

  let bandwidthChartCanvas: HTMLCanvasElement;
  let bandwidthChart: Chart;

  onMount(async () => {
    // Fetch aggregated data from our endpoint
    aggregatedData = await sensorService.getAggregatedSensorData();
    stateSummary = aggregatedData.state_summary;
    alertCount = aggregatedData.alert_count;
    timestamps = aggregatedData.timestamps;
    avgBandwidthTrend = aggregatedData.avg_bandwidth_trend;
    overallMetrics = aggregatedData.overall_metrics;

    initBandwidthChart();
  });

  function initBandwidthChart() {
    const ctx = bandwidthChartCanvas.getContext('2d');
    if (!ctx) {
      console.error('Failed to get canvas context');
      return;
    }
    // Create a vertical gradient for a modern, cozy look
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(75,192,192,0.4)');
    gradient.addColorStop(1, 'rgba(75,192,192,0)');

    bandwidthChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: timestamps,
        datasets: [{
          label: 'Avg Bandwidth (Mbps)',
          data: avgBandwidthTrend,
          backgroundColor: gradient,
          borderColor: 'rgba(75,192,192,1)',
          tension: 0.4, // smooth curve
          fill: true,
          pointRadius: 3,
          pointHoverRadius: 5,
        }]
      },
      options: {
        plugins: {
          legend: {
            display: true,
            labels: {
              color: '#333',
              font: { size: 14 }
            }
          },
          tooltip: {
            backgroundColor: '#fff',
            titleColor: '#333',
            bodyColor: '#666',
            borderColor: '#ddd',
            borderWidth: 1,
          }
        },
        scales: {
          x: {
            ticks: {
              color: '#555',
              font: { size: 12 }
            },
            grid: { color: 'rgba(200,200,200,0.1)' }
          },
          y: {
            ticks: {
              color: '#555',
              font: { size: 12 }
            },
            grid: { color: 'rgba(200,200,200,0.1)' }
          }
        },
        responsive: true,
        maintainAspectRatio: false,
      }
    });
  }
</script>

<div class="min-h-screen bg-gray-50 p-6">
  <!-- Header -->
  <header class="mb-8">
    <h1 class="text-3xl font-semibold text-gray-800">Network Monitoring Dashboard</h1>
    <p class="text-gray-600">Real-time overview of switch states and performance metrics</p>
  </header>
  
  <!-- KPI Cards: State Summary -->
  <section class="grid grid-cols-1 sm:grid-cols-4 gap-6 mb-8">
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Healthy</h2>
      <p class="mt-4 text-4xl font-bold text-green-600">{stateSummary.healthy || 0}</p>
    </div>
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Warning</h2>
      <p class="mt-4 text-4xl font-bold text-yellow-500">{stateSummary.warning || 0}</p>
    </div>
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Unhealthy</h2>
      <p class="mt-4 text-4xl font-bold text-red-500">{stateSummary.unhealthy || 0}</p>
    </div>
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Alerts</h2>
      <p class="mt-4 text-4xl font-bold text-red-600">{alertCount}</p>
    </div>
  </section>

  <!-- Overall Metrics -->
  <section class="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Avg Bandwidth</h2>
      <p class="mt-4 text-3xl font-bold text-blue-600">
        {overallMetrics.avg_bandwidth ? overallMetrics.avg_bandwidth.toFixed(2) : '--'} Mbps
      </p>
    </div>
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Avg Latency</h2>
      <p class="mt-4 text-3xl font-bold text-indigo-600">
        {overallMetrics.avg_latency ? overallMetrics.avg_latency.toFixed(2) : '--'} ms
      </p>
    </div>
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Avg Packet Loss</h2>
      <p class="mt-4 text-3xl font-bold text-purple-600">
        {overallMetrics.avg_packet_loss ? overallMetrics.avg_packet_loss.toFixed(2) : '--'} %
      </p>
    </div>
  </section>

  <!-- Bandwidth Trend Chart -->
  <section class="bg-white rounded-lg shadow p-6">
    <h2 class="text-lg font-medium text-gray-700 mb-4">Avg Bandwidth Trend</h2>
    <div class="relative h-80">
      <canvas bind:this={bandwidthChartCanvas}></canvas>
    </div>
  </section>
</div>
