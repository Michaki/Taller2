<script lang="ts">
  import { onMount } from 'svelte';
  import type { AggregatedSensorData } from '../domain/AggregatedSensorData';
  import { getSensorData } from '../application/sensorService';

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
          <div class="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow duration-300">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">Record ID: {sensor.id}</h2>
            <div class="mb-2">
              <span class="block text-gray-600">Average Temperature:</span>
              <span class="text-2xl font-bold text-blue-500">
                {sensor.avg_temperature.toFixed(1)} °F
              </span>
            </div>
            <div class="mb-2">
              <span class="block text-gray-600">Average Humidity:</span>
              <span class="text-2xl font-bold text-green-500">
                {sensor.avg_humidity.toFixed(1)}%
              </span>
            </div>
            <div class="mb-2">
              <span class="block text-gray-600">Records Count:</span>
              <span class="text-xl font-semibold text-gray-700">
                {sensor.count}
              </span>
            </div>
            <div class="mb-2">
              <span class="block text-gray-600">Timestamp:</span>
              <span class="text-sm text-gray-500">
                {new Date(sensor.timestamp).toLocaleString()}
              </span>
            </div>
            <div>
              <span class="block text-gray-600">Alert:</span>
              {#if sensor.alert}
                <span class="inline-block bg-red-500 text-white px-2 py-1 rounded">
                  Yes
                </span>
              {:else}
                <span class="inline-block bg-green-500 text-white px-2 py-1 rounded">
                  No
                </span>
              {/if}
            </div>
          </div>
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
