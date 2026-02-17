import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { useAuth } from "./hooks/useAuth";
import { HistoryPage } from "./pages/HistoryPage";
import { LoginPage } from "./pages/LoginPage";
import { SubmitPage } from "./pages/SubmitPage";

interface AuthState {
  token: string | null;
  username: string | null;
  isAuthenticated: boolean;
  logout: () => void;
}

function AuthenticatedApp({ auth }: { auth: AuthState }) {
  const location = useLocation();

  if (!auth.isAuthenticated || !auth.token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return (
    <>
      <div className="app-shell">
        <Navbar username={auth.username} onLogout={auth.logout} />
      </div>
      <Routes>
        <Route path="/" element={<SubmitPage token={auth.token} />} />
        <Route path="/history" element={<HistoryPage token={auth.token} />} />
      </Routes>
    </>
  );
}

export default function App() {
  const auth = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={<LoginPage onLogin={auth.login} loading={auth.loading} error={auth.error} />}
      />
      <Route
        path="/*"
        element={
          <AuthenticatedApp
            auth={{
              token: auth.token,
              username: auth.username,
              isAuthenticated: auth.isAuthenticated,
              logout: auth.logout,
            }}
          />
        }
      />
    </Routes>
  );
}
