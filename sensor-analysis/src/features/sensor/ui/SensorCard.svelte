<script lang="ts">
  import type { AggregatedSensorData } from '../domain/AggregatedSensorData';
  export let sensor: AggregatedSensorData;
  let showDetails = false;
</script>

<div class="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow duration-300 cursor-pointer">
  <!-- Header with Record ID -->
  <h2 class="text-xl font-semibold text-gray-800 mb-4">
    Record ID: {sensor.id}
  </h2>

  <!-- Clickable Details Box -->
  <div 
    class="border border-gray-300 rounded p-4 hover:bg-gray-50" 
    on:click={() => showDetails = !showDetails}
  >
    <p class="text-gray-600">
      {showDetails ? 'Hide Details' : 'Click here to view details'}
    </p>

    {#if showDetails}
      <div class="mt-4 space-y-2">
        <div>
          <span class="block text-gray-600">Average Temperature:</span>
          <span class="text-2xl font-bold text-blue-500">
            {sensor.avg_temperature.toFixed(1)} °F
          </span>
        </div>
        <div>
          <span class="block text-gray-600">Average Humidity:</span>
          <span class="text-2xl font-bold text-green-500">
            {sensor.avg_humidity.toFixed(1)}%
          </span>
        </div>
        <div>
          <span class="block text-gray-600">Records Count:</span>
          <span class="text-xl font-semibold text-gray-700">
            {sensor.count}
          </span>
        </div>
        <div>
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
    {/if}
  </div>
</div>
