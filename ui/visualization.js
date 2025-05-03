function visualizeTokens(tokenMap) {
  const svg = d3.select("#visualization").html("").append("svg")
    .attr("width", "100%")
    .attr("height", 300);

  const width = document.getElementById('visualization').clientWidth;
  const height = 300;

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
    ...tokens.map(t => ({ id: t, group: 'token' })),
    ...[...papers].map(p => ({ id: p, group: 'paper' }))
  ];

  const links = [];
  tokens.forEach(token => {
    tokenMap[token].forEach(paper => {
      links.push({ source: token, target: paper });
    });
  });

  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(100))
    .force("charge", d3.forceManyBody().strength(-200))
    .force("center", d3.forceCenter(width / 2, height / 2));

  const link = svg.append("g")
    .selectAll("line")
    .data(links)
    .enter().append("line")
    .attr("stroke", "#00FF00")
    .attr("stroke-opacity", 0.5);

  const node = svg.append("g")
    .selectAll("circle")
    .data(nodes)
    .enter().append("circle")
    .attr("r", 5)
    .attr("fill", d => d.group === 'token' ? "#00FF00" : "#009900")
    .call(drag(simulation));

  const label = svg.append("g")
    .selectAll("text")
    .data(nodes)
    .enter().append("text")
    .text(d => d.id)
    .attr("font-size", "10px")
    .attr("fill", "#00FF00");

  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
    node
      .attr("cx", d => d.x).attr("cy", d => d.y);
    label
      .attr("x", d => d.x + 6).attr("y", d => d.y);
  });

  function drag(simulation) {
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

    return d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended);
  }
}