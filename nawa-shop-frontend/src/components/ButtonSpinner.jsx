/** Petit spinner animé pour remplacer un texte "…" figé dans les boutons en cours de chargement (feedback CX plus lisible). */
export default function ButtonSpinner({ label }) {
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
      <span className="btn-spinner" /> {label}
    </span>
  );
}
