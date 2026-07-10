import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function NavBar() {
  const { user, logout } = useAuth();

  return (
    <header className="navbar">
      <div className="navbar-brand">Mental Health Tracker</div>
      <nav className="navbar-links">
        <NavLink to="/" end>
          Journals
        </NavLink>
        <NavLink to="/analytics">Analytics</NavLink>
      </nav>
      <div className="navbar-user">
        {user && (
          <>
            {user.avatar_url && <img className="avatar" src={user.avatar_url} alt={user.name} />}
            <span>{user.name}</span>
            <button className="btn btn-ghost" onClick={() => logout()}>
              Log out
            </button>
          </>
        )}
      </div>
    </header>
  );
}
