<script lang="ts">
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';
  import { sensorService } from '../features/sensor/application/sensorService';

  // Aggregated metrics from the backend
  let aggregatedData: any = {};
  let healthyCount = 0;
  let alertCount = 0;
  let timestamps: string[] = [];
  let avgBandwidthValues: number[] = [];

  let bandwidthChartCanvas: HTMLCanvasElement;
  let healthChartCanvas: HTMLCanvasElement;
  let bandwidthChart: Chart;
  let healthChart: Chart;

  onMount(async () => {
    // Get data from the updated aggregated endpoint
    aggregatedData = await sensorService.getAggregatedSensorData();
    healthyCount = aggregatedData.healthy_count;
    alertCount = aggregatedData.alert_count;
    timestamps = aggregatedData.timestamps;
    avgBandwidthValues = aggregatedData.avg_bandwidth;

    // Initialize both charts after data loads
    initBandwidthChart();
    initHealthChart();
  });

  function initBandwidthChart() {
    const ctx = bandwidthChartCanvas.getContext('2d');
    if(!ctx) return;

    // Create a vertical gradient for a cozy, modern look
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(75,192,192,0.4)');
    gradient.addColorStop(1, 'rgba(75,192,192,0)');

    bandwidthChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: timestamps,
        datasets: [{
          label: 'Avg Bandwidth (Mbps)',
          data: avgBandwidthValues,
          backgroundColor: gradient,
          borderColor: 'rgba(75,192,192,1)',
          tension: 0.4,  // smooth curve
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

  function initHealthChart() {
    const ctx = healthChartCanvas.getContext('2d');
    if(!ctx) return;
    healthChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Healthy', 'Alerts'],
        datasets: [{
          data: [healthyCount, alertCount],
          backgroundColor: ['#34D399', '#F87171'],
          hoverBackgroundColor: ['#059669', '#EF4444'],
          borderWidth: 0,
        }]
      },
      options: {
        plugins: {
          legend: {
            position: 'bottom',
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
          },
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
    <p class="text-gray-600">Real-time overview of your network health</p>
  </header>
  
  <!-- KPI Cards -->
  <section class="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-8">
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Healthy Switches</h2>
      <p class="mt-4 text-4xl font-bold text-green-600">{healthyCount}</p>
    </div>
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700">Alerts</h2>
      <p class="mt-4 text-4xl font-bold text-red-500">{alertCount}</p>
    </div>
  </section>

  <!-- Charts -->
  <section class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700 mb-4">Avg Bandwidth Usage</h2>
      <div class="relative h-80">
        <canvas bind:this={bandwidthChartCanvas}></canvas>
      </div>
    </div>
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-lg font-medium text-gray-700 mb-4">Switch Health Distribution</h2>
      <div class="relative h-80">
        <canvas bind:this={healthChartCanvas}></canvas>
      </div>
    </div>
  </section>
</div>
