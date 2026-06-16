import { useCallback, useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api/client";

export default function IncidentDetail() {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<any>(null);
  const [runningTriage, setRunningTriage] = useState(false);
  const [triageError, setTriageError] = useState("");

  const load = useCallback(() => {
    if (id) {
      api.getIncident(id).then(setIncident).catch(console.error);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  const handleRunTriage = async () => {
    setRunningTriage(true);
    setTriageError("");
    try {
      const updated = await api.runTriage(id!);
      setIncident(updated);
    } catch (err: any) {
      setTriageError(err.message || "Triage failed");
    } finally {
      setRunningTriage(false);
    }
  };

  if (!incident) {
    return <div className="p-8 text-center text-gray-400">Loading...</div>;
  }

  const severityColor = (s: string) =>
    s === "CRITICAL" ? "bg-red-100 text-red-700" :
    s === "HIGH" ? "bg-orange-100 text-orange-700" :
    s === "MEDIUM" ? "bg-yellow-100 text-yellow-700" :
    "bg-green-100 text-green-700";

  const needsTriage = incident.status === "FIRED";

  return (
    <div className="p-6">
      <div className="mb-6">
        <Link to="/" className="text-sm text-gray-500 hover:text-gray-700">&larr; Back to Queue</Link>
      </div>

      <div className="rounded-lg border bg-white p-6">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{incident.title}</h1>
            {needsTriage && (
              <button
                onClick={handleRunTriage}
                disabled={runningTriage}
                className="rounded bg-indigo-600 px-3 py-1 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                {runningTriage ? "Running..." : "Run Triage"}
              </button>
            )}
          </div>
          <span className={`rounded-full px-3 py-1 text-sm font-medium ${severityColor(incident.severity)}`}>{incident.severity}</span>
        </div>

        {triageError && (
          <div className="mb-4 rounded bg-red-50 p-3 text-sm text-red-600">{triageError}</div>
        )}

        <div className="mb-6 grid grid-cols-2 gap-4 text-sm">
          <div><span className="text-gray-400">Status:</span> <span className="font-medium">{incident.status}</span></div>
          <div><span className="text-gray-400">Created:</span> <span className="font-medium">{new Date(incident.created_at).toLocaleString()}</span></div>
          <div><span className="text-gray-400">Assigned Engineer:</span> <span className="font-medium">{incident.assigned_engineer_id || "Unassigned"}</span></div>
        </div>

        {incident.description && (
          <div className="mb-6">
            <h2 className="mb-2 text-sm font-semibold text-gray-700">Description</h2>
            <p className="rounded bg-gray-50 p-3 text-sm text-gray-600">{incident.description}</p>
          </div>
        )}

        {incident.agent_summary && (
          <div className="mb-6 rounded-lg border border-indigo-100 bg-indigo-50 p-4">
            <div className="mb-2 flex items-center gap-2">
              <span className="rounded bg-indigo-200 px-2 py-0.5 text-xs font-medium text-indigo-800">AI Analysis</span>
              {incident.agent_trace_id && (
                <span className="text-xs text-gray-400">Trace: {incident.agent_trace_id}</span>
              )}
            </div>
            <p className="text-sm text-gray-700">{incident.agent_summary}</p>
          </div>
        )}

        {!incident.agent_summary && !needsTriage && (
          <div className="rounded-lg border-2 border-dashed border-gray-200 p-6 text-center text-sm text-gray-400">
            No AI analysis available for this incident.
          </div>
        )}
      </div>
    </div>
  );
}
