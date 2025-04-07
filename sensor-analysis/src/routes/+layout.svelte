<script>
  let { children } = $props();
  import "../app.css";
</script>

<nav class="bg-gray-800 text-white p-4">
  <ul class="flex space-x-4">
    <li><a href="/" class="hover:underline">Dashboard</a></li>
    <li><a href="/alerts" class="hover:underline">Alerts</a></li>
    <li><a href="/network" class="hover:underline">Network Diagram</a></li>
  </ul>
</nav>

{@render children()}