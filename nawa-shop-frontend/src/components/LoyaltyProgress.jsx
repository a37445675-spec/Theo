const TIERS = [
  { key: "bronze", label: "Bronze", threshold: 0 },
  { key: "silver", label: "Argent", threshold: 100 },
  { key: "gold", label: "Or", threshold: 300 },
];

/** Barre de progression animée vers le palier de fidélité suivant — rend visible ce qu'un simple nombre de points ne dit pas. */
export default function LoyaltyProgress({ points, tier }) {
  const currentIndex = TIERS.findIndex((t) => t.key === tier);
  const current = TIERS[currentIndex] || TIERS[0];
  const next = TIERS[currentIndex + 1];

  const progress = next
    ? Math.min(100, Math.round(((points - current.threshold) / (next.threshold - current.threshold)) * 100))
    : 100;

  return (
    <div className="loyalty-progress">
      <span className={`loyalty-tier-badge loyalty-tier-${tier}`}>★ {current.label}</span>
      <div className="loyalty-progress-track" style={{ marginTop: 10 }}>
        <div className="loyalty-progress-fill" style={{ width: `${progress}%` }} />
      </div>
      <div className="loyalty-progress-labels">
        <span>{points} pts</span>
        <span>{next ? `${next.threshold - points > 0 ? next.threshold - points : 0} pts avant ${next.label}` : "Palier maximum atteint"}</span>
      </div>
    </div>
  );
}
