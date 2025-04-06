<script lang="ts">
  import { onMount } from 'svelte';
  import type { AggregatedSensorData } from '../domain/AggregatedSensorData';
  import { getSensorData } from '../application/sensorService';
  import SensorCard from './SensorCard.svelte';

  let sensors: AggregatedSensorData[] = [];

  onMount(async () => {
    sensors = await getSensorData();
    console.log("Aggregated sensor data loaded:", sensors);
  });
</script>

<div class="min-h-screen bg-gray-50">
  <!-- Header -->
  <header class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-6 shadow">
    <div class="container mx-auto px-4">
      <h1 class="text-3xl font-bold">Sensor Data Dashboard</h1>
      <p class="mt-2">Overview of Aggregated Sensor Data</p>
    </div>
  </header>

  <!-- Main Content -->
  <main class="container mx-auto px-4 py-8">
    {#if sensors.length === 0}
      <div class="text-center text-gray-600">Loading sensor data...</div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each sensors as sensor (sensor.id)}
          <SensorCard {sensor} />
        {/each}
      </div>
    {/if}
  </main>

  <!-- Footer -->
  <footer class="bg-gray-200 py-4 mt-8">
    <div class="container mx-auto px-4 text-center text-gray-600">
      &copy; {new Date().getFullYear()} Sensor Dashboard. All rights reserved.
    </div>
  </footer>
</div>
