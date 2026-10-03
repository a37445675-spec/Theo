/**
 * Phase 11 — Widgets Commerce (7 composants).
 * Panier, checkout, compte, résumé.
 */
import { apiFetch } from "../../utils/apiClient";
import React from "react";
import { Link } from "react-router-dom";
import { useCurrentProduct, useCartData, useProducts, formatPrice } from "../hooks/useProductContext";

// ============================================================
//  CART — Panier complet
// ============================================================

export const Cart = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Mon panier" },
    showContinue: {
      type: "radio", label: "Bouton continuer",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: { title: "Mon panier", showContinue: "true" },
  render: ({ title, showContinue }) => {
    const { cart, loading, refresh } = useCartData();

    if (loading) return <div style={{ padding: "2rem", textAlign: "center", color: "#888" }}>Chargement...</div>;

    const lines = cart?.lines || [];
    const subtotal = cart?.subtotal || "0.00";

    if (!lines.length) {
      return (
        <div style={{ padding: "3rem", textAlign: "center", background: "#F7F0E4", borderRadius: "16px" }}>
          <div style={{ fontSize: "3rem", marginBottom: "12px" }}>🛍</div>
          <h3>{title} est vide</h3>
          <p style={{ color: "#6B6259", marginBottom: "20px" }}>Découvrez notre sélection.</p>
          <Link to="/boutique/cosmetiques" className="btn btn-primary">Découvrir la boutique</Link>
        </div>
      );
    }

    return (
      <div>
        <h2>{title} ({lines.length})</h2>
        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "24px", marginTop: "20px" }}>
          <div>
            {lines.map((line) => (
              <div key={line.id} style={{
                display: "flex", gap: "16px", padding: "16px",
                background: "#fff", borderRadius: "12px", marginBottom: "12px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
              }}>
                <div style={{ width: 80, height: 80, borderRadius: "8px", overflow: "hidden", background: "#f5f5f5", flexShrink: 0 }}>
                  <img
                    src={line.image_url || "/fallbacks/product-fallback.jpg"}
                    alt={line.product_name}
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600 }}>{line.product_name}</div>
                  <div style={{ fontSize: "0.85rem", color: "#6B6259" }}>Quantité : {line.quantity}</div>
                  <div style={{ fontWeight: 700, color: "#C1652F", marginTop: "6px" }}>
                    {formatPrice(line.unit_price || line.price, cart.currency)}
                  </div>
                </div>
                <button
                  onClick={async () => {
                    await fetch(`/api/v1/cart/lines/${line.id}/`, { method: "DELETE", credentials: "include" });
                    refresh();
                  }}
                  style={{ background: "none", border: "none", cursor: "pointer", color: "#DC2626", fontSize: "1.2rem" }}
                >×</button>
              </div>
            ))}
            {showContinue === "true" && (
              <Link to="/boutique/cosmetiques" style={{ color: "#C1652F", fontWeight: 600 }}>
                ← Continuer mes achats
              </Link>
            )}
          </div>
          <div style={{ background: "#F7F0E4", padding: "24px", borderRadius: "16px", alignSelf: "start" }}>
            <h3>Sous-total</h3>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "16px", fontSize: "1.2rem", fontWeight: 700 }}>
              <span>Total</span>
              <span>{formatPrice(subtotal, cart.currency)}</span>
            </div>
            <Link to="/commande" className="btn btn-primary btn-lg" style={{ display: "block", textAlign: "center", width: "100%" }}>
              Passer commande
            </Link>
          </div>
        </div>
      </div>
    );
  },
};

// ============================================================
//  CHECKOUT — Tunnel de commande (info)
// ============================================================

export const Checkout = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Finaliser la commande" },
  },
  defaultProps: { title: "Finaliser la commande" },
  render: ({ title }) => {
    const { cart } = useCartData();
    const total = cart?.subtotal || "0.00";

    return (
      <div style={{ maxWidth: "600px", margin: "0 auto" }}>
        <h2>{title}</h2>
        <div style={{ background: "#F7F0E4", padding: "24px", borderRadius: "16px", marginTop: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px" }}>
            <span>Sous-total</span>
            <span>{formatPrice(total, cart?.currency || "EUR")}</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", paddingTop: "12px", borderTop: "1px solid #ddd", fontWeight: 700, fontSize: "1.15rem" }}>
            <span>Total</span>
            <span>{formatPrice(total, cart?.currency || "EUR")}</span>
          </div>
        </div>
        <Link to="/commande" className="btn btn-primary btn-lg" style={{ display: "block", textAlign: "center", marginTop: "20px" }}>
          Continuer vers le paiement
        </Link>
      </div>
    );
  },
};

// ============================================================
//  PURCHASE SUMMARY — Récap commande
// ============================================================

export const PurchaseSummary = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Récapitulatif" },
  },
  defaultProps: { title: "Récapitulatif" },
  render: ({ title }) => {
    const { cart } = useCartData();
    const lines = cart?.lines || [];
    const subtotal = cart?.subtotal || "0.00";

    return (
      <div style={{ background: "#fff", padding: "24px", borderRadius: "16px", boxShadow: "0 2px 12px rgba(0,0,0,0.06)" }}>
        <h3>{title}</h3>
        <ul style={{ listStyle: "none", padding: 0, margin: "16px 0" }}>
          {lines.map((l) => (
            <li key={l.id} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #eee" }}>
              <span>{l.product_name} × {l.quantity}</span>
              <span>{formatPrice((l.unit_price || 0) * l.quantity, cart.currency)}</span>
            </li>
          ))}
        </ul>
        <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700, fontSize: "1.1rem" }}>
          <span>Total</span>
          <span>{formatPrice(subtotal, cart?.currency || "EUR")}</span>
        </div>
      </div>
    );
  },
};

// ============================================================
//  MY ACCOUNT — Espace client
// ============================================================

export const MyAccount = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Mon compte" },
  },
  defaultProps: { title: "Mon compte" },
  render: ({ title }) => (
    <div style={{ maxWidth: "800px", margin: "0 auto" }}>
      <h2>{title}</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px", marginTop: "20px" }}>
        {[
          { to: "/compte", label: "Profil", icon: "👤" },
          { to: "/compte/commandes", label: "Commandes", icon: "📦" },
          { to: "/compte/fidelite", label: "Fidélité", icon: "🎁" },
          { to: "/compte/adresses", label: "Adresses", icon: "📍" },
          { to: "/compte/factures", label: "Factures", icon: "🧾" },
          { to: "/compte/abonnements", label: "Abonnements", icon: "🔄" },
        ].map((item) => (
          <Link
            key={item.to}
            to={item.to}
            style={{
              display: "block", padding: "24px", background: "#F7F0E4",
              borderRadius: "16px", textDecoration: "none", color: "#221B15", textAlign: "center",
            }}
          >
            <div style={{ fontSize: "2rem", marginBottom: "8px" }}>{item.icon}</div>
            <div style={{ fontWeight: 600 }}>{item.label}</div>
          </Link>
        ))}
      </div>
    </div>
  ),
};

// ============================================================
//  WC BREADCRUMBS (déjà couvert par Breadcrumbs, version commerce)
// ============================================================

export const WcBreadcrumbs = {
  fields: {
    homeLabel: { type: "text", label: "Accueil", defaultValue: "Accueil" },
    shopLabel: { type: "text", label: "Boutique", defaultValue: "Boutique" },
  },
  defaultProps: { homeLabel: "Accueil", shopLabel: "Boutique" },
  render: ({ homeLabel, shopLabel }) => {
    const { product } = useCurrentProduct();
    const path = window.location.pathname;

    let crumbs = [{ label: homeLabel, to: "/" }, { label: shopLabel, to: "/boutique" }];
    if (path.includes("/boutique/")) {
      const cat = path.split("/boutique/")[1].split("/")[0];
      crumbs.push({ label: cat.replace(/-/g, " "), to: null });
    } else if (path.includes("/produit/")) {
      if (product?.category) {
        crumbs.push({ label: product.category.name, to: `/boutique/${product.category.slug}` });
      }
      crumbs.push({ label: product?.name || "Produit", to: null });
    }

    return (
      <nav style={{ fontSize: "0.85rem", color: "#6B6259", marginBottom: "16px" }}>
        {crumbs.map((c, i) => (
          <React.Fragment key={i}>
            {i > 0 && <span style={{ margin: "0 8px" }}>/</span>}
            {c.to ? (
              <Link to={c.to} style={{ color: "#6B6259", textDecoration: "none" }}>{c.label}</Link>
            ) : (
              <span style={{ color: "#C1652F", fontWeight: 600 }}>{c.label}</span>
            )}
          </React.Fragment>
        ))}
      </nav>
    );
  },
};

// ============================================================
//  MENU CART ÉTENDU (basé sur CartContext)
// ============================================================

export const MenuCartExtended = {
  fields: {
    iconLabel: { type: "text", label: "Icône", defaultValue: "🛒" },
    showItems: {
      type: "radio", label: "Afficher les articles",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: { iconLabel: "🛒", showItems: "true" },
  render: ({ iconLabel, showItems }) => {
    const { cart, loading } = useCartData();
    const [open, setOpen] = React.useState(false);
    const lines = cart?.lines || [];
    const totalItems = lines.reduce((acc, l) => acc + (l.quantity || 0), 0);

    return (
      <div
        style={{ position: "relative", display: "inline-block" }}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
      >
        <button style={{ position: "relative", background: "none", border: "none", cursor: "pointer", fontSize: "1.5rem", padding: "8px" }}>
          {iconLabel}
          {totalItems > 0 && (
            <span style={{
              position: "absolute", top: 0, right: 0,
              background: "#C1652F", color: "#fff", fontSize: "10px", fontWeight: 700,
              minWidth: "18px", height: "18px", borderRadius: "999px",
              display: "inline-flex", alignItems: "center", justifyContent: "center", padding: "0 4px",
            }}>
              {totalItems}
            </span>
          )}
        </button>

        {open && showItems === "true" && (
          <div style={{
            position: "absolute", top: "100%", right: 0, width: "320px",
            background: "#fff", borderRadius: "12px",
            boxShadow: "0 10px 40px rgba(0,0,0,0.15)", padding: "16px",
            zIndex: 100, marginTop: "8px",
          }}>
            {loading ? (
              <div style={{ color: "#888", textAlign: "center", padding: "1rem" }}>Chargement...</div>
            ) : lines.length === 0 ? (
              <div style={{ textAlign: "center", color: "#888", padding: "1rem" }}>Panier vide</div>
            ) : (
              <>
                {lines.slice(0, 3).map((l) => (
                  <div key={l.id} style={{ display: "flex", gap: "12px", padding: "8px 0", borderBottom: "1px solid #eee" }}>
                    <div style={{ width: 50, height: 50, borderRadius: "6px", overflow: "hidden", background: "#f5f5f5" }}>
                      <img src={l.image_url || "/fallbacks/product-fallback.jpg"} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                    </div>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: "0.9rem", fontWeight: 600 }}>{l.product_name}</div>
                      <div style={{ fontSize: "0.8rem", color: "#6B6259" }}>× {l.quantity}</div>
                    </div>
                    <div style={{ fontWeight: 600, fontSize: "0.9rem" }}>
                      {formatPrice((l.unit_price || 0) * l.quantity, cart.currency)}
                    </div>
                  </div>
                ))}
                <div style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
                  <Link to="/panier" className="btn btn-ghost" style={{ flex: 1, textAlign: "center", padding: "8px", textDecoration: "none" }}>Voir</Link>
                  <Link to="/commande" className="btn btn-primary" style={{ flex: 1, textAlign: "center", padding: "8px", textDecoration: "none" }}>Commander</Link>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    );
  },
};
