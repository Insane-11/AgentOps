import { useEffect, useState } from "react";
import { api } from "../api/client";
import { Link } from "react-router-dom";

export default function EngineersPage() {
  const [engineers, setEngineers] = useState<any[]>([]);

  useEffect(() => {
    api.getEngineers().then(setEngineers).catch(console.error);
  }, []);

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Engineers</h1>
        <Link to="/" className="text-sm text-gray-500 hover:text-gray-700">&larr; Dashboard</Link>
      </div>
      <div className="overflow-x-auto rounded-lg border bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b bg-gray-50">
            <tr>
              <th className="px-4 py-3 font-medium text-gray-600">Name</th>
              <th className="px-4 py-3 font-medium text-gray-600">Email</th>
              <th className="px-4 py-3 font-medium text-gray-600">Role</th>
              <th className="px-4 py-3 font-medium text-gray-600">On Call</th>
              <th className="px-4 py-3 font-medium text-gray-600">Active</th>
            </tr>
          </thead>
          <tbody>
            {engineers.map((eng) => (
              <tr key={eng.id} className="border-b hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{eng.name}</td>
                <td className="px-4 py-3 text-gray-500">{eng.email}</td>
                <td className="px-4 py-3 capitalize">{eng.role}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${eng.is_on_call ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"}`}>
                    {eng.is_on_call ? "Yes" : "No"}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${eng.is_active ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
                    {eng.is_active ? "Active" : "Inactive"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
