/**
 * Widgets avancés Série 2 — Pricing, Stats, Steps, Team, Logos, Features.
 * Noms 100% uniques (pas de conflit).
 */
import React from "react";
import { useResponsiveId } from "../hooks/useResponsive";


// ============================================================
//  HELPERS
// ============================================================

function splitLines(text) {
  return String(text || "").split("\n").map((s) => s.trim()).filter(Boolean);
}

function useInViewOnce(options = {}) {
  const ref = React.useRef(null);
  const [visible, setVisible] = React.useState(false);
  React.useEffect(() => {
    if (!ref.current || visible) return;
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setVisible(true); },
      { threshold: 0.2, ...options }
    );
    obs.observe(ref.current);
    return () => obs.disconnect();
  }, [visible, options]);
  return [ref, visible];
}


// ============================================================
//  PRICING PRO — Tableau de tarifs avancé
// ============================================================

export const PricingPro = {
  fields: {
    planName: { type: "text", label: "Nom du plan", defaultValue: "Premium" },
    price: { type: "text", label: "Prix", defaultValue: "29.90" },
    currency: { type: "text", label: "Devise", defaultValue: "€" },
    period: { type: "text", label: "Période", defaultValue: "/mois" },
    description: { type: "text", label: "Description", defaultValue: "Pour les clients réguliers" },
    features: {
      type: "textarea", label: "Caractéristiques (✓ ou ✗ en préfixe)",
      defaultValue: "✓ Livraison offerte\n✓ Support 24/7\n✓ -10% permanent\n✗ Accès B2B\n✓ Retours gratuits",
    },
    ctaLabel: { type: "text", label: "Bouton", defaultValue: "Choisir ce plan" },
    ctaUrl: { type: "text", label: "Lien du bouton", defaultValue: "/inscription" },
    highlighted: {
      type: "radio", label: "Mis en avant",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    badge: { type: "text", label: "Badge (optionnel)", defaultValue: "" },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    showSavings: {
      type: "radio", label: "Afficher les économies",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    planName: "Premium",
    price: "29.90",
    currency: "€",
    period: "/mois",
    description: "Pour les clients réguliers",
    features: "✓ Livraison offerte\n✓ Support 24/7\n✓ -10% permanent\n✗ Accès B2B\n✓ Retours gratuits",
    ctaLabel: "Choisir ce plan",
    ctaUrl: "/inscription",
    highlighted: "false",
    badge: "",
    accentColor: "#C1652F",
    showSavings: "false",
  },
  render: (props) => {
    const id = useResponsiveId("pricingpro");
    const { planName, price, currency, period, description, features,
            ctaLabel, ctaUrl, highlighted, badge, accentColor, showSavings } = props;
    const isHighlighted = highlighted === "true";
    const featureList = splitLines(features);

    const css = `
      #${id} {
        background: ${isHighlighted ? "#2F4A3C" : "#FFFFFF"};
        color: ${isHighlighted ? "#F7F0E4" : "#221B15"};
        border-radius: 20px;
        padding: 32px 28px;
        box-shadow: ${isHighlighted
          ? `0 20px 40px ${accentColor}40, 0 0 0 2px ${accentColor}`
          : "0 4px 12px rgba(0,0,0,0.06)"};
        position: relative;
        transition: transform 0.3s, box-shadow 0.3s;
        height: 100%;
        display: flex;
        flex-direction: column;
      }
      #${id}:hover {
        transform: translateY(-6px);
        box-shadow: ${isHighlighted
          ? `0 24px 48px ${accentColor}50, 0 0 0 2px ${accentColor}`
          : "0 12px 32px rgba(0,0,0,0.12)"};
      }
      #${id} .pp-badge {
        position: absolute; top: -12px; left: 50%; transform: translateX(-50%);
        background: ${accentColor}; color: #fff;
        padding: 6px 16px; border-radius: 999px;
        font-size: 0.75rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.05em;
        white-space: nowrap;
      }
      #${id} .pp-price {
        display: flex; align-items: baseline; gap: 4px;
        margin: 16px 0;
      }
      #${id} .pp-price-amount {
        font-size: 3rem; font-weight: 800; line-height: 1;
        color: ${isHighlighted ? "#F7F0E4" : accentColor};
      }
      #${id} .pp-price-period {
        opacity: 0.7; font-size: 1rem;
      }
      #${id} .pp-features {
        list-style: none; padding: 0; margin: 20px 0;
        flex: 1;
      }
      #${id} .pp-features li {
        padding: 8px 0;
        display: flex; align-items: center; gap: 10px;
        font-size: 0.95rem;
        opacity: ${isHighlighted ? "0.95" : "0.9"};
      }
      #${id} .pp-features li.negative {
        opacity: 0.4;
        text-decoration: line-through;
      }
      #${id} .pp-cta {
        display: block;
        padding: 14px 24px;
        background: ${isHighlighted ? accentColor : "transparent"};
        color: ${isHighlighted ? "#fff" : accentColor};
        border: 2px solid ${accentColor};
        border-radius: 12px;
        text-decoration: none;
        text-align: center;
        font-weight: 700;
        transition: all 0.2s;
        margin-top: auto;
      }
      #${id} .pp-cta:hover {
        background: ${isHighlighted ? "#fff" : accentColor};
        color: ${isHighlighted ? accentColor : "#fff"};
      }
      @media (max-width: 768px) {
        #${id} { padding: 24px 20px; }
        #${id} .pp-price-amount { font-size: 2.5rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {badge && <span className="pp-badge">{badge}</span>}
          <h3 style={{ margin: 0, fontSize: "1.25rem", fontFamily: "var(--font-heading, serif)" }}>
            {planName}
          </h3>
          {description && (
            <p style={{ margin: "6px 0 0", opacity: 0.7, fontSize: "0.9rem" }}>{description}</p>
          )}
          <div className="pp-price">
            <span className="pp-price-amount">{price}{currency}</span>
            <span className="pp-price-period">{period}</span>
          </div>
          <ul className="pp-features">
            {featureList.map((f, i) => {
              const isNegative = f.startsWith("✗") || f.startsWith("x ");
              const text = f.replace(/^[✓✗x]\s*/, "");
              return (
                <li key={i} className={isNegative ? "negative" : ""}>
                  <span style={{
                    color: isNegative ? "#DC2626" : accentColor,
                    fontWeight: 700, fontSize: "1.1rem",
                  }}>
                    {isNegative ? "✗" : "✓"}
                  </span>
                  <span>{text}</span>
                </li>
              );
            })}
          </ul>
          <a href={ctaUrl} className="pp-cta">{ctaLabel}</a>
        </div>
      </>
    );
  },
};


// ============================================================
//  COUNTDOWN PRO — Compte à rebours avancé
// ============================================================

export const CountdownPro = {
  fields: {
    targetDate: {
      type: "text", label: "Date cible (format ISO)",
      defaultValue: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 19),
    },
    title: { type: "text", label: "Titre", defaultValue: "Offre limitée" },
    subtitle: { type: "text", label: "Sous-titre", defaultValue: "Ne ratez pas -20% sur tout le site" },
    layout: {
      type: "select", label: "Disposition",
      options: [
        { label: "Boîtes séparées", value: "boxes" },
        { label: "Bandeau horizontal", value: "inline" },
        { label: "Cartes", value: "cards" },
      ],
    },
    showDays: { type: "radio", label: "Jours", options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }] },
    showHours: { type: "radio", label: "Heures", options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }] },
    showMinutes: { type: "radio", label: "Minutes", options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }] },
    showSeconds: { type: "radio", label: "Secondes", options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }] },
    background: { type: "text", label: "Fond", defaultValue: "#221B15" },
    textColor: { type: "text", label: "Texte", defaultValue: "#F7F0E4" },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#D4A843" },
    borderRadius: { type: "text", label: "Arrondi", defaultValue: "20px" },
  },
  defaultProps: {
    targetDate: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().slice(0, 19),
    title: "Offre limitée",
    subtitle: "Ne ratez pas -20% sur tout le site",
    layout: "boxes",
    showDays: "true",
    showHours: "true",
    showMinutes: "true",
    showSeconds: "true",
    background: "#221B15",
    textColor: "#F7F0E4",
    accentColor: "#D4A843",
    borderRadius: "20px",
  },
  render: (props) => {
    const id = useResponsiveId("cdpro");
    const { targetDate, title, subtitle, layout, showDays, showHours,
            showMinutes, showSeconds, background, textColor, accentColor, borderRadius } = props;

    const calc = () => {
      const target = new Date(targetDate).getTime();
      const diff = Math.max(0, target - Date.now());
      return {
        d: Math.floor(diff / 86400000),
        h: Math.floor((diff % 86400000) / 3600000),
        m: Math.floor((diff % 3600000) / 60000),
        s: Math.floor((diff % 60000) / 1000),
      };
    };

    const [time, setTime] = React.useState(calc);
    React.useEffect(() => {
      const int = setInterval(() => setTime(calc()), 1000);
      return () => clearInterval(int);
    }, [targetDate]);

    const units = [];
    if (showDays === "true") units.push({ key: "d", label: "Jours", value: time.d });
    if (showHours === "true") units.push({ key: "h", label: "Heures", value: time.h });
    if (showMinutes === "true") units.push({ key: "m", label: "Minutes", value: time.m });
    if (showSeconds === "true") units.push({ key: "s", label: "Secondes", value: time.s });

    const css = `
      #${id} {
        background: ${background};
        color: ${textColor};
        padding: 40px 32px;
        border-radius: ${borderRadius};
        text-align: center;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .cd-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 8px; }
      #${id} .cd-subtitle { opacity: 0.8; margin-bottom: 24px; }
      #${id} .cd-units {
        display: flex;
        justify-content: center;
        gap: ${layout === "inline" ? "24px" : "16px"};
        flex-wrap: wrap;
      }
      #${id} .cd-unit {
        ${layout === "boxes" ? `
          background: rgba(255,255,255,0.08);
          padding: 16px 20px;
          border-radius: 12px;
          min-width: 80px;
        ` : ""}
        ${layout === "cards" ? `
          background: linear-gradient(135deg, ${accentColor}, ${accentColor}AA);
          color: #fff;
          padding: 20px 24px;
          border-radius: 16px;
          min-width: 90px;
          box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        ` : ""}
      }
      #${id} .cd-number {
        font-size: ${layout === "inline" ? "2.5rem" : "2.25rem"};
        font-weight: 800;
        color: ${layout === "cards" ? "#fff" : accentColor};
        line-height: 1;
        font-variant-numeric: tabular-nums;
      }
      #${id} .cd-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 6px;
        opacity: 0.7;
      }
      @media (max-width: 768px) {
        #${id} { padding: 28px 20px; }
        #${id} .cd-number { font-size: 1.75rem; }
        #${id} .cd-unit { min-width: 64px; padding: 12px 14px; }
        #${id} .cd-units { gap: 10px; }
        #${id} .cd-title { font-size: 1.25rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {title && <div className="cd-title">{title}</div>}
          {subtitle && <div className="cd-subtitle">{subtitle}</div>}
          <div className="cd-units">
            {units.map((u) => (
              <div key={u.key} className="cd-unit">
                <div className="cd-number">{String(u.value).padStart(2, "0")}</div>
                <div className="cd-label">{u.label}</div>
              </div>
            ))}
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  TESTIMONIAL WALL — Mur de témoignages masonry
// ============================================================

export const TestimonialWall = {
  fields: {
    testimonials: {
      type: "textarea", label: "Témoignages (citation|auteur|rôle|avatar, un par ligne)",
      defaultValue: "Service impeccable, livraison rapide !|Fatou D.|Cliente fidèle||Produits d'une qualité rare, je recommande vivement.|Aminata K.|Cliente||L'équipe est très à l'écoute, bravo !|Ibrahim S.|Client||Mes cheveux n'ont jamais été aussi beaux.|Awa B.|Cliente||Rapport qualité-prix imbattable.|Moussa T.|Client||Je commande chez NAWA depuis 2 ans, jamais déçu.|Nadia S.|Cliente",
    },
    columns: {
      type: "select", label: "Colonnes (desktop)",
      options: [
        { label: "2 colonnes", value: "2" },
        { label: "3 colonnes", value: "3" },
        { label: "4 colonnes", value: "4" },
      ],
    },
    cardBackground: { type: "text", label: "Fond carte", defaultValue: "#FFFFFF" },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    showStars: {
      type: "radio", label: "Afficher les étoiles",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    showAvatars: {
      type: "radio", label: "Afficher les avatars",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    gap: { type: "text", label: "Espacement", defaultValue: "20px" },
  },
  defaultProps: {
    testimonials: "Service impeccable, livraison rapide !|Fatou D.|Cliente fidèle||Produits d'une qualité rare, je recommande vivement.|Aminata K.|Cliente||L'équipe est très à l'écoute, bravo !|Ibrahim S.|Client||Mes cheveux n'ont jamais été aussi beaux.|Awa B.|Cliente||Rapport qualité-prix imbattable.|Moussa T.|Client||Je commande chez NAWA depuis 2 ans, jamais déçu.|Nadia S.|Cliente",
    columns: "3",
    cardBackground: "#FFFFFF",
    accentColor: "#C1652F",
    showStars: "true",
    showAvatars: "true",
    gap: "20px",
  },
  render: (props) => {
    const id = useResponsiveId("twall");
    const { testimonials, columns, cardBackground, accentColor, showStars, showAvatars, gap } = props;

    const items = splitLines(testimonials).map((line) => {
      const [quote, author, role, avatar] = line.split("|").map((s) => s.trim());
      return { quote, author, role, avatar };
    });

    const cols = Number(columns) || 3;

    const css = `
      #${id} {
        display: grid;
        grid-template-columns: repeat(${cols}, 1fr);
        gap: ${gap};
        width: 100%;
      }
      #${id} .tw-card {
        background: ${cardBackground};
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        transition: transform 0.3s, box-shadow 0.3s;
        break-inside: avoid;
      }
      #${id} .tw-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
      }
      #${id} .tw-stars {
        color: #D4A843;
        font-size: 1rem;
        margin-bottom: 12px;
        letter-spacing: 2px;
      }
      #${id} .tw-quote {
        font-style: italic;
        line-height: 1.6;
        margin-bottom: 16px;
        color: #221B15;
      }
      #${id} .tw-author {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      #${id} .tw-avatar {
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
        overflow: hidden;
      }
      #${id} .tw-avatar img { width: 100%; height: 100%; object-fit: cover; }
      #${id} .tw-name { font-weight: 600; font-size: 0.95rem; }
      #${id} .tw-role { color: #6B6259; font-size: 0.8rem; }
      @media (max-width: 1024px) {
        #${id} { grid-template-columns: repeat(2, 1fr); }
      }
      @media (max-width: 768px) {
        #${id} { grid-template-columns: 1fr; gap: 12px; }
        #${id} .tw-card { padding: 20px; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {items.map((t, i) => (
            <article key={i} className="tw-card">
              {showStars === "true" && <div className="tw-stars">★★★★★</div>}
              <p className="tw-quote">"{t.quote}"</p>
              <div className="tw-author">
                {showAvatars === "true" && (
                  <div className="tw-avatar">
                    {t.avatar ? (
                      <img src={t.avatar} alt={t.author} />
                    ) : (
                      (t.author || "?").split(" ").map((s) => s[0]).join("").slice(0, 2).toUpperCase()
                    )}
                  </div>
                )}
                <div>
                  <div className="tw-name">{t.author}</div>
                  <div className="tw-role">{t.role}</div>
                </div>
              </div>
            </article>
          ))}
        </div>
      </>
    );
  },
};


// ============================================================
//  STATS SECTION — Bandeau de statistiques animées
// ============================================================

export const StatsSection = {
  fields: {
    stats: {
      type: "textarea", label: "Stats (valeur|suffixe|label, un par ligne)",
      defaultValue: "1250|+|Clients satisfaits\n42|%|Croissance annuelle\n15|+|Marques partenaires\n4.8|/5|Note moyenne",
    },
    columns: {
      type: "select", label: "Colonnes",
      options: [
        { label: "2 colonnes", value: "2" },
        { label: "3 colonnes", value: "3" },
        { label: "4 colonnes", value: "4" },
      ],
    },
    animateOnScroll: {
      type: "radio", label: "Animation au scroll",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    duration: { type: "number", label: "Durée animation (ms)", defaultValue: 2000 },
    background: { type: "text", label: "Fond", defaultValue: "#F7F0E4" },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    numberColor: { type: "text", label: "Couleur nombres", defaultValue: "#221B15" },
    borderRadius: { type: "text", label: "Arrondi", defaultValue: "20px" },
  },
  defaultProps: {
    stats: "1250|+|Clients satisfaits\n42|%|Croissance annuelle\n15|+|Marques partenaires\n4.8|/5|Note moyenne",
    columns: "4",
    animateOnScroll: "true",
    duration: 2000,
    background: "#F7F0E4",
    accentColor: "#C1652F",
    numberColor: "#221B15",
    borderRadius: "20px",
  },
  render: (props) => {
    const id = useResponsiveId("statssect");
    const { stats, columns, animateOnScroll, duration, background,
            accentColor, numberColor, borderRadius } = props;
    const [ref, visible] = useInViewOnce();

    const items = splitLines(stats).map((line) => {
      const [value, suffix, label] = line.split("|").map((s) => s.trim());
      return { value: Number(value) || 0, suffix: suffix || "", label: label || "" };
    });

    const cols = Number(columns) || 4;
    const shouldAnimate = animateOnScroll === "true";

    const css = `
      #${id} {
        background: ${background};
        padding: 48px 32px;
        border-radius: ${borderRadius};
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .ss-grid {
        display: grid;
        grid-template-columns: repeat(${cols}, 1fr);
        gap: 24px;
        max-width: 1100px;
        margin: 0 auto;
      }
      #${id} .ss-item {
        text-align: center;
      }
      #${id} .ss-value {
        font-size: 3rem;
        font-weight: 800;
        color: ${numberColor};
        line-height: 1;
        font-variant-numeric: tabular-nums;
      }
      #${id} .ss-suffix {
        color: ${accentColor};
        font-size: 2rem;
      }
      #${id} .ss-label {
        margin-top: 8px;
        color: #6B6259;
        font-size: 0.9rem;
      }
      @media (max-width: 1024px) {
        #${id} .ss-grid { grid-template-columns: repeat(2, 1fr); }
      }
      @media (max-width: 768px) {
        #${id} { padding: 32px 20px; }
        #${id} .ss-value { font-size: 2.25rem; }
        #${id} .ss-grid { grid-template-columns: repeat(2, 1fr); gap: 20px; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id} ref={ref}>
          <div className="ss-grid">
            {items.map((s, i) => (
              <StatItem key={i} {...s} animate={shouldAnimate} visible={visible} duration={duration} />
            ))}
          </div>
        </div>
      </>
    );
  },
};

function StatItem({ value, suffix, label, animate, visible, duration }) {
  const [count, setCount] = React.useState(animate ? 0 : value);
  const isDecimal = !Number.isInteger(value);

  React.useEffect(() => {
    if (!animate || !visible) {
      if (!animate) setCount(value);
      return;
    }
    const start = Date.now();
    const step = () => {
      const progress = Math.min(1, (Date.now() - start) / duration);
      // Ease out
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(value * eased);
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [visible, animate, value, duration]);

  const display = isDecimal ? count.toFixed(1) : Math.floor(count).toLocaleString("fr-FR");

  return (
    <div className="ss-item">
      <div className="ss-value">
        {display}
        {suffix && <span className="ss-suffix">{suffix}</span>}
      </div>
      <div className="ss-label">{label}</div>
    </div>
  );
}


// ============================================================
//  STEPS PROCESS — Étapes numérotées
// ============================================================

export const StepsProcess = {
  fields: {
    steps: {
      type: "textarea", label: "Étapes (titre|description, un par ligne)",
      defaultValue: "Choisissez vos produits|Parcourez notre catalogue et ajoutez au panier.\nPassez commande|Remplissez vos informations de livraison.\nRecevez votre colis|Livraison en 48-72h partout en Afrique de l'Ouest.\nProfitez !|Utilisez vos produits et laissez un avis.",
    },
    layout: {
      type: "select", label: "Disposition",
      options: [
        { label: "Horizontal", value: "horizontal" },
        { label: "Vertical", value: "vertical" },
        { label: "Alterné (zigzag)", value: "alternate" },
      ],
    },
    numberColor: { type: "text", label: "Couleur des numéros", defaultValue: "#C1652F" },
    lineColor: { type: "text", label: "Couleur de la ligne", defaultValue: "#e5e5e5" },
    showConnector: {
      type: "radio", label: "Afficher les connecteurs",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    background: { type: "text", label: "Fond", defaultValue: "transparent" },
  },
  defaultProps: {
    steps: "Choisissez vos produits|Parcourez notre catalogue et ajoutez au panier.\nPassez commande|Remplissez vos informations de livraison.\nRecevez votre colis|Livraison en 48-72h partout en Afrique de l'Ouest.\nProfitez !|Utilisez vos produits et laissez un avis.",
    layout: "horizontal",
    numberColor: "#C1652F",
    lineColor: "#e5e5e5",
    showConnector: "true",
    background: "transparent",
  },
  render: (props) => {
    const id = useResponsiveId("steps");
    const { steps, layout, numberColor, lineColor, showConnector, background } = props;

    const items = splitLines(steps).map((line) => {
      const [title, ...descParts] = line.split("|");
      return { title: title.trim(), description: descParts.join("|").trim() };
    });

    const isHorizontal = layout === "horizontal";
    const isAlternate = layout === "alternate";

    const css = `
      #${id} {
        background: ${background};
        padding: 40px 20px;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .steps-container {
        display: ${isHorizontal ? "flex" : "block"};
        ${isHorizontal ? "gap: 0;" : ""}
        max-width: 1100px;
        margin: 0 auto;
        position: relative;
      }
      #${id} .step {
        ${isHorizontal ? "flex: 1; text-align: center; position: relative; padding: 0 16px;" : "display: flex; gap: 24px; margin-bottom: 40px; position: relative;"}
        ${isAlternate ? `
          display: flex;
          gap: 32px;
          margin-bottom: 48px;
          align-items: center;
          flex-direction: ${"row"};
        ` : ""}
      }
      #${id} .step-number {
        width: 56px; height: 56px;
        border-radius: 50%;
        background: ${numberColor};
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.25rem;
        flex-shrink: 0;
        position: relative;
        z-index: 2;
        box-shadow: 0 4px 12px ${numberColor}40;
        ${isHorizontal ? "margin: 0 auto 16px;" : ""}
      }
      #${id} .step-content {
        ${isHorizontal ? "" : "flex: 1; padding-top: 8px;"}
      }
      #${id} .step-title {
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 8px;
        color: #221B15;
      }
      #${id} .step-desc {
        color: #6B6259;
        line-height: 1.6;
        font-size: 0.95rem;
      }
      ${isHorizontal && showConnector === "true" ? `
        #${id} .step:not(:last-child)::after {
          content: "";
          position: absolute;
          top: 28px;
          left: 50%;
          width: 100%;
          height: 2px;
          background: ${lineColor};
          z-index: 1;
        }
      ` : ""}
      ${!isHorizontal && showConnector === "true" ? `
        #${id} .step:not(:last-child)::after {
          content: "";
          position: absolute;
          top: 64px;
          left: 27px;
          width: 2px;
          height: calc(100% - 40px);
          background: ${lineColor};
        }
      ` : ""}
      @media (max-width: 768px) {
        #${id} .steps-container {
          display: block !important;
        }
        #${id} .step {
          display: flex !important;
          gap: 20px !important;
          text-align: left !important;
          margin-bottom: 32px !important;
          padding: 0 !important;
          flex-direction: row !important;
        }
        #${id} .step-number {
          margin: 0 !important;
          width: 44px; height: 44px;
          font-size: 1rem;
        }
        #${id} .step:not(:last-child)::after {
          content: "";
          position: absolute;
          top: 52px;
          left: 21px;
          width: 2px;
          height: calc(100% - 32px);
          background: ${lineColor};
        }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <div className="steps-container">
            {items.map((step, i) => (
              <div key={i} className="step">
                <div className="step-number">{i + 1}</div>
                <div className="step-content">
                  <div className="step-title">{step.title}</div>
                  <div className="step-desc">{step.description}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  TEAM GRID — Grille d'équipe
// ============================================================

export const TeamGrid = {
  fields: {
    members: {
      type: "textarea", label: "Membres (nom|rôle|avatar URL, un par ligne)",
      defaultValue: "Aïcha Koné|Fondatrice & CEO|\nFatou Diallo|Directrice Artistique|\nIbrahim Sissoko|Responsable Technique|\nAwa Traoré|Head of Marketing|",
    },
    columns: {
      type: "select", label: "Colonnes (desktop)",
      options: [
        { label: "2 colonnes", value: "2" },
        { label: "3 colonnes", value: "3" },
        { label: "4 colonnes", value: "4" },
      ],
    },
    showRole: {
      type: "radio", label: "Afficher le rôle",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    showSocial: {
      type: "radio", label: "Afficher les réseaux sociaux",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    avatarShape: {
      type: "select", label: "Forme de l'avatar",
      options: [
        { label: "Cercle", value: "circle" },
        { label: "Carré arrondi", value: "rounded" },
      ],
    },
    cardStyle: {
      type: "select", label: "Style de carte",
      options: [
        { label: "Ombre", value: "shadow" },
        { label: "Bordure", value: "border" },
        { label: "Minimal", value: "minimal" },
      ],
    },
  },
  defaultProps: {
    members: "Aïcha Koné|Fondatrice & CEO|\nFatou Diallo|Directrice Artistique|\nIbrahim Sissoko|Responsable Technique|\nAwa Traoré|Head of Marketing|",
    columns: "4",
    showRole: "true",
    showSocial: "true",
    accentColor: "#C1652F",
    avatarShape: "circle",
    cardStyle: "shadow",
  },
  render: (props) => {
    const id = useResponsiveId("teamgrid");
    const { members, columns, showRole, showSocial, accentColor, avatarShape, cardStyle } = props;

    const items = splitLines(members).map((line) => {
      const [name, role, avatar] = line.split("|").map((s) => s.trim());
      return { name, role, avatar };
    });

    const cols = Number(columns) || 4;

    const cardBase = {
      shadow: "box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: none;",
      border: "border: 1px solid #e5e5e5; box-shadow: none;",
      minimal: "border: none; box-shadow: none; background: transparent; padding: 0;",
    }[cardStyle] || "";

    const css = `
      #${id} {
        display: grid;
        grid-template-columns: repeat(${cols}, 1fr);
        gap: 24px;
        width: 100%;
      }
      #${id} .team-card {
        ${cardBase}
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        background: ${cardStyle === "minimal" ? "transparent" : "#fff"};
        transition: transform 0.3s;
      }
      #${id} .team-card:hover {
        transform: translateY(-4px);
      }
      #${id} .team-avatar {
        width: 100px;
        height: 100px;
        margin: 0 auto 16px;
        background: ${accentColor};
        color: #fff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: 700;
        border-radius: ${avatarShape === "circle" ? "50%" : "16px"};
        overflow: hidden;
      }
      #${id} .team-avatar img {
        width: 100%; height: 100%;
        object-fit: cover;
      }
      #${id} .team-name {
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 4px;
      }
      #${id} .team-role {
        color: #6B6259;
        font-size: 0.85rem;
        margin-bottom: 12px;
      }
      #${id} .team-social {
        display: flex;
        justify-content: center;
        gap: 8px;
      }
      #${id} .team-social a {
        width: 32px; height: 32px;
        border-radius: 50%;
        background: ${accentColor}15;
        color: ${accentColor};
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        font-size: 0.9rem;
        transition: all 0.2s;
      }
      #${id} .team-social a:hover {
        background: ${accentColor};
        color: #fff;
      }
      @media (max-width: 1024px) {
        #${id} { grid-template-columns: repeat(2, 1fr); }
      }
      @media (max-width: 768px) {
        #${id} { grid-template-columns: repeat(2, 1fr); gap: 16px; }
        #${id} .team-card { padding: 16px; }
        #${id} .team-avatar { width: 72px; height: 72px; font-size: 1.4rem; }
        #${id} .team-name { font-size: 0.95rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {items.map((m, i) => (
            <div key={i} className="team-card">
              <div className="team-avatar">
                {m.avatar ? (
                  <img src={m.avatar} alt={m.name} />
                ) : (
                  (m.name || "?").split(" ").map((s) => s[0]).join("").slice(0, 2).toUpperCase()
                )}
              </div>
              <div className="team-name">{m.name}</div>
              {showRole === "true" && <div className="team-role">{m.role}</div>}
              {showSocial === "true" && (
                <div className="team-social">
                  <a href="#" title="LinkedIn">in</a>
                  <a href="#" title="Twitter">𝕏</a>
                  <a href="#" title="Email">✉</a>
                </div>
              )}
            </div>
          ))}
        </div>
      </>
    );
  },
};


// ============================================================
//  LOGO CLOUD — Nuage de logos
// ============================================================

export const LogoCloud = {
  fields: {
    logos: {
      type: "textarea", label: "Logos (URL, un par ligne)",
      defaultValue: "/fallbacks/brand-fallback.jpg\n/fallbacks/brand-fallback.jpg\n/fallbacks/brand-fallback.jpg\n/fallbacks/brand-fallback.jpg\n/fallbacks/brand-fallback.jpg",
    },
    title: { type: "text", label: "Titre", defaultValue: "Ils nous font confiance" },
    columns: {
      type: "select", label: "Colonnes",
      options: [
        { label: "3 colonnes", value: "3" },
        { label: "4 colonnes", value: "4" },
        { label: "5 colonnes", value: "5" },
        { label: "6 colonnes", value: "6" },
      ],
    },
    logoHeight: { type: "text", label: "Hauteur des logos", defaultValue: "60px" },
    grayscale: {
      type: "radio", label: "Noir et blanc",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    hoverColor: {
      type: "radio", label: "Couleur au survol",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    gap: { type: "text", label: "Espacement", defaultValue: "32px" },
  },
  defaultProps: {
    logos: "/fallbacks/brand-fallback.jpg\n/fallbacks/brand-fallback.jpg\n/fallbacks/brand-fallback.jpg\n/fallbacks/brand-fallback.jpg\n/fallbacks/brand-fallback.jpg",
    title: "Ils nous font confiance",
    columns: "5",
    logoHeight: "60px",
    grayscale: "true",
    hoverColor: "true",
    gap: "32px",
  },
  render: (props) => {
    const id = useResponsiveId("logocloud");
    const { logos, title, columns, logoHeight, grayscale, hoverColor, gap } = props;
    const items = splitLines(logos);
    const cols = Number(columns) || 5;

    const css = `
      #${id} {
        text-align: center;
        padding: 40px 20px;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .lc-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        color: #6B6259;
        margin-bottom: 32px;
        font-weight: 600;
      }
      #${id} .lc-grid {
        display: grid;
        grid-template-columns: repeat(${cols}, 1fr);
        gap: ${gap};
        align-items: center;
        max-width: 1100px;
        margin: 0 auto;
      }
      #${id} .lc-logo {
        display: flex;
        align-items: center;
        justify-content: center;
        height: ${logoHeight};
        filter: ${grayscale === "true" ? "grayscale(100%)" : "none"};
        opacity: ${grayscale === "true" ? "0.6" : "1"};
        transition: all 0.3s;
      }
      #${id} .lc-logo img {
        max-height: 100%;
        max-width: 100%;
        object-fit: contain;
      }
      ${hoverColor === "true" ? `
        #${id} .lc-logo:hover {
          filter: none;
          opacity: 1;
          transform: scale(1.05);
        }
      ` : ""}
      @media (max-width: 768px) {
        #${id} .lc-grid { grid-template-columns: repeat(3, 1fr); gap: 20px; }
        #${id} .lc-logo { height: 40px; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {title && <div className="lc-title">{title}</div>}
          <div className="lc-grid">
            {items.map((url, i) => (
              <div key={i} className="lc-logo">
                <img src={url} alt={`Logo ${i + 1}`} loading="lazy" />
              </div>
            ))}
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  FEATURE LIST — Liste de features avec checkmarks
// ============================================================

export const FeatureList = {
  fields: {
    features: {
      type: "textarea", label: "Features (titre|description, un par ligne)",
      defaultValue: "✓ Livraison offerte dès 49€|Partout en Afrique de l'Ouest en 48-72h\n✓ Paiement sécurisé|Stripe, PayPal, mobile money\n✓ Retours gratuits|30 jours pour changer d'avis\n✓ Support client 7j/7|Par chat, email ou WhatsApp\n✓ Produits naturels|Traçabilité complète jusqu'aux productrices\n✓ Programme fidélité|Cumulez des points à chaque achat",
    },
    layout: {
      type: "select", label: "Disposition",
      options: [
        { label: "1 colonne", value: "1" },
        { label: "2 colonnes", value: "2" },
        { label: "3 colonnes", value: "3" },
      ],
    },
    iconColor: { type: "text", label: "Couleur icône", defaultValue: "#16A34A" },
    iconBackground: { type: "text", label: "Fond icône", defaultValue: "#DCFCE7" },
    showIcon: {
      type: "radio", label: "Afficher l'icône",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    features: "✓ Livraison offerte dès 49€|Partout en Afrique de l'Ouest en 48-72h\n✓ Paiement sécurisé|Stripe, PayPal, mobile money\n✓ Retours gratuits|30 jours pour changer d'avis\n✓ Support client 7j/7|Par chat, email ou WhatsApp\n✓ Produits naturels|Traçabilité complète jusqu'aux productrices\n✓ Programme fidélité|Cumulez des points à chaque achat",
    layout: "2",
    iconColor: "#16A34A",
    iconBackground: "#DCFCE7",
    showIcon: "true",
  },
  render: (props) => {
    const id = useResponsiveId("featlist");
    const { features, layout, iconColor, iconBackground, showIcon } = props;

    const items = splitLines(features).map((line) => {
      const [title, ...descParts] = line.split("|");
      return {
        title: title.replace(/^✓\s*/, "").trim(),
        description: descParts.join("|").trim(),
      };
    });

    const cols = Number(layout) || 2;

    const css = `
      #${id} {
        display: grid;
        grid-template-columns: repeat(${cols}, 1fr);
        gap: 24px;
        width: 100%;
      }
      #${id} .fl-item {
        display: flex;
        gap: 16px;
        align-items: flex-start;
      }
      #${id} .fl-icon {
        width: 36px; height: 36px;
        background: ${iconBackground};
        color: ${iconColor};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-weight: 700;
        font-size: 1rem;
      }
      #${id} .fl-title {
        font-weight: 600;
        margin-bottom: 4px;
        color: #221B15;
      }
      #${id} .fl-desc {
        color: #6B6259;
        font-size: 0.9rem;
        line-height: 1.5;
      }
      @media (max-width: 768px) {
        #${id} { grid-template-columns: 1fr; gap: 16px; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {items.map((f, i) => (
            <div key={i} className="fl-item">
              {showIcon === "true" && <div className="fl-icon">✓</div>}
              <div>
                <div className="fl-title">{f.title}</div>
                {f.description && <div className="fl-desc">{f.description}</div>}
              </div>
            </div>
          ))}
        </div>
      </>
    );
  },
};
