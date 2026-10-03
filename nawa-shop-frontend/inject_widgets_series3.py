"""
Ajoute 8 widgets avancés Série 3 — noms 100% uniques.
Aucun conflit avec les 122 widgets existants.

Usage : python inject_widgets_series3.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
WIDGETS_DIR = os.path.join(SRC_DIR, "puck", "widgets")
CONFIG_PATH = os.path.join(SRC_DIR, "puck", "config.jsx")


# ============================================================
#              WIDGETS SÉRIE 3
# ============================================================

WIDGETS_SERIES_3 = '''/**
 * Widgets avancés Série 3 — FAQ, Timeline, Comparison, Before/After,
 * ProgressRing, RatingBreakdown, NotificationBanner, TrustBadges.
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
//  FAQ PRO — FAQ avec catégories
// ============================================================

export const FaqPro = {
  fields: {
    items: {
      type: "textarea",
      label: "Questions (question|réponse|catégorie — 1 par ligne)",
      defaultValue: "Quels sont les délais de livraison ?|Livraison en 48-72h partout en Afrique de l'Ouest.|Livraison\\nPuis-je retourner un produit ?|Oui, sous 30 jours, retour gratuit.|Retours\\nQuels moyens de paiement acceptez-vous ?|Stripe, PayPal et mobile money (Orange, MTN, Wave).|Paiement\\nLivrez-vous à l'international ?|Pour l'instant, nous livrons uniquement en Afrique de l'Ouest.|Livraison\\nProposez-vous des échantillons ?|Oui, sur demande pour les commandes > 50€.|Produits\\nComment fonctionne le programme fidélité ?|1€ dépensé = 1 point, 100 points = 5€ de réduction.|Fidélité",
    },
    title: { type: "text", label: "Titre", defaultValue: "Questions fréquentes" },
    subtitle: { type: "text", label: "Sous-titre", defaultValue: "Tout ce que vous devez savoir sur NAWA" },
    showSearch: {
      type: "radio", label: "Barre de recherche",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    showCategories: {
      type: "radio", label: "Filtres par catégorie",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    columns: {
      type: "select", label: "Disposition",
      options: [
        { label: "1 colonne", value: "1" },
        { label: "2 colonnes", value: "2" },
      ],
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    cardBackground: { type: "text", label: "Fond des cartes", defaultValue: "#FFFFFF" },
    expandFirst: {
      type: "radio", label: "Ouvrir la première",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    items: "Quels sont les délais de livraison ?|Livraison en 48-72h partout en Afrique de l'Ouest.|Livraison\\nPuis-je retourner un produit ?|Oui, sous 30 jours, retour gratuit.|Retours\\nQuels moyens de paiement acceptez-vous ?|Stripe, PayPal et mobile money (Orange, MTN, Wave).|Paiement\\nLivrez-vous à l'international ?|Pour l'instant, nous livrons uniquement en Afrique de l'Ouest.|Livraison\\nProposez-vous des échantillons ?|Oui, sur demande pour les commandes > 50€.|Produits\\nComment fonctionne le programme fidélité ?|1€ dépensé = 1 point, 100 points = 5€ de réduction.|Fidélité",
    title: "Questions fréquentes",
    subtitle: "Tout ce que vous devez savoir sur NAWA",
    showSearch: "true",
    showCategories: "true",
    columns: "1",
    accentColor: "#C1652F",
    cardBackground: "#FFFFFF",
    expandFirst: "true",
  },
  render: (props) => {
    const id = useResponsiveId("faqpro");
    const { items, title, subtitle, showSearch, showCategories,
            columns, accentColor, cardBackground, expandFirst } = props;

    const parsed = splitLines(items).map((line) => {
      const [q, a, cat] = line.split("|").map((s) => s.trim());
      return { question: q, answer: a, category: cat || "Général" };
    });

    const categories = ["Toutes", ...Array.from(new Set(parsed.map((p) => p.category)))];
    const [search, setSearch] = React.useState("");
    const [activeCat, setActiveCat] = React.useState("Toutes");
    const [openSet, setOpenSet] = React.useState(() => {
      const s = new Set();
      if (expandFirst === "true" && parsed.length > 0) s.add(0);
      return s;
    });

    const filtered = parsed.filter((p) => {
      const matchesCat = activeCat === "Toutes" || p.category === activeCat;
      const matchesSearch = !search || p.question.toLowerCase().includes(search.toLowerCase()) || p.answer.toLowerCase().includes(search.toLowerCase());
      return matchesCat && matchesSearch;
    });

    const toggle = (globalIndex) => {
      const s = new Set(openSet);
      s.has(globalIndex) ? s.delete(globalIndex) : s.add(globalIndex);
      setOpenSet(s);
    };

    const css = `
      #${id} {
        padding: 60px 24px;
        max-width: 1200px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .faq-header { text-align: center; margin-bottom: 40px; }
      #${id} .faq-title { font-size: 2rem; margin-bottom: 8px; }
      #${id} .faq-subtitle { color: #6B6259; font-size: 1.05rem; }
      #${id} .faq-search {
        max-width: 500px;
        margin: 24px auto 0;
        position: relative;
      }
      #${id} .faq-search input {
        width: 100%;
        padding: 12px 20px 12px 44px;
        border: 2px solid #e5e5e5;
        border-radius: 999px;
        font-size: 0.95rem;
        outline: none;
        transition: border-color 0.2s;
        box-sizing: border-box;
      }
      #${id} .faq-search input:focus { border-color: ${accentColor}; }
      #${id} .faq-search::before {
        content: "🔍";
        position: absolute;
        left: 16px; top: 50%;
        transform: translateY(-50%);
        font-size: 1rem;
        opacity: 0.5;
      }
      #${id} .faq-cats {
        display: flex;
        justify-content: center;
        gap: 8px;
        flex-wrap: wrap;
        margin: 20px 0 32px;
      }
      #${id} .faq-cat {
        padding: 6px 16px;
        border-radius: 999px;
        border: 1px solid #e5e5e5;
        background: #fff;
        cursor: pointer;
        font-size: 0.85rem;
        transition: all 0.2s;
      }
      #${id} .faq-cat.active {
        background: ${accentColor};
        color: #fff;
        border-color: ${accentColor};
      }
      #${id} .faq-grid {
        display: grid;
        grid-template-columns: repeat(${columns}, 1fr);
        gap: 12px;
      }
      #${id} .faq-item {
        background: ${cardBackground};
        border: 1px solid #e5e5e5;
        border-radius: 12px;
        overflow: hidden;
        transition: border-color 0.2s, box-shadow 0.2s;
      }
      #${id} .faq-item.open {
        border-color: ${accentColor};
        box-shadow: 0 4px 12px ${accentColor}20;
      }
      #${id} .faq-q {
        width: 100%;
        padding: 18px 20px;
        background: none;
        border: none;
        cursor: pointer;
        text-align: left;
        font-weight: 600;
        font-size: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
      }
      #${id} .faq-icon {
        color: ${accentColor};
        font-size: 1.25rem;
        flex-shrink: 0;
        transition: transform 0.3s;
      }
      #${id} .faq-item.open .faq-icon { transform: rotate(45deg); }
      #${id} .faq-a {
        padding: 0 20px 18px;
        color: #6B6259;
        line-height: 1.6;
        font-size: 0.95rem;
      }
      @media (max-width: 768px) {
        #${id} { padding: 40px 16px; }
        #${id} .faq-grid { grid-template-columns: 1fr; }
        #${id} .faq-title { font-size: 1.5rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <section id={id}>
          <div className="faq-header">
            {title && <h2 className="faq-title">{title}</h2>}
            {subtitle && <p className="faq-subtitle">{subtitle}</p>}
            {showSearch === "true" && (
              <div className="faq-search">
                <input
                  type="search"
                  placeholder="Rechercher une question..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
            )}
          </div>
          {showCategories === "true" && (
            <div className="faq-cats">
              {categories.map((c) => (
                <button
                  key={c}
                  className={`faq-cat ${activeCat === c ? "active" : ""}`}
                  onClick={() => setActiveCat(c)}
                >
                  {c}
                </button>
              ))}
            </div>
          )}
          <div className="faq-grid">
            {filtered.length === 0 ? (
              <p style={{ textAlign: "center", color: "#6B6259", gridColumn: "1 / -1" }}>
                Aucune question ne correspond à votre recherche.
              </p>
            ) : (
              filtered.map((item, i) => {
                const isOpen = openSet.has(parsed.indexOf(item));
                return (
                  <div key={i} className={`faq-item ${isOpen ? "open" : ""}`}>
                    <button className="faq-q" onClick={() => toggle(parsed.indexOf(item))}>
                      <span>{item.question}</span>
                      <span className="faq-icon">+</span>
                    </button>
                    {isOpen && <div className="faq-a">{item.answer}</div>}
                  </div>
                );
              })
            )}
          </div>
        </section>
      </>
    );
  },
};


// ============================================================
//  TIMELINE PRO — Chronologie verticale/horizontale
// ============================================================

export const TimelinePro = {
  fields: {
    events: {
      type: "textarea",
      label: "Événements (date|titre|description|icône — 1 par ligne)",
      defaultValue: "2018|Création de NAWA|Naissance de l'idée chez Aïcha Koné.|🌱\\n2020|Première boutique|Ouverture à Abidjan, 50 produits.|🏪\\n2022|100 000 clients|Cap symbolique franchi.|🎉\\n2024|Expansion régionale|Livraison au Sénégal, Mali, Burkina.|🌍\\n2026|Application mobile|Lancement de l'app iOS et Android.|📱",
    },
    orientation: {
      type: "select", label: "Orientation",
      options: [
        { label: "Verticale", value: "vertical" },
        { label: "Horizontale", value: "horizontal" },
        { label: "Alternée (zigzag)", value: "alternate" },
      ],
    },
    lineColor: { type: "text", label: "Couleur de la ligne", defaultValue: "#e5e5e5" },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    dotSize: { type: "text", label: "Taille des points", defaultValue: "20px" },
    showIcons: {
      type: "radio", label: "Afficher les icônes",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    animated: {
      type: "radio", label: "Animation à l'apparition",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    events: "2018|Création de NAWA|Naissance de l'idée chez Aïcha Koné.|🌱\\n2020|Première boutique|Ouverture à Abidjan, 50 produits.|🏪\\n2022|100 000 clients|Cap symbolique franchi.|🎉\\n2024|Expansion régionale|Livraison au Sénégal, Mali, Burkina.|🌍\\n2026|Application mobile|Lancement de l'app iOS et Android.|📱",
    orientation: "vertical",
    lineColor: "#e5e5e5",
    accentColor: "#C1652F",
    dotSize: "20px",
    showIcons: "true",
    animated: "true",
  },
  render: (props) => {
    const id = useResponsiveId("timeline");
    const { events, orientation, lineColor, accentColor, dotSize, showIcons, animated } = props;

    const items = splitLines(events).map((line) => {
      const [date, title, description, icon] = line.split("|").map((s) => s.trim());
      return { date, title, description, icon };
    });

    const [ref, visible] = useInViewOnce();
    const isVertical = orientation === "vertical";
    const isAlternate = orientation === "alternate";
    const isAnimated = animated === "true";

    const css = `
      #${id} {
        padding: 40px 24px;
        max-width: 1200px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .tl-container {
        position: relative;
        ${isVertical ? "padding-left: 40px;" : ""}
      }
      ${isVertical ? `
        #${id} .tl-container::before {
          content: "";
          position: absolute;
          left: 9px; top: 0; bottom: 0;
          width: 2px;
          background: ${lineColor};
        }
      ` : ""}
      #${id} .tl-list {
        ${isVertical ? "display: block;" : "display: flex; gap: 0; overflow-x: auto; padding-bottom: 20px;"}
      }
      ${!isVertical && !isAlternate ? `
        #${id} .tl-list::before {
          content: "";
          position: absolute;
          left: 0; right: 0; top: 32px;
          height: 2px;
          background: ${lineColor};
        }
      ` : ""}
      #${id} .tl-item {
        ${isVertical ? "position: relative; margin-bottom: 40px;" : "flex: 1; min-width: 220px; text-align: center; position: relative;"}
        opacity: ${isAnimated ? "0" : "1"};
        transform: ${isAnimated ? "translateY(20px)" : "none"};
        transition: opacity 0.6s ease, transform 0.6s ease;
      }
      #${id}.visible .tl-item { opacity: 1; transform: none; }
      #${id} .tl-dot {
        ${isVertical
          ? `position: absolute; left: -40px; top: 4px;`
          : `margin: 0 auto 16px; position: relative;`}
        width: ${dotSize}; height: ${dotSize};
        background: ${accentColor};
        border-radius: 50%;
        border: 4px solid #fff;
        box-shadow: 0 0 0 2px ${accentColor};
        z-index: 2;
        ${showIcons === "true"
          ? "display: flex; align-items: center; justify-content: center; font-size: 1.5rem; width: calc(" + dotSize + " * 2); height: calc(" + dotSize + " * 2);"
          : ""}
      }
      #${id} .tl-date {
        font-weight: 800;
        color: ${accentColor};
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
      }
      #${id} .tl-title {
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 6px;
        color: #221B15;
      }
      #${id} .tl-desc {
        color: #6B6259;
        font-size: 0.9rem;
        line-height: 1.6;
      }
      @media (max-width: 768px) {
        #${id} .tl-list {
          display: block !important;
          overflow: visible !important;
        }
        #${id} .tl-list::before { display: none; }
        #${id} .tl-container {
          padding-left: 40px !important;
        }
        #${id} .tl-container::before {
          display: block !important;
          left: 9px !important;
        }
        #${id} .tl-item {
          text-align: left !important;
          margin-bottom: 32px !important;
          position: relative !important;
        }
        #${id} .tl-dot {
          position: absolute !important;
          left: -40px !important;
          top: 4px !important;
          margin: 0 !important;
        }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <section id={id} ref={ref} className={visible ? "visible" : ""}>
          <div className="tl-container">
            <div className="tl-list">
              {items.map((item, i) => (
                <div key={i} className="tl-item" style={{ transitionDelay: `${i * 0.1}s` }}>
                  <div className="tl-dot">{showIcons === "true" && item.icon}</div>
                  <div className="tl-content">
                    <div className="tl-date">{item.date}</div>
                    <div className="tl-title">{item.title}</div>
                    <div className="tl-desc">{item.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      </>
    );
  },
};


// ============================================================
//  COMPARISON PRO — Tableau comparatif
// ============================================================

export const ComparisonPro = {
  fields: {
    columns: {
      type: "textarea", label: "Colonnes (nom|prix|highlight oui/non — 1 par ligne)",
      defaultValue: "Basique|0€|non\\nPremium|29.90€|oui\\nEntreprise|Sur devis|non",
    },
    features: {
      type: "textarea", label: "Features (nom|valeur 1|valeur 2|valeur 3 — 1 par ligne)",
      defaultValue: "Livraison offerte|✗|✓|✓\\nSupport 24/7|✗|✓|✓\\nRemise permanente|✗|-10%|-20%\\nAccès B2B|✗|✗|✓\\nRetours gratuits|✓|✓|✓\\nCompte multi-utilisateurs|✗|✗|✓",
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    highlightColor: { type: "text", label: "Couleur mise en avant", defaultValue: "#2F4A3C" },
  },
  defaultProps: {
    columns: "Basique|0€|non\\nPremium|29.90€|oui\\nEntreprise|Sur devis|non",
    features: "Livraison offerte|✗|✓|✓\\nSupport 24/7|✗|✓|✓\\nRemise permanente|✗|-10%|-20%\\nAccès B2B|✗|✗|✓\\nRetours gratuits|✓|✓|✓\\nCompte multi-utilisateurs|✗|✗|✓",
    accentColor: "#C1652F",
    highlightColor: "#2F4A3C",
  },
  render: (props) => {
    const id = useResponsiveId("comppro");
    const { columns, features, accentColor, highlightColor } = props;

    const cols = splitLines(columns).map((line) => {
      const [name, price, highlight] = line.split("|").map((s) => s.trim());
      return { name, price, highlight: highlight === "oui" };
    });

    const feats = splitLines(features).map((line) => {
      const parts = line.split("|").map((s) => s.trim());
      return { name: parts[0], values: parts.slice(1) };
    });

    const css = `
      #${id} {
        overflow-x: auto;
        padding: 20px;
        max-width: 1200px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        min-width: 600px;
      }
      #${id} th, #${id} td {
        padding: 16px;
        text-align: center;
        border-bottom: 1px solid #e5e5e5;
      }
      #${id} th:first-child, #${id} td:first-child {
        text-align: left;
        font-weight: 600;
        color: #221B15;
      }
      #${id} thead th {
        background: #F7F0E4;
        font-size: 1rem;
        position: relative;
      }
      #${id} thead th.highlight {
        background: ${highlightColor};
        color: #F7F0E4;
        border-top-left-radius: 16px;
        border-top-right-radius: 16px;
      }
      #${id} .col-price {
        display: block;
        font-size: 1.5rem;
        font-weight: 800;
        margin-top: 6px;
        color: ${accentColor};
      }
      #${id} thead th.highlight .col-price { color: #D4A843; }
      #${id} .col-badge {
        position: absolute;
        top: -12px;
        left: 50%;
        transform: translateX(-50%);
        background: #D4A843;
        color: #221B15;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        white-space: nowrap;
      }
      #${id} td.check { color: #16A34A; font-size: 1.25rem; font-weight: 700; }
      #${id} td.cross { color: #DC2626; font-size: 1.25rem; }
      #${id} tbody tr:hover { background: #F7F0E4; }
      #${id} td.highlight { background: rgba(47, 74, 60, 0.05); }
      #${id} tfoot td { padding-top: 24px; border: none; }
      #${id} .cta-btn {
        display: inline-block;
        padding: 12px 24px;
        background: ${accentColor};
        color: #fff;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9rem;
      }
      @media (max-width: 768px) {
        #${id} th, #${id} td { padding: 12px 8px; font-size: 0.85rem; }
        #${id} .col-price { font-size: 1.1rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <table>
            <thead>
              <tr>
                <th></th>
                {cols.map((c, i) => (
                  <th key={i} className={c.highlight ? "highlight" : ""}>
                    {c.highlight && <span className="col-badge">Recommandé</span>}
                    {c.name}
                    <span className="col-price">{c.price}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {feats.map((f, i) => (
                <tr key={i}>
                  <td>{f.name}</td>
                  {f.values.map((v, j) => {
                    const isCheck = v === "✓";
                    const isCross = v === "✗";
                    return (
                      <td
                        key={j}
                        className={`${isCheck ? "check" : ""} ${isCross ? "cross" : ""} ${cols[j]?.highlight ? "highlight" : ""}`}
                      >
                        {v}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <td></td>
                {cols.map((c, i) => (
                  <td key={i} className={c.highlight ? "highlight" : ""}>
                    <a href="/inscription" className="cta-btn">
                      Choisir {c.name}
                    </a>
                  </td>
                ))}
              </tr>
            </tfoot>
          </table>
        </div>
      </>
    );
  },
};


// ============================================================
//  BEFORE AFTER PRO — Slider avant/après
// ============================================================

export const BeforeAfterPro = {
  fields: {
    beforeImage: { type: "text", label: "Image AVANT (URL)", defaultValue: "/fallbacks/product-fallback.jpg" },
    afterImage: { type: "text", label: "Image APRÈS (URL)", defaultValue: "/fallbacks/hero-fallback.jpg" },
    beforeLabel: { type: "text", label: "Label AVANT", defaultValue: "Avant" },
    afterLabel: { type: "text", label: "Label APRÈS", defaultValue: "Après" },
    initialPosition: { type: "number", label: "Position initiale (%)", defaultValue: 50 },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    heightDesktop: { type: "text", label: "Hauteur (desktop)", defaultValue: "500px" },
    heightMobile: { type: "text", label: "Hauteur (mobile)", defaultValue: "300px" },
    borderRadius: { type: "text", label: "Arrondi", defaultValue: "16px" },
  },
  defaultProps: {
    beforeImage: "/fallbacks/product-fallback.jpg",
    afterImage: "/fallbacks/hero-fallback.jpg",
    beforeLabel: "Avant",
    afterLabel: "Après",
    initialPosition: 50,
    accentColor: "#C1652F",
    heightDesktop: "500px",
    heightMobile: "300px",
    borderRadius: "16px",
  },
  render: (props) => {
    const id = useResponsiveId("bap");
    const { beforeImage, afterImage, beforeLabel, afterLabel,
            initialPosition, accentColor, heightDesktop, heightMobile, borderRadius } = props;

    const [position, setPosition] = React.useState(Number(initialPosition) || 50);
    const containerRef = React.useRef(null);
    const dragging = React.useRef(false);

    const handleMove = (clientX) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const pct = ((clientX - rect.left) / rect.width) * 100;
      setPosition(Math.max(0, Math.min(100, pct)));
    };

    const onMouseDown = () => { dragging.current = true; };
    const onMouseUp = () => { dragging.current = false; };
    const onMouseMove = (e) => { if (dragging.current) handleMove(e.clientX); };
    const onTouchMove = (e) => { handleMove(e.touches[0].clientX); };

    React.useEffect(() => {
      const onUp = () => { dragging.current = false; };
      window.addEventListener("mouseup", onUp);
      return () => window.removeEventListener("mouseup", onUp);
    }, []);

    const css = `
      #${id} {
        position: relative;
        height: ${heightDesktop};
        border-radius: ${borderRadius};
        overflow: hidden;
        user-select: none;
        cursor: ew-resize;
        width: 100%;
      }
      #${id} .ba-image {
        position: absolute;
        inset: 0;
        background-size: cover;
        background-position: center;
      }
      #${id} .ba-before {
        background-image: url('${beforeImage}');
      }
      #${id} .ba-after {
        background-image: url('${afterImage}');
        clip-path: inset(0 ${100 - position}% 0 0);
      }
      #${id} .ba-slider {
        position: absolute;
        top: 0; bottom: 0;
        left: ${position}%;
        width: 4px;
        background: ${accentColor};
        z-index: 10;
        transform: translateX(-50%);
        box-shadow: 0 0 20px rgba(0,0,0,0.4);
      }
      #${id} .ba-handle {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 48px;
        height: 48px;
        background: ${accentColor};
        border: 3px solid #fff;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        font-size: 1.1rem;
        font-weight: 700;
        cursor: grab;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      }
      #${id} .ba-label {
        position: absolute;
        top: 16px;
        background: rgba(0,0,0,0.7);
        color: #fff;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
      #${id} .ba-label.before { left: 16px; }
      #${id} .ba-label.after { right: 16px; }
      @media (max-width: 768px) {
        #${id} { height: ${heightMobile}; }
        #${id} .ba-handle { width: 40px; height: 40px; font-size: 0.9rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div
          id={id}
          ref={containerRef}
          onMouseDown={onMouseDown}
          onMouseMove={onMouseMove}
          onTouchStart={onMouseDown}
          onTouchMove={onTouchMove}
          onTouchEnd={onMouseUp}
        >
          <div className="ba-image ba-before" />
          <div className="ba-image ba-after" />
          <span className="ba-label before">{beforeLabel}</span>
          <span className="ba-label after">{afterLabel}</span>
          <div className="ba-slider" style={{ left: `${position}%` }}>
            <div className="ba-handle">↔</div>
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  PROGRESS RING PRO — Anneaux de progression animés
// ============================================================

export const ProgressRingPro = {
  fields: {
    rings: {
      type: "textarea", label: "Anneaux (label|pourcentage|couleur — 1 par ligne)",
      defaultValue: "Satisfaction|92|#16A34A\\nRapidité|85|#C1652F\\nQualité|98|#D4A843\\nPrix|78|#2F4A3C",
    },
    size: { type: "text", label: "Taille (desktop)", defaultValue: "140px" },
    sizeMobile: { type: "text", label: "Taille (mobile)", defaultValue: "100px" },
    strokeWidth: { type: "number", label: "Épaisseur", defaultValue: 10 },
    animateOnScroll: {
      type: "radio", label: "Animation au scroll",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    layout: {
      type: "select", label: "Disposition",
      options: [
        { label: "Horizontal", value: "horizontal" },
        { label: "Grille 2×2", value: "grid" },
      ],
    },
  },
  defaultProps: {
    rings: "Satisfaction|92|#16A34A\\nRapidité|85|#C1652F\\nQualité|98|#D4A843\\nPrix|78|#2F4A3C",
    size: "140px",
    sizeMobile: "100px",
    strokeWidth: 10,
    animateOnScroll: "true",
    layout: "horizontal",
  },
  render: (props) => {
    const id = useResponsiveId("progring");
    const { rings, size, sizeMobile, strokeWidth, animateOnScroll, layout } = props;

    const items = splitLines(rings).map((line) => {
      const [label, value, color] = line.split("|").map((s) => s.trim());
      return { label, value: Number(value) || 0, color: color || "#C1652F" };
    });

    const [ref, visible] = useInViewOnce();
    const shouldAnimate = animateOnScroll === "true";

    const css = `
      #${id} {
        padding: 40px 24px;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .pr-grid {
        display: ${layout === "grid" ? "grid; grid-template-columns: repeat(2, 1fr); gap: 24px;" : "flex; gap: 32px; flex-wrap: wrap; justify-content: center;"}
        max-width: 1000px;
        margin: 0 auto;
      }
      #${id} .pr-item {
        text-align: center;
      }
      @media (max-width: 768px) {
        #${id} { padding: 24px 16px; }
        #${id} .pr-grid { flex-wrap: wrap; gap: 20px; }
        #${id} .pr-svg { width: ${sizeMobile} !important; height: ${sizeMobile} !important; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id} ref={ref}>
          <div className="pr-grid">
            {items.map((item, i) => (
              <RingItem
                key={i}
                {...item}
                size={size}
                strokeWidth={Number(strokeWidth) || 10}
                animate={shouldAnimate}
                visible={visible}
                delay={i * 150}
              />
            ))}
          </div>
        </div>
      </>
    );
  },
};

function RingItem({ label, value, color, size, strokeWidth, animate, visible, delay }) {
  const [progress, setProgress] = React.useState(animate ? 0 : value);
  const radius = 50 - strokeWidth / 2;
  const circumference = 2 * Math.PI * radius;

  React.useEffect(() => {
    if (!animate || !visible) {
      if (!animate) setProgress(value);
      return;
    }
    const start = Date.now() + delay;
    const dur = 1500;
    const tick = () => {
      const now = Date.now();
      if (now < start) { requestAnimationFrame(tick); return; }
      const p = Math.min(1, (now - start) / dur);
      const eased = 1 - Math.pow(1 - p, 3);
      setProgress(value * eased);
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [visible, animate, value, delay]);

  const dashOffset = circumference * (1 - progress / 100);

  return (
    <div className="pr-item">
      <div style={{ position: "relative", width: size, height: size, margin: "0 auto" }}>
        <svg
          className="pr-svg"
          width={size}
          height={size}
          viewBox="0 0 100 100"
          style={{ transform: "rotate(-90deg)" }}
        >
          <circle
            cx="50" cy="50" r={radius}
            fill="none"
            stroke="#e5e5e5"
            strokeWidth={strokeWidth}
          />
          <circle
            cx="50" cy="50" r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{ transition: "stroke-dashoffset 0.3s" }}
          />
        </svg>
        <div style={{
          position: "absolute", inset: 0,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: "1.5rem", fontWeight: 800, color,
        }}>
          {Math.round(progress)}%
        </div>
      </div>
      <div style={{ marginTop: 12, fontWeight: 600, color: "#221B15", fontSize: "0.95rem" }}>
        {label}
      </div>
    </div>
  );
}


// ============================================================
//  RATING BREAKDOWN PRO — Répartition des notes
// ============================================================

export const RatingBreakdownPro = {
  fields: {
    average: { type: "number", label: "Note moyenne", defaultValue: 4.6 },
    totalReviews: { type: "number", label: "Total d'avis", defaultValue: 247 },
    breakdown: {
      type: "textarea", label: "Répartition (étoiles|nombre — 1 par ligne)",
      defaultValue: "5|180\\n4|45\\n3|15\\n2|5\\n1|2",
    },
    showCTA: {
      type: "radio", label: "Bouton 'Laisser un avis'",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    ctaLabel: { type: "text", label: "Texte du bouton", defaultValue: "Laisser un avis" },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    starColor: { type: "text", label: "Couleur étoiles", defaultValue: "#D4A843" },
  },
  defaultProps: {
    average: 4.6,
    totalReviews: 247,
    breakdown: "5|180\\n4|45\\n3|15\\n2|5\\n1|2",
    showCTA: "true",
    ctaLabel: "Laisser un avis",
    accentColor: "#C1652F",
    starColor: "#D4A843",
  },
  render: (props) => {
    const id = useResponsiveId("rbp");
    const { average, totalReviews, breakdown, showCTA, ctaLabel, accentColor, starColor } = props;

    const rows = splitLines(breakdown).map((line) => {
      const [stars, count] = line.split("|").map((s) => Number(s.trim()));
      return { stars, count };
    });

    const total = rows.reduce((sum, r) => sum + r.count, 0) || 1;

    const css = `
      #${id} {
        padding: 32px;
        background: #F7F0E4;
        border-radius: 20px;
        max-width: 800px;
        margin: 0 auto;
        display: grid;
        grid-template-columns: 1fr 2fr;
        gap: 40px;
        align-items: center;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .rb-summary {
        text-align: center;
      }
      #${id} .rb-average {
        font-size: 4rem;
        font-weight: 800;
        color: #221B15;
        line-height: 1;
      }
      #${id} .rb-stars {
        font-size: 1.5rem;
        color: ${starColor};
        margin: 12px 0 8px;
        letter-spacing: 2px;
      }
      #${id} .rb-total {
        color: #6B6259;
        font-size: 0.9rem;
      }
      #${id} .rb-bars {
        display: flex;
        flex-direction: column;
        gap: 10px;
      }
      #${id} .rb-row {
        display: flex;
        align-items: center;
        gap: 12px;
        cursor: pointer;
        transition: opacity 0.2s;
      }
      #${id} .rb-row:hover { opacity: 0.85; }
      #${id} .rb-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #221B15;
        width: 40px;
        display: flex;
        align-items: center;
        gap: 4px;
      }
      #${id} .rb-track {
        flex: 1;
        height: 10px;
        background: #fff;
        border-radius: 999px;
        overflow: hidden;
        position: relative;
      }
      #${id} .rb-fill {
        height: 100%;
        background: ${starColor};
        border-radius: 999px;
        transition: width 0.6s ease;
      }
      #${id} .rb-count {
        font-size: 0.85rem;
        color: #6B6259;
        width: 60px;
        text-align: right;
        font-variant-numeric: tabular-nums;
      }
      #${id} .rb-cta {
        grid-column: 1 / -1;
        text-align: center;
        margin-top: 12px;
      }
      #${id} .rb-cta button {
        padding: 12px 28px;
        background: ${accentColor};
        color: #fff;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.95rem;
      }
      @media (max-width: 768px) {
        #${id} {
          grid-template-columns: 1fr;
          gap: 24px;
          padding: 24px 20px;
        }
        #${id} .rb-average { font-size: 3rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <div className="rb-summary">
            <div className="rb-average">{Number(average).toFixed(1)}</div>
            <div className="rb-stars">
              {"★".repeat(Math.round(average))}{"☆".repeat(5 - Math.round(average))}
            </div>
            <div className="rb-total">{totalReviews} avis au total</div>
          </div>
          <div className="rb-bars">
            {rows.map((r, i) => {
              const pct = (r.count / total) * 100;
              return (
                <div key={i} className="rb-row">
                  <div className="rb-label">{r.stars} ★</div>
                  <div className="rb-track">
                    <div className="rb-fill" style={{ width: `${pct}%` }} />
                  </div>
                  <div className="rb-count">{r.count}</div>
                </div>
              );
            })}
          </div>
          {showCTA === "true" && (
            <div className="rb-cta">
              <button>{ctaLabel}</button>
            </div>
          )}
        </div>
      </>
    );
  },
};


// ============================================================
//  NOTIFICATION BANNER PRO — Bannière d'alerte sticky
// ============================================================

export const NotificationBannerPro = {
  fields: {
    message: { type: "text", label: "Message", defaultValue: "🎉 Offre limitée : -20% sur tout le site avec le code NAWA20" },
    type: {
      type: "select", label: "Type",
      options: [
        { label: "Info", value: "info" },
        { label: "Succès", value: "success" },
        { label: "Avertissement", value: "warning" },
        { label: "Erreur", value: "error" },
        { label: "Promo", value: "promo" },
      ],
    },
    position: {
      type: "select", label: "Position",
      options: [
        { label: "Haut sticky", value: "top" },
        { label: "Haut fixe", value: "top-fixed" },
        { label: "Bas fixe", value: "bottom" },
        { label: "Inline", value: "inline" },
      ],
    },
    ctaLabel: { type: "text", label: "Texte du CTA", defaultValue: "J'en profite" },
    ctaUrl: { type: "text", label: "Lien du CTA", defaultValue: "/boutique/cosmetiques" },
    dismissible: {
      type: "radio", label: "Fermable",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    showIcon: {
      type: "radio", label: "Afficher l'icône",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    accentOverride: { type: "text", label: "Couleur personnalisée (optionnel)", defaultValue: "" },
  },
  defaultProps: {
    message: "🎉 Offre limitée : -20% sur tout le site avec le code NAWA20",
    type: "promo",
    position: "inline",
    ctaLabel: "J'en profite",
    ctaUrl: "/boutique/cosmetiques",
    dismissible: "true",
    showIcon: "true",
    accentOverride: "",
  },
  render: (props) => {
    const id = useResponsiveId("nbpro");
    const { message, type, position, ctaLabel, ctaUrl,
            dismissible, showIcon, accentOverride } = props;

    const [closed, setClosed] = React.useState(false);
    if (closed) return null;

    const palettes = {
      info: { bg: "#DBEAFE", color: "#1E40AF", icon: "ℹ" },
      success: { bg: "#DCFCE7", color: "#166534", icon: "✓" },
      warning: { bg: "#FEF3C7", color: "#92400E", icon: "⚠" },
      error: { bg: "#FEE2E2", color: "#991B1B", icon: "✕" },
      promo: { bg: "#221B15", color: "#D4A843", icon: "🎉" },
    };
    const palette = palettes[type] || palettes.info;
    const bgColor = accentOverride || palette.bg;
    const textColor = accentOverride ? "#fff" : palette.color;

    const positionStyles = {
      "top": "position: sticky; top: 0;",
      "top-fixed": "position: fixed; top: 0; left: 0; right: 0;",
      "bottom": "position: fixed; bottom: 0; left: 0; right: 0;",
      "inline": "",
    };

    const css = `
      #${id} {
        background: ${bgColor};
        color: ${textColor};
        padding: 12px 20px;
        ${positionStyles[position] || ""}
        z-index: 9998;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 16px;
        flex-wrap: wrap;
        font-size: 0.9rem;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .nb-icon {
        font-size: 1.1rem;
        font-weight: 700;
      }
      #${id} .nb-message {
        font-weight: 500;
      }
      #${id} .nb-cta {
        background: ${type === "promo" ? "#D4A843" : "rgba(255,255,255,0.5)"};
        color: ${type === "promo" ? "#221B15" : textColor};
        padding: 6px 16px;
        border-radius: 999px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.85rem;
        transition: transform 0.2s;
      }
      #${id} .nb-cta:hover {
        transform: scale(1.05);
      }
      #${id} .nb-close {
        background: none;
        border: none;
        color: ${textColor};
        cursor: pointer;
        font-size: 1.2rem;
        padding: 4px 8px;
        opacity: 0.7;
      }
      #${id} .nb-close:hover { opacity: 1; }
      @media (max-width: 768px) {
        #${id} { padding: 10px 14px; font-size: 0.8rem; gap: 8px; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {showIcon === "true" && <span className="nb-icon">{palette.icon}</span>}
          <span className="nb-message">{message}</span>
          {ctaLabel && ctaUrl && (
            <a href={ctaUrl} className="nb-cta">{ctaLabel}</a>
          )}
          {dismissible === "true" && (
            <button className="nb-close" onClick={() => setClosed(true)} aria-label="Fermer">×</button>
          )}
        </div>
      </>
    );
  },
};


// ============================================================
//  TRUST BADGES PRO — Badges de confiance
// ============================================================

export const TrustBadgesPro = {
  fields: {
    badges: {
      type: "textarea", label: "Badges (icône|titre|sous-titre — 1 par ligne)",
      defaultValue: "🔒|Paiement 100% sécurisé|SSL & 3D Secure\\n🚚|Livraison rapide|48-72h en Afrique de l'Ouest\\n↩|Retours gratuits|Sous 30 jours\\n⭐|Satisfaction client|4.8/5 sur 247 avis\\n🌿|Produits naturels|Ingrédients tracés\\n📞|Support 7j/7|Chat, email, WhatsApp",
    },
    columns: {
      type: "select", label: "Colonnes (desktop)",
      options: [
        { label: "2 colonnes", value: "2" },
        { label: "3 colonnes", value: "3" },
        { label: "4 colonnes", value: "4" },
        { label: "6 colonnes", value: "6" },
      ],
    },
    cardStyle: {
      type: "select", label: "Style",
      options: [
        { label: "Carte", value: "card" },
        { label: "Bordure", value: "border" },
        { label: "Minimal", value: "minimal" },
      ],
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    showSubtitle: {
      type: "radio", label: "Afficher les sous-titres",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    badges: "🔒|Paiement 100% sécurisé|SSL & 3D Secure\\n🚚|Livraison rapide|48-72h en Afrique de l'Ouest\\n↩|Retours gratuits|Sous 30 jours\\n⭐|Satisfaction client|4.8/5 sur 247 avis\\n🌿|Produits naturels|Ingrédients tracés\\n📞|Support 7j/7|Chat, email, WhatsApp",
    columns: "4",
    cardStyle: "card",
    accentColor: "#C1652F",
    showSubtitle: "true",
  },
  render: (props) => {
    const id = useResponsiveId("trust");
    const { badges, columns, cardStyle, accentColor, showSubtitle } = props;

    const items = splitLines(badges).map((line) => {
      const [icon, title, subtitle] = line.split("|").map((s) => s.trim());
      return { icon, title, subtitle };
    });

    const cols = Number(columns) || 4;

    const styleCss = {
      card: "background: #fff; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: none; padding: 24px 16px;",
      border: "background: transparent; border: 1px solid #e5e5e5; padding: 20px 16px;",
      minimal: "background: transparent; border: none; padding: 12px 8px;",
    }[cardStyle] || "";

    const css = `
      #${id} {
        display: grid;
        grid-template-columns: repeat(${cols}, 1fr);
        gap: 16px;
        padding: 40px 24px;
        max-width: 1200px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .tb-item {
        ${styleCss}
        border-radius: 16px;
        text-align: center;
        transition: transform 0.3s, box-shadow 0.3s;
      }
      #${id} .tb-item:hover {
        transform: translateY(-4px);
        ${cardStyle === "card" ? "box-shadow: 0 8px 24px rgba(0,0,0,0.1);" : ""}
      }
      #${id} .tb-icon {
        font-size: 2.5rem;
        margin-bottom: 12px;
        display: block;
      }
      #${id} .tb-title {
        font-weight: 700;
        font-size: 0.95rem;
        color: #221B15;
        margin-bottom: 4px;
        line-height: 1.3;
      }
      #${id} .tb-subtitle {
        color: #6B6259;
        font-size: 0.8rem;
        line-height: 1.4;
      }
      @media (max-width: 1024px) {
        #${id} { grid-template-columns: repeat(3, 1fr); }
      }
      @media (max-width: 768px) {
        #${id} { grid-template-columns: repeat(2, 1fr); gap: 12px; padding: 24px 16px; }
        #${id} .tb-icon { font-size: 2rem; }
        #${id} .tb-title { font-size: 0.85rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {items.map((b, i) => (
            <div key={i} className="tb-item">
              <span className="tb-icon">{b.icon}</span>
              <div className="tb-title">{b.title}</div>
              {showSubtitle === "true" && b.subtitle && (
                <div className="tb-subtitle">{b.subtitle}</div>
              )}
            </div>
          ))}
        </div>
      </>
    );
  },
};
'''


# ============================================================
#                    PATCH CONFIG
# ============================================================

MARKER = "/* === WIDGETS SERIES 3 === */"

NEW_NAMES = [
    "FaqPro", "TimelinePro", "ComparisonPro", "BeforeAfterPro",
    "ProgressRingPro", "RatingBreakdownPro", "NotificationBannerPro", "TrustBadgesPro",
]


def write_widgets():
    os.makedirs(WIDGETS_DIR, exist_ok=True)
    path = os.path.join(WIDGETS_DIR, "widgetsSeries3.jsx")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if "export const FaqPro" in f.read():
                print(f"  [SKIP] widgetsSeries3.jsx existe déjà")
                return False
        shutil.copy2(path, path + ".bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(WIDGETS_SERIES_3)
    print(f"  [OK] src/puck/widgets/widgetsSeries3.jsx créé")
    return True


def update_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"  [ERREUR] config.jsx introuvable")
        return False

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER in content:
        print("  [SKIP] config.jsx déjà patché pour Série 3")
        return False

    # Anti-doublon : ne garder que les noms absents
    new_names = []
    for name in NEW_NAMES:
        if re.search(rf'\b{name}\b', content):
            print(f"  [ATTENTION] {name} existe déjà, ignoré")
        else:
            new_names.append(name)

    if not new_names:
        print("  [SKIP] Tous les widgets existent déjà")
        return False

    shutil.copy2(CONFIG_PATH, CONFIG_PATH + ".before-series3.bak")
    print(f"  [BACKUP] config.jsx.before-series3.bak")

    # 1. Imports
    imports = f'''
{MARKER}
import {{
  {", ".join(new_names)},
}} from "./widgets/widgetsSeries3";
{MARKER}
'''
    content = re.sub(
        r'(import React from "react";\n)',
        r'\1' + imports,
        content,
        count=1,
    )

    # 2. Composants
    new_components = f"    // === Série 3 ===\n    {', '.join(new_names)},\n"

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

    # 3. Catégorie
    cat_name = 'series3: { title: "Série 3", components: [\n'
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
        print("  [OK] Catégorie 'Série 3' ajoutée")

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  AJOUT DES WIDGETS SÉRIE 3")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable")
        return

    print("\n[1/2] Création des 8 widgets Série 3...")
    write_widgets()

    print("\n[2/2] Mise à jour de config.jsx...")
    update_config()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ — 8 widgets ajoutés (noms uniques)")
    print("=" * 60)
    print("\nSérie 3 :")
    print("  • FaqPro                — FAQ avec catégories + recherche")
    print("  • TimelinePro           — Chronologie verticale/horizontale")
    print("  • ComparisonPro         — Tableau comparatif produits")
    print("  • BeforeAfterPro        — Slider avant/après interactif")
    print("  • ProgressRingPro       — Anneaux de progression animés")
    print("  • RatingBreakdownPro    — Répartition détaillée des notes")
    print("  • NotificationBannerPro — Bannière d'alerte sticky")
    print("  • TrustBadgesPro        — Badges de confiance")
    print()
    print("Total widgets :", 122 + len(NEW_NAMES))
    print()
    print("Redémarrer :")
    print("  Remove-Item -Recurse -Force node_modules\\.vite")
    print("  npm run dev")


if __name__ == "__main__":
    main()