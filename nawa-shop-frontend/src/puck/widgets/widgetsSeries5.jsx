/**
 * Widgets avancés Série 5 — Recherche, Comparateur, Quiz, Simulateur,
 * Booking, Wishlist, Historique.
 * Noms 100% uniques.
 */
import React from "react";
import { useResponsiveId } from "../hooks/useResponsive";


// ============================================================
//  HELPERS
// ============================================================

function splitLines(text) {
  return String(text || "").split("\n").map((s) => s.trim()).filter(Boolean);
}

function useLocalStorage(key, initial = null) {
  const [value, setValue] = React.useState(() => {
    if (typeof localStorage === "undefined") return initial;
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : initial;
    } catch { return initial; }
  });
  React.useEffect(() => {
    if (typeof localStorage === "undefined") return;
    try { localStorage.setItem(key, JSON.stringify(value)); } catch {}
  }, [key, value]);
  return [value, setValue];
}


// ============================================================
//  SEARCH BAR ADVANCED — Recherche avec autocomplete
// ============================================================

export const SearchBarAdvanced = {
  fields: {
    placeholder: { type: "text", label: "Placeholder", defaultValue: "Rechercher un produit, une marque..." },
    suggestions: {
      type: "textarea", label: "Suggestions (texte|catégorie — 1 par ligne)",
      defaultValue: "Beurre de Karité|Produits\nHuile de Baobab|Produits\nHuile de Ricin|Produits\nShampoing Doux|Produits\nMasque Capillaire|Produits\nRobe Wax|Vêtements\nChemise Bazin|Vêtements\nSneakers Toile|Chaussures\nRéfrigérateur|Électroménager",
    },
    popularSearches: {
      type: "textarea", label: "Recherches populaires (1 par ligne)",
      defaultValue: "karité\nhuile\nwax\nboucles",
    },
    searchUrl: { type: "text", label: "URL de recherche", defaultValue: "/boutique/recherche?q=" },
    showCategories: {
      type: "radio", label: "Afficher les catégories",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    maxSuggestions: { type: "number", label: "Max suggestions", defaultValue: 6 },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    size: {
      type: "select", label: "Taille",
      options: [
        { label: "Normal", value: "normal" },
        { label: "Grand", value: "large" },
      ],
    },
  },
  defaultProps: {
    placeholder: "Rechercher un produit, une marque...",
    suggestions: "Beurre de Karité|Produits\nHuile de Baobab|Produits\nHuile de Ricin|Produits\nShampoing Doux|Produits\nMasque Capillaire|Produits\nRobe Wax|Vêtements\nChemise Bazin|Vêtements\nSneakers Toile|Chaussures\nRéfrigérateur|Électroménager",
    popularSearches: "karité\nhuile\nwax\nboucles",
    searchUrl: "/boutique/recherche?q=",
    showCategories: "true",
    maxSuggestions: 6,
    accentColor: "#C1652F",
    size: "normal",
  },
  render: (props) => {
    const id = useResponsiveId("searchpro");
    const { placeholder, suggestions, popularSearches, searchUrl,
            showCategories, maxSuggestions, accentColor, size } = props;

    const allSuggestions = splitLines(suggestions).map((line) => {
      const [text, category] = line.split("|").map((s) => s.trim());
      return { text, category };
    });
    const popular = splitLines(popularSearches);
    const [query, setQuery] = React.useState("");
    const [focused, setFocused] = React.useState(false);
    const [activeIndex, setActiveIndex] = React.useState(-1);

    const filtered = query
      ? allSuggestions.filter((s) => s.text.toLowerCase().includes(query.toLowerCase())).slice(0, Number(maxSuggestions))
      : [];

    const showDropdown = focused && (filtered.length > 0 || (!query && popular.length > 0));

    const submit = (q) => {
      const term = q || query;
      if (!term) return;
      window.location.href = `${searchUrl}${encodeURIComponent(term)}`;
    };

    const onKeyDown = (e) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setActiveIndex((i) => Math.min(i + 1, filtered.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setActiveIndex((i) => Math.max(i - 1, -1));
      } else if (e.key === "Enter") {
        if (activeIndex >= 0 && filtered[activeIndex]) {
          submit(filtered[activeIndex].text);
        } else {
          submit();
        }
      } else if (e.key === "Escape") {
        setFocused(false);
      }
    };

    const isLarge = size === "large";
    const padding = isLarge ? "16px 20px" : "12px 16px";

    const css = `
      #${id} {
        position: relative;
        max-width: 640px;
        width: 100%;
        margin: 0 auto;
        font-family: var(--font-body, sans-serif);
      }
      #${id} .sb-input-wrap {
        position: relative;
        display: flex;
        align-items: center;
        background: #fff;
        border: 2px solid ${focused ? accentColor : "#e5e5e5"};
        border-radius: ${isLarge ? "16px" : "12px"};
        transition: border-color 0.2s, box-shadow 0.2s;
        ${focused ? `box-shadow: 0 0 0 4px ${accentColor}20;` : ""}
      }
      #${id} .sb-icon {
        padding-left: ${isLarge ? "20px" : "16px"};
        font-size: ${isLarge ? "1.2rem" : "1rem"};
        opacity: 0.5;
      }
      #${id} input {
        flex: 1;
        padding: ${padding};
        border: none;
        background: transparent;
        font-size: ${isLarge ? "1.05rem" : "0.95rem"};
        outline: none;
        color: #221B15;
      }
      #${id} .sb-submit {
        background: ${accentColor};
        color: #fff;
        border: none;
        padding: ${isLarge ? "12px 24px" : "10px 20px"};
        border-radius: ${isLarge ? "12px" : "8px"};
        margin: 4px;
        cursor: pointer;
        font-weight: 600;
        font-size: ${isLarge ? "0.95rem" : "0.85rem"};
      }
      #${id} .sb-dropdown {
        position: absolute;
        top: calc(100% + 8px);
        left: 0; right: 0;
        background: #fff;
        border-radius: 12px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        overflow: hidden;
        z-index: 50;
        max-height: 400px;
        overflow-y: auto;
      }
      #${id} .sb-section-title {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6B6259;
        padding: 12px 16px 6px;
        font-weight: 700;
      }
      #${id} .sb-item {
        padding: 10px 16px;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.9rem;
        transition: background 0.15s;
      }
      #${id} .sb-item:hover,
      #${id} .sb-item.active {
        background: #F7F0E4;
      }
      #${id} .sb-item.active {
        border-left: 3px solid ${accentColor};
      }
      #${id} .sb-category {
        font-size: 0.75rem;
        color: #6B6259;
        background: #F7F0E4;
        padding: 2px 8px;
        border-radius: 999px;
      }
      #${id} .sb-popular {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        padding: 8px 16px 16px;
      }
      #${id} .sb-popular-tag {
        padding: 4px 12px;
        background: #F7F0E4;
        border-radius: 999px;
        font-size: 0.8rem;
        cursor: pointer;
        color: #221B15;
        transition: all 0.2s;
      }
      #${id} .sb-popular-tag:hover {
        background: ${accentColor};
        color: #fff;
      }
      @media (max-width: 768px) {
        #${id} input { font-size: 0.9rem; }
        #${id} .sb-submit { display: none; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <div className="sb-input-wrap">
            <span className="sb-icon">🔍</span>
            <input
              type="search"
              placeholder={placeholder}
              value={query}
              onChange={(e) => { setQuery(e.target.value); setActiveIndex(-1); }}
              onFocus={() => setFocused(true)}
              onBlur={() => setTimeout(() => setFocused(false), 200)}
              onKeyDown={onKeyDown}
            />
            <button className="sb-submit" onClick={() => submit()}>Rechercher</button>
          </div>

          {showDropdown && (
            <div className="sb-dropdown">
              {filtered.length > 0 && (
                <>
                  <div className="sb-section-title">Suggestions</div>
                  {filtered.map((s, i) => (
                    <div
                      key={i}
                      className={`sb-item ${i === activeIndex ? "active" : ""}`}
                      onClick={() => submit(s.text)}
                      onMouseEnter={() => setActiveIndex(i)}
                    >
                      <span>🔍 {s.text}</span>
                      {showCategories === "true" && s.category && (
                        <span className="sb-category">{s.category}</span>
                      )}
                    </div>
                  ))}
                </>
              )}
              {!query && popular.length > 0 && (
                <>
                  <div className="sb-section-title">Recherches populaires</div>
                  <div className="sb-popular">
                    {popular.map((p, i) => (
                      <span key={i} className="sb-popular-tag" onClick={() => submit(p)}>{p}</span>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </>
    );
  },
};


// ============================================================
//  PRODUCT COMPARATOR — Comparateur de produits
// ============================================================

export const ProductComparator = {
  fields: {
    products: {
      type: "textarea", label: "Produits (nom|prix|image|note|attributs séparés par virgule — 1 par ligne)",
      defaultValue: "Beurre de Karité|14.90|/fallbacks/product-fallback.jpg|4.8|100% naturel,200g,Vegan\nHuile de Baobab|19.90|/fallbacks/product-fallback.jpg|4.6|Premium,100ml,Anti-âge\nCrème Hydratante|16.50|/fallbacks/product-fallback.jpg|4.7|Karitié-miel,150ml,Fabrication locale",
    },
    maxProducts: { type: "number", label: "Max produits", defaultValue: 3 },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    highlightBestPrice: {
      type: "radio", label: "Mettre en avant le meilleur prix",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    showCTA: {
      type: "radio", label: "Bouton Ajouter au panier",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    products: "Beurre de Karité|14.90|/fallbacks/product-fallback.jpg|4.8|100% naturel,200g,Vegan\nHuile de Baobab|19.90|/fallbacks/product-fallback.jpg|4.6|Premium,100ml,Anti-âge\nCrème Hydratante|16.50|/fallbacks/product-fallback.jpg|4.7|Karitié-miel,150ml,Fabrication locale",
    maxProducts: 3,
    accentColor: "#C1652F",
    highlightBestPrice: "true",
    showCTA: "true",
  },
  render: (props) => {
    const id = useResponsiveId("comparator");
    const { products, maxProducts, accentColor, highlightBestPrice, showCTA } = props;

    const items = splitLines(products).slice(0, Number(maxProducts)).map((line) => {
      const [name, price, image, rating, ...attrParts] = line.split("|").map((s) => s.trim());
      const attrs = attrParts.join("|").split(",").map((s) => s.trim());
      return { name, price: Number(price), image, rating: Number(rating), attrs };
    });

    const bestPrice = highlightBestPrice === "true"
      ? Math.min(...items.map((i) => i.price))
      : null;

    const maxAttrs = Math.max(...items.map((i) => i.attrs.length), 0);

    const css = `
      #${id} {
        padding: 32px 16px;
        max-width: 1100px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
        overflow-x: auto;
      }
      #${id} .cmp-grid {
        display: grid;
        grid-template-columns: 140px repeat(${items.length}, 1fr);
        gap: 12px;
        min-width: 500px;
      }
      #${id} .cmp-header {
        padding: 20px 12px;
        text-align: center;
        background: #F7F0E4;
        border-radius: 12px;
        position: relative;
      }
      #${id} .cmp-header.best {
        background: ${accentColor}15;
        border: 2px solid ${accentColor};
      }
      #${id} .cmp-best-badge {
        position: absolute;
        top: -10px;
        left: 50%;
        transform: translateX(-50%);
        background: ${accentColor};
        color: #fff;
        font-size: 0.65rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 999px;
        text-transform: uppercase;
        white-space: nowrap;
      }
      #${id} .cmp-product-img {
        width: 80px; height: 80px;
        border-radius: 12px;
        object-fit: cover;
        margin: 0 auto 12px;
        display: block;
        background: #fff;
      }
      #${id} .cmp-product-name {
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 6px;
      }
      #${id} .cmp-product-rating {
        color: #D4A843;
        font-size: 0.8rem;
        margin-bottom: 6px;
      }
      #${id} .cmp-product-price {
        color: ${accentColor};
        font-weight: 800;
        font-size: 1.15rem;
      }
      #${id} .cmp-label {
        padding: 12px;
        font-weight: 600;
        color: #6B6259;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
      }
      #${id} .cmp-cell {
        padding: 12px;
        text-align: center;
        font-size: 0.9rem;
        background: #fff;
        border-radius: 8px;
      }
      #${id} .cmp-cell.best {
        background: ${accentColor}10;
        font-weight: 600;
      }
      #${id} .cmp-cta {
        display: block;
        margin: 12px 12px 0;
        padding: 10px 16px;
        background: ${accentColor};
        color: #fff;
        text-align: center;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.85rem;
      }
      @media (max-width: 768px) {
        #${id} .cmp-product-img { width: 60px; height: 60px; }
        #${id} .cmp-product-name { font-size: 0.8rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <div className="cmp-grid">
            <div></div>
            {items.map((p, i) => {
              const isBest = p.price === bestPrice;
              return (
                <div key={i} className={`cmp-header ${isBest ? "best" : ""}`}>
                  {isBest && <span className="cmp-best-badge">Meilleur prix</span>}
                  <img src={p.image} alt={p.name} className="cmp-product-img" />
                  <div className="cmp-product-name">{p.name}</div>
                  <div className="cmp-product-rating">
                    {"★".repeat(Math.round(p.rating))}{"☆".repeat(5 - Math.round(p.rating))}
                  </div>
                  <div className="cmp-product-price">{p.price.toFixed(2)} €</div>
                </div>
              );
            })}

            {/* Lignes attributs */}
            {Array.from({ length: maxAttrs }).map((_, rowIdx) => (
              <React.Fragment key={rowIdx}>
                <div className="cmp-label">Caractéristique {rowIdx + 1}</div>
                {items.map((p, colIdx) => (
                  <div
                    key={colIdx}
                    className={`cmp-cell ${p.price === bestPrice ? "best" : ""}`}
                  >
                    {p.attrs[rowIdx] || "—"}
                  </div>
                ))}
              </React.Fragment>
            ))}

            {showCTA === "true" && (
              <>
                <div></div>
                {items.map((p, i) => (
                  <a key={i} href="/panier" className="cmp-cta">
                    Ajouter
                  </a>
                ))}
              </>
            )}
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  MULTI STEP FORM PRO — Formulaire multi-étapes
// ============================================================

export const MultiStepFormPro = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Créez votre profil beauté" },
    steps: {
      type: "textarea", label: "Étapes (titre|champs séparés par virgule — 1 par ligne)",
      defaultValue: "Vos cheveux|type_cheveux,texture,longueur\nVos objectifs|hydratation,croissance,définition\nVos préférences|sans_sulfates,vegan,fragrance",
    },
    submitLabel: { type: "text", label: "Bouton final", defaultValue: "Créer mon profil" },
    successMessage: { type: "text", label: "Message de succès", defaultValue: "Votre profil beauté est prêt ✨" },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    showProgressBar: {
      type: "radio", label: "Barre de progression",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    allowBack: {
      type: "radio", label: "Bouton retour",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    title: "Créez votre profil beauté",
    steps: "Vos cheveux|type_cheveux,texture,longueur\nVos objectifs|hydratation,croissance,définition\nVos préférences|sans_sulfates,vegan,fragrance",
    submitLabel: "Créer mon profil",
    successMessage: "Votre profil beauté est prêt ✨",
    accentColor: "#C1652F",
    showProgressBar: "true",
    allowBack: "true",
  },
  render: (props) => {
    const id = useResponsiveId("msf");
    const { title, steps, submitLabel, successMessage, accentColor, showProgressBar, allowBack } = props;

    const stepDefs = splitLines(steps).map((line) => {
      const [title_, fields] = line.split("|");
      return {
        title: title_.trim(),
        fields: (fields || "").split(",").map((f) => f.trim()).filter(Boolean),
      };
    });

    const [currentStep, setCurrentStep] = React.useState(0);
    const [answers, setAnswers] = React.useState({});
    const [done, setDone] = React.useState(false);

    const total = stepDefs.length;
    const step = stepDefs[currentStep];
    const progress = ((currentStep + 1) / total) * 100;

    const toggle = (field) => {
      setAnswers((a) => ({ ...a, [field]: !a[field] }));
    };

    const next = () => {
      if (currentStep < total - 1) setCurrentStep(currentStep + 1);
      else setDone(true);
    };

    const prev = () => {
      if (currentStep > 0) setCurrentStep(currentStep - 1);
    };

    const css = `
      #${id} {
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
        padding: 40px 32px;
        max-width: 640px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .msf-title {
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 24px;
        color: #221B15;
      }
      #${id} .msf-progress {
        height: 6px;
        background: #F7F0E4;
        border-radius: 999px;
        margin-bottom: 32px;
        overflow: hidden;
      }
      #${id} .msf-progress-fill {
        height: 100%;
        background: ${accentColor};
        border-radius: 999px;
        transition: width 0.4s ease;
      }
      #${id} .msf-step-info {
        font-size: 0.8rem;
        color: #6B6259;
        margin-bottom: 8px;
        font-weight: 600;
      }
      #${id} .msf-step-title {
        font-size: 1.15rem;
        font-weight: 700;
        margin-bottom: 20px;
        color: #221B15;
      }
      #${id} .msf-fields {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 24px;
      }
      #${id} .msf-field {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 18px;
        border: 2px solid #e5e5e5;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.95rem;
      }
      #${id} .msf-field:hover {
        border-color: ${accentColor}80;
      }
      #${id} .msf-field.selected {
        border-color: ${accentColor};
        background: ${accentColor}08;
      }
      #${id} .msf-check {
        width: 22px; height: 22px;
        border: 2px solid #ccc;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        font-weight: 700;
        font-size: 0.75rem;
        flex-shrink: 0;
        transition: all 0.2s;
      }
      #${id} .msf-field.selected .msf-check {
        background: ${accentColor};
        border-color: ${accentColor};
      }
      #${id} .msf-actions {
        display: flex;
        gap: 10px;
      }
      #${id} .msf-btn {
        flex: 1;
        padding: 14px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.95rem;
        cursor: pointer;
        transition: all 0.2s;
        border: none;
      }
      #${id} .msf-btn.primary {
        background: ${accentColor};
        color: #fff;
      }
      #${id} .msf-btn.primary:hover { transform: translateY(-2px); }
      #${id} .msf-btn.secondary {
        background: #F7F0E4;
        color: #221B15;
        flex: 0 0 100px;
      }
      #${id} .msf-success {
        text-align: center;
        padding: 20px 0;
      }
      #${id} .msf-success-icon {
        font-size: 3.5rem;
        margin-bottom: 16px;
      }
      @media (max-width: 768px) {
        #${id} { padding: 28px 20px; }
        #${id} .msf-title { font-size: 1.25rem; }
      }
    `;

    if (done) {
      return (
        <>
          <style dangerouslySetInnerHTML={{ __html: css }} />
          <div id={id}>
            <div className="msf-success">
              <div className="msf-success-icon">✓</div>
              <h3 style={{ marginBottom: 8, color: "#221B15" }}>{successMessage}</h3>
              <p style={{ color: "#6B6259", fontSize: "0.9rem" }}>
                Nous vous recommandons des produits adaptés.
              </p>
            </div>
          </div>
        </>
      );
    }

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {title && <div className="msf-title">{title}</div>}
          {showProgressBar === "true" && (
            <div className="msf-progress">
              <div className="msf-progress-fill" style={{ width: `${progress}%` }} />
            </div>
          )}
          <div className="msf-step-info">Étape {currentStep + 1} / {total}</div>
          <div className="msf-step-title">{step.title}</div>
          <div className="msf-fields">
            {step.fields.map((f) => (
              <div
                key={f}
                className={`msf-field ${answers[f] ? "selected" : ""}`}
                onClick={() => toggle(f)}
              >
                <div className="msf-check">{answers[f] ? "✓" : ""}</div>
                <span style={{ textTransform: "capitalize" }}>{f.replace(/_/g, " ")}</span>
              </div>
            ))}
          </div>
          <div className="msf-actions">
            {allowBack === "true" && currentStep > 0 && (
              <button className="msf-btn secondary" onClick={prev}>← Retour</button>
            )}
            <button className="msf-btn primary" onClick={next}>
              {currentStep < total - 1 ? "Continuer →" : submitLabel}
            </button>
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  PRICE SIMULATOR PRO — Simulateur de financement
// ============================================================

export const PriceSimulatorPro = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Simulez votre paiement" },
    price: { type: "number", label: "Prix du produit (€)", defaultValue: 389 },
    minMonths: { type: "number", label: "Mois minimum", defaultValue: 3 },
    maxMonths: { type: "number", label: "Mois maximum", defaultValue: 24 },
    defaultMonths: { type: "number", label: "Mois par défaut", defaultValue: 12 },
    interestRate: { type: "number", label: "TAEG (%)", defaultValue: 0 },
    showTotal: {
      type: "radio", label: "Afficher le total",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
  },
  defaultProps: {
    title: "Simulez votre paiement",
    price: 389,
    minMonths: 3,
    maxMonths: 24,
    defaultMonths: 12,
    interestRate: 0,
    showTotal: "true",
    accentColor: "#C1652F",
  },
  render: (props) => {
    const id = useResponsiveId("simpro");
    const { title, price, minMonths, maxMonths, defaultMonths, interestRate, showTotal, accentColor } = props;

    const [months, setMonths] = React.useState(Number(defaultMonths));
    const [downPayment, setDownPayment] = React.useState(0);

    const rate = Number(interestRate) / 100 / 12;
    const principal = Number(price) - Number(downPayment);
    const monthly = rate > 0
      ? (principal * rate) / (1 - Math.pow(1 + rate, -months))
      : principal / months;
    const totalCost = monthly * months;
    const interestCost = totalCost - principal;

    const css = `
      #${id} {
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        padding: 32px;
        max-width: 560px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .sim-title {
        font-size: 1.25rem;
        font-weight: 800;
        margin-bottom: 24px;
        color: #221B15;
      }
      #${id} .sim-block {
        margin-bottom: 24px;
      }
      #${id} .sim-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #6B6259;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
      }
      #${id} input[type="range"] {
        width: 100%;
        accent-color: ${accentColor};
        height: 6px;
      }
      #${id} .sim-price-input {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 12px 16px;
        background: #F7F0E4;
        border-radius: 12px;
      }
      #${id} .sim-price-input input {
        flex: 1;
        background: transparent;
        border: none;
        font-size: 1rem;
        outline: none;
        font-weight: 600;
      }
      #${id} .sim-result {
        background: linear-gradient(135deg, ${accentColor}, ${accentColor}CC);
        color: #fff;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        margin-top: 24px;
      }
      #${id} .sim-monthly {
        font-size: 2.5rem;
        font-weight: 800;
        line-height: 1;
      }
      #${id} .sim-monthly-period {
        font-size: 1rem;
        font-weight: 400;
        opacity: 0.9;
      }
      #${id} .sim-detail {
        margin-top: 12px;
        font-size: 0.85rem;
        opacity: 0.95;
      }
      #${id} .sim-detail-row {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
      }
      @media (max-width: 768px) {
        #${id} { padding: 24px 20px; }
        #${id} .sim-monthly { font-size: 2rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {title && <div className="sim-title">{title}</div>}

          <div className="sim-block">
            <div className="sim-label">
              <span>Montant</span>
              <span>{Number(price).toFixed(2)} €</span>
            </div>
            <div className="sim-price-input">
              <span>💰</span>
              <input
                type="number"
                value={downPayment}
                onChange={(e) => setDownPayment(Math.max(0, Math.min(Number(price), Number(e.target.value))))}
                min="0"
                max={price}
              />
              <span style={{ fontSize: "0.8rem", color: "#6B6259" }}>Apport</span>
            </div>
          </div>

          <div className="sim-block">
            <div className="sim-label">
              <span>Durée</span>
              <span>{months} mois</span>
            </div>
            <input
              type="range"
              min={minMonths}
              max={maxMonths}
              value={months}
              onChange={(e) => setMonths(Number(e.target.value))}
              step="1"
            />
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem", color: "#6B6259", marginTop: 4 }}>
              <span>{minMonths} mois</span>
              <span>{maxMonths} mois</span>
            </div>
          </div>

          <div className="sim-result">
            <div className="sim-monthly">
              {monthly.toFixed(2)} €
              <span className="sim-monthly-period">/mois</span>
            </div>
            {showTotal === "true" && (
              <div className="sim-detail">
                <div className="sim-detail-row">
                  <span>Capital financé</span>
                  <span>{principal.toFixed(2)} €</span>
                </div>
                {interestCost > 0 && (
                  <div className="sim-detail-row">
                    <span>Intérêts totaux</span>
                    <span>{interestCost.toFixed(2)} €</span>
                  </div>
                )}
                <div className="sim-detail-row" style={{ fontWeight: 700, borderTop: "1px solid rgba(255,255,255,0.3)", marginTop: 8, paddingTop: 8 }}>
                  <span>Coût total</span>
                  <span>{totalCost.toFixed(2)} €</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  BOOKING CALENDAR PRO — Prise de rendez-vous
// ============================================================

export const BookingCalendarPro = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Prendre rendez-vous" },
    serviceLabel: { type: "text", label: "Nom du service", defaultValue: "Consultation beauté" },
    duration: { type: "number", label: "Durée (min)", defaultValue: 45 },
    price: { type: "number", label: "Prix (€)", defaultValue: 0 },
    availableSlots: {
      type: "textarea", label: "Créneaux disponibles (JJ/MM/AAAA|HH:MM,HH:MM — 1 par ligne)",
      defaultValue: "15/10/2026|09:00,10:30,14:00,16:00\n16/10/2026|09:00,11:00,15:30\n17/10/2026|10:00,14:00,17:00\n18/10/2026|09:30,13:00,16:30",
    },
    successMessage: { type: "text", label: "Message de succès", defaultValue: "Rendez-vous confirmé ! Un email vous a été envoyé." },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
  },
  defaultProps: {
    title: "Prendre rendez-vous",
    serviceLabel: "Consultation beauté",
    duration: 45,
    price: 0,
    availableSlots: "15/10/2026|09:00,10:30,14:00,16:00\n16/10/2026|09:00,11:00,15:30\n17/10/2026|10:00,14:00,17:00\n18/10/2026|09:30,13:00,16:30",
    successMessage: "Rendez-vous confirmé ! Un email vous a été envoyé.",
    accentColor: "#C1652F",
  },
  render: (props) => {
    const id = useResponsiveId("bookpro");
    const { title, serviceLabel, duration, price, availableSlots, successMessage, accentColor } = props;

    const slotsByDate = splitLines(availableSlots).map((line) => {
      const [date, times] = line.split("|");
      return {
        date: date.trim(),
        times: (times || "").split(",").map((t) => t.trim()).filter(Boolean),
      };
    });

    const [selectedDate, setSelectedDate] = React.useState(slotsByDate[0]?.date || null);
    const [selectedTime, setSelectedTime] = React.useState(null);
    const [done, setDone] = React.useState(false);

    const currentSlots = slotsByDate.find((s) => s.date === selectedDate);

    const confirm = () => {
      if (!selectedDate || !selectedTime) return;
      setDone(true);
    };

    const css = `
      #${id} {
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        padding: 32px;
        max-width: 640px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .bk-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #221B15;
        margin-bottom: 4px;
      }
      #${id} .bk-meta {
        color: #6B6259;
        font-size: 0.9rem;
        margin-bottom: 24px;
      }
      #${id} .bk-meta strong {
        color: ${accentColor};
        font-weight: 700;
      }
      #${id} .bk-section-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6B6259;
        font-weight: 700;
        margin-bottom: 12px;
      }
      #${id} .bk-dates {
        display: flex;
        gap: 8px;
        overflow-x: auto;
        padding-bottom: 8px;
        margin-bottom: 24px;
      }
      #${id} .bk-date {
        flex: 0 0 auto;
        padding: 12px 16px;
        border-radius: 12px;
        border: 2px solid #e5e5e5;
        background: #fff;
        cursor: pointer;
        text-align: center;
        transition: all 0.2s;
        font-size: 0.85rem;
        font-weight: 600;
      }
      #${id} .bk-date.selected {
        border-color: ${accentColor};
        background: ${accentColor};
        color: #fff;
      }
      #${id} .bk-date:hover:not(.selected) {
        border-color: ${accentColor}80;
      }
      #${id} .bk-times {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
        gap: 8px;
        margin-bottom: 24px;
      }
      #${id} .bk-time {
        padding: 12px 8px;
        border-radius: 10px;
        border: 2px solid #e5e5e5;
        background: #fff;
        cursor: pointer;
        text-align: center;
        font-size: 0.9rem;
        font-weight: 600;
        transition: all 0.2s;
      }
      #${id} .bk-time.selected {
        border-color: ${accentColor};
        background: ${accentColor};
        color: #fff;
      }
      #${id} .bk-time:hover:not(.selected) {
        border-color: ${accentColor}80;
      }
      #${id} .bk-confirm {
        width: 100%;
        padding: 16px;
        background: ${accentColor};
        color: #fff;
        border: none;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1rem;
        cursor: pointer;
        transition: opacity 0.2s;
      }
      #${id} .bk-confirm:disabled {
        opacity: 0.4;
        cursor: not-allowed;
      }
      #${id} .bk-success {
        text-align: center;
        padding: 24px 0;
      }
      #${id} .bk-success-icon {
        font-size: 3.5rem;
        margin-bottom: 16px;
      }
      #${id} .bk-success-detail {
        background: #F7F0E4;
        padding: 16px;
        border-radius: 12px;
        margin-top: 16px;
        font-size: 0.9rem;
      }
      @media (max-width: 768px) {
        #${id} { padding: 24px 20px; }
      }
    `;

    if (done) {
      return (
        <>
          <style dangerouslySetInnerHTML={{ __html: css }} />
          <div id={id}>
            <div className="bk-success">
              <div className="bk-success-icon">✓</div>
              <h3 style={{ color: "#221B15", marginBottom: 8 }}>{successMessage}</h3>
              <div className="bk-success-detail">
                <strong>{serviceLabel}</strong><br />
                {selectedDate} à {selectedTime} · {duration} min
              </div>
            </div>
          </div>
        </>
      );
    }

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {title && <div className="bk-title">{title}</div>}
          <div className="bk-meta">
            <strong>{serviceLabel}</strong> · {duration} min · {Number(price) === 0 ? "Gratuit" : `${price} €`}
          </div>

          <div className="bk-section-title">Choisissez une date</div>
          <div className="bk-dates">
            {slotsByDate.map((slot) => (
              <button
                key={slot.date}
                className={`bk-date ${selectedDate === slot.date ? "selected" : ""}`}
                onClick={() => { setSelectedDate(slot.date); setSelectedTime(null); }}
              >
                {slot.date}
              </button>
            ))}
          </div>

          {currentSlots && (
            <>
              <div className="bk-section-title">Créneaux disponibles</div>
              <div className="bk-times">
                {currentSlots.times.map((t) => (
                  <button
                    key={t}
                    className={`bk-time ${selectedTime === t ? "selected" : ""}`}
                    onClick={() => setSelectedTime(t)}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </>
          )}

          <button
            className="bk-confirm"
            disabled={!selectedDate || !selectedTime}
            onClick={confirm}
          >
            Confirmer le rendez-vous
          </button>
        </div>
      </>
    );
  },
};


// ============================================================
//  QUIZ PRO — Quiz "Trouvez votre produit"
// ============================================================

export const QuizPro = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Trouvez le produit fait pour vous" },
    subtitle: { type: "text", label: "Sous-titre", defaultValue: "3 questions, 30 secondes" },
    questions: {
      type: "textarea", label: "Questions (question|choix1,choix2,choix3 — 1 par ligne)",
      defaultValue: "Quel est votre type de peau ?|Sèche,Grassa,Mixte,Normale\nQuel est votre objectif principal ?|Hydratation,Anti-âge,Éclat,Apaisement\nQuel est votre budget ?|Moins de 15€,15-30€,Plus de 30€",
    },
    results: {
      type: "textarea", label: "Résultats (titre|description|produit — 1 par ligne)",
      defaultValue: "Routine hydratante|Pour votre peau sèche, misez sur le karité et les huiles.|Beurre de Karité Pur\nSoin éclat|Votre peau mérite des actifs premium.|Huile de Baobab Précieuse\nRoutine équilibrée|Une routine simple et efficace pour votre peau mixte.|Crème Hydratante Karité-Miel",
    },
    ctaLabel: { type: "text", label: "Bouton final", defaultValue: "Voir ma recommandation" },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    showProgress: {
      type: "radio", label: "Barre de progression",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    title: "Trouvez le produit fait pour vous",
    subtitle: "3 questions, 30 secondes",
    questions: "Quel est votre type de peau ?|Sèche,Grassa,Mixte,Normale\nQuel est votre objectif principal ?|Hydratation,Anti-âge,Éclat,Apaisement\nQuel est votre budget ?|Moins de 15€,15-30€,Plus de 30€",
    results: "Routine hydratante|Pour votre peau sèche, misez sur le karité et les huiles.|Beurre de Karité Pur\nSoin éclat|Votre peau mérite des actifs premium.|Huile de Baobab Précieuse\nRoutine équilibrée|Une routine simple et efficace pour votre peau mixte.|Crème Hydratante Karité-Miel",
    ctaLabel: "Voir ma recommandation",
    accentColor: "#C1652F",
    showProgress: "true",
  },
  render: (props) => {
    const id = useResponsiveId("quizpro");
    const { title, subtitle, questions, results, ctaLabel, accentColor, showProgress } = props;

    const questionDefs = splitLines(questions).map((line) => {
      const [q, choices] = line.split("|");
      return {
        question: q.trim(),
        choices: (choices || "").split(",").map((c) => c.trim()).filter(Boolean),
      };
    });

    const resultDefs = splitLines(results).map((line) => {
      const [resultTitle, description, product] = line.split("|").map((s) => s.trim());
      return { title: resultTitle, description, product };
    });

    const [currentQ, setCurrentQ] = React.useState(0);
    const [answers, setAnswers] = React.useState([]);
    const [done, setDone] = React.useState(false);

    const total = questionDefs.length;
    const progress = ((currentQ + 1) / total) * 100;

    const answer = (choice) => {
      const newAnswers = [...answers, choice];
      setAnswers(newAnswers);
      if (currentQ < total - 1) setCurrentQ(currentQ + 1);
      else setDone(true);
    };

    // Résultat basé sur le hash des réponses
    const resultIndex = done
      ? Math.abs(answers.join("").split("").reduce((a, c) => a + c.charCodeAt(0), 0)) % resultDefs.length
      : 0;
    const result = resultDefs[resultIndex];

    const restart = () => {
      setCurrentQ(0);
      setAnswers([]);
      setDone(false);
    };

    const css = `
      #${id} {
        background: #fff;
        border-radius: 20px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
        padding: 40px 32px;
        max-width: 640px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .qz-header {
        text-align: center;
        margin-bottom: 32px;
      }
      #${id} .qz-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #221B15;
        margin-bottom: 6px;
      }
      #${id} .qz-subtitle {
        color: #6B6259;
        font-size: 0.95rem;
      }
      #${id} .qz-progress {
        height: 6px;
        background: #F7F0E4;
        border-radius: 999px;
        margin-bottom: 32px;
        overflow: hidden;
      }
      #${id} .qz-progress-fill {
        height: 100%;
        background: ${accentColor};
        border-radius: 999px;
        transition: width 0.4s ease;
      }
      #${id} .qz-step {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: ${accentColor};
        font-weight: 700;
        margin-bottom: 12px;
      }
      #${id} .qz-question {
        font-size: 1.2rem;
        font-weight: 700;
        color: #221B15;
        margin-bottom: 24px;
      }
      #${id} .qz-choices {
        display: flex;
        flex-direction: column;
        gap: 10px;
      }
      #${id} .qz-choice {
        padding: 16px 20px;
        border: 2px solid #e5e5e5;
        border-radius: 12px;
        background: #fff;
        cursor: pointer;
        font-size: 0.95rem;
        text-align: left;
        transition: all 0.2s;
        font-weight: 500;
        color: #221B15;
      }
      #${id} .qz-choice:hover {
        border-color: ${accentColor};
        background: ${accentColor}08;
        transform: translateX(4px);
      }
      #${id} .qz-result {
        text-align: center;
      }
      #${id} .qz-result-icon {
        font-size: 3rem;
        margin-bottom: 16px;
      }
      #${id} .qz-result-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #221B15;
        margin-bottom: 12px;
      }
      #${id} .qz-result-desc {
        color: #6B6259;
        line-height: 1.6;
        margin-bottom: 20px;
      }
      #${id} .qz-result-product {
        background: #F7F0E4;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 20px;
      }
      #${id} .qz-result-product-label {
        font-size: 0.75rem;
        color: #6B6259;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
      }
      #${id} .qz-result-product-name {
        font-weight: 700;
        color: ${accentColor};
        font-size: 1.05rem;
      }
      #${id} .qz-cta {
        display: block;
        padding: 16px;
        background: ${accentColor};
        color: #fff;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 12px;
      }
      #${id} .qz-restart {
        background: none;
        border: none;
        color: #6B6259;
        cursor: pointer;
        font-size: 0.85rem;
        text-decoration: underline;
      }
      @media (max-width: 768px) {
        #${id} { padding: 28px 20px; }
        #${id} .qz-title { font-size: 1.25rem; }
        #${id} .qz-question { font-size: 1.05rem; }
      }
    `;

    if (done && result) {
      return (
        <>
          <style dangerouslySetInnerHTML={{ __html: css }} />
          <div id={id}>
            <div className="qz-result">
              <div className="qz-result-icon">✨</div>
              <div className="qz-result-title">{result.title}</div>
              <div className="qz-result-desc">{result.description}</div>
              <div className="qz-result-product">
                <div className="qz-result-product-label">Produit recommandé</div>
                <div className="qz-result-product-name">{result.product}</div>
              </div>
              <a href="/boutique/cosmetiques" className="qz-cta">{ctaLabel}</a>
              <button className="qz-restart" onClick={restart}>Refaire le quiz</button>
            </div>
          </div>
        </>
      );
    }

    const q = questionDefs[currentQ];
    if (!q) return null;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <div className="qz-header">
            {title && <div className="qz-title">{title}</div>}
            {subtitle && <div className="qz-subtitle">{subtitle}</div>}
          </div>
          {showProgress === "true" && (
            <div className="qz-progress">
              <div className="qz-progress-fill" style={{ width: `${progress}%` }} />
            </div>
          )}
          <div className="qz-step">Question {currentQ + 1} / {total}</div>
          <div className="qz-question">{q.question}</div>
          <div className="qz-choices">
            {q.choices.map((c) => (
              <button key={c} className="qz-choice" onClick={() => answer(c)}>
                {c}
              </button>
            ))}
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  WISHLIST PRO — Bouton favoris
// ============================================================

export const WishlistPro = {
  fields: {
    productId: { type: "text", label: "ID produit (ou 'current' pour l'URL)", defaultValue: "current" },
    iconFilled: { type: "text", label: "Icône ajoutée", defaultValue: "❤️" },
    iconEmpty: { type: "text", label: "Icône non ajoutée", defaultValue: "🤍" },
    showLabel: {
      type: "radio", label: "Afficher le texte",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    labelAdd: { type: "text", label: "Texte ajout", defaultValue: "Ajouter aux favoris" },
    labelRemove: { type: "text", label: "Texte retiré", defaultValue: "Retirer des favoris" },
    style: {
      type: "select", label: "Style",
      options: [
        { label: "Bouton plein", value: "filled" },
        { label: "Contour", value: "outline" },
        { label: "Icône seule", value: "icon" },
      ],
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#DC2626" },
    showCount: {
      type: "radio", label: "Afficher le compteur global",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    productId: "current",
    iconFilled: "❤️",
    iconEmpty: "🤍",
    showLabel: "true",
    labelAdd: "Ajouter aux favoris",
    labelRemove: "Retirer des favoris",
    style: "outline",
    accentColor: "#DC2626",
    showCount: "true",
  },
  render: (props) => {
    const id = useResponsiveId("wishpro");
    const { productId, iconFilled, iconEmpty, showLabel, labelAdd, labelRemove,
            style, accentColor, showCount } = props;

    // Récupérer l'ID depuis l'URL si "current"
    const effectiveId = productId === "current"
      ? (typeof window !== "undefined" ? window.location.pathname.split("/").pop() : "unknown")
      : productId;

    const [wishlist, setWishlist] = useLocalStorage("nawa_wishlist", []);
    const inWishlist = wishlist.includes(effectiveId);

    const toggle = () => {
      if (inWishlist) {
        setWishlist(wishlist.filter((id) => id !== effectiveId));
      } else {
        setWishlist([...wishlist, effectiveId]);
      }
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("nawa:wishlist-change", {
          detail: { id: effectiveId, added: !inWishlist, count: wishlist.length + (inWishlist ? -1 : 1) }
        }));
      }
    };

    const isFilled = style === "filled";
    const isIcon = style === "icon";

    const css = `
      #${id} {
        display: inline-flex;
        align-items: center;
        gap: 8px;
      }
      #${id} .wl-btn {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: ${isIcon ? "8px" : "10px 18px"};
        border-radius: ${isIcon ? "50%" : "999px"};
        cursor: pointer;
        font-size: 0.9rem;
        font-weight: 600;
        transition: all 0.2s;
        border: 2px solid ${accentColor};
        background: ${isFilled && inWishlist ? accentColor : "transparent"};
        color: ${isFilled && inWishlist ? "#fff" : accentColor};
        ${isIcon ? "width: 44px; height: 44px; justify-content: center; padding: 0;" : ""}
      }
      #${id} .wl-btn:hover {
        background: ${accentColor};
        color: #fff;
        transform: scale(1.05);
      }
      #${id} .wl-icon {
        font-size: ${isIcon ? "1.3rem" : "1.1rem"};
        transition: transform 0.2s;
      }
      #${id} .wl-btn:hover .wl-icon {
        transform: scale(1.15);
      }
      #${id} .wl-count {
        background: ${accentColor};
        color: #fff;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 999px;
        min-width: 20px;
        text-align: center;
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <button className="wl-btn" onClick={toggle} aria-label={inWishlist ? labelRemove : labelAdd}>
            <span className="wl-icon">{inWishlist ? iconFilled : iconEmpty}</span>
            {showLabel === "true" && !isIcon && (
              <span>{inWishlist ? labelRemove : labelAdd}</span>
            )}
          </button>
          {showCount === "true" && wishlist.length > 0 && (
            <span className="wl-count">{wishlist.length}</span>
          )}
        </div>
      </>
    );
  },
};


// ============================================================
//  RECENTLY VIEWED PRO — Historique des produits vus
// ============================================================

export const RecentlyViewedPro = {
  fields: {
    title: { type: "text", label: "Titre", defaultValue: "Vus récemment" },
    maxItems: { type: "number", label: "Nombre max", defaultValue: 4 },
    columnsDesktop: { type: "number", label: "Colonnes (desktop)", defaultValue: 4 },
    columnsMobile: { type: "number", label: "Colonnes (mobile)", defaultValue: 2 },
    showIfEmpty: {
      type: "radio", label: "Afficher si vide",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    demoProducts: {
      type: "textarea", label: "Produits démo (nom|prix|image|url — 1 par ligne)",
      defaultValue: "Beurre de Karité|14.90|/fallbacks/product-fallback.jpg|/produit/beurre-karite\nHuile de Baobab|19.90|/fallbacks/product-fallback.jpg|/produit/huile-baobab\nShampoing Doux|11.90|/fallbacks/product-fallback.jpg|/produit/shampoing\nMasque Capillaire|22.00|/fallbacks/product-fallback.jpg|/produit/masque",
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
  },
  defaultProps: {
    title: "Vus récemment",
    maxItems: 4,
    columnsDesktop: 4,
    columnsMobile: 2,
    showIfEmpty: "true",
    demoProducts: "Beurre de Karité|14.90|/fallbacks/product-fallback.jpg|/produit/beurre-karite\nHuile de Baobab|19.90|/fallbacks/product-fallback.jpg|/produit/huile-baobab\nShampoing Doux|11.90|/fallbacks/product-fallback.jpg|/produit/shampoing\nMasque Capillaire|22.00|/fallbacks/product-fallback.jpg|/produit/masque",
    accentColor: "#C1652F",
  },
  render: (props) => {
    const id = useResponsiveId("recentpro");
    const { title, maxItems, columnsDesktop, columnsMobile,
            showIfEmpty, demoProducts, accentColor } = props;

    const [viewed, setViewed] = useLocalStorage("nawa_recently_viewed", []);

    const demo = splitLines(demoProducts).map((line) => {
      const [name, price, image, url] = line.split("|").map((s) => s.trim());
      return { name, price: Number(price), image, url };
    });

    // Utiliser l'historique réel OU les démos si vide
    const items = viewed.length > 0 ? viewed.slice(0, Number(maxItems)) : demo.slice(0, Number(maxItems));
    const isEmpty = viewed.length === 0;

    if (isEmpty && showIfEmpty === "false") return null;

    const css = `
      #${id} {
        padding: 32px 16px;
        max-width: 1200px;
        margin: 0 auto;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .rv-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #221B15;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
      }
      #${id} .rv-title-icon {
        color: ${accentColor};
      }
      #${id} .rv-hint {
        font-size: 0.8rem;
        color: #6B6259;
        font-weight: 400;
        margin-left: auto;
      }
      #${id} .rv-grid {
        display: grid;
        grid-template-columns: repeat(${columnsDesktop}, 1fr);
        gap: 16px;
      }
      #${id} .rv-card {
        background: #fff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        text-decoration: none;
        color: inherit;
        transition: transform 0.2s, box-shadow 0.2s;
        display: block;
      }
      #${id} .rv-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
      }
      #${id} .rv-image {
        aspect-ratio: 1/1;
        background: #f5f5f5;
        overflow: hidden;
      }
      #${id} .rv-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s;
      }
      #${id} .rv-card:hover .rv-image img {
        transform: scale(1.05);
      }
      #${id} .rv-info {
        padding: 12px;
      }
      #${id} .rv-name {
        font-size: 0.9rem;
        font-weight: 600;
        color: #221B15;
        margin-bottom: 6px;
        line-height: 1.3;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }
      #${id} .rv-price {
        color: ${accentColor};
        font-weight: 700;
        font-size: 1rem;
      }
      @media (max-width: 1024px) {
        #${id} .rv-grid { grid-template-columns: repeat(3, 1fr); }
      }
      @media (max-width: 768px) {
        #${id} .rv-grid { grid-template-columns: repeat(${columnsMobile}, 1fr); gap: 12px; }
        #${id} .rv-title { font-size: 1.1rem; }
        #${id} .rv-name { font-size: 0.8rem; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <section id={id}>
          <div className="rv-title">
            <span className="rv-title-icon">🕐</span>
            {title}
            {isEmpty && <span className="rv-hint">(démo)</span>}
          </div>
          <div className="rv-grid">
            {items.map((p, i) => (
              <a key={i} href={p.url || "#"} className="rv-card">
                <div className="rv-image">
                  <img src={p.image} alt={p.name} loading="lazy" />
                </div>
                <div className="rv-info">
                  <div className="rv-name">{p.name}</div>
                  <div className="rv-price">{Number(p.price).toFixed(2)} €</div>
                </div>
              </a>
            ))}
          </div>
        </section>
      </>
    );
  },
};
