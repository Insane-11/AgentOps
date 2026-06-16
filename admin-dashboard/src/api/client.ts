const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem("agentops_token", token);
    } else {
      localStorage.removeItem("agentops_token");
    }
  }

  loadToken(): string | null {
    const saved = localStorage.getItem("agentops_token");
    if (saved) this.token = saved;
    return this.token;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }

    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(`API ${res.status}: ${body}`);
    }
    return res.json();
  }

  login(email: string, password: string) {
    return this.request<{ access_token: string; role: string }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  getIncidents() {
    return this.request<any[]>("/api/incidents");
  }

  getIncident(id: string) {
    return this.request<any>(`/api/incidents/${id}`);
  }

  createIncident(data: { title: string; description?: string; severity?: string }) {
    return this.request<any>("/api/incidents", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  getEngineers() {
    return this.request<any[]>("/api/engineers");
  }

  getEngineer(id: string) {
    return this.request<any>(`/api/engineers/${id}`);
  }

  createEngineer(data: { name: string; email: string; password: string; role?: string }) {
    return this.request<any>("/api/engineers", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  createAlert(data: { title: string; description?: string; severity?: string }) {
    return this.request<any>("/api/alerts", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  runTriage(incidentId: string) {
    return this.request<any>(`/api/triage/run/${incidentId}`, {
      method: "POST",
    });
  }

  runWorkflow(incidentId: string, onEvent: (data: any) => void, onResult: (data: any) => void): AbortController {
    const controller = new AbortController();
    const token = this.token;
    const baseUrl = API_BASE;

    (async () => {
      try {
        const res = await fetch(`${baseUrl}/api/workflow/run/${incidentId}`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}`, Accept: "text/event-stream" },
          signal: controller.signal,
        });
        const reader = res.body!.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let currentEvent = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";
          for (const line of lines) {
            const t = line.trim();
            if (t.startsWith("event:")) { currentEvent = t.slice(6).trim(); }
            else if (t.startsWith("data:")) {
              try {
                const p = JSON.parse(t.slice(5).trim());
                currentEvent === "result" ? onResult(p) : onEvent(p);
              } catch {}
              currentEvent = "";
            }
          }
        }
      } catch (err: any) {
        if (err.name !== "AbortError") console.error("SSE error:", err);
      }
    })();
    return controller;
  }
}

export const api = new ApiClient();
