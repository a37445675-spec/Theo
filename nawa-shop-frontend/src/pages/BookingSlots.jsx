import { useState } from "react";
import { useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { useFetch } from "../hooks/useFetch.js";
import { getProduct } from "../api/catalog.js";
import * as bookingsApi from "../api/bookings.js";
import { extractErrorMessage } from "../api/client.js";
import { formatPrice } from "../utils.js";
import { EmptyState, ErrorState } from "../components/StateBlocks.jsx";
import { SkeletonGrid } from "../components/Skeleton.jsx";
import SEO from "../components/SEO.jsx";

export default function BookingSlots() {
  const { slug } = useParams();
  const { isAuthenticated } = useAuth();
  const { data: product, loading: productLoading } = useFetch(() => getProduct(slug), [slug]);
  const { data: slots, loading, error, refetch } = useFetch(() => bookingsApi.getSlots(product?.id), [product?.id]);
  const [bookingId, setBookingId] = useState(null);
  const [message, setMessage] = useState("");
  const [bookingError, setBookingError] = useState("");

  async function handleBook(slotId) {
    setBookingId(slotId);
    setBookingError("");
    try {
      await bookingsApi.bookSlot(slotId);
      setMessage("Réservation confirmée !");
      refetch();
    } catch (err) {
      setBookingError(extractErrorMessage(err));
    } finally {
      setBookingId(null);
    }
  }

  if (productLoading || (!product && !error)) return <div className="container" style={{ padding: "60px 0" }}><SkeletonGrid count={1} /></div>;

  return (
    <>
      <SEO title={`Réserver — ${product?.name || "Service"} — NAWA`} description="Réservez un créneau pour ce service NAWA." />

      <section className="page-header">
        <div className="container">
          <span className="eyebrow">Réservation</span>
          <h1>{product?.name}</h1>
          <p>{product?.shortDescription}</p>
          {product && <p className="product-price">{formatPrice(product.price, product.currency)}</p>}
        </div>
      </section>

      <section className="section">
        <div className="container">
          {!isAuthenticated && <p className="muted">Connectez-vous pour réserver un créneau.</p>}
          {message && <p className="newsletter-success">{message}</p>}
          {bookingError && <p className="promo-error">{bookingError}</p>}

          {loading && <SkeletonGrid count={3} />}
          {error && <ErrorState onRetry={refetch} />}
          {!loading && !error && (!slots || slots.length === 0) && <EmptyState icon="🗓️" title="Aucun créneau disponible pour le moment" />}
          {!loading && slots?.length > 0 && (
            <ul className="order-list" style={{ background: "var(--color-white)", borderRadius: 16, padding: 20, boxShadow: "var(--shadow-sm)" }}>
              {slots.map((slot) => (
                <li key={slot.id}>
                  <span>{new Date(slot.startAt).toLocaleString("fr-FR", { dateStyle: "full", timeStyle: "short" })}</span>
                  <span className="muted">{slot.durationMinutes} min</span>
                  <button className="btn btn-primary" disabled={!isAuthenticated || !slot.isAvailable || bookingId === slot.id} onClick={() => handleBook(slot.id)}>
                    {!slot.isAvailable ? "Complet" : bookingId === slot.id ? "Réservation…" : "Réserver"}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </>
  );
}
