import React, { useState, useEffect } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";
import CitationGraph from "./components/CitationGraph";

export default function App() {
  const [metaReview, setMetaReview] = useState("");
  const [topics, setTopics] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [query, setQuery] = useState("");

  const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    axios
      .get(`${apiUrl}/summarize`)
      .then(res => setMetaReview(res.data.meta_review))
      .catch(err => console.error("Error fetching meta review:", err));

    axios
      .get(`${apiUrl}/topics`)
      .then(res => {
        const topicInfo = res.data.topic_info || {};
        const names = topicInfo["Name"] || {};
        const counts = topicInfo["Count"] || {};

        const data = Object.keys(names).map(i => ({
          topic: names[i],
          count: counts[i] || 0,
        }));
        setTopics(data);
      })
      .catch(err => console.error("Error fetching topics:", err));
  }, [apiUrl]);

  const handleSearch = async () => {
    try {
      const res = await axios.get(`${apiUrl}/search?query=${query}`);
      setSearchResults(res.data.results || []);
    } catch (err) {
      console.error("Error during search:", err);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Research Review Dashboard</h1>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Meta Review</h2>
        <pre className="bg-gray-100 p-4 rounded">{metaReview}</pre>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Topic Clusters</h2>
        <BarChart width={600} height={300} data={topics}>
          <XAxis dataKey="topic" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#3b82f6" />
        </BarChart>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Citation Graph</h2>
        <CitationGraph />
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-2">Semantic Search</h2>
        <div className="flex gap-2">
          <input
            className="border p-2 rounded w-64"
            placeholder="Search related papers..."
            value={query}
            onChange={e => setQuery(e.target.value)}
          />
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded"
            onClick={handleSearch}
          >
            Search
          </button>
        </div>
        <ul className="mt-4">
          {searchResults.map((r, i) => (
            <li key={i} className="border-b py-2">
              <strong>{r.title}</strong> ({(r.score || 0).toFixed(2)})
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

