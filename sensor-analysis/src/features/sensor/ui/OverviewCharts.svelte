<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import Chart from "chart.js/auto";

  export let aggregatedData: any; 

  let canvas: HTMLCanvasElement;
  let chart: Chart;

  onMount(() => {
    console.log("Aggregated Data:", aggregatedData);
    chart = new Chart(canvas, {
      type: "line",
      data: {
        labels: aggregatedData.map((d: any) => d.timestamp),
        datasets: [{
          label: "Avg Bandwidth",
          data: aggregatedData.map((d: any) => d.avg_bandwidth),
          borderColor: "blue",
          fill: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
      }
    });
  });

  $: if (chart && aggregatedData) {
    chart.data.labels = aggregatedData.map((d: any) => d.timestamp);
    chart.data.datasets[0].data = aggregatedData.map((d: any) => d.bandwidth_usage);
    chart.update();
  }

  onDestroy(() => {
    chart.destroy();
  });
</script>

<div class="w-full h-64">
  <canvas bind:this={canvas}></canvas>
</div>
