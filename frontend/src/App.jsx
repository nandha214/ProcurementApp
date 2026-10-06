import { useState, useEffect } from 'react';

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
  const [errorMsg, setErrorMsg] = useState(null);
  const [dynamoLogged, setDynamoLogged] = useState(false);
  const [dynamoInfo, setDynamoInfo] = useState('');
  const [cloudStatus, setCloudStatus] = useState(null);
  const [showStatusModal, setShowStatusModal] = useState(false);

  // Dynamic API base: use env var if provided (e.g. VITE_API_URL=http://ec2-ip:8000),
  // otherwise relative path (works with Vite proxy locally and Nginx on EC2)
  const API_BASE = import.meta.env.VITE_API_URL || '';

  const fetchCloudStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/status/`);
      if (res.ok) {
        const data = await res.json();
        setCloudStatus(data);
      }
    } catch (err) {
      console.warn("Could not fetch cloud status:", err);
    }
  };

  useEffect(() => {
    fetchCloudStatus();
  }, []);

  const runSearch = async (text) => {
    if (!text.trim()) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const response = await fetch(`${API_BASE}/api/recommend/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tender_text: text }),
      });

      if (!response.ok) {
        throw new Error(`API returned status ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setResults(data.recommendations || []);
      setModelName(data.model || '');
      setInferenceTimeMs(data.inference_time_ms ?? null);
      setDynamoLogged(!!data.aws_dynamodb_logged);
      setDynamoInfo(data.aws_dynamodb_info || '');
    } catch (error) {
      console.error("Error fetching recommendations:", error);
      setErrorMsg(
        `Unable to reach recommendation engine. Ensure backend is running at ${API_BASE || 'http://127.0.0.1:8000'}`
      );
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
    <div className="min-h-screen bg-slate-50 text-slate-800 p-6 md:p-10 font-sans">
      <div className="max-w-5xl mx-auto">
        
        {/* Top Header & AWS Architecture Badges */}
        <header className="mb-8 border-b border-slate-200 pb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <span className="inline-block px-3 py-1 bg-amber-100 text-amber-800 text-xs font-semibold rounded-full mb-2 tracking-wide uppercase">
                CSE2025 • AWS Solution Architect Project
              </span>
              <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                Procurement Standards Recommendation System
              </h1>
              <p className="text-sm text-slate-600 mt-1">
                Zero-shot semantic retrieval of Indian Standards (BIS) powered by Sentence Transformers &amp; AWS Cloud
              </p>
            </div>
            
            <button
              onClick={() => { setShowStatusModal(true); fetchCloudStatus(); }}
              className="self-start md:self-auto px-4 py-2 bg-indigo-50 border border-indigo-200 text-indigo-700 text-xs font-medium rounded-lg hover:bg-indigo-100 transition shadow-sm flex items-center gap-2"
            >
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              View AWS Architecture Status
            </button>
          </div>

          {/* Mandatory AWS Services Badges */}
          <div className="mt-4 flex flex-wrap gap-2 text-xs">
            <span className="px-2.5 py-1 bg-blue-100 text-blue-800 font-semibold rounded-md border border-blue-200">
              Compute: Amazon EC2
            </span>
            <span className="px-2.5 py-1 bg-emerald-100 text-emerald-800 font-semibold rounded-md border border-emerald-200">
              Storage: Amazon S3
            </span>
            <span className="px-2.5 py-1 bg-purple-100 text-purple-800 font-semibold rounded-md border border-purple-200">
              Database: Amazon DynamoDB
            </span>
            <span className="px-2.5 py-1 bg-amber-100 text-amber-800 font-semibold rounded-md border border-amber-200">
              Security: AWS IAM
            </span>
          </div>
        </header>

        {/* Search Input Box */}
        <section className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 mb-6">
          <form onSubmit={handleSearch} className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter a procurement requirement (e.g., 100W LED street lights for municipal roads)"
              className="flex-1 px-4 py-3 border border-slate-300 rounded-lg text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg text-sm shadow-sm transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                  </svg>
                  <span>Searching...</span>
                </>
              ) : (
                'Search Standards'
              )}
            </button>
          </form>

          {/* Sample Query Pills */}
          <div className="mt-4">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Sample Tender Requirements:</p>
            <div className="flex flex-wrap gap-2">
              {SAMPLE_QUERIES.map((sample) => (
                <button
                  key={sample}
                  type="button"
                  onClick={() => handleSampleClick(sample)}
                  className="px-3 py-1.5 text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-md transition text-left border border-slate-200"
                >
                  {sample}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Error notification banner */}
        {errorMsg && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm flex items-start gap-3">
            <span className="font-bold">Error:</span>
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Model Metrics & AWS Logging notification */}
        {modelName && (
          <div className="mb-6 p-4 bg-white rounded-lg border border-slate-200 flex flex-wrap items-center justify-between gap-3 text-xs text-slate-600 shadow-sm">
            <div>
              <span className="font-medium text-slate-500">Active AI Model:</span>{' '}
              <span className="font-semibold text-slate-800">{modelName}</span>
            </div>
            <div className="flex items-center gap-4">
              {inferenceTimeMs !== null && (
                <div>
                  <span className="font-medium text-slate-500">Inference Time:</span>{' '}
                  <span className="font-bold text-blue-600">{inferenceTimeMs} ms</span>
                </div>
              )}
              {dynamoLogged && (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  Logged to AWS DynamoDB
                </span>
              )}
            </div>
          </div>
        )}

        {/* Results List */}
        <div className="space-y-4">
          {results.map((item) => (
            <div
              key={item.is_code}
              className="p-6 bg-white rounded-xl shadow-sm border border-slate-200 hover:border-blue-300 transition"
            >
              <div className="flex flex-wrap justify-between items-start gap-2 mb-3">
                <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <span className="inline-block px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-xs font-semibold">
                    #{item.rank}
                  </span>
                  <span>{item.is_code}</span>
                </h2>
                {item.mandatory_cert ? (
                  <span className="px-3 py-1 bg-rose-50 text-rose-700 border border-rose-200 text-xs font-semibold rounded-full">
                    Mandatory: {item.scheme}
                  </span>
                ) : (
                  <span className="px-3 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 text-xs font-semibold rounded-full">
                    Voluntary Standard
                  </span>
                )}
              </div>

              <p className="text-slate-700 font-medium text-sm mb-4 leading-relaxed">
                {item.title}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs bg-slate-50 p-4 rounded-lg border border-slate-100">
                <div>
                  <strong className="text-slate-800 block mb-1 uppercase tracking-wider">Allied Standards:</strong>
                  {item.allied_standards && item.allied_standards.length > 0 ? (
                    <ul className="list-disc pl-4 text-slate-600 space-y-1">
                      {item.allied_standards.map((std) => (
                        <li key={std}>{std}</li>
                      ))}
                    </ul>
                  ) : (
                    <span className="text-slate-400 italic">None listed</span>
                  )}
                </div>
                <div>
                  <strong className="text-slate-800 block mb-1 uppercase tracking-wider">Test Methods:</strong>
                  {item.test_methods && item.test_methods.length > 0 ? (
                    <ul className="list-disc pl-4 text-slate-600 space-y-1">
                      {item.test_methods.map((test) => (
                        <li key={test}>{test}</li>
                      ))}
                    </ul>
                  ) : (
                    <span className="text-slate-400 italic">None listed</span>
                  )}
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex justify-between items-center text-xs text-slate-500">
                <div>Status: <span className="font-semibold text-slate-700">{item.status}</span></div>
                <div className="font-semibold text-blue-600">Relevance Score: {item.relevance_score}%</div>
              </div>
            </div>
          ))}
        </div>

        {/* Modal for AWS Architecture Details */}
        {showStatusModal && (
          <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-100">
              <div className="flex justify-between items-center mb-4 pb-3 border-b border-slate-100">
                <h3 className="text-lg font-bold text-slate-900">AWS Cloud Architecture</h3>
                <button
                  onClick={() => setShowStatusModal(false)}
                  className="text-slate-400 hover:text-slate-600 text-lg font-bold"
                >
                  &times;
                </button>
              </div>

              <div className="space-y-3 text-xs">
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
                  <span className="font-bold text-blue-900 block">1. Compute Service: Amazon EC2</span>
                  <span className="text-blue-700">Hosts Django REST API &amp; Gunicorn server. Executes Sentence Transformers &amp; ChromaDB similarity search.</span>
                </div>

                <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-100">
                  <span className="font-bold text-emerald-900 block">2. Storage Service: Amazon S3</span>
                  <span className="text-emerald-700">Stores master BIS standards dataset (bis_data.json) and query report backups in S3 bucket.</span>
                </div>

                <div className="p-3 bg-purple-50 rounded-lg border border-purple-100">
                  <span className="font-bold text-purple-900 block">3. Database Service: Amazon DynamoDB</span>
                  <span className="text-purple-700">Table: bis_search_logs. Persists real-time search queries, latency metrics, and audit timestamps.</span>
                </div>

                <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
                  <span className="font-bold text-amber-900 block">4. Security: AWS IAM</span>
                  <span className="text-amber-700">EC2 Instance Profile Role with least privilege access to S3 bucket and DynamoDB table.</span>
                </div>

                {cloudStatus && (
                  <div className="mt-4 p-3 bg-slate-100 rounded-lg text-slate-700">
                    <p><strong>Configured Region:</strong> {cloudStatus.region}</p>
                    <p><strong>Standards in Vector DB:</strong> {cloudStatus.indexed_standards_count}</p>
                    <p><strong>Status:</strong> {cloudStatus.status}</p>
                  </div>
                )}
              </div>

              <button
                onClick={() => setShowStatusModal(false)}
                className="mt-6 w-full py-2 bg-slate-900 text-white rounded-lg text-xs font-semibold hover:bg-slate-800"
              >
                Close
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
