function updateKnowledgeGraph(graphData) {
    if (!graphData || !graphData.nodes || !graphData.edges) {
        console.error('Invalid graph data:', graphData);
        return;
    }

    const width = document.getElementById('visualization').clientWidth;
    const height = document.getElementById('visualization').clientHeight;

    // Clear previous visualization
    d3.select('#visualization').selectAll('*').remove();

    // Create SVG
    const svg = d3.select('#visualization')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .style('font', '10px sans-serif')
        .style('user-select', 'none');

    // Create zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    svg.call(zoom);

    // Create main group
    const g = svg.append('g');

    // Create circle packing layout
    const pack = data => d3.pack()
        .size([width - 2, height - 2])
        .padding(3)
        (d3.hierarchy(data)
            .sum(d => d.value)
            .sort((a, b) => b.value - a.value));

    // Process the data
    const root = pack(graphData);

    // Create circles
    const node = g.append('g')
        .selectAll('g')
        .data(root.descendants())
        .enter()
        .append('g')
        .attr('transform', d => `translate(${d.x + 1},${d.y + 1})`);

    // Add circles
    node.append('circle')
        .attr('r', d => d.r)
        .attr('fill', d => d.depth === 0 ? 'none' : d.depth === 1 ? '#40ff40' : '#1a1a1a')
        .attr('stroke', '#40ff40')
        .attr('stroke-width', d => d.depth === 0 ? 0 : 1)
        .style('cursor', 'pointer')
        .on('click', (event, d) => {
            if (d.depth > 0) {
                // Zoom to the clicked node
                svg.transition()
                    .duration(750)
                    .call(zoom.transform, d3.zoomIdentity
                        .translate(width / 2, height / 2)
                        .scale(4)
                        .translate(-d.x, -d.y));
            }
        });

    // Add labels
    node.append('text')
        .attr('dy', '0.3em')
        .text(d => d.depth === 0 ? '' : d.data.name)
        .style('fill', '#40ff40')
        .style('text-anchor', 'middle')
        .style('pointer-events', 'none')
        .style('font-size', d => Math.min(2 * d.r, 12) + 'px')
        .style('opacity', d => d.r > 20 ? 1 : 0);

    // Add tooltips
    node.append('title')
        .text(d => d.depth === 0 ? '' : d.data.name);

    // Initial zoom to fit
    svg.call(zoom.transform, d3.zoomIdentity
        .translate(width / 2, height / 2)
        .scale(0.8)
        .translate(-root.x, -root.y));
}

function fitTextToCircle(text, radius, minFont = 8, maxFont = 18) {
    // Create a temporary SVG text element to measure width
    const svg = d3.select('body').append('svg').attr('style', 'position:absolute;left:-9999px;top:-9999px');
    let fontSize = maxFont;
    let textElem = svg.append('text').text(text).style('font-size', fontSize + 'px').style('font-family', 'Orbitron, Arial Black, Arial, sans-serif');
    let width = textElem.node().getBBox().width;
    const maxWidth = radius * 1.7; // fit inside circle
    while (width > maxWidth && fontSize > minFont) {
        fontSize -= 1;
        textElem.style('font-size', fontSize + 'px');
        width = textElem.node().getBBox().width;
    }
    svg.remove();
    // If still too long, truncate and add ellipsis
    let displayText = text;
    if (width > maxWidth) {
        let chars = text.length;
        while (width > maxWidth && chars > 3) {
            chars--;
            displayText = text.slice(0, chars) + '…';
            svg.selectAll('*').remove();
            textElem = svg.append('text').text(displayText).style('font-size', fontSize + 'px').style('font-family', 'Orbitron, Arial Black, Arial, sans-serif');
            width = textElem.node().getBBox().width;
        }
        svg.remove();
    }
    return { displayText, fontSize };
}

const colors = [
    '#f8fafc', // root (white)
    '#dbeafe', // 1st level (light blue)
    '#f1f5f9', // 2nd level (light gray)
    '#60a5fa', // 3rd level (medium blue)
    '#e0e7ef', // 4th level (pale blue/gray)
    '#3b82f6', // 5th level (blue)
    '#64748b'  // 6th level (slate gray)
];

function updateConceptHierarchy(hierarchy) {
    if (!hierarchy) {
        console.error('Invalid hierarchy data:', hierarchy);
        return;
    }

    const width = document.getElementById('visualization').clientWidth;
    const height = document.getElementById('visualization').clientHeight;

    // Clear previous visualization
    d3.select('#visualization').selectAll('*').remove();

    // Create SVG
    const svg = d3.select('#visualization')
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .style('font', '16px "Orbitron", "Arial Black", Arial, sans-serif')
        .style('user-select', 'none');

    // Create zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.1, 4])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    svg.call(zoom);

    // Create main group
    const g = svg.append('g');

    // Create circle packing layout
    const pack = data => d3.pack()
        .size([width - 2, height - 2])
        .padding(6)
        (d3.hierarchy(data)
            .sum(d => d.value || 1)
            .sort((a, b) => b.value - a.value));

    // Process the data
    const root = pack(hierarchy);

    // Track zoom state
    let zoomedNode = null;

    // Create circles with blue/gray alternation
    const node = g.append('g')
        .selectAll('g')
        .data(root.descendants())
        .enter()
        .append('g')
        .attr('transform', d => `translate(${d.x + 1},${d.y + 1})`);

    node.append('circle')
        .attr('r', d => d.r)
        .attr('fill', d => colors[d.depth % colors.length])
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .style('cursor', d => d.depth === 0 ? 'pointer' : 'default')
        .on('click', function(event, d) {
            if (d.depth === 0 && !zoomedNode) {
                // Zoom in to this paper
                zoomedNode = d;
                svg.transition()
                    .duration(750)
                    .call(zoom.transform, d3.zoomIdentity
                        .translate(width / 2, height / 2)
                        .scale(1.5)
                        .translate(-d.x, -d.y));
                // Show the title in the center
                d3.select(this.parentNode).select('text').text(d.data.name).style('font-size', Math.max(18, d.r / 8) + 'px');
            } else if (zoomedNode) {
                // Zoom out
                zoomedNode = null;
                svg.transition()
                    .duration(750)
                    .call(zoom.transform, d3.zoomIdentity
                        .translate(width / 2, height / 2)
                        .scale(0.8)
                        .translate(-root.x, -root.y));
                // Restore label to paper number
                node.each(function(nd) {
                    if (nd.depth === 0) {
                        d3.select(this).select('text').text('Paper 1').style('font-size', Math.max(18, nd.r / 8) + 'px');
                    }
                });
            }
        });

    // Add labels: only show paper number in big circle, show title only when zoomed in
    node.append('text')
        .attr('dy', '0.3em')
        .text(d => d.depth === 0 ? 'Paper 1' : '')
        .style('fill', '#222')
        .style('text-anchor', 'middle')
        .style('pointer-events', 'none')
        .style('font-size', d => Math.max(18, d.r / 8) + 'px')
        .attr('class', 'mathjax-label');

    // Add tooltips with summaries
    node.append('title')
        .text(d => {
            let tooltip = typeof d.data.name === 'string' ? d.data.name : '';
            if (typeof d.data.summary === 'string' && d.data.summary) {
                tooltip += '\n\n' + d.data.summary;
            }
            return tooltip;
        });

    // Initial zoom to fit
    svg.call(zoom.transform, d3.zoomIdentity
        .translate(width / 2, height / 2)
        .scale(0.8)
        .translate(-root.x, -root.y));

    // Render MathJax for all text labels (in modals/tooltips only)
    setTimeout(() => {
        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise();
        }
    }, 100);
}

// Function to show concept details in a modal
function showConceptDetails(concept) {
    // Create modal container
    const modal = document.createElement('div');
    modal.className = 'concept-modal';
    modal.style.position = 'fixed';
    modal.style.top = '50%';
    modal.style.left = '50%';
    modal.style.transform = 'translate(-50%, -50%)';
    modal.style.backgroundColor = '#0a0a1a';
    modal.style.padding = '20px';
    modal.style.borderRadius = '12px';
    modal.style.boxShadow = '0 0 30px #00fff7, 0 0 10px #ff00ea';
    modal.style.zIndex = '1000';
    modal.style.maxWidth = '80%';
    modal.style.maxHeight = '80%';
    modal.style.overflow = 'auto';
    modal.style.border = '2px solid #ff00ea';

    // Add content with improved formatting, always using .name and .summary
    modal.innerHTML = `
        <h2 class="mathjax-label">${concept.name || ''}</h2>
        ${concept.summary ? `<p class="concept-summary mathjax-label">${concept.summary}</p>` : ''}
        ${concept.children ? `
            <div class="concept-children">
                <h3>Related Concepts:</h3>
                <ul>
                    ${concept.children.map(child => `
                        <li>
                            <strong class="mathjax-label">${child.name || ''}</strong>
                            ${child.summary ? `<p class="child-summary mathjax-label">${child.summary}</p>` : ''}
                        </li>
                    `).join('')}
                </ul>
            </div>
        ` : ''}
        <button onclick="this.parentElement.remove()" class="close-button">Close</button>
    `;

    // Add overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(0,0,0,0.7)';
    overlay.style.zIndex = '999';
    overlay.onclick = () => {
        overlay.remove();
        modal.remove();
    };

    document.body.appendChild(overlay);
    document.body.appendChild(modal);

    // Render MathJax for modal content
    setTimeout(() => {
        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([modal]);
        }
    }, 100);
} 