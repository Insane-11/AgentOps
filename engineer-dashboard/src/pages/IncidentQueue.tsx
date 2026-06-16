import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";

export default function IncidentQueue() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [showAlertForm, setShowAlertForm] = useState(false);
  const [alertTitle, setAlertTitle] = useState("");
  const [alertDesc, setAlertDesc] = useState("");

  useEffect(() => {
    api.getIncidents().then(setIncidents).catch(console.error);
  }, []);

  const handleCreateAlert = async () => {
    try {
      await api.createAlert({ title: alertTitle, description: alertDesc });
      setAlertTitle("");
      setAlertDesc("");
      setShowAlertForm(false);
      const updated = await api.getIncidents();
      setIncidents(updated);
    } catch (err) {
      console.error(err);
    }
  };

  const severityColor = (s: string) =>
    s === "CRITICAL" ? "bg-red-100 text-red-700" :
    s === "HIGH" ? "bg-orange-100 text-orange-700" :
    s === "MEDIUM" ? "bg-yellow-100 text-yellow-700" :
    "bg-green-100 text-green-700";

  const activeIncidents = incidents.filter((i) => i.status !== "RESOLVED");

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Incident Queue</h1>
        <button onClick={() => setShowAlertForm(!showAlertForm)} className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
          {showAlertForm ? "Cancel" : "Report Alert"}
        </button>
      </div>

      {showAlertForm && (
        <div className="mb-6 rounded-lg border bg-white p-4">
          <h2 className="mb-3 font-semibold">Report New Alert</h2>
          <input value={alertTitle} onChange={(e) => setAlertTitle(e.target.value)} placeholder="Alert title" className="mb-2 w-full rounded border px-3 py-2 text-sm" />
          <textarea value={alertDesc} onChange={(e) => setAlertDesc(e.target.value)} placeholder="Description" className="mb-3 w-full rounded border px-3 py-2 text-sm" rows={3} />
          <button onClick={handleCreateAlert} className="rounded bg-green-600 px-4 py-2 text-sm text-white hover:bg-green-700">Submit Alert</button>
        </div>
      )}

      <div className="space-y-3">
        {activeIncidents.map((inc) => (
          <Link key={inc.id} to={`/incidents/${inc.id}`} className="block rounded-lg border bg-white p-4 transition hover:shadow-md">
            <div className="flex items-start justify-between">
              <div>
                <div className="font-medium text-gray-900">{inc.title}</div>
                <div className="mt-1 text-sm text-gray-500">{inc.description || "No description"}</div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${severityColor(inc.severity)}`}>{inc.severity}</span>
                <span className="text-xs text-gray-400">{inc.status}</span>
              </div>
            </div>
          </Link>
        ))}
        {activeIncidents.length === 0 && (
          <div className="rounded-lg border bg-white p-8 text-center text-gray-400">No active incidents</div>
        )}
      </div>
    </div>
  );
}
