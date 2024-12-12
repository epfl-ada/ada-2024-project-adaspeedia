import React, { useEffect, useState } from 'react';

const PlotlyChart = () => {
    const [Plot, setPlot] = useState(null);

    useEffect(() => {
        // Dynamically import react-plotly.js only in the browser
        import('react-plotly.js').then((module) => setPlot(() => module.default));
    }, []);

    // Show a loading message until Plotly is loaded
    if (!Plot) return <div>Loading chart...</div>;

    return (
        <Plot
            data={[
                { x: [1, 2, 3, 4], y: [10, 15, 13, 17], type: 'scatter' },
            ]}
            layout={{ title: 'Sample Chart' }}
        />
    );
};

export default PlotlyChart;
