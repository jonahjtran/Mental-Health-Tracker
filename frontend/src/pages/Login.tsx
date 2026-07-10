import { GOOGLE_LOGIN_URL } from "../api/client";

export function Login() {
  return (
    <div className="centered-page">
      <div className="card login-card">
        <h1>Mental Health Tracker</h1>
        <p>Sign in to view your journals, insights, and mood analytics.</p>
        <a className="btn btn-primary" href={GOOGLE_LOGIN_URL}>
          Sign in with Google
        </a>
      </div>
    </div>
  );
}
