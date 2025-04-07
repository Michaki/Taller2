<script lang="ts">
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  import { sensorService } from '../../features/sensor/application/sensorService';
  import { sensorWS, type TopologyUpdateCallback } from '../../features/sensor/infrastructure/sensorWS';

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

  // Zoom behavior instance
  let zoom: d3.ZoomBehavior<Element, unknown>;

  async function loadTopology() {
    topology = await sensorService.getTopology();
    renderGraph();
  }

  function renderGraph() {
    const width = 800;
    const height = 600;
    const svg = d3.select(svgElement)
      .attr('width', width)
      .attr('height', height);

    // Clear previous content
    svg.selectAll('*').remove();

    // Create a container group that will be zoomed and panned
    const container = svg.append('g');

    // Set up zoom behavior
    zoom = d3.zoom()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        container.attr('transform', event.transform);
      });
    (svg as d3.Selection<SVGSVGElement, unknown, null, undefined>).call(zoom as unknown as (selection: d3.Selection<SVGSVGElement, unknown, null, undefined>) => void);

    // Set up simulation with nodes and links
    simulation = d3.forceSimulation(topology.nodes)
      .force('link', d3.forceLink(topology.edges).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2));

    // Draw links inside container
    const link = container.append('g')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .selectAll('line')
      .data(topology.edges)
      .enter()
      .append('line')
      .attr('stroke-width', 2);

    // Draw nodes inside container
    const node = container.append('g')
      .attr('stroke', '#fff')
      .attr('stroke-width', 1.5)
      .selectAll('circle')
      .data(topology.nodes)
      .enter()
      .append('circle')
      .attr('r', 10)
      .attr('fill', d => {
        if (d.nodeState === 'healthy') return 'green';
        if (d.nodeState === 'warning') return 'yellow';
        if (d.nodeState === 'critical') return 'red';
        return 'gray';
      })
      .call(d3.drag<SVGCircleElement, Node>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    // Add labels inside container
    const labels = container.append('g')
      .selectAll('text')
      .data(topology.nodes)
      .enter()
      .append('text')
      .attr('dy', -15)
      .attr('text-anchor', 'middle')
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
        .filter((d: unknown) => (d as Node).id === data.switch_id)
        .transition()
        .duration(500)
        .attr('fill', data.state === 'healthy'
          ? 'green'
          : data.state === 'warning'
          ? 'yellow'
          : data.state === 'critical'
          ? 'red'
          : 'gray');
    }
  }

  onMount(() => {
    loadTopology();
    sensorWS.subscribe(handleTopologyUpdate);
  });
</script>

<div class="min-h-screen bg-gray-50 p-6">
  <!-- Header -->
  <header class="mb-8">
    <h1 class="text-3xl font-semibold text-gray-800">Network Topology</h1>
    <p class="text-gray-600">Real-time visualization of switch relationships (drag, pan, and zoom enabled)</p>
  </header>
  
  <!-- Graph Container -->
  <div class="bg-white rounded-lg shadow p-6">
    <svg bind:this={svgElement}></svg>
  </div>
</div>
