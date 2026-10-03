import { Link } from "react-router-dom";
import { useFetch } from "../hooks/useFetch.js";
import { getOrders } from "../api/orders.js";
import { formatDate, formatPrice } from "../utils.js";
import { EmptyState, ErrorState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";

const STATUS_LABELS = {
  pending: "En attente de paiement", paid: "Payée", processing: "En préparation",
  shipped: "Expédiée", delivered: "Livrée", cancelled: "Annulée", refunded: "Remboursée",
};

export default function AccountOrders() {
  const { data: orders, loading, error, refetch } = useFetch(getOrders, []);

  return (
    <>
      <SEO title="Mes commandes — NAWA" description="Historique de vos commandes NAWA." />
      <section className="page-header"><div className="container"><h1>Mes commandes</h1></div></section>

      <section className="section">
        <div className="container">
          {loading && <SkeletonGrid count={3} />}
          {error && <ErrorState onRetry={refetch} />}
          {!loading && !error && (!orders || orders.length === 0) && (
            <EmptyState icon="📦" title="Aucune commande pour le moment" action={<Link to="/boutique/cosmetiques" className="btn btn-primary">Découvrir la boutique</Link>} />
          )}
          {!loading && !error && orders?.length > 0 && (
            <ul className="order-list" style={{ background: "var(--color-white)", borderRadius: 16, padding: 20, boxShadow: "var(--shadow-sm)" }}>
              {orders.map((order) => (
                <li key={order.id}>
                  <Link to={`/compte/commandes/${order.id}`}>{order.orderNumber}</Link>
                  <span className="muted">{formatDate(order.createdAt)}</span>
                  <span className="muted">{STATUS_LABELS[order.status] || order.status}</span>
                  <span>{formatPrice(order.total, order.currency)}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </>
  );
}
