import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import LoginPage from "./pages/LoginPage";
import Dashboard from "./pages/Dashboard";
import IncidentsPage from "./pages/IncidentsPage";
import EngineersPage from "./pages/EngineersPage";
import AnalyticsPage from "./pages/AnalyticsPage";

function ProtectedRoute({ children, role }: { children: React.ReactNode; role?: string }) {
  const auth = useAuth();
  if (auth.loading) return <div className="p-8 text-center">Loading...</div>;
  if (!auth.isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  const auth = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/login" element={<LoginPage onLogin={auth.login} />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/incidents"
          element={
            <ProtectedRoute>
              <IncidentsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/engineers"
          element={
            <ProtectedRoute>
              <EngineersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <AnalyticsPage />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}
