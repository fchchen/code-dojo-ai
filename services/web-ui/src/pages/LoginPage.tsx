import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

interface LoginPageProps {
  onLogin: (username: string) => Promise<void>;
  loading: boolean;
  error: string | null;
}

export function LoginPage({ onLogin, loading, error }: LoginPageProps) {
  const navigate = useNavigate();
  const [username, setUsername] = useState("demo");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await onLogin(username);
      navigate("/");
    } catch {
      // Error state is owned by useAuth; keep user on login page.
    }
  }

  return (
    <div className="app-shell">
      <div className="card" style={{ maxWidth: "520px", margin: "8vh auto" }}>
        <h1 className="title">Welcome to Code Dojo AI</h1>
        <p className="small">Sign in with a demo username to start coaching sessions.</p>
        <form onSubmit={handleSubmit}>
          <label className="label" htmlFor="username">
            Username
          </label>
          <input
            id="username"
            className="input"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
          />
          <div style={{ height: "8px" }} />
          {error ? <div className="error">{error}</div> : null}
          <div style={{ height: "12px" }} />
          <button className="btn" type="submit" disabled={loading || username.trim().length === 0}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}
