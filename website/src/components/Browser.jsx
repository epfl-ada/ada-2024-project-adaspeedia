import React, { useState, useEffect } from 'react';
import Select from 'react-select';

const PathDropdownSearch = () => {
  const [paths, setPaths] = useState([]);
  const [articles, setArticles] = useState([]);
  const [uniqueStarts, setUniqueStarts] = useState([]);

  // State for selected start and filtered ends
  const [selectedStart, setSelectedStart] = useState(null);
  const [filteredEnds, setFilteredEnds] = useState([]);
  const [selectedEnd, setSelectedEnd] = useState(null);

  // State to display results
  const [resultPathIds, setResultPathIds] = useState([]);
  const [resultFullPath, setResultFullPath] = useState('');

  // Fetch data from the provided URL
  useEffect(() => {
    const fetchPaths = async () => {
      try {
        const response = await fetch('data/paths_humain_unique_cleaned.json');
        const data = await response.json();
        setPaths(data);

        // Process data to extract articles
        const articlesData = data.map(({ path, path_id }) => {
          const decodedPath = path.split(';').map(decodeURIComponent);
          return {
            path_id,
            start: decodedPath[0],
            end: decodedPath[decodedPath.length - 1],
            fullPath: decodedPath
          };
        });

        setArticles(articlesData);
        setUniqueStarts([...new Set(articlesData.map(({ start }) => start))]);
      } catch (error) {
        console.error('Error fetching paths:', error);
      }
    };

    fetchPaths();
  }, []);

  const handleStartChange = (selectedOption) => {
    setSelectedStart(selectedOption);
    const start = selectedOption?.value;
    const matchingPaths = articles.filter((article) => article.start === start);
    const ends = [...new Set(matchingPaths.map(({ end }) => end))];
    setFilteredEnds(ends.map((end) => ({ value: end, label: end })));
    setSelectedEnd(null); // Reset end selection when start changes
    setResultPathIds([]);
    setResultFullPath('');
  };

  const handleEndChange = (selectedOption) => {
    setSelectedEnd(selectedOption);
  };

  const findPathIds = () => {
    const matchingPaths = articles.filter(
      (article) =>
        article.start === selectedStart?.value && article.end === selectedEnd?.value
    );

    const pathIds = matchingPaths.map((p) => p.path_id);
    const fullPath = matchingPaths.length > 0 ? matchingPaths[0].fullPath.join(' → ') : '';

    setResultPathIds(pathIds);
    setResultFullPath(fullPath);
  };

  return (
    <div>
      <div>
        <label htmlFor="startDropdown">Select Start Article:</label>
        <Select
          id="startDropdown"
          options={uniqueStarts.map((start) => ({ value: start, label: start }))}
          value={selectedStart}
          onChange={handleStartChange}
          placeholder="-- Select Start --"
        />
      </div>

      <div>
        <label htmlFor="endDropdown">Select End Article:</label>
        <Select
          id="endDropdown"
          options={filteredEnds}
          value={selectedEnd}
          onChange={handleEndChange}
          isDisabled={!filteredEnds.length}
          placeholder="-- Select End --"
        />
      </div>

      <button onClick={findPathIds} disabled={!selectedStart || !selectedEnd} style={{ marginTop: '20px' }}>
        Analyse this path
      </button>

      {resultPathIds.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <p><strong>(Internal) Path ID:</strong> {resultPathIds.join(', ')}</p>
          <p><strong>Full Path:</strong> {resultFullPath}</p>
        </div>
      )}
    </div>
  );
};

export default PathDropdownSearch;