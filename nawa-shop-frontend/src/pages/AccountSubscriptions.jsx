import { useState } from "react";
import { useFetch } from "../hooks/useFetch.js";
import * as subsApi from "../api/subscriptions.js";
import { EmptyState, ErrorState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";

const FREQUENCIES = [
  { value: 30, label: "Tous les 30 jours" }, { value: 45, label: "Tous les 45 jours" },
  { value: 60, label: "Tous les 60 jours" }, { value: 90, label: "Tous les 90 jours" },
];

export default function AccountSubscriptions() {
  const { data: subscriptions, loading, error, refetch } = useFetch(subsApi.getSubscriptions, []);
  const [updating, setUpdating] = useState(null);

  async function handleFrequencyChange(sub, frequencyDays) {
    setUpdating(sub.id);
    try {
      await subsApi.updateSubscription(sub.id, { frequencyDays });
      refetch();
    } finally {
      setUpdating(null);
    }
  }

  async function handleToggleActive(sub) {
    setUpdating(sub.id);
    try {
      await subsApi.updateSubscription(sub.id, { active: !sub.active });
      refetch();
    } finally {
      setUpdating(null);
    }
  }

  async function handleDelete(sub) {
    setUpdating(sub.id);
    try {
      await subsApi.deleteSubscription(sub.id);
      refetch();
    } finally {
      setUpdating(null);
    }
  }

  return (
    <>
      <SEO title="Mes abonnements — NAWA" description="Gérez vos rituels récurrents NAWA." />
      <section className="page-header">
        <div className="container">
          <h1>Mes abonnements</h1>
          <p className="muted">Recevez vos produits favoris automatiquement, avec une remise fidélité.</p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          {loading && <SkeletonGrid count={2} />}
          {error && <ErrorState onRetry={refetch} />}
          {!loading && !error && (!subscriptions || subscriptions.length === 0) && (
            <EmptyState icon="🔁" title="Aucun abonnement actif" action={<p className="muted">Activez un abonnement depuis la fiche d'un produit éligible.</p>} />
          )}
          {!loading && subscriptions?.length > 0 && (
            <div className="account-dashboard">
              {subscriptions.map((sub) => (
                <div className="account-card" key={sub.id}>
                  <h2>{sub.productName}</h2>
                  <p className="muted">Remise fidélité : -{sub.discountPercent}%</p>
                  <label>
                    Fréquence
                    <select value={sub.frequencyDays} disabled={updating === sub.id} onChange={(e) => handleFrequencyChange(sub, Number(e.target.value))}>
                      {FREQUENCIES.map((f) => <option key={f.value} value={f.value}>{f.label}</option>)}
                    </select>
                  </label>
                  <p className="muted">Prochaine livraison : {sub.nextDeliveryDate}</p>
                  <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                    <button className="btn btn-ghost" disabled={updating === sub.id} onClick={() => handleToggleActive(sub)}>{sub.active ? "Suspendre" : "Réactiver"}</button>
                    <button className="btn btn-ghost" disabled={updating === sub.id} onClick={() => handleDelete(sub)}>Supprimer</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
