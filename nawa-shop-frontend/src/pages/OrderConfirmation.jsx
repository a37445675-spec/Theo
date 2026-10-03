import { Link, useLocation, useParams } from "react-router-dom";
import { useFetch } from "../hooks/useFetch.js";
import { getOrder } from "../api/orders.js";
import { formatPrice } from "../utils.js";
import { ErrorState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";
import OrderStatusTimeline from "../components/OrderStatusTimeline.jsx";

export default function OrderConfirmation() {
  const { id } = useParams();
  const location = useLocation();
  const preloaded = location.state?.order;

  const { data: fetched, loading, error, refetch } = useFetch(() => getOrder(id), [id]);
  const order = preloaded && String(preloaded.id) === String(id) ? preloaded : fetched;

  if (!preloaded && loading) return <div className="container" style={{ padding: "60px 0" }}><SkeletonGrid count={1} /></div>;
  if (!preloaded && (error || !order)) {
    return <div className="container" style={{ padding: "60px 0" }}><ErrorState title="Commande introuvable" onRetry={refetch} /></div>;
  }

  const isSimulatedPayment = order.status === "pending";

  return (
    <>
      <SEO title="Commande confirmée — NAWA" description="Récapitulatif de votre commande NAWA." />

      <section className="section">
        <div className="container confirmation-inner">
          <span className="state-icon">{isSimulatedPayment ? "⏳" : "✅"}</span>
          <h1>Commande {order.orderNumber}</h1>

          {isSimulatedPayment ? (
            <p className="muted">
              Votre commande est enregistrée et en attente de confirmation de paiement. En environnement de
              démonstration (sans clé Stripe configurée), le paiement est simulé : c'est la réception du
              webhook Stripe (<code>payment_intent.succeeded</code>) qui fait basculer la commande en "Payée" —
              en développement, un gestionnaire peut la faire passer manuellement via l'admin.
            </p>
          ) : (
            <p className="muted">Merci pour votre commande ! Un email de confirmation vous a été envoyé.</p>
          )}

          {order.statusHistory?.length > 0 && (
            <div style={{ textAlign: "left", maxWidth: 420, margin: "24px auto 0" }}>
              <OrderStatusTimeline history={order.statusHistory} />
            </div>
          )}

          <div className="cart-summary" style={{ textAlign: "left", marginTop: 24 }}>
            {order.items?.map((item) => (
              <div className="summary-line" key={item.id}>
                <span>{item.quantity} × {item.productNameSnapshot}</span>
                <span>{formatPrice(item.lineTotal, order.currency)}</span>
              </div>
            ))}
            <div className="summary-line total"><span>Total</span><span>{formatPrice(order.total, order.currency)}</span></div>
          </div>

          <Link to="/compte/commandes" className="btn btn-primary" style={{ marginTop: 24 }}>Voir mes commandes</Link>
        </div>
      </section>
    </>
  );
}
