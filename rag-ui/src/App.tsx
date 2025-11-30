import { useEffect, useState } from "react";

type Citation = {
  id: string;
  source_type: string;
  source_id?: string | null;
};

type Metric = {
  metric_name: string;
  value: number;
  district_rank?: number | null;
  year?: number | null;
  source?: string;
};

type RAGResponse = {
  answer: string;
  high_level_bullets: string[];
  metrics: Metric[];
  citations: Citation[];
};

type Mode = "district_risk_overview" | "explain_metric";

type BackendStatus = {
  use_fake_embeddings: boolean;
  use_fake_llm: boolean;
  embedding_model: string;
  llm_model: string;
};

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_URL = `${API_BASE}/api/rag/query`;
const STATUS_URL = `${API_BASE}/api/status`;
const FRONTEND_FAKE_MODE =
  (import.meta.env.VITE_FAKE_MODE || "false").toLowerCase() === "true";

function App() {
  const [question, setQuestion] = useState(
    "What are the top risk indicators for District 29 schools with high SVI?"
  );
  const [districtId, setDistrictId] = useState<number | undefined>(29);
  const [year, setYear] = useState<number | undefined>(2024);
  const [mode, setMode] = useState<Mode>("district_risk_overview");

  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<RAGResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [backendStatus, setBackendStatus] = useState<BackendStatus | null>(
    null
  );
  const [statusError, setStatusError] = useState<string | null>(null);

  // Fetch backend status once on load
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch(STATUS_URL);
        if (!res.ok) {
          throw new Error(`status ${res.status}`);
        }
        const data = await res.json();
        setBackendStatus(data);
      } catch (err: any) {
        setStatusError(err.message || "Failed to load backend status");
      }
    };

    fetchStatus();
  }, []);

  const handleAsk = async () => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const body = {
        question,
        district_id: districtId,
        year,
        mode,
      };

      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(
          `Request failed with status ${res.status}: ${
            text || "no response body"
          }`
        );
      }

      const data: RAGResponse = await res.json();
      setResponse(data);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setResponse(null);
    setError(null);
  };

  const setPreset = (presetMode: Mode) => {
    setMode(presetMode);
    if (presetMode === "district_risk_overview") {
      setQuestion(
        "Provide a district-level risk and equity overview for District 29 using SVI and climate data."
      );
    } else {
      setQuestion(
        "Explain student response rate in the context of SVI and school climate."
      );
    }
    setResponse(null);
    setError(null);
  };

  const backendFake =
    backendStatus?.use_fake_embeddings || backendStatus?.use_fake_llm;

  const backendBadgeText = backendStatus
    ? backendFake
      ? "BACKEND: FAKE MODE"
      : "BACKEND: REAL MODE"
    : statusError
    ? "BACKEND: UNKNOWN"
    : "BACKEND: LOADING...";

  const backendBadgeClass = backendFake
    ? "bg-amber-100 text-amber-800 border-amber-200"
    : "bg-emerald-100 text-emerald-800 border-emerald-200";

  return (
    <div className="min-h-screen bg-slate-900 flex justify-center p-6 text-slate-100">
      <div className="w-full max-w-5xl bg-slate-950 shadow-xl rounded-2xl p-6 space-y-6 border border-slate-800">
        <header className="space-y-2 border-b border-slate-800 pb-4">
          <h1 className="text-2xl font-semibold">
            School Climate &amp; SVI Q&amp;A (RAG Demo)
          </h1>

          <div className="text-xs text-slate-300 mt-1">
            BACKEND:{" "}
            {backendStatus
              ? backendStatus.use_fake_embeddings || backendStatus.use_fake_llm
                ? "FAKE MODE"
                : "REAL MODE"
              : statusError
              ? "UNKNOWN"
              : "LOADING..."}
            <br />
            FRONTEND FAKE FLAG: {FRONTEND_FAKE_MODE ? "true" : "false"}
          </div>

          <p className="text-xs text-slate-400 pt-1">
            Back-end mode is controlled via <code>USE_FAKE_EMBEDDINGS</code> and{" "}
            <code>USE_FAKE_LLM</code>. Front-end uses <code>VITE_FAKE_MODE</code> for
            labeling only. This lets you test both real and offline local RAG behavior.
          </p>
        </header>

        {/* Mode selector */}
        <section className="space-y-2">
          <label className="block text-sm font-medium">Mode</label>
          <div className="flex flex-wrap gap-3 items-center">
            <select
              className="border rounded-lg p-1 text-sm bg-slate-900 border-slate-700 text-slate-100"
              value={mode}
              onChange={(e) => setMode(e.target.value as Mode)}
              disabled={loading}
            >
              <option value="district_risk_overview">
                District risk overview
              </option>
              <option value="explain_metric">Explain a metric</option>
            </select>

            <button
              type="button"
              onClick={() => setPreset("district_risk_overview")}
              disabled={loading}
              className="text-xs border rounded-lg px-2 py-1 disabled:opacity-50 border-slate-600"
            >
              Sample overview question
            </button>
            <button
              type="button"
              onClick={() => setPreset("explain_metric")}
              disabled={loading}
              className="text-xs border rounded-lg px-2 py-1 disabled:opacity-50 border-slate-600"
            >
              Sample metric question
            </button>
          </div>
          <p className="text-xs text-slate-400">
            • <strong>District risk overview</strong> → high-level SVI + climate
            summary for a district. <br />
            • <strong>Explain a metric</strong> → deep dive on one metric (e.g.
            student response rate) and why it matters for equity.
          </p>
        </section>

        {/* Question + filters */}
        <section className="space-y-2">
          <label className="block text-sm font-medium">Question</label>
          <textarea
            className="w-full border rounded-lg p-2 text-sm bg-slate-900 border-slate-700 text-slate-100 focus:outline-none focus:ring"
            rows={3}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />

          <div className="flex gap-4 mt-2 flex-wrap">
            <div>
              <label className="block text-sm font-medium">District ID</label>
              <input
                type="number"
                className="border rounded-lg p-1 text-sm w-24 bg-slate-900 border-slate-700 text-slate-100"
                value={districtId ?? ""}
                onChange={(e) =>
                  setDistrictId(
                    e.target.value ? Number(e.target.value) : undefined
                  )
                }
              />
            </div>
            <div>
              <label className="block text-sm font-medium">Year</label>
              <input
                type="number"
                className="border rounded-lg p-1 text-sm w-24 bg-slate-900 border-slate-700 text-slate-100"
                value={year ?? ""}
                onChange={(e) =>
                  setYear(
                    e.target.value ? Number(e.target.value) : undefined
                  )
                }
              />
            </div>
          </div>
        </section>

        {/* Actions */}
        <section className="flex gap-3">
          <button
            onClick={handleAsk}
            disabled={loading}
            className="px-4 py-2 rounded-lg text-sm font-medium border bg-emerald-500 text-slate-950 disabled:opacity-50 flex items-center gap-2"
          >
            {loading && (
              <span className="h-3 w-3 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
            )}
            {loading ? "Thinking..." : "Ask"}
          </button>

          <button
            type="button"
            onClick={handleClear}
            disabled={loading || (!response && !error)}
            className="px-3 py-2 rounded-lg text-sm border text-slate-200 border-slate-600 disabled:opacity-40"
          >
            Clear
          </button>
        </section>

        {/* Error */}
        {error && (
          <section className="text-sm text-red-300 bg-red-950/60 border border-red-700 rounded-lg p-3">
            <span className="font-semibold">Error:</span> {error}
          </section>
        )}

        {/* Response */}
        {response && (
          <section className="space-y-4">
            <div className="border rounded-xl p-4 bg-slate-900 border-slate-700">
              <div className="flex justify-between items-center mb-2">
                <h2 className="text-lg font-semibold">Answer</h2>
                <span className="text-xs px-2 py-1 rounded-full bg-slate-800 text-slate-200 font-mono border border-slate-600">
                  mode: {mode}
                </span>
              </div>
              <p className="text-sm whitespace-pre-line">
                {response.answer}
              </p>
            </div>

            {response.high_level_bullets.length > 0 && (
              <div className="border rounded-xl p-4 bg-slate-900 border-slate-700">
                <h3 className="text-sm font-semibold mb-1">Details</h3>
                <ul className="list-disc list-inside text-sm space-y-1">
                  {response.high_level_bullets.map((b, idx) => (
                    <li key={idx}>{b}</li>
                  ))}
                </ul>
              </div>
            )}

            {response.metrics.length > 0 && (
              <div className="border rounded-xl p-4 bg-slate-900 border-slate-700">
                <h3 className="text-sm font-semibold mb-1">
                  Metrics referenced
                </h3>
                <ul className="text-sm space-y-1">
                  {response.metrics.map((m, i) => (
                    <li key={i}>
                      <strong>{m.metric_name}</strong>: {m.value}{" "}
                      {m.district_rank != null &&
                        `(district rank ${m.district_rank})`}
                      {m.year && ` – ${m.year}`}
                      {m.source && (
                        <span className="text-xs text-slate-400">
                          {" "}
                          ({m.source})
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {response.citations.length > 0 && (
              <div className="border rounded-xl p-4 bg-slate-900 border-slate-700">
                <h3 className="text-sm font-semibold mb-1">
                  Sources (semantic)
                </h3>
                <ul className="text-xs text-slate-400 space-y-1">
                  {response.citations.map((c) => (
                    <li key={c.id}>
                      [{c.source_type}] {c.source_id ?? c.id}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  );
}

export default App;
