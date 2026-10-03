"""
Phase 9 — Widgets Marketing & Social (13 widgets).

Usage : python inject_phase9.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
WIDGETS_DIR = os.path.join(SRC_DIR, "puck", "widgets")


# ============================================================
#         MARKETING (Facebook + Paiement) — 6 widgets
# ============================================================

MARKETING_WIDGETS_JSX = '''/**
 * Phase 9 — Widgets Marketing (6 composants).
 * Facebook (page, bouton, embed, commentaires) + PayPal + Stripe.
 *
 * Les SDK sont chargés à la demande et une seule fois.
 */
import React from "react";

// ============================================================
//  LOADERS INTELLIGENTS
// ============================================================

let fbLoaded = false;
function ensureFacebookSDK(appId = "") {
  if (fbLoaded || typeof document === "undefined") return;
  if (document.getElementById("facebook-jssdk")) {
    fbLoaded = true;
    return;
  }
  const script = document.createElement("script");
  script.id = "facebook-jssdk";
  script.async = true;
  script.defer = true;
  script.crossOrigin = "anonymous";
  script.src = "https://connect.facebook.net/fr_FR/sdk.js#xfbml=1&version=v18.0" +
    (appId ? `&appId=${appId}` : "");
  document.body.appendChild(script);
  fbLoaded = true;
}

let stripeLoaded = false;
function ensureStripeSDK() {
  if (stripeLoaded || typeof document === "undefined") return;
  if (document.querySelector("script[data-stripe]")) {
    stripeLoaded = true;
    return;
  }
  const script = document.createElement("script");
  script.src = "https://js.stripe.com/v3/";
  script.async = true;
  script.setAttribute("data-stripe", "true");
  document.head.appendChild(script);
  stripeLoaded = true;
}

let paypalLoaded = false;
function ensurePayPalSDK(clientId = "test") {
  if (paypalLoaded || typeof document === "undefined") return;
  if (document.querySelector("script[data-paypal]")) {
    paypalLoaded = true;
    return;
  }
  const script = document.createElement("script");
  script.src = `https://www.paypal.com/sdk/js?client-id=${clientId}&currency=EUR`;
  script.async = true;
  script.setAttribute("data-paypal", "true");
  document.head.appendChild(script);
  paypalLoaded = true;
}

// ============================================================
//  FACEBOOK PAGE — Page Facebook embarquée
// ============================================================

export const FacebookPage = {
  fields: {
    pageUrl: { type: "text", label: "URL de la page Facebook" },
    width: { type: "number", label: "Largeur (px)", defaultValue: 340 },
    height: { type: "number", label: "Hauteur (px)", defaultValue: 500 },
    tabs: {
      type: "select",
      label: "Onglets",
      options: [
        { label: "Timeline", value: "timeline" },
        { label: "Messages", value: "messages" },
        { label: "Événements", value: "events" },
      ],
    },
    hideCover: {
      type: "radio", label: "Masquer la couverture",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    showFacepile: {
      type: "radio", label: "Afficher les visages",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
  },
  defaultProps: {
    pageUrl: "https://www.facebook.com/facebook",
    width: 340, height: 500, tabs: "timeline",
    hideCover: "false", showFacepile: "true",
  },
  render: ({ pageUrl, width, height, tabs, hideCover, showFacepile }) => {
    React.useEffect(() => {
      ensureFacebookSDK();
      const timer = setTimeout(() => {
        if (window.FB && window.FB.XFBML) window.FB.XFBML.parse();
      }, 600);
      return () => clearTimeout(timer);
    }, [pageUrl, width, height, tabs, hideCover, showFacepile]);

    return (
      <div className="fb-page-wrapper" style={{ display: "flex", justifyContent: "center" }}>
        <div
          className="fb-page"
          data-href={pageUrl}
          data-tabs={tabs}
          data-width={width}
          data-height={height}
          data-small-header="false"
          data-adapt-container-width="true"
          data-hide-cover={hideCover}
          data-show-facepile={showFacepile}
        >
          <blockquote cite={pageUrl} className="fb-xfbml-parse-ignore">
            <a href={pageUrl}>NAWA sur Facebook</a>
          </blockquote>
        </div>
      </div>
    );
  },
};

// ============================================================
//  FACEBOOK BUTTON — Bouton J'aime / Partager
// ============================================================

export const FacebookButton = {
  fields: {
    url: { type: "text", label: "URL de la page à liker" },
    layout: {
      type: "select", label: "Mise en page",
      options: [
        { label: "Standard", value: "standard" },
        { label: "Bouton", value: "button_count" },
        { label: "Box", value: "box_count" },
      ],
    },
    action: {
      type: "select", label: "Action",
      options: [
        { label: "J'aime", value: "like" },
        { label: "Recommander", value: "recommend" },
      ],
    },
    size: {
      type: "select", label: "Taille",
      options: [
        { label: "Petit", value: "small" },
        { label: "Grand", value: "large" },
      ],
    },
  },
  defaultProps: {
    url: "https://www.facebook.com/facebook",
    layout: "button_count", action: "like", size: "small",
  },
  render: ({ url, layout, action, size }) => {
    React.useEffect(() => {
      ensureFacebookSDK();
      const timer = setTimeout(() => {
        if (window.FB && window.FB.XFBML) window.FB.XFBML.parse();
      }, 600);
      return () => clearTimeout(timer);
    }, [url, layout, action, size]);

    return (
      <div
        className="fb-like"
        data-href={url}
        data-width=""
        data-layout={layout}
        data-action={action}
        data-size={size}
        data-share="true"
      />
    );
  },
};

// ============================================================
//  FACEBOOK EMBED — Post Facebook
// ============================================================

export const FacebookEmbed = {
  fields: {
    postUrl: { type: "text", label: "URL du post Facebook" },
    width: { type: "number", label: "Largeur (px)", defaultValue: 500 },
  },
  defaultProps: {
    postUrl: "https://www.facebook.com/facebook/posts/10160012256004248",
    width: 500,
  },
  render: ({ postUrl, width }) => {
    React.useEffect(() => {
      ensureFacebookSDK();
      const timer = setTimeout(() => {
        if (window.FB && window.FB.XFBML) window.FB.XFBML.parse();
      }, 600);
      return () => clearTimeout(timer);
    }, [postUrl, width]);

    return (
      <div style={{ display: "flex", justifyContent: "center" }}>
        <div
          className="fb-post"
          data-href={postUrl}
          data-width={width}
          data-show-text="true"
        />
      </div>
    );
  },
};

// ============================================================
//  FACEBOOK COMMENTS — Commentaires Facebook
// ============================================================

export const FacebookComments = {
  fields: {
    url: { type: "text", label: "URL de la page" },
    numPosts: { type: "number", label: "Nombre de commentaires", defaultValue: 5 },
    orderBy: {
      type: "select", label: "Tri",
      options: [
        { label: "Social", value: "social" },
        { label: "Chronologique", value: "time" },
        { label: "Inverse", value: "reverse_time" },
      ],
    },
  },
  defaultProps: {
    url: "https://www.facebook.com/facebook",
    numPosts: 5, orderBy: "social",
  },
  render: ({ url, numPosts, orderBy }) => {
    React.useEffect(() => {
      ensureFacebookSDK();
      const timer = setTimeout(() => {
        if (window.FB && window.FB.XFBML) window.FB.XFBML.parse();
      }, 600);
      return () => clearTimeout(timer);
    }, [url, numPosts, orderBy]);

    return (
      <div
        className="fb-comments"
        data-href={url}
        data-width="100%"
        data-numposts={numPosts}
        data-order-by={orderBy}
      />
    );
  },
};

// ============================================================
//  PAYPAL BUTTON — Bouton PayPal (sandbox par défaut)
// ============================================================

export const PayPalButton = {
  fields: {
    clientId: {
      type: "text", label: "Client ID PayPal",
      defaultValue: "test",
    },
    amount: { type: "text", label: "Montant", defaultValue: "29.90" },
    currency: { type: "text", label: "Devise", defaultValue: "EUR" },
    description: { type: "text", label: "Description", defaultValue: "Commande NAWA" },
  },
  defaultProps: {
    clientId: "test", amount: "29.90",
    currency: "EUR", description: "Commande NAWA",
  },
  render: ({ clientId, amount, currency, description }) => {
    const containerRef = React.useRef(null);

    React.useEffect(() => {
      ensurePayPalSDK(clientId);
      const interval = setInterval(() => {
        if (window.paypal && containerRef.current && !containerRef.current.hasChildNodes()) {
          window.paypal.Buttons({
            createOrder: (data, actions) => actions.order.create({
              purchase_units: [{ amount: { value: amount, currency_code: currency }, description }],
            }),
            onApprove: (data, actions) => actions.order.capture().then(() => {
              alert(`✅ Paiement PayPal simulé : ${amount} ${currency}`);
            }),
          }).render(containerRef.current);
          clearInterval(interval);
        }
      }, 300);
      return () => clearInterval(interval);
    }, [clientId, amount, currency, description]);

    return (
      <div style={{ padding: "16px", background: "#F7F0E4", borderRadius: "12px" }}>
        <div style={{ fontSize: "0.75rem", color: "#D4A843", fontWeight: 700, marginBottom: "8px" }}>
          MODE TEST
        </div>
        <div ref={containerRef} />
      </div>
    );
  },
};

// ============================================================
//  STRIPE BUTTON — Bouton Stripe (mode test)
// ============================================================

export const StripeButton = {
  fields: {
    publishableKey: {
      type: "text", label: "Clé publique Stripe (pk_test_...)",
      defaultValue: "pk_test_demo",
    },
    priceId: {
      type: "text", label: "Price ID (price_...)",
      defaultValue: "price_demo",
    },
    amount: { type: "text", label: "Montant affiché", defaultValue: "29.90 €" },
    label: { type: "text", label: "Texte du bouton", defaultValue: "Payer maintenant" },
  },
  defaultProps: {
    publishableKey: "pk_test_demo",
    priceId: "price_demo",
    amount: "29.90 €",
    label: "Payer maintenant",
  },
  render: ({ publishableKey, priceId, amount, label }) => {
    React.useEffect(() => { ensureStripeSDK(); }, []);

    const handleClick = async () => {
      if (!window.Stripe) {
        alert("Stripe n'est pas encore chargé. Réessayez.");
        return;
      }
      if (!publishableKey || !publishableKey.startsWith("pk_")) {
        alert("Configurez une clé publique Stripe (pk_test_...) dans le widget.");
        return;
      }
      try {
        const stripe = window.Stripe(publishableKey);
        // Simule un checkout en mode test (pas de serveur requis)
        alert(`✅ Paiement Stripe simulé : ${amount}\\n\\nPrice ID : ${priceId}\\n\\nEn production, un appel API créerait une session Checkout.`);
      } catch (err) {
        alert(`Erreur Stripe : ${err.message}`);
      }
    };

    return (
      <div style={{ padding: "16px" }}>
        <button
          onClick={handleClick}
          className="btn btn-primary btn-lg"
          style={{ width: "100%" }}
        >
          💳 {label} — {amount}
        </button>
        <div style={{ fontSize: "0.7rem", color: "#D4A843", marginTop: "8px", textAlign: "center", fontWeight: 600 }}>
          MODE TEST
        </div>
      </div>
    );
  },
};
'''


# ============================================================
#    SOCIAL (Menu + Partage + Popups) — 7 widgets
# ============================================================

SOCIAL_WIDGETS_JSX = '''/**
 * Phase 9 — Widgets Social (7 composants).
 * Mega menu, off-canvas, mini panier, partage, WhatsApp, popups, cookies.
 */
import React from "react";

function splitLines(text) {
  return String(text || "").split("\\n").map((s) => s.trim()).filter(Boolean);
}

// ============================================================
//  MEGA MENU — Menu déroulant riche
// ============================================================

export const MegaMenu = {
  fields: {
    title: { type: "text", label: "Titre du menu", defaultValue: "Catégories" },
    columns: {
      type: "textarea",
      label: "Colonnes (titre|item1,item2,item3 — un par ligne)",
      defaultValue: "Cosmétiques|Karité,Cheveux,Visage,Corps\\nMode|Robes,Wax,Boubou,Homme\\nMaison|Cuisine,Salle de bain,Électro",
    },
  },
  defaultProps: {
    title: "Catégories",
    columns: "Cosmétiques|Karité,Cheveux,Visage,Corps\\nMode|Robes,Wax,Boubou,Homme\\nMaison|Cuisine,Salle de bain,Électro",
  },
  render: ({ title, columns }) => {
    const cols = splitLines(columns).map((line) => {
      const [colTitle, items] = line.split("|");
      return {
        title: colTitle.trim(),
        items: (items || "").split(",").map((i) => i.trim()),
      };
    });
    const [open, setOpen] = React.useState(false);

    return (
      <div
        style={{ position: "relative", display: "inline-block" }}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
      >
        <button
          style={{
            padding: "10px 20px",
            background: "#C1652F",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          {title} ▾
        </button>
        {open && (
          <div
            style={{
              position: "absolute",
              top: "100%",
              left: 0,
              background: "#fff",
              boxShadow: "0 10px 40px rgba(0,0,0,0.15)",
              borderRadius: "12px",
              padding: "24px",
              display: "grid",
              gridTemplateColumns: `repeat(${Math.min(cols.length, 3)}, minmax(180px, 1fr))`,
              gap: "24px",
              zIndex: 100,
              minWidth: "500px",
              marginTop: "8px",
            }}
          >
            {cols.map((col, i) => (
              <div key={i}>
                <div
                  style={{
                    fontWeight: 700,
                    marginBottom: "12px",
                    color: "#C1652F",
                    fontSize: "0.85rem",
                    textTransform: "uppercase",
                  }}
                >
                  {col.title}
                </div>
                <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
                  {col.items.map((item, j) => (
                    <li key={j} style={{ marginBottom: "8px" }}>
                      <a
                        href="#"
                        style={{
                          color: "#221B15",
                          textDecoration: "none",
                          fontSize: "0.9rem",
                        }}
                      >
                        {item}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  },
};

// ============================================================
//  OFF-CANVAS — Panneau latéral
// ============================================================

export const OffCanvas = {
  fields: {
    buttonLabel: { type: "text", label: "Texte du bouton", defaultValue: "Ouvrir" },
    title: { type: "text", label: "Titre du panneau", defaultValue: "À propos" },
    content: {
      type: "textarea",
      label: "Contenu",
      defaultValue: "Bienvenue chez NAWA, la marketplace qui sublime la beauté d'Afrique.",
    },
    position: {
      type: "select", label: "Position",
      options: [
        { label: "Gauche", value: "left" },
        { label: "Droite", value: "right" },
      ],
    },
    bgColor: { type: "text", label: "Couleur de fond", defaultValue: "#F7F0E4" },
  },
  defaultProps: {
    buttonLabel: "Ouvrir",
    title: "À propos",
    content: "Bienvenue chez NAWA, la marketplace qui sublime la beauté d'Afrique.",
    position: "right",
    bgColor: "#F7F0E4",
  },
  render: ({ buttonLabel, title, content, position, bgColor }) => {
    const [open, setOpen] = React.useState(false);
    const sideStyle = position === "left" ? { left: 0 } : { right: 0 };
    const transformOpen = position === "left" ? "translateX(0)" : "translateX(0)";
    const transformClosed = position === "left" ? "translateX(-100%)" : "translateX(100%)";

    return (
      <>
        <button
          onClick={() => setOpen(true)}
          style={{
            padding: "10px 20px",
            background: "#C1652F",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          {buttonLabel}
        </button>

        {open && (
          <div
            onClick={() => setOpen(false)}
            style={{
              position: "fixed",
              inset: 0,
              background: "rgba(0,0,0,0.5)",
              zIndex: 9998,
            }}
          />
        )}

        <div
          style={{
            position: "fixed",
            top: 0,
            bottom: 0,
            ...sideStyle,
            width: "min(400px, 90vw)",
            background: bgColor,
            zIndex: 9999,
            padding: "32px",
            transform: open ? transformOpen : transformClosed,
            transition: "transform 0.3s ease",
            boxShadow: "0 0 40px rgba(0,0,0,0.15)",
          }}
        >
          <button
            onClick={() => setOpen(false)}
            style={{
              position: "absolute",
              top: 16,
              right: 16,
              background: "none",
              border: "none",
              fontSize: "1.5rem",
              cursor: "pointer",
              color: "#221B15",
            }}
          >
            ×
          </button>
          <h2 style={{ marginBottom: "16px" }}>{title}</h2>
          <p style={{ lineHeight: 1.7, color: "#6B6259" }}>{content}</p>
        </div>
      </>
    );
  },
};

// ============================================================
//  MENU CART — Mini panier déroulant
// ============================================================

export const MenuCart = {
  fields: {
    iconLabel: { type: "text", label: "Icône", defaultValue: "🛒" },
    showBadge: {
      type: "radio", label: "Afficher le badge",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
  },
  defaultProps: { iconLabel: "🛒", showBadge: "true" },
  render: ({ iconLabel, showBadge }) => {
    const [open, setOpen] = React.useState(false);
    // Données de démonstration (à remplacer par useCart() si disponible)
    const items = [
      { name: "Beurre de Karité Pur", qty: 1, price: "14.90" },
      { name: "Huile de Baobab", qty: 2, price: "19.90" },
    ];
    const total = items
      .reduce((acc, it) => acc + Number(it.price) * it.qty, 0)
      .toFixed(2);

    return (
      <div
        style={{ position: "relative", display: "inline-block" }}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
      >
        <button
          style={{
            position: "relative",
            background: "none",
            border: "none",
            cursor: "pointer",
            fontSize: "1.5rem",
            padding: "8px",
          }}
        >
          {iconLabel}
          {showBadge === "true" && items.length > 0 && (
            <span
              style={{
                position: "absolute",
                top: 0,
                right: 0,
                background: "#C1652F",
                color: "#fff",
                fontSize: "10px",
                fontWeight: 700,
                minWidth: "18px",
                height: "18px",
                borderRadius: "999px",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                padding: "0 4px",
              }}
            >
              {items.length}
            </span>
          )}
        </button>

        {open && (
          <div
            style={{
              position: "absolute",
              top: "100%",
              right: 0,
              width: "320px",
              background: "#fff",
              borderRadius: "12px",
              boxShadow: "0 10px 40px rgba(0,0,0,0.15)",
              padding: "16px",
              zIndex: 100,
              marginTop: "8px",
            }}
          >
            <div style={{ fontWeight: 700, marginBottom: "12px" }}>
              Mon panier ({items.length})
            </div>
            {items.map((item, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  padding: "8px 0",
                  borderBottom: "1px solid #eee",
                  fontSize: "0.9rem",
                }}
              >
                <div>
                  {item.name}
                  <div style={{ fontSize: "0.8rem", color: "#888" }}>
                    × {item.qty}
                  </div>
                </div>
                <div style={{ fontWeight: 600 }}>
                  {(Number(item.price) * item.qty).toFixed(2)} €
                </div>
              </div>
            ))}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginTop: "12px",
                paddingTop: "12px",
                borderTop: "1px solid #ddd",
                fontWeight: 700,
              }}
            >
              <span>Total</span>
              <span>{total} €</span>
            </div>
            <div style={{ display: "flex", gap: "8px", marginTop: "12px" }}>
              <a
                href="/panier"
                className="btn btn-ghost"
                style={{ flex: 1, textAlign: "center", padding: "8px", textDecoration: "none" }}
              >
                Voir
              </a>
              <a
                href="/commande"
                className="btn btn-primary"
                style={{ flex: 1, textAlign: "center", padding: "8px", textDecoration: "none" }}
              >
                Commander
              </a>
            </div>
          </div>
        )}
      </div>
    );
  },
};

// ============================================================
//  SOCIAL SHARE — Partage avancé (étendu)
// ============================================================

export const SocialShareExtended = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Partager cet article" },
    url: { type: "text", label: "URL à partager (vide = URL actuelle)" },
    message: { type: "text", label: "Message à partager", defaultValue: "Découvrez NAWA !" },
    style: {
      type: "radio", label: "Style",
      options: [
        { label: "Boutons", value: "buttons" },
        { label: "Icônes rondes", value: "circles" },
      ],
    },
  },
  defaultProps: {
    title: "Partager cet article",
    url: "",
    message: "Découvrez NAWA !",
    style: "circles",
  },
  render: ({ title, url, message, style }) => {
    const shareUrl = url || (typeof window !== "undefined" ? window.location.href : "");
    const encodedUrl = encodeURIComponent(shareUrl);
    const encodedMsg = encodeURIComponent(message);

    const networks = [
      { name: "Facebook", href: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`, emoji: "📘", color: "#1877F2" },
      { name: "Twitter / X", href: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedMsg}`, emoji: "𝕏", color: "#000" },
      { name: "WhatsApp", href: `https://wa.me/?text=${encodedMsg}%20${encodedUrl}`, emoji: "💬", color: "#25D366" },
      { name: "LinkedIn", href: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`, emoji: "💼", color: "#0A66C2" },
      { name: "Email", href: `mailto:?subject=${encodedMsg}&body=${encodedUrl}`, emoji: "✉️", color: "#6B6259" },
    ];

    if (style === "buttons") {
      return (
        <div>
          <div style={{ fontWeight: 600, marginBottom: "12px" }}>{title}</div>
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            {networks.map((n) => (
              <a
                key={n.name}
                href={n.href}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  padding: "10px 16px",
                  background: n.color,
                  color: "#fff",
                  borderRadius: "8px",
                  textDecoration: "none",
                  fontSize: "0.9rem",
                  fontWeight: 600,
                }}
              >
                {n.emoji} {n.name}
              </a>
            ))}
          </div>
        </div>
      );
    }

    return (
      <div>
        <div style={{ fontWeight: 600, marginBottom: "12px" }}>{title}</div>
        <div style={{ display: "flex", gap: "8px" }}>
          {networks.map((n) => (
            <a
              key={n.name}
              href={n.href}
              target="_blank"
              rel="noopener noreferrer"
              title={n.name}
              style={{
                width: 44,
                height: 44,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: n.color,
                color: "#fff",
                borderRadius: "50%",
                textDecoration: "none",
                fontSize: "1.1rem",
                boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
              }}
            >
              {n.emoji}
            </a>
          ))}
        </div>
      </div>
    );
  },
};

// ============================================================
//  WHATSAPP FLOAT — Bouton flottant
// ============================================================

export const WhatsAppFloat = {
  fields: {
    phone: { type: "text", label: "Numéro (format international, ex: 2250700000000)" },
    message: { type: "text", label: "Message pré-rempli", defaultValue: "Bonjour NAWA !" },
    position: {
      type: "select", label: "Position",
      options: [
        { label: "Bas droite", value: "bottom-right" },
        { label: "Bas gauche", value: "bottom-left" },
      ],
    },
    showLabel: {
      type: "radio", label: "Afficher le texte",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
  },
  defaultProps: {
    phone: "2250700000000",
    message: "Bonjour NAWA !",
    position: "bottom-right",
    showLabel: "true",
  },
  render: ({ phone, message, position, showLabel }) => {
    const href = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
    const posStyle = position === "bottom-left"
      ? { left: 20 }
      : { right: 20 };

    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          position: "fixed",
          bottom: 20,
          ...posStyle,
          background: "#25D366",
          color: "#fff",
          padding: showLabel === "true" ? "12px 20px" : "12px",
          borderRadius: "999px",
          display: "flex",
          alignItems: "center",
          gap: "8px",
          textDecoration: "none",
          fontWeight: 600,
          boxShadow: "0 4px 16px rgba(37,211,102,0.4)",
          zIndex: 9997,
          fontSize: "0.95rem",
        }}
      >
        <span style={{ fontSize: "1.3rem" }}>💬</span>
        {showLabel === "true" && <span>Discutons sur WhatsApp</span>}
      </a>
    );
  },
};

// ============================================================
//  NEWSLETTER POPUP — Popup d'inscription
// ============================================================

export const NewsletterPopup = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Rejoignez NAWA" },
    subtitle: {
      type: "text",
      label: "Sous-titre",
      defaultValue: "Recevez 10% sur votre première commande",
    },
    buttonLabel: { type: "text", label: "Bouton", defaultValue: "Je m'inscris" },
    delaySeconds: { type: "number", label: "Délai (secondes)", defaultValue: 5 },
    formSlug: { type: "text", label: "Slug du formulaire", defaultValue: "newsletter" },
  },
  defaultProps: {
    title: "Rejoignez NAWA",
    subtitle: "Recevez 10% sur votre première commande",
    buttonLabel: "Je m'inscris",
    delaySeconds: 5,
    formSlug: "newsletter",
  },
  render: ({ title, subtitle, buttonLabel, delaySeconds, formSlug }) => {
    const [visible, setVisible] = React.useState(false);
    const [email, setEmail] = React.useState("");
    const [done, setDone] = React.useState(false);

    React.useEffect(() => {
      if (typeof window === "undefined") return;
      const dismissed = localStorage.getItem("nawa_newsletter_dismissed");
      if (dismissed) return;
      const timer = setTimeout(() => setVisible(true), delaySeconds * 1000);
      return () => clearTimeout(timer);
    }, [delaySeconds]);

    const dismiss = () => {
      localStorage.setItem("nawa_newsletter_dismissed", "1");
      setVisible(false);
    };

    const submit = async (e) => {
      e.preventDefault();
      if (!email) return;
      try {
        const res = await fetch("/api/v1/forms/definitions/" + formSlug + "/");
        const form = await res.json();
        await fetch("/api/v1/forms/submissions/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ form: form.id, data: { email } }),
        });
      } catch (err) {
        // Silencieux : on confirme quand même pour ne pas bloquer l'UX
      }
      setDone(true);
      setTimeout(dismiss, 2500);
    };

    if (!visible) return null;

    return (
      <div
        onClick={dismiss}
        style={{
          position: "fixed",
          inset: 0,
          background: "rgba(0,0,0,0.6)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 9999,
        }}
      >
        <div
          onClick={(e) => e.stopPropagation()}
          style={{
            background: "#fff",
            borderRadius: "24px",
            padding: "40px",
            maxWidth: "500px",
            width: "90%",
            position: "relative",
            textAlign: "center",
          }}
        >
          <button
            onClick={dismiss}
            style={{
              position: "absolute",
              top: 12,
              right: 16,
              background: "none",
              border: "none",
              fontSize: "1.5rem",
              cursor: "pointer",
              color: "#888",
            }}
          >
            ×
          </button>

          {done ? (
            <div>
              <div style={{ fontSize: "3rem", marginBottom: "12px" }}>✅</div>
              <h3>Merci !</h3>
              <p style={{ color: "#6B6259" }}>Votre inscription a bien été prise en compte.</p>
            </div>
          ) : (
            <>
              <h2 style={{ marginBottom: "8px" }}>{title}</h2>
              <p style={{ color: "#6B6259", marginBottom: "24px" }}>{subtitle}</p>
              <form onSubmit={submit} style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                <input
                  type="email"
                  required
                  placeholder="vous@exemple.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  style={{
                    flex: 1,
                    padding: "12px 16px",
                    border: "1px solid #ddd",
                    borderRadius: "8px",
                    fontSize: "1rem",
                    minWidth: "200px",
                  }}
                />
                <button type="submit" className="btn btn-primary">
                  {buttonLabel}
                </button>
              </form>
            </>
          )}
        </div>
      </div>
    );
  },
};

// ============================================================
//  COOKIE BANNER — Bandeau cookies RGPD
// ============================================================

export const CookieBanner = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Cookies & vie privée" },
    message: {
      type: "textarea",
      label: "Message",
      defaultValue: "Nous utilisons des cookies pour améliorer votre expérience, analyser le trafic et personnaliser les contenus. Vous pouvez accepter ou refuser.",
    },
    acceptLabel: { type: "text", label: "Bouton Accepter", defaultValue: "Tout accepter" },
    refuseLabel: { type: "text", label: "Bouton Refuser", defaultValue: "Continuer sans accepter" },
    privacyUrl: { type: "text", label: "URL politique de confidentialité", defaultValue: "/confidentialite" },
    position: {
      type: "select", label: "Position",
      options: [
        { label: "Bas de page", value: "bottom" },
        { label: "Bandeau haut", value: "top" },
      ],
    },
  },
  defaultProps: {
    title: "Cookies & vie privée",
    message:
      "Nous utilisons des cookies pour améliorer votre expérience, analyser le trafic et personnaliser les contenus. Vous pouvez accepter ou refuser.",
    acceptLabel: "Tout accepter",
    refuseLabel: "Continuer sans accepter",
    privacyUrl: "/confidentialite",
    position: "bottom",
  },
  render: ({ title, message, acceptLabel, refuseLabel, privacyUrl, position }) => {
    const [visible, setVisible] = React.useState(false);

    React.useEffect(() => {
      if (typeof window === "undefined") return;
      const consent = localStorage.getItem("nawa_cookie_consent");
      if (!consent) setVisible(true);
    }, []);

    const decide = (value) => {
      localStorage.setItem("nawa_cookie_consent", value);
      localStorage.setItem("nawa_cookie_consent_date", new Date().toISOString());
      setVisible(false);
      // Notifie le reste de l'app
      window.dispatchEvent(new CustomEvent("nawa:cookie-consent", { detail: { value } }));
    };

    if (!visible) return null;

    const posStyle = position === "top" ? { top: 0 } : { bottom: 0 };
    const borderStyle = position === "top"
      ? { borderBottom: "1px solid #eee" }
      : { borderTop: "1px solid #eee" };

    return (
      <div
        style={{
          position: "fixed",
          left: 0,
          right: 0,
          ...posStyle,
          background: "#fff",
          ...borderStyle,
          padding: "20px 24px",
          zIndex: 99999,
          boxShadow: "0 -4px 20px rgba(0,0,0,0.08)",
        }}
      >
        <div
          style={{
            maxWidth: "1200px",
            margin: "0 auto",
            display: "flex",
            gap: "20px",
            flexWrap: "wrap",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ flex: "1 1 400px" }}>
            <div style={{ fontWeight: 700, marginBottom: "6px" }}>{title}</div>
            <p style={{ margin: 0, color: "#6B6259", fontSize: "0.9rem", lineHeight: 1.5 }}>
              {message}{" "}
              <a href={privacyUrl} style={{ color: "#C1652F" }}>
                En savoir plus
              </a>
            </p>
          </div>
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
            <button
              onClick={() => decide("refused")}
              style={{
                padding: "10px 20px",
                background: "transparent",
                border: "1px solid #ccc",
                borderRadius: "8px",
                cursor: "pointer",
                fontWeight: 500,
                fontSize: "0.9rem",
              }}
            >
              {refuseLabel}
            </button>
            <button
              onClick={() => decide("accepted")}
              style={{
                padding: "10px 20px",
                background: "#C1652F",
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.9rem",
              }}
            >
              {acceptLabel}
            </button>
          </div>
        </div>
      </div>
    );
  },
};
'''


# ============================================================
#                    PATCH DU CONFIG
# ============================================================

MARKER = "/* === PHASE 9 WIDGETS === */"


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    label = os.path.relpath(path, BASE_DIR)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return False
        shutil.copy2(path, path + ".bak")
        print(f"  [BACKUP] {label}.bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")
    return True


def update_config():
    config_path = os.path.join(SRC_DIR, "puck", "config.jsx")
    if not os.path.exists(config_path):
        print("  [ERREUR] config.jsx introuvable.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER in content:
        print("  [SKIP] config.jsx déjà patché Phase 9")
        return

    shutil.copy2(config_path, config_path + ".bak")
    print(f"  [BACKUP] {os.path.relpath(config_path, BASE_DIR)}.bak")

    # 1. Imports
    imports = (
        f"\n{MARKER}\n"
        'import {\n'
        '  FacebookPage, FacebookButton, FacebookEmbed, FacebookComments,\n'
        '  PayPalButton, StripeButton,\n'
        '} from "./widgets/marketingWidgets";\n'
        'import {\n'
        '  MegaMenu, OffCanvas, MenuCart, SocialShareExtended,\n'
        '  WhatsAppFloat, NewsletterPopup, CookieBanner,\n'
        '} from "./widgets/socialWidgets";\n'
        f"{MARKER}\n"
    )

    content = re.sub(
        r'(import React from "react";\n)',
        r'\1' + imports,
        content,
        count=1,
    )

    # 2. Ajouter les composants
    new_components = (
        "    // === Phase 9 : Marketing & Social ===\n"
        "    FacebookPage, FacebookButton, FacebookEmbed, FacebookComments,\n"
        "    PayPalButton, StripeButton,\n"
        "    MegaMenu, OffCanvas, MenuCart, SocialShareExtended,\n"
        "    WhatsAppFloat, NewsletterPopup, CookieBanner,\n"
    )

    components_pattern = re.compile(
        r'(components:\s*\{)(.*?)(\n\s*\},\s*\n\s*categories:)',
        re.DOTALL,
    )
    match = components_pattern.search(content)
    if match:
        content = (
            content[: match.start(2)]
            + "\n"
            + new_components
            + match.group(2).rstrip()
            + "\n  "
            + content[match.start(3):]
        )
    else:
        print("  [ATTENTION] Structure 'components: {' non standard.")

    # 3. Catégories
    new_categories = (
        '    facebook: { title: "Facebook", components: [\n'
        '      "FacebookPage", "FacebookButton", "FacebookEmbed", "FacebookComments",\n'
        '    ]},\n'
        '    payments: { title: "Paiement", components: [\n'
        '      "PayPalButton", "StripeButton",\n'
        '    ]},\n'
        '    navigationAdvanced: { title: "Navigation avancée", components: [\n'
        '      "MegaMenu", "OffCanvas", "MenuCart",\n'
        '    ]},\n'
        '    socialAdvanced: { title: "Social avancé", components: [\n'
        '      "SocialShareExtended", "WhatsAppFloat",\n'
        '    ]},\n'
        '    popups: { title: "Popups & RGPD", components: [\n'
        '      "NewsletterPopup", "CookieBanner",\n'
        '    ]},\n'
    )

    cat_pattern = re.compile(
        r'(categories:\s*\{)(.*?)(\n\s*\},)',
        re.DOTALL,
    )
    cat_match = cat_pattern.search(content)
    if cat_match:
        content = (
            content[: cat_match.start(2)]
            + "\n"
            + new_categories
            + cat_match.group(2)
            + content[cat_match.start(3):]
        )

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] config.jsx patché (13 widgets + 5 catégories)")


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  PHASE 9 — WIDGETS MARKETING & SOCIAL")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable dans {BASE_DIR}")
        return

    print("\n[1/3] Création des widgets Marketing (6)...")
    write_file(os.path.join(WIDGETS_DIR, "marketingWidgets.jsx"), MARKETING_WIDGETS_JSX)

    print("\n[2/3] Création des widgets Social (7)...")
    write_file(os.path.join(WIDGETS_DIR, "socialWidgets.jsx"), SOCIAL_WIDGETS_JSX)

    print("\n[3/3] Mise à jour de puckConfig...")
    update_config()

    print("\n" + "=" * 60)
    print("  ✅ PHASE 9 — 13 WIDGETS AJOUTÉS")
    print("=" * 60)
    print("\nFacebook (4) :")
    print("  FacebookPage, FacebookButton, FacebookEmbed, FacebookComments")
    print("\nPaiement (2) :")
    print("  PayPalButton (sandbox), StripeButton (mode test)")
    print("\nNavigation avancée (3) :")
    print("  MegaMenu, OffCanvas, MenuCart")
    print("\nSocial avancé (2) :")
    print("  SocialShareExtended, WhatsAppFloat")
    print("\nPopups & RGPD (2) :")
    print("  NewsletterPopup, CookieBanner")


if __name__ == "__main__":
    main()