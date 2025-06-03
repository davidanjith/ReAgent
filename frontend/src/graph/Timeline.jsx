import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

function Timeline({ data }) {
  const svgRef = useRef();

  useEffect(() => {
    if (!data.length) return;

    // Clear previous visualization
    d3.select(svgRef.current).selectAll("*").remove();

    // Sort data by timestamp
    const sortedData = [...data].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    // Set up dimensions
    const margin = { top: 20, right: 30, bottom: 30, left: 60 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Create SVG
    const svg = d3.select(svgRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Create scales
    const x = d3.scaleTime()
      .domain(d3.extent(sortedData, d => new Date(d.timestamp)))
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(sortedData, d => d.value || 1)])
      .range([height, 0]);

    // Add X axis
    svg.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .style("text-anchor", "end")
      .attr("dx", "-.8em")
      .attr("dy", ".15em")
      .attr("transform", "rotate(-45)");

    // Add Y axis
    svg.append("g")
      .call(d3.axisLeft(y));

    // Add line
    const line = d3.line()
      .x(d => x(new Date(d.timestamp)))
      .y(d => y(d.value || 1))
      .curve(d3.curveMonotoneX);

    svg.append("path")
      .datum(sortedData)
      .attr("fill", "none")
      .attr("stroke", "#93c5fd")
      .attr("stroke-width", 2)
      .attr("d", line);

    // Add dots
    const dots = svg.selectAll("circle")
      .data(sortedData)
      .join("circle")
      .attr("cx", d => x(new Date(d.timestamp)))
      .attr("cy", d => y(d.value || 1))
      .attr("r", 5)
      .attr("fill", "#93c5fd")
      .attr("stroke", "#fff")
      .attr("stroke-width", 2);

    // Add tooltips
    dots.append("title")
      .text(d => `Q: ${d.question}\nA: ${d.answer}\nTime: ${new Date(d.timestamp).toLocaleString()}`);

    // Add hover effects
    dots
      .on("mouseover", function(event, d) {
        d3.select(this)
          .attr("r", 8)
          .attr("fill", "#3b82f6");
      })
      .on("mouseout", function(event, d) {
        d3.select(this)
          .attr("r", 5)
          .attr("fill", "#93c5fd");
      });

    // Add zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.5, 8])
      .on("zoom", (event) => {
        svg.selectAll("g")
          .attr("transform", event.transform);
      });

    d3.select(svgRef.current).call(zoom);

  }, [data]);

  return (
    <div className="w-full overflow-hidden">
      <svg ref={svgRef} className="w-full h-full"></svg>
    </div>
  );
}

export default Timeline; 