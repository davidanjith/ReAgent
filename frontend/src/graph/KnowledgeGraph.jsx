import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

function KnowledgeGraph({ data }) {
  const svgRef = useRef();

  useEffect(() => {
    if (!data.length) return;

    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();

    // Create nodes and links
    const nodes = data.map((qa, i) => ({
      id: i,
      label: qa.question.substring(0, 30) + "...",
      question: qa.question,
      answer: qa.answer
    }));

    // Create links between nodes based on similarity
    const links = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        // Simple similarity check - can be improved with actual NLP
        if (nodes[i].question.toLowerCase().includes(nodes[j].question.toLowerCase()) ||
            nodes[j].question.toLowerCase().includes(nodes[i].question.toLowerCase())) {
          links.push({
            source: i,
            target: j,
            value: 1
          });
        }
      }
    }

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(400, 200));

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr("width", 800)
      .attr("height", 400);

    // Add links
    const link = svg.append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", 1);

    // Add nodes
    const node = svg.append("g")
      .selectAll("g")
      .data(nodes)
      .join("g")
      .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Add circles to nodes
    node.append("circle")
      .attr("r", 10)
      .attr("fill", "#93c5fd")
      .attr("stroke", "#fff")
      .attr("stroke-width", 2);

    // Add labels to nodes
    node.append("text")
      .attr("dy", 20)
      .attr("text-anchor", "middle")
      .style("font-size", "10px")
      .style("fill", "#1f2937")
      .text(d => d.label);

    // Add tooltips
    node.append("title")
      .text(d => `Q: ${d.question}\nA: ${d.answer}`);

    // Update positions on each tick
    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("transform", d => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.5, 8])
      .on("zoom", (event) => {
        svg.selectAll("g")
          .attr("transform", event.transform);
      });

    svg.call(zoom);

  }, [data]);

  return (
    <div className="w-full overflow-hidden">
      <svg ref={svgRef} className="w-full h-full"></svg>
    </div>
  );
}

export default KnowledgeGraph; 