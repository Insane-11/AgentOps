import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api/client";

export default function IncidentDetail() {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<any>(null);

  useEffect(() => {
    if (id) {
      api.getIncident(id).then(setIncident).catch(console.error);
    }
  }, [id]);

  if (!incident) {
    return <div className="p-8 text-center text-gray-400">Loading...</div>;
  }

  const severityColor = (s: string) =>
    s === "CRITICAL" ? "bg-red-100 text-red-700" :
    s === "HIGH" ? "bg-orange-100 text-orange-700" :
    s === "MEDIUM" ? "bg-yellow-100 text-yellow-700" :
    "bg-green-100 text-green-700";

  return (
    <div className="p-6">
      <div className="mb-6">
        <Link to="/" className="text-sm text-gray-500 hover:text-gray-700">&larr; Back to Queue</Link>
      </div>

      <div className="rounded-lg border bg-white p-6">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">{incident.title}</h1>
          <span className={`rounded-full px-3 py-1 text-sm font-medium ${severityColor(incident.severity)}`}>{incident.severity}</span>
        </div>

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

        <div className="rounded-lg border-2 border-dashed border-gray-200 p-6 text-center text-sm text-gray-400">
          Agent analysis and workflow visualization will appear here in Phase 2/3.
        </div>
      </div>
    </div>
  );
}
