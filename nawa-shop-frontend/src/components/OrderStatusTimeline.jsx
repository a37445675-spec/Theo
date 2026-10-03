import { formatDate } from "../utils.js";

const STEP_ICONS = { pending: "🕓", paid: "✓", processing: "📦", shipped: "🚚", delivered: "🏠", cancelled: "✕", refunded: "↩" };
const STEP_LABELS = {
  pending: "En attente de paiement", paid: "Paiement confirmé", processing: "En préparation",
  shipped: "Expédiée", delivered: "Livrée", cancelled: "Annulée", refunded: "Remboursée",
};

/** Suivi visuel animé de commande — chaque étape apparaît en cascade (CSS) plutôt qu'une simple liste plate. */
export default function OrderStatusTimeline({ history }) {
  if (!history || history.length === 0) return null;
  const chronological = [...history].reverse();

  return (
    <div className="order-timeline">
      {chronological.map((entry, i) => (
        <div className="order-timeline-step" key={i}>
          <span className="order-timeline-marker">{STEP_ICONS[entry.status] || "•"}</span>
          <div className="order-timeline-content">
            <strong>{STEP_LABELS[entry.status] || entry.status}</strong>
            <span className="muted">{formatDate(entry.createdAt)}</span>
            {entry.note && <p className="muted" style={{ margin: "4px 0 0" }}>{entry.note}</p>}
          </div>
        </div>
      ))}
    </div>
  );
}
