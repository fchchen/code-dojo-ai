import { Link } from "react-router-dom";

interface NavbarProps {
  username: string | null;
  onLogout: () => void;
}

export function Navbar({ username, onLogout }: NavbarProps) {
  return (
    <div className="nav">
      <div className="brand">Code Dojo AI</div>
      <div className="nav-links">
        <Link to="/">Submit</Link>
        <Link to="/history">History</Link>
        <span className="small">{username ?? "anonymous"}</span>
        <button className="btn secondary" onClick={onLogout} type="button">
          Logout
        </button>
      </div>
    </div>
  );
}
