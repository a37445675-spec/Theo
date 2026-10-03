import { useState } from "react";
import * as authApi from "../api/auth.js";
import { useFetch } from "../hooks/useFetch.js";
import { extractErrorMessage } from "../api/client.js";
import { EmptyState, ErrorState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";

const emptyForm = { addressType: "shipping", fullName: "", line1: "", line2: "", city: "", postalCode: "", country: "CI", phone: "", isDefault: false };

export default function AccountAddresses() {
  const { data: addresses, loading, error, refetch } = useFetch(authApi.getAddresses, []);
  const [form, setForm] = useState(emptyForm);
  const [formError, setFormError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setFormError("");
    try {
      await authApi.createAddress(form);
      setForm(emptyForm);
      refetch();
    } catch (err) {
      setFormError(extractErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id) {
    await authApi.deleteAddress(id);
    refetch();
  }

  return (
    <>
      <SEO title="Mes adresses — NAWA" description="Gérez vos adresses de livraison et de facturation." />
      <section className="page-header"><div className="container"><h1>Mes adresses</h1></div></section>

      <section className="section">
        <div className="container account-dashboard">
          <div className="account-card">
            <h2>Adresses enregistrées</h2>
            {loading && <SkeletonGrid count={2} />}
            {error && <ErrorState onRetry={refetch} />}
            {!loading && !error && (!addresses || addresses.length === 0) && <EmptyState icon="📍" title="Aucune adresse enregistrée" />}
            {!loading && addresses?.map((addr) => (
              <div key={addr.id} className="producer-mini">
                <strong>{addr.fullName}</strong> ({addr.addressType === "shipping" ? "Livraison" : "Facturation"}{addr.isDefault ? ", par défaut" : ""})
                <div>{addr.line1}{addr.line2 ? `, ${addr.line2}` : ""}</div>
                <div>{addr.postalCode} {addr.city}, {addr.country}</div>
                <button className="btn btn-ghost" style={{ marginTop: 8 }} onClick={() => handleDelete(addr.id)}>Supprimer</button>
              </div>
            ))}
          </div>

          <div className="account-card">
            <h2>Ajouter une adresse</h2>
            <form className="auth-form" onSubmit={handleSubmit}>
              {formError && <p className="promo-error">{formError}</p>}
              <label>
                Type
                <select value={form.addressType} onChange={(e) => update("addressType", e.target.value)}>
                  <option value="shipping">Livraison</option>
                  <option value="billing">Facturation</option>
                </select>
              </label>
              <label>Nom complet<input required value={form.fullName} onChange={(e) => update("fullName", e.target.value)} /></label>
              <label>Adresse<input required value={form.line1} onChange={(e) => update("line1", e.target.value)} /></label>
              <label>Ville<input required value={form.city} onChange={(e) => update("city", e.target.value)} /></label>
              <label>Code postal<input required value={form.postalCode} onChange={(e) => update("postalCode", e.target.value)} /></label>
              <label>
                Pays
                <select value={form.country} onChange={(e) => update("country", e.target.value)}>
                  <option value="CI">Côte d'Ivoire</option>
                  <option value="SN">Sénégal</option>
                  <option value="FR">France</option>
                </select>
              </label>
              <label style={{ flexDirection: "row", alignItems: "center", gap: 10 }}>
                <input type="checkbox" checked={form.isDefault} onChange={(e) => update("isDefault", e.target.checked)} style={{ width: "auto" }} />
                Adresse par défaut
              </label>
              <button type="submit" className="btn btn-primary" disabled={submitting}>{submitting ? "Ajout…" : "Ajouter"}</button>
            </form>
          </div>
        </div>
      </section>
    </>
  );
}
