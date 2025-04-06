<script lang="ts">
  import { onMount } from 'svelte';
  import { alerts } from '$lib/alerts';

  let socket: WebSocket;

  onMount(() => {
    socket = new WebSocket('ws://localhost:8000/ws/alerts');
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // For example, data could be: { id: "some-parent-id", status: "unhealthy" }
      alerts.update((cur) => {
        // Update the store with new alert info; simple merge logic here
        return [...cur.filter(a => a.id !== data.id), data];
      });
    };

    return () => {
      socket.close();
    };
  });
</script>

<div>
  <h2>Live Alerts</h2>
  <ul>
    {#each $alerts as alert}
      <li>{alert.id} - {alert.status}</li>
    {/each}
  </ul>
</div>
