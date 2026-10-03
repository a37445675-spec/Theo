import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { extractErrorMessage } from "../api/client.js";
import SEO from "../components/SEO.jsx";
import ButtonSpinner from "../components/ButtonSpinner.jsx";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await login(form.username, form.password);
      navigate(location.state?.from?.pathname || "/compte");
    } catch (err) {
      setError(extractErrorMessage(err, "Identifiants incorrects."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <SEO title="Connexion — NAWA" description="Connectez-vous à votre compte NAWA." />
      <section className="section auth-section">
        <div className="container auth-container">
          <h1 style={{ textAlign: "center", marginBottom: 24 }}>Connexion</h1>
          <form className="auth-form" onSubmit={handleSubmit}>
            {error && <p className="promo-error">{error}</p>}
            <label>Nom d'utilisateur<input required value={form.username} onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))} /></label>
            <label>Mot de passe<input required type="password" value={form.password} onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))} /></label>
            <button type="submit" className="btn btn-primary btn-block btn-lg" disabled={submitting}>{submitting ? <ButtonSpinner label="Connexion…" /> : "Se connecter"}</button>
          </form>
          <p className="muted" style={{ textAlign: "center", marginTop: 16 }}>
            Pas encore de compte ? <Link to="/inscription">Créer un compte</Link>
          </p>
        </div>
      </section>
    </>
  );
}
