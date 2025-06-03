import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

function CirclePacking({ data }) {
  const svgRef = useRef();

  useEffect(() => {
    if (!data.length) return;

    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();

    // Prepare data for hierarchy
    const root = d3.hierarchy({
      name: "root",
      children: data.map((qa, i) => ({
        name: `qa_${i}`,
        value: 1,
        question: qa.question,
        answer: qa.answer
      }))
    }).sum(d => d.value);

    // Create circle packing layout
    const pack = d3.pack()
      .size([800, 400])
      .padding(3);

    const packed = pack(root);

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr("width", 800)
      .attr("height", 400);

    // Add circles
    const node = svg.selectAll("g")
      .data(packed.descendants())
      .join("g")
      .attr("transform", d => `translate(${d.x},${d.y})`);

    // Add circles
    node.append("circle")
      .attr("r", d => d.r)
      .attr("fill", d => d.depth === 0 ? "#e2e8f0" : "#93c5fd")
      .attr("stroke", "#fff")
      .attr("stroke-width", 2);

    // Add text labels
    node.append("text")
      .attr("dy", ".3em")
      .style("text-anchor", "middle")
      .style("font-size", "12px")
      .style("fill", "#1f2937")
      .text(d => {
        if (d.depth === 0) return "";
        const text = d.data.question;
        return text.length > 20 ? text.substring(0, 20) + "..." : text;
      });

    // Add tooltips
    node.append("title")
      .text(d => {
        if (d.depth === 0) return "";
        return `Q: ${d.data.question}\nA: ${d.data.answer}`;
      });

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

export default CirclePacking; 