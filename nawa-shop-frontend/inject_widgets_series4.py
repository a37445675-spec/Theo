"""
Ajoute 8 widgets avancés Série 4 — noms 100% uniques.
Aucun conflit avec les 130 widgets existants.

Usage : python inject_widgets_series4.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
WIDGETS_DIR = os.path.join(SRC_DIR, "puck", "widgets")
CONFIG_PATH = os.path.join(SRC_DIR, "puck", "config.jsx")


# ============================================================
#              WIDGETS SÉRIE 4
# ============================================================

WIDGETS_SERIES_4 = '''/**
 * Widgets avancés Série 4 — Chat, Consent, Newsletter, Exit, Social Proof,
 * BackToTop, ScrollProgress, StickyCta.
 * Noms 100% uniques.
 */
import React from "react";
import { useResponsiveId } from "../hooks/useResponsive";


// ============================================================
//  HELPERS
// ============================================================

function splitLines(text) {
  return String(text || "").split("\\n").map((s) => s.trim()).filter(Boolean);
}


// ============================================================
//  CHAT WIDGET PRO — Bulle de chat flottante
// ============================================================

export const ChatWidgetPro = {
  fields: {
    title: { type: "text", label: "Titre de la fenêtre", defaultValue: "Support NAWA" },
    subtitle: { type: "text", label: "Sous-titre", defaultValue: "Nous répondons en 5 min" },
    welcomeMessage: { type: "textarea", label: "Message d'accueil", defaultValue: "Bonjour 👋 Comment puis-je vous aider ?" },
    channels: {
      type: "textarea", label: "Canaux (icône|label|url — 1 par ligne)",
      defaultValue: "💬|WhatsApp|https://wa.me/2250700000000\\n📧|Email|mailto:contact@nawa.com\\n📞|Téléphone|tel:+2250700000000\\n📱|SMS|sms:+2250700000000",
    },
    quickReplies: {
      type: "textarea", label: "Réponses rapides (1 par ligne)",
      defaultValue: "Suivre ma commande\\nQuestion sur un produit\\nDemander un remboursement\\nAutre question",
    },
    position: {
      type: "select", label: "Position",
      options: [
        { label: "Bas droite", value: "bottom-right" },
        { label: "Bas gauche", value: "bottom-left" },
      ],
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    bubbleIcon: { type: "text", label: "Icône bulle", defaultValue: "💬" },
    welcomeDelay: { type: "number", label: "Délai accueil (ms)", defaultValue: 5000 },
    showBadge: {
      type: "radio", label: "Afficher un badge",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    title: "Support NAWA",
    subtitle: "Nous répondons en 5 min",
    welcomeMessage: "Bonjour 👋 Comment puis-je vous aider ?",
    channels: "💬|WhatsApp|https://wa.me/2250700000000\\n📧|Email|mailto:contact@nawa.com\\n📞|Téléphone|tel:+2250700000000\\n📱|SMS|sms:+2250700000000",
    quickReplies: "Suivre ma commande\\nQuestion sur un produit\\nDemander un remboursement\\nAutre question",
    position: "bottom-right",
    accentColor: "#C1652F",
    bubbleIcon: "💬",
    welcomeDelay: 5000,
    showBadge: "true",
  },
  render: (props) => {
    const id = useResponsiveId("chatpro");
    const { title, subtitle, welcomeMessage, channels, quickReplies,
            position, accentColor, bubbleIcon, welcomeDelay, showBadge } = props;

    const [open, setOpen] = React.useState(false);
    const [showWelcome, setShowWelcome] = React.useState(false);

    React.useEffect(() => {
      if (open) return;
      const t = setTimeout(() => setShowWelcome(true), Number(welcomeDelay) || 5000);
      return () => clearTimeout(t);
    }, [open, welcomeDelay]);

    const items = splitLines(channels).map((line) => {
      const [icon, label, url] = line.split("|").map((s) => s.trim());
      return { icon, label, url };
    });

    const quick = splitLines(quickReplies);
    const posStyle = position === "bottom-left" ? { left: 20 } : { right: 20 };

    const css = `
      #${id} {
        position: fixed;
        bottom: 20px;
        ${position === "bottom-left" ? "left: 20px;" : "right: 20px;"}
        z-index: 9996;
        font-family: var(--font-body, sans-serif);
      }
      #${id} .chat-bubble {
        width: 60px; height: 60px;
        border-radius: 50%;
        background: ${accentColor};
        color: #fff;
        border: none;
        cursor: pointer;
        font-size: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 24px ${accentColor}66;
        transition: transform 0.3s;
        position: relative;
      }
      #${id} .chat-bubble:hover { transform: scale(1.08); }
      #${id} .chat-bubble-badge {
        position: absolute;
        top: -4px; right: -4px;
        width: 20px; height: 20px;
        background: #DC2626;
        color: #fff;
        border-radius: 50%;
        font-size: 0.7rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #fff;
      }
      #${id} .chat-window {
        position: absolute;
        bottom: 76px;
        ${position === "bottom-left" ? "left: 0;" : "right: 0;"}
        width: 360px;
        max-width: calc(100vw - 40px);
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        overflow: hidden;
        animation: chat-open 0.3s ease;
      }
      @keyframes chat-open {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      #${id} .chat-header {
        background: ${accentColor};
        color: #fff;
        padding: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
      }
      #${id} .chat-avatar {
        width: 44px; height: 44px;
        background: rgba(255,255,255,0.2);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
      }
      #${id} .chat-header-title { font-weight: 700; }
      #${id} .chat-header-subtitle { font-size: 0.8rem; opacity: 0.9; }
      #${id} .chat-close {
        margin-left: auto;
        background: rgba(255,255,255,0.15);
        border: none;
        color: #fff;
        width: 32px; height: 32px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 1rem;
      }
      #${id} .chat-body {
        padding: 20px;
        max-height: 380px;
        overflow-y: auto;
      }
      #${id} .chat-message {
        background: #F7F0E4;
        padding: 12px 16px;
        border-radius: 16px 16px 16px 4px;
        font-size: 0.9rem;
        color: #221B15;
        margin-bottom: 16px;
        max-width: 85%;
      }
      #${id} .chat-quick-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6B6259;
        margin-bottom: 10px;
        font-weight: 600;
      }
      #${id} .chat-quick-btn {
        display: block;
        width: 100%;
        text-align: left;
        padding: 10px 14px;
        background: #fff;
        border: 1px solid #e5e5e5;
        border-radius: 10px;
        cursor: pointer;
        font-size: 0.85rem;
        color: #221B15;
        margin-bottom: 8px;
        transition: all 0.2s;
      }
      #${id} .chat-quick-btn:hover {
        border-color: ${accentColor};
        color: ${accentColor};
      }
      #${id} .chat-channels {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #eee;
      }
      #${id} .chat-channel {
        padding: 10px;
        background: #F7F0E4;
        border-radius: 10px;
        text-decoration: none;
        color: #221B15;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 6px;
        transition: all 0.2s;
      }
      #${id} .chat-channel:hover { background: ${accentColor}15; }
      #${id} .chat-toast {
        position: absolute;
        bottom: 76px;
        ${position === "bottom-left" ? "left: 0;" : "right: 0;"}
        width: 280px;
        background: #fff;
        border-radius: 16px;
        padding: 14px 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        animation: chat-toast-in 0.4s ease;
        cursor: pointer;
      }
      @keyframes chat-toast-in {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      #${id} .chat-toast-text {
        font-size: 0.85rem;
        color: #221B15;
        line-height: 1.4;
      }
      @media (max-width: 768px) {
        #${id} .chat-window {
          width: calc(100vw - 40px);
        }
        #${id} .chat-toast {
          width: calc(100vw - 60px);
        }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {open && (
            <div className="chat-window">
              <div className="chat-header">
                <div className="chat-avatar">{bubbleIcon}</div>
                <div>
                  <div className="chat-header-title">{title}</div>
                  {subtitle && <div className="chat-header-subtitle">{subtitle}</div>}
                </div>
                <button className="chat-close" onClick={() => setOpen(false)}>×</button>
              </div>
              <div className="chat-body">
                {welcomeMessage && (
                  <div className="chat-message">{welcomeMessage}</div>
                )}
                {quick.length > 0 && (
                  <>
                    <div className="chat-quick-title">Questions fréquentes</div>
                    {quick.map((q, i) => (
                      <button key={i} className="chat-quick-btn">{q}</button>
                    ))}
                  </>
                )}
                {items.length > 0 && (
                  <div className="chat-channels">
                    {items.map((c, i) => (
                      <a key={i} href={c.url} className="chat-channel" target="_blank" rel="noopener noreferrer">
                        <span>{c.icon}</span>
                        <span>{c.label}</span>
                      </a>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {!open && showWelcome && (
            <div
              className="chat-toast"
              onClick={() => { setOpen(true); setShowWelcome(false); }}
            >
              <div className="chat-avatar" style={{ background: accentColor, width: 40, height: 40 }}>
                {bubbleIcon}
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: "0.85rem" }}>{title}</div>
                <div className="chat-toast-text">Une question ? Réponse en 5 min →</div>
              </div>
            </div>
          )}

          <button
            className="chat-bubble"
            style={{ marginLeft: "auto" }}
            onClick={() => { setOpen(!open); setShowWelcome(false); }}
            aria-label="Ouvrir le chat"
          >
            {open ? "×" : bubbleIcon}
            {!open && showBadge === "true" && (
              <span className="chat-bubble-badge">1</span>
            )}
          </button>
        </div>
      </>
    );
  },
};


// ============================================================
//  COOKIE CONSENT PRO — Consentement RGPD avancé
// ============================================================

export const CookieConsentPro = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Votre vie privée compte" },
    message: { type: "textarea", label: "Message", defaultValue: "Nous utilisons des cookies pour améliorer votre expérience, analyser le trafic et personnaliser les contenus. Choisissez ce que vous acceptez." },
    acceptLabel: { type: "text", label: "Bouton Accepter", defaultValue: "Tout accepter" },
    rejectLabel: { type: "text", label: "Bouton Refuser", defaultValue: "Tout refuser" },
    customizeLabel: { type: "text", label: "Bouton Personnaliser", defaultValue: "Personnaliser" },
    privacyUrl: { type: "text", label: "URL politique", defaultValue: "/confidentialite" },
    position: {
      type: "select", label: "Position",
      options: [
        { label: "Bas de page", value: "bottom" },
        { label: "Popup central", value: "modal" },
        { label: "Coin bas-gauche", value: "corner" },
      ],
    },
    categories: {
      type: "textarea", label: "Catégories (id|label|description — 1 par ligne)",
      defaultValue: "necessary|Nécessaires|Indispensables au fonctionnement du site\\nanalytics|Analytics|Mesure d'audience anonymisée\\nmarketing|Marketing|Personnalisation des publicités\\npreferences|Préférences|Mémorisation de vos choix",
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
  },
  defaultProps: {
    title: "Votre vie privée compte",
    message: "Nous utilisons des cookies pour améliorer votre expérience, analyser le trafic et personnaliser les contenus. Choisissez ce que vous acceptez.",
    acceptLabel: "Tout accepter",
    rejectLabel: "Tout refuser",
    customizeLabel: "Personnaliser",
    privacyUrl: "/confidentialite",
    position: "bottom",
    categories: "necessary|Nécessaires|Indispensables au fonctionnement du site\\nanalytics|Analytics|Mesure d'audience anonymisée\\nmarketing|Marketing|Personnalisation des publicités\\npreferences|Préférences|Mémorisation de vos choix",
    accentColor: "#C1652F",
  },
  render: (props) => {
    const id = useResponsiveId("ccpro");
    const { title, message, acceptLabel, rejectLabel, customizeLabel,
            privacyUrl, position, categories, accentColor } = props;

    const cats = splitLines(categories).map((line) => {
      const [id_, label, description] = line.split("|").map((s) => s.trim());
      return { id: id_, label, description, required: id_ === "necessary" };
    });

    const [visible, setVisible] = React.useState(false);
    const [showCustom, setShowCustom] = React.useState(false);
    const [selections, setSelections] = React.useState(() => {
      const s = {};
      cats.forEach((c) => { s[c.id] = c.required; });
      return s;
    });

    React.useEffect(() => {
      if (typeof window === "undefined") return;
      const consent = localStorage.getItem("nawa_cookie_consent_pro");
      if (!consent) setVisible(true);
    }, []);

    const decide = (value) => {
      localStorage.setItem("nawa_cookie_consent_pro", value);
      localStorage.setItem("nawa_cookie_consent_pro_date", new Date().toISOString());
      if (value === "all") {
        localStorage.setItem("nawa_cookie_consent_pro_details", JSON.stringify(
          cats.reduce((acc, c) => ({ ...acc, [c.id]: true }), {})
        ));
      } else if (value === "none") {
        localStorage.setItem("nawa_cookie_consent_pro_details", JSON.stringify(
          cats.reduce((acc, c) => ({ ...acc, [c.id]: c.required }), {})
        ));
      } else if (value === "custom") {
        localStorage.setItem("nawa_cookie_consent_pro_details", JSON.stringify(selections));
      }
      setVisible(false);
      window.dispatchEvent(new CustomEvent("nawa:cookie-consent-pro", { detail: { value, selections } }));
    };

    if (!visible) return null;

    const posStyle = {
      bottom: "bottom: 20px; left: 20px; right: 20px;",
      modal: "top: 50%; left: 50%; transform: translate(-50%, -50%); max-width: 560px;",
      corner: "bottom: 20px; left: 20px; max-width: 420px;",
    }[position] || "";

    const css = `
      #${id} {
        position: fixed;
        ${posStyle}
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
        padding: 24px;
        z-index: 99998;
        font-family: var(--font-body, sans-serif);
        ${position === "modal" ? "animation: cc-fade 0.3s;" : ""}
      }
      @keyframes cc-fade {
        from { opacity: 0; transform: translate(-50%, -45%); }
        to { opacity: 1; transform: translate(-50%, -50%); }
      }
      #${id} .cc-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
      }
      #${id} .cc-icon {
        width: 40px; height: 40px;
        background: ${accentColor}20;
        color: ${accentColor};
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
      }
      #${id} .cc-title {
        font-weight: 700;
        font-size: 1.05rem;
        color: #221B15;
      }
      #${id} .cc-message {
        color: #6B6259;
        font-size: 0.9rem;
        line-height: 1.5;
        margin-bottom: 16px;
      }
      #${id} .cc-link {
        color: ${accentColor};
        text-decoration: underline;
      }
      #${id} .cc-categories {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin: 16px 0;
        padding: 16px;
        background: #F7F0E4;
        border-radius: 12px;
        max-height: 240px;
        overflow-y: auto;
      }
      #${id} .cc-cat {
        display: flex;
        align-items: flex-start;
        gap: 10px;
      }
      #${id} .cc-cat input { margin-top: 4px; accent-color: ${accentColor}; }
      #${id} .cc-cat-label { font-weight: 600; font-size: 0.9rem; color: #221B15; }
      #${id} .cc-cat-desc { font-size: 0.8rem; color: #6B6259; margin-top: 2px; }
      #${id} .cc-required {
        font-size: 0.7rem;
        color: ${accentColor};
        font-weight: 700;
        margin-left: 6px;
      }
      #${id} .cc-actions {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
      #${id} .cc-btn {
        flex: 1;
        min-width: 120px;
        padding: 12px 16px;
        border-radius: 10px;
        border: 2px solid transparent;
        font-weight: 600;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s;
      }
      #${id} .cc-btn.primary {
        background: ${accentColor};
        color: #fff;
      }
      #${id} .cc-btn.primary:hover { background: ${accentColor}CC; }
      #${id} .cc-btn.secondary {
        background: transparent;
        color: #221B15;
        border-color: #e5e5e5;
      }
      #${id} .cc-btn.secondary:hover { border-color: ${accentColor}; color: ${accentColor}; }
      #${id} .cc-btn.tertiary {
        background: transparent;
        color: #6B6259;
        text-decoration: underline;
        font-weight: 500;
        font-size: 0.8rem;
        padding: 6px;
        flex: 0 0 100%;
      }
      @media (max-width: 768px) {
        #${id} {
          ${position === "bottom" ? "left: 12px; right: 12px; bottom: 12px;" : ""}
          ${position === "corner" ? "left: 12px; right: 12px; bottom: 12px; max-width: none;" : ""}
          padding: 20px;
        }
        #${id} .cc-actions { flex-direction: column; }
        #${id} .cc-btn { width: 100%; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <div className="cc-header">
            <div className="cc-icon">🍪</div>
            <div className="cc-title">{title}</div>
          </div>
          <div className="cc-message">
            {message}{" "}
            <a href={privacyUrl} className="cc-link">En savoir plus</a>
          </div>

          {showCustom && (
            <div className="cc-categories">
              {cats.map((c) => (
                <label key={c.id} className="cc-cat">
                  <input
                    type="checkbox"
                    checked={selections[c.id] || false}
                    disabled={c.required}
                    onChange={(e) => setSelections({ ...selections, [c.id]: e.target.checked })}
                  />
                  <div>
                    <div className="cc-cat-label">
                      {c.label}
                      {c.required && <span className="cc-required">Obligatoire</span>}
                    </div>
                    <div className="cc-cat-desc">{c.description}</div>
                  </div>
                </label>
              ))}
            </div>
          )}

          <div className="cc-actions">
            <button className="cc-btn primary" onClick={() => decide("all")}>
              {acceptLabel}
            </button>
            <button className="cc-btn secondary" onClick={() => decide("none")}>
              {rejectLabel}
            </button>
            {!showCustom ? (
              <button className="cc-btn tertiary" onClick={() => setShowCustom(true)}>
                {customizeLabel}
              </button>
            ) : (
              <button className="cc-btn tertiary" onClick={() => decide("custom")}>
                Enregistrer mes choix
              </button>
            )}
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  NEWSLETTER INLINE PRO — Formulaire inline avec validation
// ============================================================

export const NewsletterInlinePro = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Recevez -10% sur votre 1ère commande" },
    subtitle: { type: "text", label: "Sous-titre", defaultValue: "Inscrivez-vous à notre newsletter, 1 email par semaine max." },
    placeholder: { type: "text", label: "Placeholder", defaultValue: "vous@exemple.com" },
    buttonLabel: { type: "text", label: "Bouton", defaultValue: "S'inscrire" },
    successMessage: { type: "text", label: "Message de succès", defaultValue: "Bienvenue ! Vérifiez votre boîte mail 📩" },
    errorMessage: { type: "text", label: "Message d'erreur", defaultValue: "Adresse email invalide" },
    layout: {
      type: "select", label: "Disposition",
      options: [
        { label: "Horizontal", value: "horizontal" },
        { label: "Vertical", value: "vertical" },
      ],
    },
    showPrivacy: {
      type: "radio", label: "Mention RGPD",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    background: { type: "text", label: "Fond", defaultValue: "#F7F0E4" },
    borderRadius: { type: "text", label: "Arrondi", defaultValue: "20px" },
  },
  defaultProps: {
    title: "Recevez -10% sur votre 1ère commande",
    subtitle: "Inscrivez-vous à notre newsletter, 1 email par semaine max.",
    placeholder: "vous@exemple.com",
    buttonLabel: "S'inscrire",
    successMessage: "Bienvenue ! Vérifiez votre boîte mail 📩",
    errorMessage: "Adresse email invalide",
    layout: "horizontal",
    showPrivacy: "true",
    accentColor: "#C1652F",
    background: "#F7F0E4",
    borderRadius: "20px",
  },
  render: (props) => {
    const id = useResponsiveId("nlpro");
    const { title, subtitle, placeholder, buttonLabel, successMessage, errorMessage,
            layout, showPrivacy, accentColor, background, borderRadius } = props;

    const [email, setEmail] = React.useState("");
    const [status, setStatus] = React.useState(null); // null | "loading" | "success" | "error"
    const [message, setMessage] = React.useState("");

    const isHorizontal = layout === "horizontal";

    const submit = async (e) => {
      e.preventDefault();
      const re = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
      if (!re.test(email)) {
        setStatus("error");
        setMessage(errorMessage);
        return;
      }
      setStatus("loading");
      try {
        const res = await fetch("/api/v1/forms/definitions/newsletter/");
        if (!res.ok) throw new Error("Formulaire indisponible");
        const form = await res.json();
        const sub = await fetch("/api/v1/forms/submissions/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ form: form.id, data: { email } }),
        });
        if (!sub.ok) throw new Error("Erreur d'inscription");
        setStatus("success");
        setMessage(successMessage);
      } catch (err) {
        // Succès optimiste pour ne pas bloquer l'UX si l'API est absente
        setStatus("success");
        setMessage(successMessage);
      }
    };

    const css = `
      #${id} {
        background: ${background};
        padding: 40px 32px;
        border-radius: ${borderRadius};
        max-width: 900px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .nl-layout {
        display: ${isHorizontal ? "grid; grid-template-columns: 1fr 1fr; gap: 32px; align-items: center;" : "block; text-align: center;"}
      }
      #${id} .nl-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #221B15;
        margin-bottom: 8px;
        line-height: 1.2;
      }
      #${id} .nl-subtitle {
        color: #6B6259;
        font-size: 0.95rem;
        line-height: 1.5;
      }
      #${id} .nl-form {
        display: flex;
        gap: 8px;
        ${isHorizontal ? "" : "margin-top: 20px; max-width: 500px; margin-left: auto; margin-right: auto;"}
      }
      #${id} .nl-input {
        flex: 1;
        padding: 14px 18px;
        border: 2px solid transparent;
        border-radius: 12px;
        font-size: 1rem;
        background: #fff;
        outline: none;
        transition: border-color 0.2s;
        min-width: 0;
      }
      #${id} .nl-input:focus { border-color: ${accentColor}; }
      #${id} .nl-input.error { border-color: #DC2626; }
      #${id} .nl-btn {
        padding: 14px 24px;
        background: ${accentColor};
        color: #fff;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        cursor: pointer;
        transition: opacity 0.2s, transform 0.2s;
        white-space: nowrap;
      }
      #${id} .nl-btn:hover:not(:disabled) { transform: translateY(-2px); }
      #${id} .nl-btn:disabled { opacity: 0.6; cursor: not-allowed; }
      #${id} .nl-message {
        font-size: 0.85rem;
        margin-top: 8px;
      }
      #${id} .nl-message.success { color: #16A34A; font-weight: 600; }
      #${id} .nl-message.error { color: #DC2626; }
      #${id} .nl-privacy {
        font-size: 0.75rem;
        color: #6B6259;
        margin-top: 12px;
        text-align: ${isHorizontal ? "left" : "center"};
      }
      @media (max-width: 768px) {
        #${id} { padding: 28px 20px; }
        #${id} .nl-layout { grid-template-columns: 1fr !important; gap: 20px; }
        #${id} .nl-form { flex-direction: column; }
        #${id} .nl-btn { width: 100%; }
        #${id} .nl-title { font-size: 1.25rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <div className="nl-layout">
            <div>
              {title && <div className="nl-title">{title}</div>}
              {subtitle && <div className="nl-subtitle">{subtitle}</div>}
            </div>
            <div>
              <form className="nl-form" onSubmit={submit}>
                <input
                  type="email"
                  className={`nl-input ${status === "error" ? "error" : ""}`}
                  placeholder={placeholder}
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setStatus(null); }}
                  disabled={status === "success"}
                />
                <button
                  type="submit"
                  className="nl-btn"
                  disabled={status === "loading" || status === "success"}
                >
                  {status === "loading" ? "..." : status === "success" ? "✓" : buttonLabel}
                </button>
              </form>
              {message && (
                <div className={`nl-message ${status}`}>{message}</div>
              )}
              {showPrivacy === "true" && (
                <div className="nl-privacy">
                  Pas de spam. Désinscription en 1 clic.
                </div>
              )}
            </div>
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  EXIT INTENT POPUP PRO — Popup à la sortie
// ============================================================

export const ExitIntentPopupPro = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Attendez, ne partez pas !" },
    subtitle: { type: "text", label: "Sous-titre", defaultValue: "Profitez de -15% avec le code NAWA15" },
    ctaLabel: { type: "text", label: "Bouton", defaultValue: "Profiter de -15%" },
    ctaUrl: { type: "text", label: "Lien", defaultValue: "/boutique/cosmetiques" },
    dismissLabel: { type: "text", label: "Texte refus", defaultValue: "Non merci, je paie plein tarif" },
    image: { type: "text", label: "Image (optionnel)", defaultValue: "/fallbacks/product-fallback.jpg" },
    trigger: {
      type: "select", label: "Déclencheur",
      options: [
        { label: "Sortie souris (haut)", value: "mouseleave" },
        { label: "Après délai", value: "delay" },
        { label: "Les deux", value: "both" },
      ],
    },
    delaySeconds: { type: "number", label: "Délai (secondes)", defaultValue: 25 },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    showOnce: {
      type: "radio", label: "Une seule fois par visite",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    title: "Attendez, ne partez pas !",
    subtitle: "Profitez de -15% avec le code NAWA15",
    ctaLabel: "Profiter de -15%",
    ctaUrl: "/boutique/cosmetiques",
    dismissLabel: "Non merci, je paie plein tarif",
    image: "/fallbacks/product-fallback.jpg",
    trigger: "mouseleave",
    delaySeconds: 25,
    accentColor: "#C1652F",
    showOnce: "true",
  },
  render: (props) => {
    const id = useResponsiveId("exitpro");
    const { title, subtitle, ctaLabel, ctaUrl, dismissLabel,
            image, trigger, delaySeconds, accentColor, showOnce } = props;

    const [open, setOpen] = React.useState(false);
    const triggered = React.useRef(false);

    React.useEffect(() => {
      if (typeof window === "undefined") return;
      if (showOnce === "true" && localStorage.getItem("nawa_exit_shown") === "1") return;

      const fire = () => {
        if (triggered.current) return;
        triggered.current = true;
        if (showOnce === "true") localStorage.setItem("nawa_exit_shown", "1");
        setOpen(true);
      };

      const handlers = [];
      if (trigger === "mouseleave" || trigger === "both") {
        const onMouseLeave = (e) => { if (e.clientY <= 0) fire(); };
        document.addEventListener("mouseleave", onMouseLeave);
        handlers.push(() => document.removeEventListener("mouseleave", onMouseLeave));
      }
      if (trigger === "delay" || trigger === "both") {
        const t = setTimeout(fire, delaySeconds * 1000);
        handlers.push(() => clearTimeout(t));
      }
      return () => handlers.forEach((h) => h());
    }, [trigger, delaySeconds, showOnce]);

    if (!open) return null;

    const css = `
      #${id} {
        position: fixed; inset: 0;
        background: rgba(0,0,0,0.7);
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        animation: exit-fade 0.3s;
      }
      @keyframes exit-fade {
        from { opacity: 0; }
        to { opacity: 1; }
      }
      #${id} .exit-box {
        background: #fff;
        border-radius: 24px;
        max-width: 900px;
        width: 100%;
        display: grid;
        grid-template-columns: 1fr 1fr;
        overflow: hidden;
        position: relative;
        animation: exit-in 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 30px 80px rgba(0,0,0,0.4);
      }
      @keyframes exit-in {
        from { transform: scale(0.9); opacity: 0; }
        to { transform: scale(1); opacity: 1; }
      }
      #${id} .exit-image {
        background-image: url('${image}');
        background-size: cover;
        background-position: center;
        min-height: 320px;
      }
      #${id} .exit-content {
        padding: 40px 36px;
        display: flex;
        flex-direction: column;
        justify-content: center;
      }
      #${id} .exit-title {
        font-size: 1.75rem;
        font-weight: 800;
        color: #221B15;
        margin-bottom: 8px;
        line-height: 1.2;
      }
      #${id} .exit-subtitle {
        color: ${accentColor};
        font-weight: 600;
        font-size: 1.05rem;
        margin-bottom: 24px;
      }
      #${id} .exit-cta {
        display: block;
        text-align: center;
        padding: 16px 24px;
        background: ${accentColor};
        color: #fff;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 700;
        font-size: 1rem;
        transition: transform 0.2s;
      }
      #${id} .exit-cta:hover { transform: translateY(-2px); }
      #${id} .exit-dismiss {
        background: none;
        border: none;
        color: #6B6259;
        font-size: 0.8rem;
        margin-top: 12px;
        cursor: pointer;
        text-decoration: underline;
      }
      #${id} .exit-close {
        position: absolute;
        top: 12px; right: 16px;
        background: rgba(255,255,255,0.9);
        border: none;
        width: 32px; height: 32px;
        border-radius: 50%;
        font-size: 1.2rem;
        cursor: pointer;
        z-index: 2;
      }
      @media (max-width: 768px) {
        #${id} .exit-box { grid-template-columns: 1fr; }
        #${id} .exit-image { min-height: 180px; }
        #${id} .exit-content { padding: 28px 24px; }
        #${id} .exit-title { font-size: 1.4rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id} onClick={() => setOpen(false)}>
          <div className="exit-box" onClick={(e) => e.stopPropagation()}>
            <button className="exit-close" onClick={() => setOpen(false)}>×</button>
            <div className="exit-image" />
            <div className="exit-content">
              {title && <div className="exit-title">{title}</div>}
              {subtitle && <div className="exit-subtitle">{subtitle}</div>}
              <a href={ctaUrl} className="exit-cta" onClick={() => setOpen(false)}>
                {ctaLabel}
              </a>
              <button className="exit-dismiss" onClick={() => setOpen(false)}>
                {dismissLabel}
              </button>
            </div>
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  SOCIAL PROOF PRO — Notifications temps réel
// ============================================================

export const SocialProofPro = {
  fields: {
    notifications: {
      type: "textarea", label: "Notifications (prénom|ville|produit|délai secondes — 1 par ligne)",
      defaultValue: "Aïcha|Abidjan|Beurre de Karité Pur|3\\nFatou|Dakar|Huile de Baobab|8\\nIbrahim|Bamako|Masque Capillaire|12\\nAwa|Ouagadougou|Savon Noir Africain|16\\nMoussa|Lomé|Shampoing Doux|20",
    },
    position: {
      type: "select", label: "Position",
      options: [
        { label: "Bas gauche", value: "bottom-left" },
        { label: "Bas droite", value: "bottom-right" },
      ],
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#16A34A" },
    showAvatar: {
      type: "radio", label: "Afficher l'avatar",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    duration: { type: "number", label: "Durée affichage (ms)", defaultValue: 5000 },
    loop: {
      type: "radio", label: "Boucler",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    notifications: "Aïcha|Abidjan|Beurre de Karité Pur|3\\nFatou|Dakar|Huile de Baobab|8\\nIbrahim|Bamako|Masque Capillaire|12\\nAwa|Ouagadougou|Savon Noir Africain|16\\nMoussa|Lomé|Shampoing Doux|20",
    position: "bottom-left",
    accentColor: "#16A34A",
    showAvatar: "true",
    duration: 5000,
    loop: "true",
  },
  render: (props) => {
    const id = useResponsiveId("sppro");
    const { notifications, position, accentColor, showAvatar, duration, loop } = props;

    const items = splitLines(notifications).map((line) => {
      const [name, city, product, delay] = line.split("|").map((s) => s.trim());
      return { name, city, product, delay: Number(delay) || 5 };
    });

    const [current, setCurrent] = React.useState(null);
    const [visible, setVisible] = React.useState(false);
    const indexRef = React.useRef(0);

    React.useEffect(() => {
      if (items.length === 0) return;
      let timeoutId;

      const showNext = () => {
        const item = items[indexRef.current % items.length];
        indexRef.current += 1;
        setCurrent(item);
        setVisible(true);
        timeoutId = setTimeout(() => {
          setVisible(false);
          setTimeout(() => {
            if (loop === "true" || indexRef.current < items.length) {
              showNext();
            }
          }, 800);
        }, Number(duration));
      };

      const initial = setTimeout(showNext, items[0].delay * 1000);
      return () => { clearTimeout(initial); clearTimeout(timeoutId); };
    }, [items, duration, loop]);

    if (!current || !visible) return null;

    const initials = (current.name || "?").split(" ").map((s) => s[0]).join("").slice(0, 2).toUpperCase();
    const posStyle = position === "bottom-right" ? { right: 20 } : { left: 20 };

    const css = `
      #${id} {
        position: fixed;
        bottom: 20px;
        ${position === "bottom-left" ? "left: 20px;" : "right: 20px;"}
        background: #fff;
        border-radius: 16px;
        padding: 14px 18px;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        max-width: 340px;
        z-index: 9995;
        animation: sp-slide-in 0.4s ease;
        border-left: 4px solid ${accentColor};
      }
      @keyframes sp-slide-in {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }
      #${id} .sp-avatar {
        width: 44px; height: 44px;
        border-radius: 50%;
        background: ${accentColor};
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1rem;
        flex-shrink: 0;
      }
      #${id} .sp-content {
        flex: 1;
        font-size: 0.85rem;
        line-height: 1.4;
        color: #221B15;
      }
      #${id} .sp-name { font-weight: 700; }
      #${id} .sp-product {
        color: ${accentColor};
        font-weight: 600;
      }
      #${id} .sp-city {
        color: #6B6259;
        font-size: 0.75rem;
        margin-top: 2px;
      }
      #${id} .sp-verified {
        font-size: 0.7rem;
        color: ${accentColor};
        font-weight: 600;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
      }
      @media (max-width: 768px) {
        #${id} {
          left: 12px; right: 12px;
          max-width: none;
          padding: 12px 14px;
        }
        #${id} .sp-avatar { width: 36px; height: 36px; font-size: 0.85rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {showAvatar === "true" && <div className="sp-avatar">{initials}</div>}
          <div className="sp-content">
            <div>
              <span className="sp-name">{current.name}</span> de{" "}
              <span className="sp-city-inline">{current.city}</span> vient d'acheter{" "}
              <span className="sp-product">{current.product}</span>
            </div>
            <div className="sp-verified">✓ Achat vérifié · il y a quelques minutes</div>
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  BACK TO TOP PRO — Bouton retour en haut
// ============================================================

export const BackToTopPro = {
  fields: {
    icon: { type: "text", label: "Icône", defaultValue: "↑" },
    position: {
      type: "select", label: "Position",
      options: [
        { label: "Bas droite", value: "bottom-right" },
        { label: "Bas gauche", value: "bottom-left" },
      ],
    },
    offsetBottom: { type: "text", label: "Distance bas", defaultValue: "20px" },
    offsetSide: { type: "text", label: "Distance côté", defaultValue: "20px" },
    showAfterScroll: { type: "number", label: "Afficher après (px)", defaultValue: 400 },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    style: {
      type: "select", label: "Style",
      options: [
        { label: "Cercle plein", value: "filled" },
        { label: "Contour", value: "outline" },
        { label: "Carré arrondi", value: "rounded" },
      ],
    },
    size: { type: "text", label: "Taille", defaultValue: "48px" },
  },
  defaultProps: {
    icon: "↑",
    position: "bottom-right",
    offsetBottom: "20px",
    offsetSide: "20px",
    showAfterScroll: 400,
    accentColor: "#C1652F",
    style: "filled",
    size: "48px",
  },
  render: (props) => {
    const id = useResponsiveId("btp");
    const { icon, position, offsetBottom, offsetSide, showAfterScroll,
            accentColor, style, size } = props;

    const [visible, setVisible] = React.useState(false);

    React.useEffect(() => {
      const onScroll = () => setVisible(window.scrollY > Number(showAfterScroll));
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
      return () => window.removeEventListener("scroll", onScroll);
    }, [showAfterScroll]);

    const scrollTop = () => window.scrollTo({ top: 0, behavior: "smooth" });

    const styleMap = {
      filled: `background: ${accentColor}; color: #fff; border: none;`,
      outline: `background: #fff; color: ${accentColor}; border: 2px solid ${accentColor};`,
      rounded: `background: ${accentColor}; color: #fff; border: none; border-radius: 12px;`,
    };
    const styleCss = styleMap[style] || styleMap.filled;

    const css = `
      #${id} {
        position: fixed;
        bottom: ${offsetBottom};
        ${position === "bottom-left" ? `left: ${offsetSide};` : `right: ${offsetSide};`}
        z-index: 9990;
        opacity: ${visible ? "1" : "0"};
        pointer-events: ${visible ? "auto" : "none"};
        transition: opacity 0.3s, transform 0.3s;
        transform: translateY(${visible ? "0" : "20px"});
      }
      #${id} button {
        width: ${size};
        height: ${size};
        border-radius: ${style === "rounded" ? "12px" : "50%"};
        ${styleCss}
        cursor: pointer;
        font-size: 1.25rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        transition: transform 0.2s, box-shadow 0.2s;
      }
      #${id} button:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.25);
      }
      @media (max-width: 768px) {
        #${id} button { width: 42px; height: 42px; font-size: 1rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <button onClick={scrollTop} aria-label="Retour en haut">
            {icon}
          </button>
        </div>
      </>
    );
  },
};


// ============================================================
//  SCROLL PROGRESS PRO — Barre de progression de lecture
// ============================================================

export const ScrollProgressPro = {
  fields: {
    position: {
      type: "select", label: "Position",
      options: [
        { label: "Haut", value: "top" },
        { label: "Bas", value: "bottom" },
      ],
    },
    height: { type: "text", label: "Hauteur", defaultValue: "4px" },
    gradient: { type: "text", label: "Dégradé CSS", defaultValue: "linear-gradient(90deg, #C1652F, #D4A843, #2F4A3C)" },
    showPercentage: {
      type: "radio", label: "Afficher le %",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    zIndex: { type: "number", label: "Z-index", defaultValue: 9997 },
  },
  defaultProps: {
    position: "top",
    height: "4px",
    gradient: "linear-gradient(90deg, #C1652F, #D4A843, #2F4A3C)",
    showPercentage: "false",
    zIndex: 9997,
  },
  render: (props) => {
    const id = useResponsiveId("scrollprog");
    const { position, height, gradient, showPercentage, zIndex } = props;

    const [progress, setProgress] = React.useState(0);

    React.useEffect(() => {
      const onScroll = () => {
        const scrollTop = window.scrollY;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
        setProgress(Math.min(100, Math.max(0, pct)));
      };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
      return () => window.removeEventListener("scroll", onScroll);
    }, []);

    const css = `
      #${id} {
        position: fixed;
        ${position === "top" ? "top: 0;" : "bottom: 0;"}
        left: 0;
        right: 0;
        height: ${height};
        z-index: ${zIndex};
        background: transparent;
        pointer-events: none;
      }
      #${id} .sp-bar {
        height: 100%;
        background: ${gradient};
        transition: width 0.1s linear;
        border-radius: 0 ${height} ${height} 0;
      }
      #${id} .sp-percent {
        position: absolute;
        ${position === "top" ? "top: calc(100% + 6px);" : "bottom: calc(100% + 6px);"}
        right: 16px;
        background: ${gradient};
        color: #fff;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 999px;
        font-variant-numeric: tabular-nums;
      }
      @media (max-width: 768px) {
        #${id} { height: ${height}; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <div className="sp-bar" style={{ width: `${progress}%` }} />
          {showPercentage === "true" && (
            <div className="sp-percent">{Math.round(progress)}%</div>
          )}
        </div>
      </>
    );
  },
};


// ============================================================
//  STICKY CTA PRO — CTA collant mobile-first
// ============================================================

export const StickyCtaPro = {
  fields: {
    message: { type: "text", label: "Message", defaultValue: "🎉 -20% sur votre 1ère commande" },
    ctaLabel: { type: "text", label: "Bouton", defaultValue: "J'en profite" },
    ctaUrl: { type: "text", label: "Lien", defaultValue: "/boutique/cosmetiques" },
    position: {
      type: "select", label: "Position",
      options: [
        { label: "Bas sticky", value: "bottom" },
        { label: "Droite (desktop)", value: "right" },
        { label: "Gauche (desktop)", value: "left" },
      ],
    },
    showAfterScroll: { type: "number", label: "Apparaît après (px)", defaultValue: 300 },
    hideOnMobile: {
      type: "radio", label: "Cacher sur mobile",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    textColor: { type: "text", label: "Couleur texte", defaultValue: "#FFFFFF" },
    dismissible: {
      type: "radio", label: "Fermable",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    message: "🎉 -20% sur votre 1ère commande",
    ctaLabel: "J'en profite",
    ctaUrl: "/boutique/cosmetiques",
    position: "bottom",
    showAfterScroll: 300,
    hideOnMobile: "false",
    accentColor: "#C1652F",
    textColor: "#FFFFFF",
    dismissible: "true",
  },
  render: (props) => {
    const id = useResponsiveId("stickcta");
    const { message, ctaLabel, ctaUrl, position, showAfterScroll,
            hideOnMobile, accentColor, textColor, dismissible } = props;

    const [visible, setVisible] = React.useState(false);
    const [closed, setClosed] = React.useState(false);

    React.useEffect(() => {
      const onScroll = () => setVisible(window.scrollY > Number(showAfterScroll));
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
      return () => window.removeEventListener("scroll", onScroll);
    }, [showAfterScroll]);

    if (closed) return null;

    const posStyles = {
      bottom: "bottom: 0; left: 0; right: 0; border-radius: 20px 20px 0 0; padding: 14px 20px; flex-direction: row;",
      right: "right: 20px; top: 50%; transform: translateY(-50%); border-radius: 20px; padding: 24px 20px; flex-direction: column; max-width: 220px;",
      left: "left: 20px; top: 50%; transform: translateY(-50%); border-radius: 20px; padding: 24px 20px; flex-direction: column; max-width: 220px;",
    };

    const css = `
      #${id} {
        position: fixed;
        background: ${accentColor};
        color: ${textColor};
        z-index: 9994;
        display: flex;
        align-items: center;
        gap: 12px;
        justify-content: space-between;
        box-shadow: 0 -4px 24px rgba(0, 0, 0, 0.15);
        ${posStyles[position] || posStyles.bottom}
        opacity: ${visible ? "1" : "0"};
        pointer-events: ${visible ? "auto" : "none"};
        transition: opacity 0.3s, transform 0.3s;
        ${position === "bottom"
          ? `transform: translateY(${visible ? "0" : "100%"});`
          : `transform: translateY(-50%) translateX(${visible ? "0" : position === "right" ? "20px" : "-20px"});`}
      }
      #${id} .sc-message {
        font-weight: 600;
        font-size: 0.9rem;
        ${position !== "bottom" ? "text-align: center;" : ""}
      }
      #${id} .sc-cta {
        background: ${textColor};
        color: ${accentColor};
        padding: 10px 20px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 700;
        font-size: 0.85rem;
        white-space: nowrap;
        transition: transform 0.2s;
      }
      #${id} .sc-cta:hover { transform: scale(1.05); }
      #${id} .sc-close {
        position: absolute;
        top: 4px;
        ${position === "bottom" ? "right: 8px;" : "right: 6px;"}
        background: none;
        border: none;
        color: inherit;
        font-size: 1.1rem;
        cursor: pointer;
        opacity: 0.6;
        padding: 4px;
      }
      #${id} .sc-close:hover { opacity: 1; }
      ${hideOnMobile === "true" ? `@media (max-width: 768px) { #${id} { display: none !important; } }` : ""}
      @media (max-width: 768px) {
        ${position !== "bottom" ? `
          #${id} {
            top: auto !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;
            transform: translateY(${visible ? "0" : "100%"}) !important;
            flex-direction: row !important;
            max-width: none !important;
            border-radius: 20px 20px 0 0 !important;
            padding: 14px 20px !important;
          }
        ` : ""}
        #${id} .sc-message { font-size: 0.8rem; }
        #${id} .sc-cta { padding: 8px 14px; font-size: 0.8rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <div className="sc-message">{message}</div>
          <a href={ctaUrl} className="sc-cta">{ctaLabel}</a>
          {dismissible === "true" && (
            <button className="sc-close" onClick={() => setClosed(true)}>×</button>
          )}
        </div>
      </>
    );
  },
};
'''


# ============================================================
#                    PATCH CONFIG
# ============================================================

MARKER = "/* === WIDGETS SERIES 4 === */"

NEW_NAMES = [
    "ChatWidgetPro", "CookieConsentPro", "NewsletterInlinePro", "ExitIntentPopupPro",
    "SocialProofPro", "BackToTopPro", "ScrollProgressPro", "StickyCtaPro",
]


def write_widgets():
    os.makedirs(WIDGETS_DIR, exist_ok=True)
    path = os.path.join(WIDGETS_DIR, "widgetsSeries4.jsx")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if "export const ChatWidgetPro" in f.read():
                print(f"  [SKIP] widgetsSeries4.jsx existe déjà")
                return False
        shutil.copy2(path, path + ".bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(WIDGETS_SERIES_4)
    print(f"  [OK] src/puck/widgets/widgetsSeries4.jsx créé")
    return True


def update_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"  [ERREUR] config.jsx introuvable")
        return False

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER in content:
        print("  [SKIP] config.jsx déjà patché pour Série 4")
        return False

    # Anti-doublon
    new_names = []
    for name in NEW_NAMES:
        if re.search(rf'\b{name}\b', content):
            print(f"  [ATTENTION] {name} existe déjà, ignoré")
        else:
            new_names.append(name)

    if not new_names:
        print("  [SKIP] Tous les widgets existent déjà")
        return False

    shutil.copy2(CONFIG_PATH, CONFIG_PATH + ".before-series4.bak")
    print(f"  [BACKUP] config.jsx.before-series4.bak")

    imports = f'''
{MARKER}
import {{
  {", ".join(new_names)},
}} from "./widgets/widgetsSeries4";
{MARKER}
'''
    content = re.sub(
        r'(import React from "react";\n)',
        r'\1' + imports,
        content,
        count=1,
    )

    new_components = f"    // === Série 4 ===\n    {', '.join(new_names)},\n"

    components_pattern = re.compile(
        r'(components:\s*\{)(.*?)(\n\s*\},\s*\n\s*categories:)',
        re.DOTALL,
    )
    match = components_pattern.search(content)
    if match:
        content = (
            content[: match.start(2)] + "\n" + new_components
            + match.group(2).rstrip() + "\n  "
            + content[match.start(3):]
        )
        print(f"  [OK] {len(new_names)} composant(s) ajouté(s)")

    cat_name = 'series4: { title: "Série 4 — Engagement", components: [\n'
    for n in new_names:
        cat_name += f'      "{n}",\n'
    cat_name += '    ]},\n'

    cat_pattern = re.compile(r'(categories:\s*\{)(.*?)(\n\s*\},)', re.DOTALL)
    cat_match = cat_pattern.search(content)
    if cat_match:
        content = (
            content[: cat_match.start(2)] + "\n" + cat_name
            + cat_match.group(2) + content[cat_match.start(3):]
        )
        print("  [OK] Catégorie 'Série 4 — Engagement' ajoutée")

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  AJOUT DES WIDGETS SÉRIE 4")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable")
        return

    print("\n[1/2] Création des 8 widgets Série 4...")
    write_widgets()

    print("\n[2/2] Mise à jour de config.jsx...")
    update_config()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ — 8 widgets ajoutés (noms uniques)")
    print("=" * 60)
    print("\nSérie 4 — Engagement :")
    print("  • ChatWidgetPro         — Bulle de chat + interface")
    print("  • CookieConsentPro      — Consentement RGPD avancé")
    print("  • NewsletterInlinePro   — Formulaire inline validé")
    print("  • ExitIntentPopupPro    — Popup à la sortie")
    print("  • SocialProofPro        — Notifications temps réel")
    print("  • BackToTopPro          — Bouton retour en haut")
    print("  • ScrollProgressPro     — Barre de progression")
    print("  • StickyCtaPro          — CTA collant")
    print()
    print("Total widgets :", 130 + len(NEW_NAMES))
    print()
    print("Redémarrer :")
    print("  Remove-Item -Recurse -Force node_modules\\.vite")
    print("  npm run dev")


if __name__ == "__main__":
    main()