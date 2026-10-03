import { useState } from "react";
import { client } from "../api/client.js";
import { useFetch } from "../hooks/useFetch.js";
import { formatDate, formatPrice } from "../utils.js";
import { ErrorState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";

const STATUS_OPTIONS = ["pending", "paid", "processing", "shipped", "delivered", "cancelled", "refunded"];

async function getManagedOrders() {
  const { data } = await client.get("/api/v1/orders/manage/");
  return data.results ?? data;
}

async function updateOrderStatus(id, status) {
  const { data } = await client.patch(`/api/v1/orders/manage/${id}/`, { status });
  return data;
}

export default function ManageOrders() {
  const { data: orders, loading, error, refetch } = useFetch(getManagedOrders, []);
  const [updating, setUpdating] = useState(null);

  async function handleStatusChange(order, status) {
    setUpdating(order.id);
    try {
      await updateOrderStatus(order.id, status);
      refetch();
    } finally {
      setUpdating(null);
    }
  }

  return (
    <>
      <SEO title="Gestion des commandes — NAWA" description="Back-office Shop Manager — gestion des commandes." />

      <section className="page-header">
        <div className="container">
          <span className="eyebrow">Back-office</span>
          <h1>Gestion des commandes</h1>
        </div>
      </section>

      <section className="section">
        <div className="container">
          {loading && <SkeletonGrid count={4} />}
          {error && <ErrorState onRetry={refetch} text="Accès réservé aux Shop Managers et administrateurs." />}
          {!loading && !error && orders?.length === 0 && <p className="muted">Aucune commande pour le moment.</p>}
          {!loading && orders?.length > 0 && (
            <ul className="order-list" style={{ background: "var(--color-white)", borderRadius: 16, padding: 20, boxShadow: "var(--shadow-sm)" }}>
              {orders.map((order) => (
                <li key={order.id}>
                  <span>{order.orderNumber}</span>
                  <span className="muted">{formatDate(order.createdAt)}</span>
                  <span className="muted">{order.salesChannel === "pos" ? "Magasin" : "En ligne"}</span>
                  <span>{formatPrice(order.total, order.currency)}</span>
                  <select value={order.status} disabled={updating === order.id} onChange={(e) => handleStatusChange(order, e.target.value)}>
                    {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </>
  );
}
