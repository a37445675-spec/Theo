import { useFetch } from "../hooks/useFetch.js";
import { getMyLoyalty } from "../api/loyalty.js";
import { formatDate } from "../utils.js";
import { EmptyState, ErrorState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";
import LoyaltyProgress from "../components/LoyaltyProgress.jsx";

export default function AccountLoyalty() {
  const { data, loading, error, refetch } = useFetch(getMyLoyalty, []);

  return (
    <>
      <SEO title="Fidélité — NAWA" description="Votre solde et historique de points de fidélité." />
      <section className="page-header"><div className="container"><h1>Fidélité</h1></div></section>

      <section className="section">
        <div className="container">
          {loading && <SkeletonGrid count={1} />}
          {error && <ErrorState onRetry={refetch} />}
          {!loading && !error && data && (
            <>
              <div className="account-card" style={{ marginBottom: 24, maxWidth: 400 }}>
                <LoyaltyProgress points={data.points} tier={data.tier} />
              </div>

              {data.transactions.length === 0 ? (
                <EmptyState icon="🎁" title="Aucun mouvement de points pour le moment" />
              ) : (
                <ul className="order-list" style={{ background: "var(--color-white)", borderRadius: 16, padding: 20, boxShadow: "var(--shadow-sm)" }}>
                  {data.transactions.map((t, i) => (
                    <li key={i}>
                      <span>{t.reason}</span>
                      <span className="muted">{formatDate(t.createdAt)}</span>
                      <span style={{ color: t.points > 0 ? "var(--color-forest)" : "var(--color-terracotta)", fontWeight: 700 }}>{t.points > 0 ? `+${t.points}` : t.points}</span>
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}
        </div>
      </section>
    </>
  );
}
