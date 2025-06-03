import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { getPaperClusters } from '../services/api';

const ClusterVisualization = ({ paperId }) => {
    const svgRef = useRef(null);

    useEffect(() => {
        loadAndVisualizeClusters();
    }, [paperId]);

    const loadAndVisualizeClusters = async () => {
        try {
            const response = await getPaperClusters(paperId);
            visualizeClusters(response.data);
        } catch (error) {
            console.error('Error loading clusters:', error);
            // Clear any existing visualization
            d3.select(svgRef.current).selectAll('*').remove();
            // Show error message
            d3.select(svgRef.current)
                .append('text')
                .attr('x', '50%')
                .attr('y', '50%')
                .attr('text-anchor', 'middle')
                .text('Failed to load clusters');
        }
    };

    const visualizeClusters = (clusters) => {
        // Clear any existing visualization
        d3.select(svgRef.current).selectAll('*').remove();

        const width = 800;
        const height = 600;
        const margin = 20;

        // Create SVG
        const svg = d3.select(svgRef.current)
            .attr('width', width)
            .attr('height', height);

        // Prepare data for circle packing
        const root = d3.hierarchy({ children: clusters })
            .sum(d => d.size || 1)
            .sort((a, b) => b.value - a.value);

        // Create circle packing layout
        const pack = d3.pack()
            .size([width - margin * 2, height - margin * 2])
            .padding(3);

        const packed = pack(root);

        // Create a group for the visualization
        const g = svg.append('g')
            .attr('transform', `translate(${margin},${margin})`);

        // Draw circles
        const node = g.selectAll('g')
            .data(packed.descendants())
            .enter()
            .append('g')
            .attr('transform', d => `translate(${d.x},${d.y})`);

        // Add circles
        node.append('circle')
            .attr('r', d => d.r)
            .style('fill', d => d.depth === 0 ? 'none' : d3.interpolateViridis(d.depth / 3))
            .style('stroke', '#fff')
            .style('stroke-width', 2)
            .style('opacity', 0.7)
            .on('mouseover', function() {
                d3.select(this)
                    .style('opacity', 1)
                    .style('stroke-width', 3);
            })
            .on('mouseout', function() {
                d3.select(this)
                    .style('opacity', 0.7)
                    .style('stroke-width', 2);
            });

        // Add labels for clusters
        node.filter(d => d.depth > 0)
            .append('text')
            .attr('dy', '.3em')
            .style('text-anchor', 'middle')
            .style('font-size', d => Math.min(2 * d.r, 14))
            .style('fill', '#fff')
            .text(d => d.data.name || `Cluster ${d.data.id}`);

        // Add tooltips
        node.filter(d => d.depth > 0)
            .append('title')
            .text(d => {
                const qaPairs = d.data.qa_pairs || [];
                return qaPairs.map(qa => `Q: ${qa.question}\nA: ${qa.answer}`).join('\n\n');
            });
    };

    return (
        <div className="w-full h-[calc(100vh-300px)] flex justify-center items-center bg-white rounded-lg shadow-lg">
            <svg ref={svgRef} className="w-full h-full"></svg>
        </div>
    );
};

export default ClusterVisualization; 