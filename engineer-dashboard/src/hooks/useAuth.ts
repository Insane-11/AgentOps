import { useState, useCallback, useEffect } from "react";
import { api } from "../api/client";

export function useAuth() {
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const saved = api.loadToken();
    if (saved) {
      setToken(saved);
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res = await api.login(email, password);
    api.setToken(res.access_token);
    setToken(res.access_token);
  }, []);

  const logout = useCallback(() => {
    api.setToken(null);
    setToken(null);
  }, []);

  return { token, loading, login, logout, isAuthenticated: !!token };
}
