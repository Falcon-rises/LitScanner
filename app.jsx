import React, { useState, useEffect } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";
import CitationGraph from "./components/CitationGraph";

export default function App() {
  const [metaReview, setMetaReview] = useState("");
  const [topics, setTopics] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [query, setQuery] = useState("");

  useEffect(() => {
    axios.get("/summarize").then(res => setMetaReview(res.data.meta_review));
    axios.get("/topics").then(res => {
      const topicInfo = res.data.topic_info;
      const data = Object.keys(topicInfo["Name"]).map(i => ({
        topic: topicInfo["Name"][i],
        count: topicInfo["Count"][i]
      }));
      setTopics(data);
    });
  }, []);

  const handleSearch = async () => {
    const res = await axios.get(`/search?query=${query}`);
    setSearchResults(res.data.results);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Research Review Dashboard</h1>
      
      {/* Meta Review */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Meta Review</h2>
        <pre className="bg-gray-100 p-4 rounded">{metaReview}</pre>
      </section>

      {/* Topic Chart */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Topic Clusters</h2>
        <BarChart width={600} height={300} data={topics}>
          <XAxis dataKey="topic" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#3b82f6" />
        </BarChart>
      </section>

      {/* Citation Graph */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Citation Graph</h2>
        <CitationGraph />
      </section>

      {/* Semantic Search */}
      <section>
        <h2 className="text-xl font-semibold mb-2">Semantic Search</h2>
        <div className="flex gap-2">
          <input 
            className="border p-2 rounded w-64"
            placeholder="Search related papers..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button 
            className="bg-blue-500 text-white px-4 py-2 rounded"
            onClick={handleSearch}>
            Search
          </button>
        </div>
        <ul className="mt-4">
          {searchResults.map((r, i) => (
            <li key={i} className="border-b py-2">
              <strong>{r.title}</strong> ({r.score.toFixed(2)})
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
