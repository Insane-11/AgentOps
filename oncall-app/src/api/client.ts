import AsyncStorage from "@react-native-async-storage/async-storage";

const API_BASE = process.env.EXPO_PUBLIC_API_BASE || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  async loadToken(): Promise<string | null> {
    const saved = await AsyncStorage.getItem("agentops_token");
    if (saved) this.token = saved;
    return this.token;
  }

  async setToken(token: string | null) {
    this.token = token;
    if (token) {
      await AsyncStorage.setItem("agentops_token", token);
    } else {
      await AsyncStorage.removeItem("agentops_token");
    }
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

  async getIncidents(): Promise<any[]> {
    const resp = await this.request<{ items: any[] }>("/api/incidents?per_page=100");
    return resp.items;
  }

  getIncident(id: string) {
    return this.request<any>(`/api/incidents/${id}`);
  }

  updateIncident(id: string, data: any) {
    return this.request<any>(`/api/incidents/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  acknowledgeIncident(id: string) {
    return this.updateIncident(id, { status: "INVESTIGATING" });
  }

  escalateIncident(id: string) {
    return this.updateIncident(id, { severity: "CRITICAL" });
  }

  resolveIncident(id: string) {
    return this.updateIncident(id, { status: "RESOLVED" });
  }
}

export const api = new ApiClient();
