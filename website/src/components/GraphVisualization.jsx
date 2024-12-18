import React, { useState, useEffect, useRef } from "react";
import Select from "react-select";
import { Sigma } from "sigma";
import Graph from "graphology";
import { random } from "graphology-layout";

const GraphVisualization = () => {
    const [options, setOptions] = useState([]);
    const [selectedArticle, setSelectedArticle] = useState(null);
    const containerRef = useRef(null);

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

                    const graph = new Graph();
                    const lines = text.trim().split("\n")

                    lines.forEach((line) => {
                        const [source, target] = line.split("\t");

                        if (source === selectedArticle.value || target === selectedArticle.value) {
                            if (!graph.hasNode(source)) {
                                graph.addNode(source, { label: decodeURIComponent(source) });
                            }
                            if (!graph.hasNode(target)) {
                                graph.addNode(target, { label: decodeURIComponent(target) });
                            }

                            graph.addEdge(source, target, { type: "arrow", color: "#888", size: 1 });
                        }
                    });

                    // Scale nodes by degree (number of edges)
                    graph.forEachNode((node) => {
                        const degree = graph.degree(node);
                        const maxDegree = 20;
                        const size = Math.min(degree + 3, maxDegree); // Add 3 to avoid zero size, cap at maxDegree
                        graph.setNodeAttribute(node, "size", size);
                        graph.setNodeAttribute(node, "color", "#666"); // Default node color
                    });

                    // Apply random layout
                    random.assign(graph);

                    // Initialize Sigma and bind hover interactions
                    if (containerRef.current) {
                        const renderer = new Sigma(graph, containerRef.current);

                        // Add hover interaction
                        renderer.on("enterNode", ({ node }) => {
                            // Highlight the hovered node and its edges
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
                                };
                            });
                            renderer.refresh(); // Update the graph display
                        });

                        renderer.on("leaveNode", () => {
                            // Remove highlights when mouse leaves a node
                            graph.updateEachNodeAttributes((n, attrs) => ({
                                ...attrs,
                                color: "#666", // Reset to original color
                            }));
                            graph.updateEachEdgeAttributes((edge, attrs) => ({
                                ...attrs,
                                color: "#888", // Reset to original color
                                size: 1, // Reset to original size
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