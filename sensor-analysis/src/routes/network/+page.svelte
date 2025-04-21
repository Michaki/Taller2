<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
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

  interface UpdateMessage {
    switch_id: string;
    parent_switch_id?: string;
    state: string;
  }

  let topology: { nodes: Node[]; edges: Edge[] } = { nodes: [], edges: [] };
  let svgElement: SVGSVGElement;
  let simulation: d3.Simulation<any, undefined>;
  let zoom: d3.ZoomBehavior<Element, unknown>;
  let wsCallback: any;
  
  // ========== Mapa de correspondencia ID ==========
  // Este objeto guardará la correspondencia entre IDs del WS y IDs de topología
  let idMapping: Record<string, string> = {};

  async function loadTopology() {
    console.log('Cargando datos de topología...');
    try {
      topology = await sensorService.getTopology();
      console.log('Datos de topología cargados:', topology);
      
      // Debug: mostrar todos los IDs de la topología
      console.log('IDs de nodos en la topología:');
      topology.nodes.forEach(node => {
        console.log(`- ${node.id} (${node.label})`);
      });
      
      renderGraph();
      
      // SOLUCIÓN: Iniciar recolección de posibles mapeos de ID
      initIdMapping();
    } catch (error) {
      console.error('Error al cargar la topología:', error);
    }
  }

  // Inicializa un mapa de ID para comparaciones futuras
  function initIdMapping() {
    // Los IDs que recibimos del WebSocket se guardarán aquí
    idMapping = {};
    
    // Preparar para recibir mensajes temporalmente, para construir el mapeo
    const tempListener = (data: UpdateMessage) => {
      console.log("Recibido mensaje para mapeo:", data);
      
      if (data.switch_id) {
        // Buscar un nodo que coincida completamente
        const exactMatch = topology.nodes.find(n => n.id === data.switch_id);
        if (exactMatch) {
          idMapping[data.switch_id] = data.switch_id;
          return;
        }
        
        // Buscar nodos que contengan el ID o viceversa
        for (const node of topology.nodes) {
          // Si el ID del nodo contiene el switch_id o viceversa
          if (node.id.includes(data.switch_id) || data.switch_id.includes(node.id)) {
            idMapping[data.switch_id] = node.id;
            console.log(`Mapeo encontrado: ${data.switch_id} => ${node.id}`);
            break;
          }
        }
      }
      
      // También intentar con parent_switch_id
      if (data.parent_switch_id && !idMapping[data.switch_id]) {
        for (const node of topology.nodes) {
          if (node.id.includes(data.parent_switch_id) || data.parent_switch_id.includes(node.id)) {
            idMapping[data.switch_id] = node.id;
            console.log(`Mapeo encontrado (por parent): ${data.switch_id} => ${node.id}`);
            break;
          }
        }
      }
    };
    
    // Añadir temporalmente para recolectar mapeos
    sensorWS.subscribe(tempListener);
    
    // Quitar después de acumular algunos mapeos
    setTimeout(() => {
      sensorWS.unsubscribe(tempListener);
      console.log("Mapa de IDs construido:", idMapping);
    }, 10000); // Recolectar por 10 segundos
  }

  function renderGraph() {
    if (!svgElement) {
      console.error('Elemento SVG no disponible');
      return;
    }

    console.log('Renderizando gráfico de topología...');
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
    
    console.log('Gráfico renderizado.');
  }

  function handleTopologyUpdate(data: UpdateMessage) {
    console.log('Actualización de topología recibida:', data);
    
    // SOLUCIÓN: Usar el mapa de ID para encontrar el nodo correcto
    let nodeId = data.switch_id;
    let mappedId = idMapping[data.switch_id];
    
    // 1. Usar el ID mapeado si existe
    if (mappedId) {
      console.log(`Usando ID mapeado: ${data.switch_id} => ${mappedId}`);
      nodeId = mappedId;
    }
    
    // 2. Buscar directamente por el ID que viene en el mensaje
    let node = topology.nodes.find(n => n.id === nodeId);
    
    // 3. Si no se encuentra, intentar estrategias alternativas
    if (!node) {
      // Opción A: Intentar con parent_switch_id
      if (data.parent_switch_id) {
        console.log(`Intentando con parent_switch_id: ${data.parent_switch_id}`);
        node = topology.nodes.find(n => n.id === data.parent_switch_id);
        
        // Si encontramos un mapeo, guardarlo para futuras referencias
        if (node) {
          idMapping[data.switch_id] = data.parent_switch_id;
          console.log(`Nuevo mapeo añadido: ${data.switch_id} => ${data.parent_switch_id}`);
        }
      }
      
      // Opción B: Buscar coincidencias parciales
      if (!node) {
        console.log('Buscando coincidencias parciales...');
        
        // Buscar si algún nodo contiene este ID o viceversa
        for (const n of topology.nodes) {
          if (n.id.includes(data.switch_id) || data.switch_id.includes(n.id)) {
            node = n;
            // Guardar esta relación para futuras referencias
            idMapping[data.switch_id] = n.id;
            console.log(`Coincidencia parcial encontrada: ${data.switch_id} => ${n.id}`);
            break;
          }
          
          // También probar con parent_switch_id
          if (data.parent_switch_id && 
              (n.id.includes(data.parent_switch_id) || data.parent_switch_id.includes(n.id))) {
            node = n;
            idMapping[data.switch_id] = n.id;
            console.log(`Coincidencia parcial (parent) encontrada: ${data.switch_id} => ${n.id}`);
            break;
          }
        }
      }
    }
    
    // Si encontramos un nodo, actualizar su estado y apariencia
    if (node) {
      console.log(`Actualizando nodo ${node.id} (${node.label}) a estado '${data.state}'`);
      node.nodeState = data.state as Node["nodeState"];
      
      // Actualizar visualmente el nodo
      const circleSelection = d3.select(svgElement)
        .selectAll('circle')
        .filter((d) => (d as Node).id === node!.id);
      
      if (circleSelection.empty()) {
        console.warn('No se encontró el círculo para actualizar visualmente');
      } else {
        const newColor = data.state === 'healthy'
          ? '#34D399'
          : data.state === 'warning'
          ? '#FBBF24'
          : data.state === 'critical' || data.state === 'unhealthy'
          ? '#F87171'
          : '#9CA3AF';
        
        console.log(`Cambiando color a ${newColor}`);
        circleSelection
          .transition()
          .duration(500)
          .attr('fill', newColor);
      }
    } else {
      console.warn(`No se encontró nodo con ID '${data.switch_id}' en la topología`);
    }
  }

  onMount(() => {
    console.log('Componente de topología montado');
    loadTopology();
    wsCallback = sensorWS.subscribe(handleTopologyUpdate);
    console.log('Suscrito a actualizaciones de topología');
  });

  onDestroy(() => {
    console.log('Componente de topología desmontado, liberando recursos');
    if (wsCallback) {
      sensorWS.unsubscribe(wsCallback);
      console.log('Desuscrito de actualizaciones de topología');
    }
    if (simulation) {
      simulation.stop();
    }
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