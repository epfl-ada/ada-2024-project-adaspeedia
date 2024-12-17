import React, { useState, useEffect } from 'react';
import Select from 'react-select';

// Fetch data from the CSV file
const fetchCSVData = async () => {
    const response = await fetch('/data/distances_humans.csv');
    const csvText = await response.text();
    return csvText;
};

// Parse CSV data into a usable JSON format
const parseCSV = (data) => {
    const rows = data.split('\n').slice(1); // Split lines and skip the header
    const result = rows
        .filter((row) => row.trim() !== '') // Ignore empty rows
        .map((row) => {
            const [pair, distance] = row.split(/,(?=\d)/); // Split by the comma before the number
            if (!pair || !distance) {
                console.error(`Invalid row format: ${row}`);
                return null;
            }

            const [article1, article2] = pair
                .replace(/['"()]/g, '') // Remove quotes and parentheses
                .split(', ')
                .map((article) => article.trim()); // Trim whitespace

            if (!article1 || !article2 || isNaN(parseFloat(distance))) {
                console.error(`Invalid data in row: ${row}`);
                return null;
            }

            return {
                article1,
                article2,
                distance: parseFloat(distance),
            };
        })
        .filter((entry) => entry !== null); // Filter out invalid entries

    return result;
};

const DistancePlotter = () => {
    const [csvData, setCsvData] = useState('');
    const [distances, setDistances] = useState([]);
    const [selectedArticle, setSelectedArticle] = useState(null);
    const [linkedDistances, setLinkedDistances] = useState([]);
    const [showArticle1, setShowArticle1] = useState(true); // Toggle for article1
    const [showArticle2, setShowArticle2] = useState(true); // Toggle for article2
    const [Plot, setPlot] = useState(null); // State for dynamically imported Plotly component

    useEffect(() => {
        // Dynamically import the Plotly.js module
        import('react-plotly.js').then((module) => {
            setPlot(() => module.default);
        });

        // Fetch and parse the CSV data on component mount
        const loadCSVData = async () => {
            const csvText = await fetchCSVData();
            setCsvData(csvText);
            const parsedDistances = parseCSV(csvText);
            setDistances(parsedDistances);
        };

        loadCSVData();
    }, []);

    const handleArticleChange = (selectedOption) => {
        setSelectedArticle(selectedOption);
        setLinkedDistances([]); // Clear previous results
    };

    const findDistances = () => {
        if (selectedArticle) {
            const filteredDistances = distances.filter(
                (d) => d.article1 === selectedArticle.value || d.article2 === selectedArticle.value
            );

            const results = filteredDistances.map((d) => ({
                linkedArticle: d.article1 === selectedArticle.value ? d.article2 : d.article1,
                distance: d.distance,
                type: d.article1 === selectedArticle.value ? 'article1' : 'article2',
            }));

            setLinkedDistances(results);
        }
    };

    // Extract unique article names for the dropdown
    const articles = [...new Set(distances.flatMap((d) => [d.article1, d.article2]))];
    const articleOptions = articles.map((article) => ({ value: article, label: article }));

    // Prepare plot data based on toggles
    const filteredData = linkedDistances.filter(
        (item) => (showArticle1 && item.type === 'article1') || (showArticle2 && item.type === 'article2')
    );

    return (
        <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
            <div>
                <label htmlFor="articleDropdown">Select Article:</label>
                <Select
                    id="articleDropdown"
                    options={articleOptions}
                    value={selectedArticle}
                    onChange={handleArticleChange}
                    placeholder="-- Select Article --"
                />
            </div>

            <button onClick={findDistances} style={{ marginTop: '20px' }}>
                Find distances
            </button>

            {filteredData.length > 0 && Plot && (
                <div style={{ marginTop: '20px' }}>
                    <h3>Linked Articles and Distances:</h3>
                    <Plot
                        data={[
                            {
                                x: filteredData
                                    .filter((item) => item.type === 'article1')
                                    .map((item) => item.distance),
                                y: filteredData
                                    .filter((item) => item.type === 'article1')
                                    .map((item) => item.linkedArticle),
                                type: 'scatter',
                                mode: 'markers',
                                name: 'Forwards',
                                marker: { color: 'blue' },
                            },
                            {
                                x: filteredData
                                    .filter((item) => item.type === 'article2')
                                    .map((item) => item.distance),
                                y: filteredData
                                    .filter((item) => item.type === 'article2')
                                    .map((item) => item.linkedArticle),
                                type: 'scatter',
                                mode: 'markers',
                                name: 'Backwards',
                                marker: { color: 'orange' },
                            },
                        ]}
                        layout={{
                            title: 'Distances to Selected Article',
                            xaxis: { title: 'Distance' },
                            yaxis: { title: 'Linked Article' },
                            legend: { title: 'Distance Type' },
                        }}
                        style={{ width: '100%', height: '500px' }}
                    />
                </div>
            )}
        </div>
    );
};

export default DistancePlotter;