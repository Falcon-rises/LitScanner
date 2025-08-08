import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import axios from "axios";

export default function CitationGraph() {
  const ref = useRef();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ✅ Replace with your actual backend URL (e.g., from Railway/Render)
  const apiUrl = "https://your-backend-service.com";

  useEffect(() => {
    axios.get(`${apiUrl}/citation-graph`)
      .then(res => {
        const nodes = res.data.nodes;
        const links = res.data.edges;
        drawGraph(nodes, links);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching citation graph:", err);
        setError("Failed to load citation graph.");
        setLoading(false);
      });
  }, []);

  const drawGraph = (nodes, links) => {
    const svg = d3.select(ref.current)
      .attr("width", 600)
      .attr("height", 400);

    svg.selectAll("*").remove(); // Clear existing graph

    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id(d => d.id).distance(100))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(300, 200));

    const link = svg.append("g")
      .attr("stroke", "#999")
      .selectAll("line")
      .data(links)
      .enter()
      .append("line")
      .attr("stroke-width", 1.5);

    const node = svg.append("g")
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
      .attr("r", 5)
      .attr("fill", "#3b82f6")
      .call(d3.drag()
        .on("start", dragStarted)
        .on("drag", dragged)
        .on("end", dragEnded));

    node.append("title").text(d => d.id);

    svg.append("g")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .attr("dy", -10)
      .attr("font-size", 10)
      .attr("text-anchor", "middle")
      .text(d => d.id);

    simulation.on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);

      svg.selectAll("text")
        .attr("x", d => d.x)
        .attr("y", d => d.y);
    });

    function dragStarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragEnded(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  };

  return (
    <div>
      {loading && <p>📘 Loading Citation Graph...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      <svg ref={ref}></svg>
    </div>
  );
}
