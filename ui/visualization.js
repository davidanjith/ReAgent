function visualizeTokens(tokenMap) {
  const svg = d3.select("#visualization").html("").append("svg")
    .attr("width", "100%")
    .attr("height", 400);

  const width = document.getElementById('visualization').clientWidth;
  const height = 400;

  // Sample list of papers with their arXiv PDF links
  const paperList = [
    { title: "Paper 1 Title", pdf: "https://arxiv.org/pdf/2101.00001.pdf" },
    { title: "Paper 2 Title", pdf: "https://arxiv.org/pdf/2101.00002.pdf" },
    { title: "Paper 3 Title", pdf: "https://arxiv.org/pdf/2101.00003.pdf" },
    { title: "Paper 4 Title", pdf: "https://arxiv.org/pdf/2101.00004.pdf" }
  ];

  // Populate the list of papers on the right side
  const paperListContainer = d3.select("#paper-list").html(""); // assuming an HTML element with id "paper-list"
  paperList.forEach(paper => {
    paperListContainer.append("div")
      .attr("class", "paper-item")
      .text(paper.title)
      .on("click", () => displayPDF(paper.pdf));
  });

  // Function to display the PDF in the right side panel
  function displayPDF(pdfUrl) {
    const pdfContainer = d3.select("#pdf-container").html(""); // assuming an HTML element with id "pdf-container"
    pdfContainer.append("iframe")
      .attr("src", pdfUrl)
      .attr("width", "100%")
      .attr("height", "500px");
  }

  const tokens = Object.keys(tokenMap);
  const papers = new Set();
  tokens.forEach(token => {
    tokenMap[token].forEach(paper => papers.add(paper));
  });

  const nodes = [
    ...tokens.map(t => ({ id: t, group: 'token', radius: 30 })),
    ...[...papers].map(p => ({ id: p, group: 'paper', radius: 40 }))
  ];

  const links = [];
  tokens.forEach(token => {
    tokenMap[token].forEach(paper => {
      links.push({ source: token, target: paper });
    });
  });

  const simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id).distance(150))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("collision", d3.forceCollide().radius(50));

  const link = svg.append("g")
    .selectAll("line")
    .data(links)
    .enter().append("line")
    .attr("stroke", "#999")
    .attr("stroke-opacity", 0.6)
    .attr("stroke-width", 2);

  const node = svg.append("g")
    .selectAll("g")
    .data(nodes)
    .enter().append("g")
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));

  node.append("circle")
    .attr("r", d => d.radius)
    .attr("fill", d => d.group === 'token' ? "#69b3a2" : "#ff7f0e")
    .attr("stroke", "#fff")
    .attr("stroke-width", 2);

  node.append("text")
    .text(d => d.id)
    .attr("x", 0)
    .attr("y", 0)
    .attr("text-anchor", "middle")
    .attr("dy", ".35em")
    .attr("fill", "#fff")
    .style("font-size", "12px")
    .style("pointer-events", "none");

  simulation.nodes(nodes).on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    node.attr("transform", d => `translate(${d.x},${d.y})`);
  });

  simulation.force("link").links(links);

  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
}