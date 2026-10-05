import { useState } from 'react';

// Keep this in sync with backend/api/sample_queries.json -
// these are the SAME 6 queries used across every model variant
// (Sentence Transformer / BiLSTM / BERT) for fair comparison.
const SAMPLE_QUERIES = [
  "We need 100W LED street lights for municipal roads.",
  "Cement for reinforced concrete construction.",
  "Industrial safety helmets for construction site workers.",
  "EV charging station for public parking area.",
  "Fire detection and alarm system for a commercial building.",
  "Solar PV modules for a rooftop solar installation.",
];

export default function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [modelName, setModelName] = useState('');
  const [inferenceTimeMs, setInferenceTimeMs] = useState(null);
  const [loading, setLoading] = useState(false);

  const runSearch = async (text) => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/recommend/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tender_text: text }),
      });
      const data = await response.json();
      setResults(data.recommendations || []);
      setModelName(data.model || '');
      setInferenceTimeMs(data.inference_time_ms ?? null);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
    setLoading(false);
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    await runSearch(query);
  };

  const handleSampleClick = async (sample) => {
    setQuery(sample);
    await runSearch(sample);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-1">Procurement Standards Recommendation System</h1>
        <p className="text-sm text-gray-500 mb-6">Recommends applicable Indian Standards for a procurement requirement.</p>

        <form onSubmit={handleSearch} className="mb-4 flex gap-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter a procurement requirement (e.g., 100W LED street lights)"
            className="flex-1 p-3 border border-gray-300 rounded-lg shadow-sm"
          />
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-sm hover:bg-blue-700"
          >
            {loading ? 'Analyzing...' : 'Search Standards'}
          </button>
        </form>

        <div className="mb-8 flex flex-wrap gap-2">
          {SAMPLE_QUERIES.map((sample) => (
            <button
              key={sample}
              type="button"
              onClick={() => handleSampleClick(sample)}
              className="px-3 py-1 text-xs bg-gray-200 text-gray-700 rounded-full hover:bg-gray-300"
            >
              {sample}
            </button>
          ))}
        </div>

        {modelName && (
          <div className="mb-4 text-sm text-gray-600">
            Model: <span className="font-semibold">{modelName}</span>
            {inferenceTimeMs !== null && (
              <span> &nbsp;|&nbsp; Inference time: <span className="font-semibold">{inferenceTimeMs} ms</span></span>
            )}
          </div>
        )}

        <div className="space-y-4">
          {results.map((item) => (
            <div key={item.is_code} className="p-6 bg-white rounded-lg shadow border border-gray-200">
              <div className="flex justify-between items-start mb-2">
                <h2 className="text-xl font-bold text-gray-900">
                  <span className="text-gray-400 mr-2">#{item.rank}</span>{item.is_code}
                </h2>
                {item.mandatory_cert ? (
                  <span className="px-3 py-1 bg-red-100 text-red-800 text-sm font-semibold rounded-full">
                    Mandatory: {item.scheme}
                  </span>
                ) : (
                  <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded-full">
                    Voluntary
                  </span>
                )}
              </div>
              <p className="text-gray-700 font-medium mb-4">{item.title}</p>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <strong className="text-gray-900 block mb-1">Allied Standards:</strong>
                  <ul className="list-disc pl-5 text-gray-600">
                    {item.allied_standards.map(std => <li key={std}>{std}</li>)}
                  </ul>
                </div>
                <div>
                  <strong className="text-gray-900 block mb-1">Test Methods:</strong>
                  <ul className="list-disc pl-5 text-gray-600">
                    {item.test_methods.map(test => <li key={test}>{test}</li>)}
                  </ul>
                </div>
              </div>
              <div className="mt-4 text-xs text-gray-400">Relevance Score: {item.relevance_score}%</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
