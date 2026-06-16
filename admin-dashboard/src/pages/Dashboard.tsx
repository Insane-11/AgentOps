import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";

export default function Dashboard() {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [engineers, setEngineers] = useState<any[]>([]);

  useEffect(() => {
    api.getIncidents().then(setIncidents).catch(console.error);
    api.getEngineers().then(setEngineers).catch(console.error);
  }, []);

  const activeIncidents = incidents.filter((i) => i.status !== "RESOLVED");
  const onCallEngineers = engineers.filter((e) => e.is_on_call);

  return (
    <div className="p-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">AgentOps</h1>
        <p className="text-gray-500">AI-Powered Incident Response Dashboard</p>
      </header>

      <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="rounded-lg border bg-white p-6">
          <div className="text-3xl font-bold text-blue-600">{activeIncidents.length}</div>
          <div className="text-sm text-gray-500">Active Incidents</div>
        </div>
        <div className="rounded-lg border bg-white p-6">
          <div className="text-3xl font-bold text-green-600">{engineers.length}</div>
          <div className="text-sm text-gray-500">Total Engineers</div>
        </div>
        <div className="rounded-lg border bg-white p-6">
          <div className="text-3xl font-bold text-amber-600">{onCallEngineers.length}</div>
          <div className="text-sm text-gray-500">On-Call Engineers</div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border bg-white p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Recent Incidents</h2>
            <Link to="/incidents" className="text-sm text-blue-600 hover:underline">View All</Link>
          </div>
          <div className="space-y-3">
            {incidents.slice(0, 5).map((inc) => (
              <div key={inc.id} className="flex items-center justify-between rounded bg-gray-50 p-3">
                <div>
                  <div className="font-medium">{inc.title}</div>
                  <div className="text-xs text-gray-400">{inc.status}</div>
                </div>
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  inc.severity === "CRITICAL" ? "bg-red-100 text-red-700" :
                  inc.severity === "HIGH" ? "bg-orange-100 text-orange-700" :
                  "bg-yellow-100 text-yellow-700"
                }`}>{inc.severity}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg border bg-white p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">On-Call Engineers</h2>
            <Link to="/engineers" className="text-sm text-blue-600 hover:underline">Manage</Link>
          </div>
          <div className="space-y-3">
            {onCallEngineers.map((eng) => (
              <div key={eng.id} className="rounded bg-gray-50 p-3">
                <div className="font-medium">{eng.name}</div>
                <div className="text-xs text-gray-400">{eng.email} &middot; {eng.role}</div>
              </div>
            ))}
            {onCallEngineers.length === 0 && (
              <div className="text-sm text-gray-400">No engineers currently on call</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
