/**
 * Phase 9 — Widgets Marketing (6 composants).
 * Facebook (page, bouton, embed, commentaires) + PayPal + Stripe.
 *
 * Les SDK sont chargés à la demande et une seule fois.
 */
import { apiFetch } from "../../utils/apiClient";
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
        alert(`✅ Paiement Stripe simulé : ${amount}\n\nPrice ID : ${priceId}\n\nEn production, un appel API créerait une session Checkout.`);
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
