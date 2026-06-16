import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";

const COLORS = ["#DC2626", "#EA580C", "#CA8A04", "#16A34A"];

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<any>(null);
  const [accuracy, setAccuracy] = useState<any>(null);
  const [coverage, setCoverage] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [o, a, c] = await Promise.all([
          api.getAnalyticsOverview(),
          api.getAnalyticsAccuracy(),
          api.getEmbeddingCoverage(),
        ]);
        setOverview(o);
        setAccuracy(a);
        setCoverage(c);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-gray-400">Loading analytics...</div>;
  }

  const severityData = accuracy?.severity_distribution
    ? Object.entries(accuracy.severity_distribution).map(([name, value]) => ({
        name,
        value,
      }))
    : [];

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center gap-4">
        <Link to="/" className="text-sm text-gray-500 hover:text-gray-700">&larr; Dashboard</Link>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Incidents" value={overview?.total_incidents ?? 0} />
        <StatCard label="Resolved" value={overview?.resolved_incidents ?? 0} />
        <StatCard label="Resolution Rate" value={`${overview?.resolution_rate ?? 0}%`} />
        <StatCard label="Avg Resolution" value={`${overview?.avg_resolution_hours ?? 0}h`} />
      </div>

      <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Severity Distribution (30d)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={severityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#4F46E5" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-lg border bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Severity Mix</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {severityData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">AI Coverage</h2>
          <div className="text-center">
            <div className="text-5xl font-bold text-indigo-600">{coverage?.coverage_pct ?? 0}%</div>
            <p className="mt-2 text-sm text-gray-500">
              {coverage?.embedded_incidents ?? 0} / {coverage?.total_incidents ?? 0} incidents embedded
            </p>
          </div>
        </div>

        <div className="rounded-lg border bg-white p-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">Agent Activity</h2>
          <div className="text-center">
            <div className="text-5xl font-bold text-emerald-600">{accuracy?.agent_analysis_count ?? 0}</div>
            <p className="mt-2 text-sm text-gray-500">AI analyses performed (last 30 days)</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border bg-white p-4">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="mt-1 text-2xl font-bold text-gray-900">{value}</div>
    </div>
  );
}
