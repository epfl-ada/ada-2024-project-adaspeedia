import React, { useState, useEffect, useRef } from "react";
import Select from "react-select";
import { Sigma } from "sigma";
import Graph from "graphology";
import { random } from "graphology-layout";
import forceAtlas2 from "graphology-layout-forceatlas2";

const LinksVisualisation = () => {
    const [options, setOptions] = useState([]);
    const [selectedArticle, setSelectedArticle] = useState(null);
    const containerRef = useRef(null);
    const sigmaInstance = useRef(null);

    useEffect(() => {
        async function loadOptions() {
            try {
                const response = await fetch('/data/links.tsv');
                if (!response.ok) {
                    throw new Error(`Failed to fetch data: ${response.statusText}`);
                }
                const text = await response.text();
                const lines = text.trim().split("\n");
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
                    if (sigmaInstance.current) {
                        sigmaInstance.current.kill();
                        sigmaInstance.current = null;
                    }

                    const response = await fetch('/data/links.tsv');
                    if (!response.ok) {
                        throw new Error(`Failed to fetch data: ${response.statusText}`);
                    }
                    const text = await response.text();

                    const graph = new Graph({ multi: true });
                    const lines = text.trim().split("\n");
                    const connectedArticles = new Set();

                    lines.forEach((line) => {
                        const [source, target] = line.split("\t");

                        if (source === selectedArticle.value || target === selectedArticle.value) {
                            if (!graph.hasNode(source)) {
                                graph.addNode(source, { label: decodeURIComponent(source) });
                                connectedArticles.add(source);
                            }
                            if (!graph.hasNode(target)) {
                                graph.addNode(target, { label: decodeURIComponent(target) });
                                connectedArticles.add(target);
                            }

                            graph.addEdge(source, target, { type: "arrow", color: "#888", size: 2 });
                        }
                    });

                    lines.forEach((line) => {
                        const [source, target] = line.split("\t");

                        if (connectedArticles.has(source) && connectedArticles.has(target)) {
                            if (!graph.hasNode(source)) {
                                graph.addNode(source, { label: decodeURIComponent(source) });
                            }
                            if (!graph.hasNode(target)) {
                                graph.addNode(target, { label: decodeURIComponent(target) });
                            }

                            graph.addEdge(source, target, { type: "arrow", color: "#888", size: 2 });
                        }
                    });

                    graph.forEachNode((node) => {
                        const degree = graph.degree(node);
                        const maxDegree = 30;
                        const size = Math.min(degree + 3, maxDegree);
                        graph.setNodeAttribute(node, "size", size);
                        graph.setNodeAttribute(node, "color", "#666");
                    });

                    random.assign(graph);

                    if (containerRef.current) {
                        const renderer = new Sigma(graph, containerRef.current);
                        sigmaInstance.current = renderer;

                        const settings = forceAtlas2.inferSettings(graph);
                        forceAtlas2.assign(graph, { settings, iterations: 500 });

                        renderer.on("enterNode", ({ node }) => {
                            const connectedEdges = new Set(graph.edges(node));
                            graph.updateEachNodeAttributes((n, attrs) => ({
                                ...attrs,
                                color: n === node || graph.hasEdge(n, node) ? 'red' : '#666',
                            }));
                            graph.updateEachEdgeAttributes((edge, attrs) => {
                                const [source, target] = graph.extremities(edge);
                                return {
                                    ...attrs,
                                    hidden: !connectedEdges.has(edge),
                                    color: connectedEdges.has(edge) ? 'red' : '#888',
                                    size: connectedEdges.has(edge) ? 3 : 2,
                                };
                            });
                            renderer.refresh();
                        });

                        renderer.on("leaveNode", () => {
                            graph.updateEachNodeAttributes((n, attrs) => ({
                                ...attrs,
                                color: "#666",
                            }));
                            graph.updateEachEdgeAttributes((edge, attrs) => ({
                                ...attrs,
                                hidden: false,
                                color: "#888",
                                size: 2,
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

export default LinksVisualisation;