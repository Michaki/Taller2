<script lang="ts">
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import { sensorService } from '../../features/sensor/application/sensorService';
  import { sensorWS } from '../../features/sensor/infrastructure/sensorWS';

  interface Node {
    id: string;
    label: string;
    nodeState: 'healthy' | 'warning' | 'critical' | 'unknown';
    x?: number;
    y?: number;
    fx?: number | null;
    fy?: number | null;
  }

  interface Edge {
    source: string | Node;
    target: string | Node;
  }

  let topology: { nodes: Node[]; edges: Edge[] } = { nodes: [], edges: [] };
  let svgElement: SVGSVGElement;
  let simulation: d3.Simulation<any, undefined>;
  let zoom: d3.ZoomBehavior<Element, unknown>;

  async function loadTopology() {
    topology = await sensorService.getTopology();
    renderGraph();
  }

  function renderGraph() {
    // Use full viewport size for the SVG container
    const width = window.innerWidth;
    const height = window.innerHeight - 120; // leave some room for header
    const svg = d3.select(svgElement)
      .attr('width', width)
      .attr('height', height);

    // Clear any previous content
    svg.selectAll('*').remove();

    // Create a group container that will be zoomed and panned
    const container = svg.append('g');

    // Setup zoom behavior on the container
    zoom = d3.zoom()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
      });
    (svg as d3.Selection<SVGSVGElement, unknown, null, undefined>).call(zoom as unknown as (selection: d3.Selection<SVGSVGElement, unknown, null, undefined>) => void);

    simulation = d3.forceSimulation(topology.nodes)
      .force('link', d3.forceLink(topology.edges).id((d: any) => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Draw links
    const link = container.append('g')
      .attr('stroke', '#bbb')
      .attr('stroke-opacity', 0.8)
      .selectAll('line')
      .data(topology.edges)
      .enter()
      .append('line')
      .attr('stroke-width', 1.5);

    // Draw nodes
    const node = container.append('g')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .selectAll('circle')
      .data(topology.nodes)
      .enter()
      .append('circle')
      .attr('r', 8)
      .attr('fill', d => {
        if (d.nodeState === 'healthy') return '#34D399';
        if (d.nodeState === 'warning') return '#FBBF24';
        if (d.nodeState === 'critical') return '#F87171';
        return '#9CA3AF';
      })
      .call(d3.drag<SVGCircleElement, Node>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Add labels
    const labels = container.append('g')
      .selectAll('text')
      .data(topology.nodes)
      .enter()
      .append('text')
      .attr('dy', -12)
      .attr('text-anchor', 'middle')
      .attr('fill', '#4B5563')
      .attr('font-size', '11px')
      .text(d => d.label);

    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node
        .attr('cx', d => d.x ?? 0)
        .attr('cy', d => d.y ?? 0);

      labels
        .attr('x', d => d.x ?? 0)
        .attr('y', d => d.y ?? 0);
    });

    function dragstarted(event: d3.D3DragEvent<SVGCircleElement, Node, Node>, d: Node) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    function dragged(event: d3.D3DragEvent<SVGCircleElement, Node, Node>, d: Node) {
      d.fx = event.x;
      d.fy = event.y;
    }
    function dragended(event: d3.D3DragEvent<SVGCircleElement, Node, Node>, d: Node) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  }

  function handleTopologyUpdate(data: { switch_id: string; state: string }) {
    const node = topology.nodes.find(n => n.id === data.switch_id);
    if (node) {
      node.nodeState = data.state as Node["nodeState"];
      d3.select(svgElement)
        .selectAll('circle')
        .filter((d) => (d as Node).id === data.switch_id)
        .transition()
        .duration(500)
        .attr('fill', data.state === 'healthy'
          ? '#34D399'
          : data.state === 'warning'
          ? '#FBBF24'
          : data.state === 'critical'
          ? '#F87171'
          : '#9CA3AF');
    }
  }

  onMount(() => {
    loadTopology();
    sensorWS.subscribe(handleTopologyUpdate);
  });
</script>

<div class="min-h-screen bg-gray-100">
  <!-- Header -->
  <header class="p-4 text-center">
    <h1 class="text-4xl font-semibold text-gray-800">Network Topology</h1>
    <p class="text-gray-600 mt-2">Real-time visualization of switch relationships (drag, pan, zoom)</p>
  </header>
  
  <!-- Graph Container -->
  <main class="flex justify-center items-center">
    <div class="bg-white shadow rounded-lg w-full h-[80vh] overflow-hidden">
      <svg bind:this={svgElement}></svg>
    </div>
  </main>
</div>
