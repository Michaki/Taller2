<script lang="ts">
  import { onMount } from 'svelte';
  import { sensorService } from '../../features/sensor/application/sensorService';

  // Alerts data and pagination state
  let alerts: any[] = [];
  let filterText = '';
  let currentPage = 1;
  let pageSize = 10;
  let totalCount = 0;
  let isLoading = false;
  
  // Load alerts based on current page, pageSize, and filterText.
  async function loadAlerts() {
    isLoading = true;
    const data = await sensorService.getAlertLogs(currentPage, pageSize, filterText);
    alerts = data.logs;
    totalCount = data.total;
    isLoading = false;
  }
  
  // Watch for changes in filterText (with a debounce if needed)
  $: if (filterText === '' || filterText.length >= 3) {
    // Reset to page 1 when search text changes
    currentPage = 1;
    loadAlerts();
  }
  
  function nextPage() {
    if (currentPage * pageSize < totalCount) {
      currentPage += 1;
      loadAlerts();
    }
  }
  
  function prevPage() {
    if (currentPage > 1) {
      currentPage -= 1;
      loadAlerts();
    }
  }
  
  onMount(loadAlerts);
</script>

<div class="min-h-screen bg-gray-50 p-6">
  <!-- Header -->
  <header class="mb-8">
    <h1 class="text-3xl font-semibold text-gray-800">Alert Logs</h1>
    <p class="text-gray-600">Detailed list of alert events with search and pagination</p>
  </header>
  
  <!-- Search Input -->
  <div class="mb-6">
    <input
      type="text"
      placeholder="Search alerts (min 3 characters)..."
      bind:value={filterText}
      class="w-full p-3 border rounded shadow-sm focus:outline-none focus:ring focus:border-blue-300"
    />
  </div>
  
  <!-- Alerts Table -->
  <div class="overflow-x-auto bg-white rounded-lg shadow">
    {#if isLoading}
      <div class="p-6 text-center">Loading...</div>
    {:else}
      <table class="min-w-full">
        <thead class="bg-gray-100">
          <tr>
            <th class="py-3 px-4 text-left text-sm font-medium text-gray-700">Switch ID</th>
            <th class="py-3 px-4 text-left text-sm font-medium text-gray-700">Status</th>
            <th class="py-3 px-4 text-left text-sm font-medium text-gray-700">Timestamp</th>
            <th class="py-3 px-4 text-left text-sm font-medium text-gray-700">Details</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          {#each alerts as alert}
            <tr>
              <td class="py-3 px-4 text-sm text-gray-800">{alert.switch_id}</td>
              <td class="py-3 px-4 text-sm">
                <span class={alert.status === 'healthy' ? 'text-green-600' : (alert.status === 'warning' ? 'text-yellow-500' : 'text-red-500')}>
                  {alert.status}
                </span>
              </td>
              <td class="py-3 px-4 text-sm text-gray-800">{alert.timestamp}</td>
              <td class="py-3 px-4 text-sm text-gray-800">{alert.details || 'N/A'}</td>
            </tr>
          {/each}
        </tbody>
      </table>
      {#if alerts.length === 0}
        <div class="p-6 text-center">No alerts found.</div>
      {/if}
    {/if}
  </div>
  
  <!-- Pagination Controls -->
  <div class="mt-6 flex items-center justify-between">
    <button
      class="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      on:click={prevPage}
      disabled={currentPage === 1 || isLoading}
    >
      Previous
    </button>
    <span class="text-gray-700">Page {currentPage} of {Math.ceil(totalCount / pageSize)}</span>
    <button
      class="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
      on:click={nextPage}
      disabled={currentPage * pageSize >= totalCount || isLoading}
    >
      Next
    </button>
  </div>
</div>
