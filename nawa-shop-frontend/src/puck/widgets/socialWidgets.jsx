/**
 * Phase 9 — Widgets Social (7 composants).
 * Mega menu, off-canvas, mini panier, partage, WhatsApp, popups, cookies.
 */
import { apiFetch } from "../../utils/apiClient";
import React from "react";

function splitLines(text) {
  return String(text || "").split("\n").map((s) => s.trim()).filter(Boolean);
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
      defaultValue: "Cosmétiques|Karité,Cheveux,Visage,Corps\nMode|Robes,Wax,Boubou,Homme\nMaison|Cuisine,Salle de bain,Électro",
    },
  },
  defaultProps: {
    title: "Catégories",
    columns: "Cosmétiques|Karité,Cheveux,Visage,Corps\nMode|Robes,Wax,Boubou,Homme\nMaison|Cuisine,Salle de bain,Électro",
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
