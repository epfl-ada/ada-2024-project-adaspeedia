import React, { useState, useEffect, useRef } from "react";
import Select from "react-select";
import { Sigma } from "sigma";
import Graph from "graphology";
import { random } from "graphology-layout";

// Helper function to recursively add nodes and edges up to a specified depth
const addNodesAndEdges = (graph, links, currentArticle, depth, currentDepth = 0) => {
    if (depth === 0) return;

    links.forEach(([source, target]) => {
        if (source === currentArticle || target === currentArticle) {
            if (!graph.hasNode(source)) {
                graph.addNode(source, { label: decodeURIComponent(source), depth: currentDepth });
            }
            if (!graph.hasNode(target)) {
                graph.addNode(target, { label: decodeURIComponent(target), depth: currentDepth });
            }
            if (!graph.hasEdge(source, target)) {
                graph.addEdge(source, target, { type: "arrow", color: "#888", size: 1 });
            }

            // Recursively add nodes and edges for the connected articles
            addNodesAndEdges(graph, links, source === currentArticle ? target : source, depth - 1, currentDepth + 1);
        }
    });
};

const GraphVisualization = () => {
    const [options, setOptions] = useState([]);
    const [selectedArticle, setSelectedArticle] = useState(null);
    const containerRef = useRef(null);
    const depth = 2;  // Set the depth for the graph traversal

    useEffect(() => {
        // Load the article options for the search dropdown
        async function loadOptions() {
            try {
                const response = await fetch('/data/links.tsv');
                if (!response.ok) {
                    throw new Error(`Failed to fetch data: ${response.statusText}`);
                }
                const text = await response.text();
                const lines = text.trim().split("\n")
                const articles = new Set();

                lines.forEach((line) => {
                    const [source, target] = line.split("\t");
                    articles.add(source);
                    articles.add(target);
                });

                const articleOptions = Array.from(articles).map(article => ({
                    value: article,
                    label: decodeURIComponent(article)
                }));
                setOptions(articleOptions);
            } catch (error) {
                console.error("Error loading article options:", error);
            }
        }

        loadOptions();
    }, []);

    useEffect(() => {
        if (selectedArticle) {
            async function loadGraph() {
                try {
                    const response = await fetch('/data/links.tsv');
                    if (!response.ok) {
                        throw new Error(`Failed to fetch data: ${response.statusText}`);
                    }
                    const text = await response.text();

                    // Initialize the graph with the 'multi' option enabled
                    const graph = new Graph({ multi: true });
                    const lines = text.trim().split("\n")
                    const links = lines.map(line => line.split("\t"));

                    // Add nodes and edges starting from the selected article
                    addNodesAndEdges(graph, links, selectedArticle.value, depth);

                    // Scale nodes by degree (number of edges) and set colors based on depth
                    graph.forEachNode((node, attributes) => {
                        const degree = graph.degree(node);
                        const maxDegree = 10;
                        const scaledDegree = Math.min(degree, maxDegree);
                        graph.setNodeAttribute(node, "size", scaledDegree + 3); // Add 3 to avoid zero size

                        // Set node colors based on depth
                        if (node === selectedArticle.value) {
                            graph.setNodeAttribute(node, "color", "blue"); // Primary node color
                        } else if (attributes.depth === 0) {
                            graph.setNodeAttribute(node, "color", "violet"); // Depth 0 nodes color
                        } else {
                            graph.setNodeAttribute(node, "color", "#666"); // Default node color
                        }
                    });

                    // Apply random layout
                    random.assign(graph);

                    // Initialize Sigma and bind hover interactions
                    if (containerRef.current) {
                        const renderer = new Sigma(graph, containerRef.current);

                        // Add hover interaction
                        renderer.on("enterNode", ({ node }) => {
                            // Highlight the hovered node and hide other edges
                            graph.updateEachNodeAttributes((n, attrs) => ({
                                ...attrs,
                                color: n === node ? 'red' : attrs.color,
                            }));
                            graph.updateEachEdgeAttributes((edge, attrs) => {
                                const [source, target] = graph.extremities(edge);
                                return {
                                    ...attrs,
                                    color: source === node || target === node ? 'red' : attrs.color,
                                    size: source === node || target === node ? 2 : attrs.size, // Increase the size of the arrow
                                    hidden: source !== node && target !== node, // Hide edges not connected to the hovered node
                                };
                            });
                            renderer.refresh(); // Update the graph display
                        });

                        renderer.on("leaveNode", () => {
                            // Remove highlights and show all edges when mouse leaves a node
                            graph.updateEachNodeAttributes((n, attrs) => ({
                                ...attrs,
                                color: n === selectedArticle.value ? 'blue' : attrs.depth === 0 ? 'violet' : '#666', // Reset to original color based on depth
                            }));
                            graph.updateEachEdgeAttributes((edge, attrs) => ({
                                ...attrs,
                                color: "#888", // Reset to original color
                                size: 1, // Reset to original size
                                hidden: false, // Show all edges
                            }));
                            renderer.refresh();
                        });
                    }
                } catch (error) {
                    console.error("Error loading or processing graph data:", error);
                }
            }

            loadGraph();
        }
    }, [selectedArticle]);

    return (
        <div>
            <Select
                options={options}
                onChange={setSelectedArticle}
                placeholder="Search for an article..."
            />
            <div
                ref={containerRef}
                style={{ width: "100%", height: "100vh" }}
            ></div>
        </div>
    );
};

export default GraphVisualization;