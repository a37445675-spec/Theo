import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { extractErrorMessage } from "../api/client.js";
import SEO from "../components/SEO.jsx";
import ButtonSpinner from "../components/ButtonSpinner.jsx";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "", firstName: "", lastName: "", isVendor: false });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await register(form);
      navigate("/compte");
    } catch (err) {
      setError(extractErrorMessage(err, "L'inscription a échoué."));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <SEO title="Créer un compte — NAWA" description="Créez votre compte NAWA." />
      <section className="section auth-section">
        <div className="container auth-container">
          <h1 style={{ textAlign: "center", marginBottom: 24 }}>Créer un compte</h1>
          <form className="auth-form" onSubmit={handleSubmit}>
            {error && <p className="promo-error">{error}</p>}
            <label>Prénom<input value={form.firstName} onChange={(e) => update("firstName", e.target.value)} /></label>
            <label>Nom<input value={form.lastName} onChange={(e) => update("lastName", e.target.value)} /></label>
            <label>Nom d'utilisateur<input required value={form.username} onChange={(e) => update("username", e.target.value)} /></label>
            <label>Email<input required type="email" value={form.email} onChange={(e) => update("email", e.target.value)} /></label>
            <label>Mot de passe<input required type="password" minLength={8} value={form.password} onChange={(e) => update("password", e.target.value)} /></label>
            <label style={{ flexDirection: "row", alignItems: "center", gap: 10 }}>
              <input type="checkbox" checked={form.isVendor} onChange={(e) => update("isVendor", e.target.checked)} style={{ width: "auto" }} />
              Je souhaite aussi vendre sur NAWA (compte vendeur)
            </label>
            <button type="submit" className="btn btn-primary btn-block btn-lg" disabled={submitting}>{submitting ? <ButtonSpinner label="Création…" /> : "Créer mon compte"}</button>
          </form>
          <p className="muted" style={{ textAlign: "center", marginTop: 16 }}>
            Déjà inscrit·e ? <Link to="/connexion">Se connecter</Link>
          </p>
        </div>
      </section>
    </>
  );
}
