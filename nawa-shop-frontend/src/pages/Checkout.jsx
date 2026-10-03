import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import { useCart } from "../context/CartContext.jsx";
import { checkout } from "../api/checkout.js";
import { validateCoupon } from "../api/promotions.js";
import { extractErrorMessage } from "../api/client.js";
import { formatPrice } from "../utils.js";
import SEO from "../components/SEO.jsx";
import ButtonSpinner from "../components/ButtonSpinner.jsx";

const initialAddress = { fullName: "", line1: "", line2: "", city: "", postalCode: "", country: "CI", phone: "" };

export default function Checkout() {
  const { user, isAuthenticated } = useAuth();
  const { cart, refresh } = useCart();
  const navigate = useNavigate();

  const [address, setAddress] = useState(initialAddress);
  const [guestEmail, setGuestEmail] = useState("");
  const [couponCode, setCouponCode] = useState("");
  const [couponResult, setCouponResult] = useState(null);
  const [couponError, setCouponError] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function update(field, value) {
    setAddress((a) => ({ ...a, [field]: value }));
  }

  async function handleApplyCoupon() {
    if (!couponCode || !cart) return;
    setCouponError("");
    try {
      const result = await validateCoupon(couponCode, cart.subtotal);
      setCouponResult(result);
    } catch (err) {
      setCouponResult(null);
      setCouponError(extractErrorMessage(err, "Code promo invalide."));
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const { order } = await checkout({
        shippingAddress: address,
        billingAddress: address,
        guestEmail: isAuthenticated ? undefined : guestEmail,
        couponCode: couponResult ? couponCode : undefined,
      });
      await refresh();
      navigate(`/commande/confirmation/${order.orderNumber}`, { state: { order } });
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  if (!cart || cart.lines.length === 0) {
    return (
      <div className="container" style={{ padding: "80px 0", textAlign: "center" }}>
        <p>Votre panier est vide.</p>
      </div>
    );
  }

  return (
    <>
      <SEO title="Commande — NAWA" description="Finalisez votre commande NAWA." />

      <section className="page-header">
        <div className="container"><h1>Finaliser la commande</h1></div>
      </section>

      <section className="section">
        <div className="container cart-layout">
          <form className="checkout-form cart-items" onSubmit={handleSubmit}>
            {error && <p className="promo-error">{error}</p>}

            {!isAuthenticated && (
              <>
                <h2>Contact</h2>
                <div className="form-grid">
                  <label className="span-2">Email<input type="email" required value={guestEmail} onChange={(e) => setGuestEmail(e.target.value)} /></label>
                </div>
              </>
            )}

            <h2>Adresse de livraison</h2>
            <div className="form-grid">
              <label className="span-2">Nom complet<input required value={address.fullName} onChange={(e) => update("fullName", e.target.value)} /></label>
              <label className="span-2">Adresse<input required value={address.line1} onChange={(e) => update("line1", e.target.value)} /></label>
              <label className="span-2">Complément (optionnel)<input value={address.line2} onChange={(e) => update("line2", e.target.value)} /></label>
              <label>Ville<input required value={address.city} onChange={(e) => update("city", e.target.value)} /></label>
              <label>Code postal<input required value={address.postalCode} onChange={(e) => update("postalCode", e.target.value)} /></label>
              <label>
                Pays
                <select value={address.country} onChange={(e) => update("country", e.target.value)}>
                  <option value="CI">Côte d'Ivoire</option>
                  <option value="SN">Sénégal</option>
                  <option value="FR">France</option>
                  <option value="BE">Belgique</option>
                </select>
              </label>
              <label>Téléphone<input value={address.phone} onChange={(e) => update("phone", e.target.value)} /></label>
            </div>

            <button type="submit" className="btn btn-primary btn-lg btn-block" disabled={submitting}>
              {submitting ? <ButtonSpinner label="Traitement…" /> : `Payer ${formatPrice(cart.subtotal, cart.currency)}`}
            </button>
          </form>

          <div className="cart-summary">
            <h2>Résumé</h2>
            {cart.lines.map((line) => (
              <div className="summary-line" key={line.id}>
                <span>{line.quantity} × {line.product.name}</span>
                <span>{formatPrice(line.lineTotal, cart.currency)}</span>
              </div>
            ))}

            <div className="promo-row" style={{ display: "flex", gap: 8, margin: "16px 0" }}>
              <input placeholder="Code promo" value={couponCode} onChange={(e) => setCouponCode(e.target.value)} />
              <button type="button" className="btn btn-ghost" onClick={handleApplyCoupon}>Appliquer</button>
            </div>
            {couponError && <p className="promo-error">{couponError}</p>}
            {couponResult && <p className="promo-success">Remise appliquée : -{formatPrice(couponResult.computedDiscount, cart.currency)}</p>}

            <div className="summary-line total">
              <span>Total estimé</span>
              <span>{formatPrice(couponResult ? cart.subtotal - couponResult.computedDiscount : cart.subtotal, cart.currency)}</span>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
