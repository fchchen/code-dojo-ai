import { useMemo, useState } from "react";
import { getDemoToken } from "../api/client";

const TOKEN_KEY = "code-dojo-token";
const USERNAME_KEY = "code-dojo-username";

export function useAuth() {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY));
  const [username, setUsername] = useState<string | null>(() => localStorage.getItem(USERNAME_KEY));
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isAuthenticated = useMemo(() => Boolean(token), [token]);

  async function login(nextUsername: string) {
    setLoading(true);
    setError(null);
    try {
      const response = await getDemoToken(nextUsername);
      localStorage.setItem(TOKEN_KEY, response.token);
      localStorage.setItem(USERNAME_KEY, response.username);
      setToken(response.token);
      setUsername(response.username);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      throw err;
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USERNAME_KEY);
    setToken(null);
    setUsername(null);
  }

  return { token, username, isAuthenticated, loading, error, login, logout };
}
