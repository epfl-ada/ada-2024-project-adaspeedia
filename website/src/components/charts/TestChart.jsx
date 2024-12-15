import React, { useEffect, useState } from 'react';

const PlotlyChart = () => {
    const [Plot, setPlot] = useState(null);

    useEffect(() => {
        // Dynamically import react-plotly.js only in the browser
        import('react-plotly.js').then((module) => setPlot(() => module.default));
    }, []);

    // Show a loading message until Plotly is loaded
    if (!Plot) return <div>Loading chart...</div>;

    // Data for the chart
    const data = [
        {
            x: [0.5511809, 0.43897092, 0.75217295], // cosine_similarity
            y: [8.725956916809082, 9.629786491394045, 6.57568359375], // euclidean_distance
            z: [0.1734122782945633, 0.25735193490982056, 0.204072967171669], // sbert_cosine_similarity
            text: ["('Football', 'South_Africa')", "('Film', 'The_Lorax')", "('Africa', 'Bhutan')"], // Labels
            mode: 'markers',
            marker: {
                size: 8,
                opacity: 0.8,
                color: [0.5511809, 0.43897092, 0.75217295], // Optional: coloring points based on similarity
                colorscale: 'Viridis',
            },
            type: 'scatter3d',
        },
    ];

    // Layout configuration for the chart
    const layout = {
        title: 'Distances entre articles',
        scene: {
            xaxis: { title: 'Cosine Similarity' },
            yaxis: { title: 'Euclidean Distance' },
            zaxis: { title: 'SBERT Cosine Similarity' },
        },
    };

    return <Plot data={data} layout={layout} />;
};

export default PlotlyChart;
