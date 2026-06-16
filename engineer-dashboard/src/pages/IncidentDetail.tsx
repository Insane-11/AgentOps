import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api/client";

interface WorkflowStep {
  node: string;
  status: "pending" | "running" | "done" | "error";
  data?: any;
}

const NODE_LABELS: Record<string, string> = {
  triage_node: "Triage",
  investigate_node: "Investigate",
  remediate_node: "Remediate",
};

const NODE_ORDER = ["triage_node", "investigate_node", "remediate_node"];

export default function IncidentDetail() {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<any>(null);
  const [runningTriage, setRunningTriage] = useState(false);
  const [runningWorkflow, setRunningWorkflow] = useState(false);
  const [triageError, setTriageError] = useState("");
  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>(
    NODE_ORDER.map((node) => ({ node, status: "pending" }))
  );
  const [workflowResult, setWorkflowResult] = useState<any>(null);
  const abortRef = useRef<AbortController | null>(null);

  const load = useCallback(() => {
    if (id) {
      api.getIncident(id).then(setIncident).catch(console.error);
    }
  }, [id]);

  useEffect(() => {
    load();
    return () => {
      if (abortRef.current) {
        abortRef.current.abort();
      }
    };
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

  const handleRunWorkflow = () => {
    setRunningWorkflow(true);
    setWorkflowSteps(NODE_ORDER.map((node) => ({ node, status: "pending" })));
    setWorkflowResult(null);

    abortRef.current = api.runWorkflow(
      id!,
      (event) => {
        if (event.type === "node_start") {
          setWorkflowSteps((prev) =>
            prev.map((s) => (s.node === event.node ? { ...s, status: "running" } : s))
          );
        } else if (event.type === "node_complete") {
          setWorkflowSteps((prev) =>
            prev.map((s) =>
              s.node === event.node ? { ...s, status: "done", data: event.state } : s
            )
          );
        } else if (event.type === "workflow_complete") {
          setWorkflowResult(event.state);
        }
      },
      (result) => {
        setIncident(result);
        setRunningWorkflow(false);
      }
    );
  };

  if (!incident) {
    return <div className="p-8 text-center text-gray-400">Loading...</div>;
  }

  const severityColor = (s: string) =>
    s === "CRITICAL" ? "bg-red-100 text-red-700" :
    s === "HIGH" ? "bg-orange-100 text-orange-700" :
    s === "MEDIUM" ? "bg-yellow-100 text-yellow-700" :
    "bg-green-100 text-green-700";

  const nodeIcon = (status: string) => {
    switch (status) {
      case "running": return "animate-spin";
      case "done": return "text-green-500";
      case "error": return "text-red-500";
      default: return "text-gray-300";
    }
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <Link to="/" className="text-sm text-gray-500 hover:text-gray-700">&larr; Back to Queue</Link>
      </div>

      <div className="mb-6 rounded-lg border bg-white p-6">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{incident.title}</h1>
            {incident.status === "FIRED" && (
              <button
                onClick={handleRunTriage}
                disabled={runningTriage}
                className="rounded bg-indigo-600 px-3 py-1 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
              >
                {runningTriage ? "Running..." : "Run Triage"}
              </button>
            )}
            {(incident.status === "TRIAGED" || incident.status === "FIRED") && (
              <button
                onClick={handleRunWorkflow}
                disabled={runningWorkflow}
                className="rounded bg-emerald-600 px-3 py-1 text-xs font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
              >
                {runningWorkflow ? "Running..." : "Run Full Workflow"}
              </button>
            )}
          </div>
          <span className={`rounded-full px-3 py-1 text-sm font-medium ${severityColor(incident.severity)}`}>
            {incident.severity}
          </span>
        </div>

        {triageError && (
          <div className="mb-4 rounded bg-red-50 p-3 text-sm text-red-600">{triageError}</div>
        )}

        <div className="mb-6 grid grid-cols-2 gap-4 text-sm">
          <div><span className="text-gray-400">Status:</span> <span className="font-medium">{incident.status}</span></div>
          <div><span className="text-gray-400">Created:</span> <span className="font-medium">{new Date(incident.created_at).toLocaleString()}</span></div>
        </div>

        {incident.description && (
          <div className="mb-6">
            <h2 className="mb-2 text-sm font-semibold text-gray-700">Description</h2>
            <p className="rounded bg-gray-50 p-3 text-sm text-gray-600">{incident.description}</p>
          </div>
        )}

        {incident.agent_summary && (
          <div className="rounded-lg border border-indigo-100 bg-indigo-50 p-4">
            <div className="mb-2 flex items-center gap-2">
              <span className="rounded bg-indigo-200 px-2 py-0.5 text-xs font-medium text-indigo-800">AI Analysis</span>
            </div>
            <p className="text-sm text-gray-700">{incident.agent_summary}</p>
          </div>
        )}
      </div>

      {/* Workflow Visualization */}
      <div className="mb-6 rounded-lg border bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Incident Workflow</h2>

        <div className="space-y-4">
          {workflowSteps.map((step, idx) => {
            const isLast = idx === workflowSteps.length - 1;
            return (
              <div key={step.node} className="relative">
                <div className="flex items-start gap-4">
                  <div className="flex flex-col items-center">
                    <div className={`flex h-8 w-8 items-center justify-center rounded-full border-2 text-xs font-bold ${
                      step.status === "done" ? "border-green-500 bg-green-50 text-green-600" :
                      step.status === "running" ? "border-blue-500 bg-blue-50 text-blue-600" :
                      step.status === "error" ? "border-red-500 bg-red-50 text-red-600" :
                      "border-gray-300 bg-white text-gray-400"
                    }`}>
                      {step.status === "running" ? (
                        <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                      ) : step.status === "done" ? (
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        idx + 1
                      )}
                    </div>
                    {!isLast && (
                      <div className={`h-8 w-0.5 ${
                        step.status === "done" ? "bg-green-300" : "bg-gray-200"
                      }`} />
                    )}
                  </div>
                  <div className="flex-1 pb-4">
                    <div className="font-medium text-gray-900">{NODE_LABELS[step.node] || step.node}</div>
                    {step.data && (
                      <div className="mt-2 rounded bg-gray-50 p-3 text-xs text-gray-600">
                        {step.node === "triage_node" && (
                          <div>
                            <div><span className="font-medium">Severity:</span> {step.data.severity}</div>
                            <div><span className="font-medium">Confidence:</span> {(step.data.triage_confidence * 100).toFixed(0)}%</div>
                            <div><span className="font-medium">Summary:</span> {step.data.triage_summary}</div>
                          </div>
                        )}
                        {step.node === "investigate_node" && (
                          <div>
                            <div><span className="font-medium">Root Cause:</span> {step.data.root_cause_hypothesis}</div>
                            <div><span className="font-medium">Confidence:</span> {(step.data.investigation_confidence * 100).toFixed(0)}%</div>
                            {step.data.affected_systems?.length > 0 && (
                              <div><span className="font-medium">Affected:</span> {step.data.affected_systems.join(", ")}</div>
                            )}
                          </div>
                        )}
                        {step.node === "remediate_node" && (
                          <div>
                            <div><span className="font-medium">Steps:</span> {step.data.remediation_steps?.length || 0}</div>
                            <div><span className="font-medium">Est. TTR:</span> {step.data.estimated_ttr}</div>
                            <div><span className="font-medium">Risk:</span> {step.data.risk_level}</div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {workflowResult && (
          <div className="mt-4 rounded-lg border border-emerald-100 bg-emerald-50 p-4">
            <div className="flex items-center gap-2">
              <svg className="h-5 w-5 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="font-medium text-emerald-800">Workflow Complete</span>
            </div>
            {workflowResult.remediation_steps?.length > 0 && (
              <div className="mt-2 space-y-1 text-sm text-emerald-700">
                {workflowResult.remediation_steps.map((step: any, i: number) => (
                  <div key={i} className="flex gap-2">
                    <span className="font-medium">{step.order}.</span>
                    <span>{step.action}</span>
                    <span className="text-emerald-500">({step.expected_duration})</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
