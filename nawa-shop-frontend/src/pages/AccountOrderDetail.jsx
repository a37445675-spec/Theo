import { useParams } from "react-router-dom";
import { useFetch } from "../hooks/useFetch.js";
import { getOrder } from "../api/orders.js";
import { formatDate, formatPrice } from "../utils.js";
import { ErrorState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";
import OrderStatusTimeline from "../components/OrderStatusTimeline.jsx";

export default function AccountOrderDetail() {
  const { id } = useParams();
  const { data: order, loading, error, refetch } = useFetch(() => getOrder(id), [id]);

  if (loading) return <div className="container" style={{ padding: "60px 0" }}><SkeletonGrid count={1} /></div>;
  if (error || !order) return <div className="container" style={{ padding: "60px 0" }}><ErrorState title="Commande introuvable" onRetry={refetch} /></div>;

  return (
    <>
      <SEO title={`Commande ${order.orderNumber} — NAWA`} description="Détail de votre commande." />

      <section className="page-header">
        <div className="container">
          <h1>Commande {order.orderNumber}</h1>
          <p className="muted">Passée le {formatDate(order.createdAt)} · {order.salesChannel === "pos" ? "Achat en magasin" : "Achat en ligne"}</p>
        </div>
      </section>

      <section className="section">
        <div className="container cart-layout">
          <div className="cart-items">
            {order.items.map((item) => (
              <div className="cart-row" key={item.id}>
                <div className="cart-row-info">
                  <span>{item.productNameSnapshot}</span>
                  <span className="muted">SKU {item.skuSnapshot} · Qté {item.quantity}</span>
                </div>
                <span className="cart-row-total">{formatPrice(item.lineTotal, order.currency)}</span>
              </div>
            ))}

            <h2 style={{ marginTop: 32 }}>Suivi de commande</h2>
            <OrderStatusTimeline history={order.statusHistory} />
          </div>

          <div className="cart-summary">
            <h2>Résumé</h2>
            <div className="summary-line"><span>Sous-total</span><span>{formatPrice(order.subtotal, order.currency)}</span></div>
            <div className="summary-line"><span>Remise</span><span>-{formatPrice(order.discountTotal, order.currency)}</span></div>
            <div className="summary-line"><span>Livraison</span><span>{formatPrice(order.shippingTotal, order.currency)}</span></div>
            <div className="summary-line"><span>Taxe</span><span>{formatPrice(order.taxTotal, order.currency)}</span></div>
            <div className="summary-line total"><span>Total</span><span>{formatPrice(order.total, order.currency)}</span></div>
            {order.balanceDue > 0 && <div className="summary-line"><span>Solde dû (acompte)</span><span>{formatPrice(order.balanceDue, order.currency)}</span></div>}
          </div>
        </div>
      </section>
    </>
  );
}
