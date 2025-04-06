<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { AggregatedSwitchData } from '../features/sensor/domain/AggregatedSensorData';
  export let switchData: AggregatedSwitchData;
  const dispatch = createEventDispatcher();

  function handleClick() {
    // Dispatch event to show details for this switch
    dispatch('select', { switchData });
  }
</script>

<div on:click={handleClick} class="cursor-pointer p-4 border rounded hover:bg-gray-100">
  <h3 class="text-lg font-bold">Parent: {switchData.parent_switch_id}</h3>
  <p>Status: <span class="{switchData.status === 'healthy' ? 'text-green-600' : switchData.status === 'warning' ? 'text-yellow-600' : 'text-red-600'}">{switchData.status}</span></p>
  {#if switchData.alert}
    <p class="text-red-500 font-bold">ALERT!</p>
  {/if}
</div>
