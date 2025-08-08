import React, { useState, useEffect } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";
import CitationGraph from "./components/CitationGraph";

export default function App() {
  const [metaReview, setMetaReview] = useState("");
  const [topics, setTopics] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [query, setQuery] = useState("");
  const [loadingMeta, setLoadingMeta] = useState(true);
  const [loadingTopics, setLoadingTopics] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");

  const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

  useEffect(() => {
    // Fetch meta review
    axios.get(`${apiUrl}/summarize`)
      .then(res => {
        setMetaReview(res.data.meta_review);
        setLoadingMeta(false);
      })
      .catch(err => {
        setErrorMsg("⚠️ Failed to load meta review.");
        setLoadingMeta(false);
      });

    // Fetch topic clusters
    axios.get(`${apiUrl}/topics`)
      .then(res => {
        const topicInfo = res.data.topic_info || {};
        const names = topicInfo["Name"] || {};
        const counts = topicInfo["Count"] || {};

        const data = Object.keys(names).map(i => ({
          topic: names[i],
          count: counts[i] || 0
        }));
        setTopics(data);
        setLoadingTopics(false);
      })
      .catch(err => {
        setErrorMsg("⚠️ Failed to load topic clusters.");
        setLoadingTopics(false);
      });
  }, [apiUrl]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    try {
      const res = await axios.get(`${apiUrl}/search?query=${query}`);
      setSearchResults(res.data.results || []);
    } catch (err) {
      setErrorMsg("⚠️ Error occurred during search.");
    }
  };

  return (
    <main className="p-6 space-y-10" role="main">
      <header>
        <h1 className="text-3xl font-bold mb-4 text-blue-700">📘 LitScanner</h1>
        {errorMsg && <p className="text-red-500">{errorMsg}</p>}
      </header>

      {/* Meta Review */}
      <section aria-label="Meta Review">
        <h2 className="text-xl font-semibold mb-2">📝 Meta Review</h2>
        {loadingMeta ? (
          <p>Loading summary...</p>
        ) : (
          <pre className="bg-gray-100 p-4 rounded overflow-auto">{metaReview}</pre>
        )}
      </section>

      {/* Topic Clusters */}
      <section aria-label="Topic Clusters">
        <h2 className="text-xl font-semibold mb-2">🧠 Topic Clusters</h2>
        {loadingTopics ? (
          <p>Loading topic clusters...</p>
        ) : (
          <BarChart width={600} height={300} data={topics}>
            <XAxis dataKey="topic" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#3b82f6" />
          </BarChart>
        )}
      </section>

      {/* Citation Graph */}
      <section aria-label="Citation Graph">
        <h2 className="text-xl font-semibold mb-2">📊 Citation Graph</h2>
        <CitationGraph />
      </section>

      {/* Semantic Search */}
      <section aria-label="Semantic Search">
        <h2 className="text-xl font-semibold mb-2">🔍 Semantic Search</h2>
        <div className="flex gap-2 items-center mb-4">
          <input
            className="border p-2 rounded w-64"
            placeholder="Search related papers..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Search Input"
          />
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            onClick={handleSearch}
            aria-label="Search Button"
          >
            Search
          </button>
        </div>
        <ul className="space-y-2">
          {searchResults.length === 0 && query && (
            <p className="text-gray-500">No results found.</p>
          )}
          {searchResults.map((r, i) => (
            <li key={i} className="border-b py-2">
              <article>
                <strong>{r.title}</strong> <span className="text-sm text-gray-500">({(r.score || 0).toFixed(2)})</span>
              </article>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}


