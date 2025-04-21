<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import Chart from 'chart.js/auto';
  import { sensorWS } from '../features/sensor/infrastructure/sensorWS';

  // Estado del dashboard
  let stateSummary = { healthy: 0, warning: 0, unhealthy: 0 };
  let alertCount = 0;
  let timestamps: string[] = [];
  let avgBandwidthTrend: number[] = [];
  let overallMetrics = { avg_latency: 0, avg_packet_loss: 0, avg_bandwidth: 0 };

  let bandwidthChartCanvas: HTMLCanvasElement;
  let bandwidthChart: Chart;

  function initBandwidthChart() {
    const ctx = bandwidthChartCanvas.getContext('2d');
    if (!ctx) {
      console.error('Failed to get canvas context');
      return;
    }
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(75,192,192,0.4)');
    gradient.addColorStop(1, 'rgba(75,192,192,0)');

    bandwidthChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: [{
          label: 'Avg Bandwidth (Mbps)',
          data: [],
          backgroundColor: gradient,
          borderColor: 'rgba(75,192,192,1)',
          tension: 0.4,
          fill: true,
          pointRadius: 3,
          pointHoverRadius: 5,
        }]
      },
      options: {
        plugins: {
          legend: { display: true, labels: { color: '#333', font: { size: 14 } } },
          tooltip: { backgroundColor: '#fff', titleColor: '#333', bodyColor: '#666', borderColor: '#ddd', borderWidth: 1 }
        },
        scales: {
          x: { ticks: { color: '#555', font: { size: 12 } }, grid: { color: 'rgba(200,200,200,0.1)' } },
          y: { ticks: { color: '#555', font: { size: 12 } }, grid: { color: 'rgba(200,200,200,0.1)' } }
        },
        responsive: true,
        maintainAspectRatio: false,
      }
    });
  }

  function updateBandwidthChart() {
    bandwidthChart.data.labels = timestamps;
    bandwidthChart.data.datasets[0].data = avgBandwidthTrend;
    bandwidthChart.update();
  }

  // Callback al recibir datos vía WS
  const handleAggregated = (data: any) => {
    stateSummary      = data.state_summary;
    alertCount        = data.alert_count;
    timestamps        = data.timestamps;
    avgBandwidthTrend = data.avg_bandwidth_trend;
    overallMetrics    = data.overall_metrics;
    updateBandwidthChart();
  };

  onMount(() => {
    initBandwidthChart();
    sensorWS.subscribeAggregated(handleAggregated);
  });

  onDestroy(() => {
    sensorWS.unsubscribeAggregated(handleAggregated);
  });
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
      <p class="mt-4 text-4xl font-bold text-green-600">{stateSummary.healthy}</p>
    </div>
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Warning</h2>
      <p class="mt-4 text-4xl font-bold text-yellow-500">{stateSummary.warning}</p>
    </div>
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Unhealthy</h2>
      <p class="mt-4 text-4xl font-bold text-red-500">{stateSummary.unhealthy}</p>
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
      <p class="mt-4 text-3xl font-bold text-blue-600">{overallMetrics.avg_bandwidth.toFixed(2)} Mbps</p>
    </div>
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Avg Latency</h2>
      <p class="mt-4 text-3xl font-bold text-indigo-600">{overallMetrics.avg_latency.toFixed(2)} ms</p>
    </div>
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Avg Packet Loss</h2>
      <p class="mt-4 text-3xl font-bold text-purple-600">{overallMetrics.avg_packet_loss.toFixed(2)} %</p>
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
