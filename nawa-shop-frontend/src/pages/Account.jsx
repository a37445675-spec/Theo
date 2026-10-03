import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import SEO from "../components/SEO.jsx";
import LoyaltyProgress from "../components/LoyaltyProgress.jsx";

export default function Account() {
  const { user, isVendor, updateProfile, logout } = useAuth();
  const [form, setForm] = useState({ firstName: user?.firstName || "", lastName: user?.lastName || "", phone: user?.phone || "" });
  const [saved, setSaved] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    await updateProfile(form);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <>
      <SEO title="Mon compte — NAWA" description="Gérez votre profil NAWA." />

      <section className="page-header">
        <div className="container">
          <h1>Bonjour {user?.firstName || user?.username} 👋</h1>
          <button className="btn btn-ghost" onClick={logout}>Se déconnecter</button>
        </div>
      </section>

      <section className="section">
        <div className="container account-dashboard">
          <div className="account-card">
            <h2>Mon profil</h2>
            <form className="auth-form" onSubmit={handleSubmit}>
              <label>Prénom<input value={form.firstName} onChange={(e) => setForm((f) => ({ ...f, firstName: e.target.value }))} /></label>
              <label>Nom<input value={form.lastName} onChange={(e) => setForm((f) => ({ ...f, lastName: e.target.value }))} /></label>
              <label>Téléphone<input value={form.phone} onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))} /></label>
              <button type="submit" className="btn btn-primary">Enregistrer</button>
              {saved && <p className="newsletter-success">Profil mis à jour ✓</p>}
            </form>
          </div>

          <div className="account-card">
            <h2>Fidélité</h2>
            <LoyaltyProgress points={user?.loyaltyPoints ?? 0} tier={user?.loyaltyTier ?? "bronze"} />
            <Link to="/compte/fidelite" className="link-arrow">Voir l'historique →</Link>
          </div>

          <div className="account-card">
            <h2>Commandes</h2>
            <p className="muted">Consultez l'historique de vos commandes.</p>
            <Link to="/compte/commandes" className="link-arrow">Voir mes commandes →</Link>
          </div>

          <div className="account-card">
            <h2>Abonnements</h2>
            <p className="muted">Gérez vos rituels récurrents et leurs remises.</p>
            <Link to="/compte/abonnements" className="link-arrow">Voir mes abonnements →</Link>
          </div>

          <div className="account-card">
            <h2>Factures</h2>
            <p className="muted">Téléchargez vos factures NAWA.</p>
            <Link to="/compte/factures" className="link-arrow">Voir mes factures →</Link>
          </div>

          <div className="account-card">
            <h2>Adresses</h2>
            <p className="muted">Gérez vos adresses de livraison et de facturation.</p>
            <Link to="/compte/adresses" className="link-arrow">Gérer mes adresses →</Link>
          </div>

          {isVendor && (
            <div className="account-card">
              <h2>Espace vendeur</h2>
              <p className="muted">Compte vendeur activé — la gestion de vos produits se fait depuis l'admin NAWA.</p>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
