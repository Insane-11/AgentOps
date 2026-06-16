import { useEffect, useState } from "react";
import { api } from "../api/client";
import { Link } from "react-router-dom";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<any[]>([]);

  useEffect(() => {
    api.getIncidents().then(setIncidents).catch(console.error);
  }, []);

  const severityColor = (s: string) =>
    s === "CRITICAL" ? "bg-red-100 text-red-700" :
    s === "HIGH" ? "bg-orange-100 text-orange-700" :
    s === "MEDIUM" ? "bg-yellow-100 text-yellow-700" :
    "bg-green-100 text-green-700";

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Incidents</h1>
        <Link to="/" className="text-sm text-gray-500 hover:text-gray-700">&larr; Dashboard</Link>
      </div>
      <div className="overflow-x-auto rounded-lg border bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b bg-gray-50">
            <tr>
              <th className="px-4 py-3 font-medium text-gray-600">Title</th>
              <th className="px-4 py-3 font-medium text-gray-600">Status</th>
              <th className="px-4 py-3 font-medium text-gray-600">Severity</th>
              <th className="px-4 py-3 font-medium text-gray-600">Created</th>
            </tr>
          </thead>
          <tbody>
            {incidents.map((inc) => (
              <tr key={inc.id} className="border-b hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{inc.title}</td>
                <td className="px-4 py-3">{inc.status}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${severityColor(inc.severity)}`}>
                    {inc.severity}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-400">{new Date(inc.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
