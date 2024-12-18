import React, { useState, useEffect, useRef } from "react";
import { Sigma } from "sigma";
import Graph from "graphology";
import { random } from "graphology-layout";

const GraphVisualization = () => {
    const containerRef = useRef(null);
    const [graph, setGraph] = useState(new Graph());
    const [searchQuery, setSearchQuery] = useState("");
    const [depth, setDepth] = useState(1);

    useEffect(() => {
        async function loadGraph() {
            try {
                const response = await fetch('/data/links.tsv');
                if (!response.ok) {
                    throw new Error(`Failed to fetch data: ${response.statusText}`);
                }
                const text = await response.text();

                const graph = new Graph();
                const lines = text.trim().split("\n").slice(0, 1000);

                lines.forEach((line) => {
                    const [source, target] = line.split("\t");

                    if (!graph.hasNode(source)) {
                        graph.addNode(source, { label: decodeURIComponent(source) });
                    }
                    if (!graph.hasNode(target)) {
                        graph.addNode(target, { label: decodeURIComponent(target) });
                    }

                    graph.addEdge(source, target, { type: "arrow", color: "#888", size: 1 });
                });

                // Scale nodes by degree (number of edges)
                graph.forEachNode((node) => {
                    const degree = graph.degree(node);
                    graph.setNodeAttribute(node, "size", degree + 3); // Add 3 to avoid zero size
                    graph.setNodeAttribute(node, "color", "#666"); // Default node color
                });

                // Apply random layout
                random.assign(graph);

                setGraph(graph);
                renderGraph(graph);

            } catch (error) {
                console.error("Error loading or processing graph data:", error);
            }
        }

        loadGraph();
    }, []);

    const renderGraph = (graph, focusNode = null, depth = 1) => {
        const subGraph = new Graph();

        if (focusNode) {
            const nodesToVisit = new Set([focusNode]);
            const visitedNodes = new Set();

            for (let i = 0; i < depth; i++) {
                const newNodesToVisit = new Set();

                nodesToVisit.forEach(node => {
                    if (!visitedNodes.has(node)) {
                        visitedNodes.add(node);
                        subGraph.mergeNode(graph.getNodeAttributes(node), node);

                        graph.forEachNeighbor(node, neighbor => {
                            if (!visitedNodes.has(neighbor)) {
                                subGraph.mergeNode(graph.getNodeAttributes(neighbor), neighbor);
                                subGraph.mergeEdge(graph.getEdge(node, neighbor));
                                newNodesToVisit.add(neighbor);
                            }
                        });
                    }
                });

                nodesToVisit.clear();
                newNodesToVisit.forEach(node => nodesToVisit.add(node));
            }
        } else {
            graph.forEachNode((node) => {
                subGraph.mergeNode(graph.getNodeAttributes(node), node);
            });
            graph.forEachEdge((edge) => {
                subGraph.mergeEdge(graph.getEdgeAttributes(edge), edge);
            });
        }

        random.assign(subGraph);

        if (containerRef.current) {
            const renderer = new Sigma(subGraph, containerRef.current);

            // Add hover interaction
            renderer.on("enterNode", ({ node }) => {
                // Highlight the hovered node and its edges
                subGraph.updateEachNodeAttributes((n, attrs) => ({
                    ...attrs,
                    color: n === node ? 'red' : attrs.color,
                }));
                subGraph.updateEachEdgeAttributes((edge, attrs) => {
                    const [source, target] = subGraph.extremities(edge);
                    return {
                        ...attrs,
                        color: source === node || target === node ? 'red' : attrs.color,
                        size: source === node || target === node ? 2 : attrs.size, // Increase the size of the arrow
                    };
                });
                renderer.refresh(); // Update the graph display
            });

            renderer.on("leaveNode", () => {
                // Remove highlights when mouse leaves a node
                subGraph.updateEachNodeAttributes((n, attrs) => ({
                    ...attrs,
                    color: "#666", // Reset to original color
                }));
                subGraph.updateEachEdgeAttributes((edge, attrs) => ({
                    ...attrs,
                    color: "#888", // Reset to original color
                    size: 1, // Reset to original size
                }));
                renderer.refresh();
            });
        }
    };

    const handleSearch = () => {
        if (searchQuery && graph.hasNode(searchQuery)) {
            renderGraph(graph, searchQuery, depth);
        } else {
            console.error("Node not found or graph not loaded");
        }
    };

    return (
        <>
            <div style={{ padding: "10px" }}>
                <input
                    type="text"
                    placeholder="Search article"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
                <input
                    type="number"
                    min="1"
                    placeholder="Depth"
                    value={depth}
                    onChange={(e) => setDepth(Number(e.target.value))}
                />
                <button onClick={handleSearch}>Search</button>
            </div>
            <div
                ref={containerRef}
                style={{ width: "100%", height: "calc(100vh - 50px)" }}
            ></div>
        </>
    );
};

export default GraphVisualization;