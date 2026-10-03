/**
 * Phase 8 — Widgets Interactifs (9 composants).
 * Témoignages, Lottie, Hotspot, Compteurs, Portfolio...
 */
import { apiFetch } from "../../utils/apiClient";
import React from "react";

function splitLines(text) {
  return String(text || "").split("\n").map((s) => s.trim()).filter(Boolean);
}

// ============================================================
//  HOOK : animation au scroll (IntersectionObserver)
// ============================================================

function useInViewOnce(options = {}) {
  const ref = React.useRef(null);
  const [visible, setVisible] = React.useState(false);

  React.useEffect(() => {
    if (!ref.current || visible) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) setVisible(true);
      },
      { threshold: 0.2, ...options }
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [visible, options]);

  return [ref, visible];
}

// ============================================================
//  TESTIMONIAL CAROUSEL — Témoignages en carrousel
// ============================================================

export const TestimonialCarousel = {
  fields: {
    testimonials: {
      type: "textarea",
      label: "Témoignages (citation|auteur|rôle — un par ligne)",
      defaultValue:
        "Excellent service !|Fatou D.|Cliente fidèle\nProduits de qualité|Aminata K.|Cliente\nLivraison rapide|Ibrahim S.|Client",
    },
    autoPlay: {
      type: "radio",
      label: "Auto",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
  },
  defaultProps: {
    testimonials:
      "Excellent service !|Fatou D.|Cliente fidèle\nProduits de qualité|Aminata K.|Cliente\nLivraison rapide|Ibrahim S.|Client",
    autoPlay: "true",
  },
  render: ({ testimonials, autoPlay }) => {
    const list = splitLines(testimonials).map((line) => {
      const [quote, author, role] = line.split("|").map((s) => s.trim());
      return { quote, author, role };
    });
    const [index, setIndex] = React.useState(0);

    React.useEffect(() => {
      if (autoPlay !== "true" || list.length <= 1) return;
      const id = setInterval(() => setIndex((i) => (i + 1) % list.length), 5000);
      return () => clearInterval(id);
    }, [autoPlay, list.length]);

    if (!list.length) return null;
    const t = list[index];

    return (
      <div
        style={{
          textAlign: "center",
          padding: "40px 24px",
          background: "#F7F0E4",
          borderRadius: "24px",
        }}
      >
        <div style={{ fontSize: "2.5rem", color: "#C1652F", marginBottom: "16px" }}>
          "
        </div>
        <p
          style={{
            fontSize: "1.25rem",
            fontStyle: "italic",
            marginBottom: "24px",
            maxWidth: "700px",
            marginLeft: "auto",
            marginRight: "auto",
          }}
        >
          {t.quote}
        </p>
        <div style={{ fontWeight: 600 }}>{t.author}</div>
        <div style={{ color: "#6B6259", fontSize: "0.9rem" }}>{t.role}</div>
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "8px",
            marginTop: "24px",
          }}
        >
          {list.map((_, i) => (
            <button
              key={i}
              onClick={() => setIndex(i)}
              style={{
                width: i === index ? "24px" : "8px",
                height: "8px",
                borderRadius: "999px",
                border: "none",
                background: i === index ? "#C1652F" : "#ccc",
                cursor: "pointer",
                transition: "all 0.3s",
              }}
            />
          ))}
        </div>
      </div>
    );
  },
};

// ============================================================
//  LOTTIE — Animation via web component <dotlottie-player>
//  Aucune dépendance npm — chargement depuis CDN officiel.
// ============================================================

let lottiePlayerLoaded = false;

function ensureLottiePlayer() {
  if (lottiePlayerLoaded || typeof document === "undefined") return;
  if (document.querySelector("script[data-dotlottie]")) {
    lottiePlayerLoaded = true;
    return;
  }
  const script = document.createElement("script");
  script.src =
    "https://unpkg.com/@dotlottie/player-component@latest/dist/dotlottie-player.mjs";
  script.type = "module";
  script.setAttribute("data-dotlottie", "true");
  document.head.appendChild(script);
  lottiePlayerLoaded = true;
}

export const LottieWidget = {
  fields: {
    url: {
      type: "text",
      label: "URL du fichier .json ou .lottie",
      defaultValue:
        "https://assets10.lottiefiles.com/packages/lf20_puciaact.json",
    },
    height: { type: "text", label: "Hauteur", defaultValue: "300px" },
    loop: {
      type: "radio",
      label: "Boucle",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    autoplay: {
      type: "radio",
      label: "Lecture auto",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    caption: { type: "text", label: "Légende (optionnel)" },
  },
  defaultProps: {
    url: "https://assets10.lottiefiles.com/packages/lf20_puciaact.json",
    height: "300px",
    loop: "true",
    autoplay: "true",
    caption: "",
  },
  render: ({ url, height, loop, autoplay, caption }) => {
    React.useEffect(() => {
      ensureLottiePlayer();
    }, []);

    if (!url) {
      return (
        <div
          style={{
            height,
            background: "#f5f5f5",
            borderRadius: "12px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#999",
          }}
        >
          Aucune animation définie
        </div>
      );
    }

    const loopAttr = loop === "true" ? "loop" : "";
    const autoplayAttr = autoplay === "true" ? "autoplay" : "";

    return (
      <div style={{ textAlign: "center" }}>
        <div
          style={{
            height,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          dangerouslySetInnerHTML={{
            __html: `<dotlottie-player
              src="${url}"
              background="transparent"
              speed="1"
              style="width:100%;height:100%;"
              ${loopAttr}
              ${autoplayAttr}
            ></dotlottie-player>`,
          }}
        />
        {caption && (
          <p style={{ marginTop: "12px", color: "#6B6259" }}>{caption}</p>
        )}
      </div>
    );
  },
};

// ============================================================
//  HOTSPOT — Image avec points cliquables
// ============================================================

export const Hotspot = {
  fields: {
    image: { type: "text", label: "Image de fond" },
    hotspots: {
      type: "textarea",
      label: "Points (x%|y%|titre|description — un par ligne)",
      defaultValue:
        "30|40|Beurre de karité|Hydratation intense\n70|60|Huile de baobab|Régénération",
    },
  },
  defaultProps: {
    image: "/fallbacks/hero-fallback.jpg",
    hotspots:
      "30|40|Beurre de karité|Hydratation intense\n70|60|Huile de baobab|Régénération",
  },
  render: ({ image, hotspots }) => {
    const points = splitLines(hotspots).map((line) => {
      const [x, y, title, ...descParts] = line.split("|").map((s) => s.trim());
      return {
        x: Number(x),
        y: Number(y),
        title,
        description: descParts.join("|"),
      };
    });
    const [active, setActive] = React.useState(null);

    return (
      <div
        style={{
          position: "relative",
          borderRadius: "16px",
          overflow: "hidden",
        }}
      >
        <img src={image} alt="" style={{ width: "100%", display: "block" }} />
        {points.map((p, i) => (
          <div key={i}>
            <button
              onMouseEnter={() => setActive(i)}
              onMouseLeave={() => setActive(null)}
              onClick={() => setActive(active === i ? null : i)}
              style={{
                position: "absolute",
                left: `${p.x}%`,
                top: `${p.y}%`,
                transform: "translate(-50%, -50%)",
                width: 32,
                height: 32,
                borderRadius: "50%",
                background: "#C1652F",
                color: "#fff",
                border: "3px solid #fff",
                cursor: "pointer",
                boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
                fontSize: "1rem",
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              +
            </button>
            {active === i && (
              <div
                style={{
                  position: "absolute",
                  left: `${p.x}%`,
                  top: `${p.y}%`,
                  transform: "translate(-50%, calc(-100% - 20px))",
                  background: "#fff",
                  padding: "12px 16px",
                  borderRadius: "8px",
                  boxShadow: "0 4px 16px rgba(0,0,0,0.15)",
                  minWidth: 200,
                  zIndex: 10,
                  pointerEvents: "none",
                }}
              >
                <div style={{ fontWeight: 600, marginBottom: "4px" }}>
                  {p.title}
                </div>
                <div style={{ fontSize: "0.85rem", color: "#6B6259" }}>
                  {p.description}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  },
};

// ============================================================
//  TABLE OF CONTENTS — Sommaire automatique
// ============================================================

export const TableOfContents = {
  fields: {
    items: {
      type: "textarea",
      label: "Entrées (niveau|titre|ancre — un par ligne)",
      defaultValue:
        "1|Introduction|#intro\n2|Fonctionnalités|#features\n2|Tarifs|#pricing\n1|FAQ|#faq",
    },
    title: { type: "text", label: "Titre", defaultValue: "Sommaire" },
  },
  defaultProps: {
    items:
      "1|Introduction|#intro\n2|Fonctionnalités|#features\n2|Tarifs|#pricing\n1|FAQ|#faq",
    title: "Sommaire",
  },
  render: ({ items, title }) => {
    const list = splitLines(items).map((line) => {
      const [level, text, anchor] = line.split("|").map((s) => s.trim());
      return { level: Number(level), text, anchor };
    });

    return (
      <nav
        style={{
          background: "#F7F0E4",
          padding: "24px",
          borderRadius: "16px",
        }}
      >
        <div
          style={{
            fontWeight: 700,
            marginBottom: "16px",
            fontSize: "1.1rem",
          }}
        >
          {title}
        </div>
        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          {list.map((item, i) => (
            <li
              key={i}
              style={{
                paddingLeft: `${(item.level - 1) * 20}px`,
                marginBottom: "8px",
              }}
            >
              <a
                href={item.anchor}
                style={{
                  color: "#221B15",
                  textDecoration: "none",
                  fontSize: "0.95rem",
                }}
              >
                → {item.text}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    );
  },
};

// ============================================================
//  COUNTER — Compteur animé au scroll
// ============================================================

export const Counter = {
  fields: {
    value: { type: "number", label: "Valeur cible", defaultValue: 1250 },
    label: { type: "text", label: "Libellé", defaultValue: "Clients satisfaits" },
    suffix: { type: "text", label: "Suffixe", defaultValue: "+" },
    duration: { type: "number", label: "Durée (ms)", defaultValue: 2000 },
    color: { type: "text", label: "Couleur", defaultValue: "#C1652F" },
  },
  defaultProps: {
    value: 1250,
    label: "Clients satisfaits",
    suffix: "+",
    duration: 2000,
    color: "#C1652F",
  },
  render: ({ value, label, suffix, duration, color }) => {
    const [ref, visible] = useInViewOnce();
    const [count, setCount] = React.useState(0);

    React.useEffect(() => {
      if (!visible) return;
      const start = Date.now();
      const step = () => {
        const progress = Math.min(1, (Date.now() - start) / duration);
        setCount(Math.floor(value * progress));
        if (progress < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }, [visible, value, duration]);

    return (
      <div ref={ref} style={{ textAlign: "center", padding: "32px" }}>
        <div
          style={{
            fontSize: "3rem",
            fontWeight: 800,
            color,
            lineHeight: 1,
          }}
        >
          {count.toLocaleString("fr-FR")}
          {suffix}
        </div>
        <div style={{ marginTop: "8px", color: "#6B6259" }}>{label}</div>
      </div>
    );
  },
};

// ============================================================
//  PROGRESS REVIEW — Suivi des avis
// ============================================================

export const ProgressReview = {
  fields: {
    average: { type: "number", label: "Note moyenne", defaultValue: 4.5 },
    total: {
      type: "number",
      label: "Nombre total d'avis",
      defaultValue: 128,
    },
    distribution: {
      type: "textarea",
      label: "Répartition (étoiles|pourcentage — un par ligne)",
      defaultValue: "5|70\n4|20\n3|6\n2|3\n1|1",
    },
  },
  defaultProps: {
    average: 4.5,
    total: 128,
    distribution: "5|70\n4|20\n3|6\n2|3\n1|1",
  },
  render: ({ average, total, distribution }) => {
    const rows = splitLines(distribution).map((line) => {
      const [stars, pct] = line.split("|").map((s) => Number(s.trim()));
      return { stars, pct };
    });

    return (
      <div
        style={{
          display: "flex",
          gap: "32px",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div
            style={{ fontSize: "3rem", fontWeight: 700, color: "#C1652F" }}
          >
            {average.toFixed(1)}
          </div>
          <div style={{ color: "#D4A843", fontSize: "1.3rem" }}>
            {"★".repeat(Math.round(average))}
            {"☆".repeat(5 - Math.round(average))}
          </div>
          <div
            style={{
              color: "#6B6259",
              fontSize: "0.85rem",
              marginTop: "4px",
            }}
          >
            {total} avis
          </div>
        </div>
        <div style={{ flex: 1, minWidth: 200 }}>
          {rows.map((r, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginBottom: "6px",
              }}
            >
              <span style={{ fontSize: "0.85rem", width: 40 }}>
                {r.stars} ★
              </span>
              <div
                style={{
                  flex: 1,
                  height: 8,
                  background: "#eee",
                  borderRadius: "999px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    height: "100%",
                    width: `${r.pct}%`,
                    background: "#D4A843",
                  }}
                />
              </div>
              <span
                style={{
                  fontSize: "0.8rem",
                  color: "#6B6259",
                  width: 32,
                  textAlign: "right",
                }}
              >
                {r.pct}%
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  },
};

// ============================================================
//  CODE HIGHLIGHT — Code coloré (simple)
// ============================================================

export const CodeHighlight = {
  fields: {
    code: { type: "textarea", label: "Code" },
    language: { type: "text", label: "Langage", defaultValue: "javascript" },
    filename: { type: "text", label: "Nom du fichier (optionnel)" },
  },
  defaultProps: {
    code: "function greet(name) {\n  return `Bonjour ${name} !`;\n}",
    language: "javascript",
    filename: "example.js",
  },
  render: ({ code, language, filename }) => (
    <div
      style={{
        background: "#1E293B",
        borderRadius: "12px",
        overflow: "hidden",
      }}
    >
      {filename && (
        <div
          style={{
            background: "#0F172A",
            color: "#94A3B8",
            padding: "10px 16px",
            fontSize: "0.85rem",
            fontFamily: "monospace",
          }}
        >
          {filename}
        </div>
      )}
      <pre
        style={{
          margin: 0,
          padding: "20px",
          color: "#E2E8F0",
          fontFamily: "Consolas, Monaco, monospace",
          fontSize: "0.9rem",
          overflowX: "auto",
          lineHeight: 1.6,
        }}
      >
        <code>{code}</code>
      </pre>
      <div
        style={{
          padding: "8px 16px",
          background: "#0F172A",
          color: "#64748B",
          fontSize: "0.75rem",
          textAlign: "right",
        }}
      >
        {language}
      </div>
    </div>
  ),
};

// ============================================================
//  PORTFOLIO — Grille portfolio filtrable
// ============================================================

export const Portfolio = {
  fields: {
    items: {
      type: "textarea",
      label: "Projets (titre|catégorie|image — un par ligne)",
      defaultValue:
        "Karité bio|Cosmétiques|/fallbacks/product-fallback.jpg\nRobe wax|Mode|/fallbacks/blog-fallback.jpg\nSérum éclat|Cosmétiques|/fallbacks/hero-fallback.jpg",
    },
  },
  defaultProps: {
    items:
      "Karité bio|Cosmétiques|/fallbacks/product-fallback.jpg\nRobe wax|Mode|/fallbacks/blog-fallback.jpg\nSérum éclat|Cosmétiques|/fallbacks/hero-fallback.jpg",
  },
  render: ({ items }) => {
    const list = splitLines(items).map((line) => {
      const [title, category, image] = line.split("|").map((s) => s.trim());
      return { title, category, image };
    });
    const categories = ["Tout", ...new Set(list.map((i) => i.category))];
    const [filter, setFilter] = React.useState("Tout");

    const filtered =
      filter === "Tout" ? list : list.filter((i) => i.category === filter);

    return (
      <div>
        <div
          style={{
            display: "flex",
            gap: "8px",
            marginBottom: "20px",
            flexWrap: "wrap",
          }}
        >
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setFilter(c)}
              style={{
                padding: "8px 18px",
                borderRadius: "999px",
                border: "none",
                cursor: "pointer",
                background: c === filter ? "#C1652F" : "#f0f0f0",
                color: c === filter ? "#fff" : "#221B15",
                fontWeight: 600,
                fontSize: "0.85rem",
              }}
            >
              {c}
            </button>
          ))}
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
            gap: "16px",
          }}
        >
          {filtered.map((item, i) => (
            <div
              key={i}
              style={{
                position: "relative",
                borderRadius: "12px",
                overflow: "hidden",
                aspectRatio: "1/1",
              }}
            >
              <img
                src={item.image}
                alt={item.title}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  background:
                    "linear-gradient(to top, rgba(0,0,0,0.7), transparent 50%)",
                  display: "flex",
                  flexDirection: "column",
                  justifyContent: "flex-end",
                  padding: "16px",
                  color: "#fff",
                }}
              >
                <div style={{ fontSize: "0.75rem", opacity: 0.8 }}>
                  {item.category}
                </div>
                <div style={{ fontWeight: 600 }}>{item.title}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  },
};

// ============================================================
//  REVIEW — Bloc avis unique
// ============================================================

export const Review = {
  fields: {
    quote: { type: "textarea", label: "Avis" },
    author: { type: "text", label: "Auteur" },
    role: { type: "text", label: "Rôle" },
    rating: { type: "number", label: "Note (1-5)", defaultValue: 5 },
    date: { type: "text", label: "Date", defaultValue: "Mars 2026" },
  },
  defaultProps: {
    quote: "Un produit qui a transformé ma routine beauté !",
    author: "Fatou Diallo",
    role: "Cliente vérifiée",
    rating: 5,
    date: "Mars 2026",
  },
  render: ({ quote, author, role, rating, date }) => (
    <div
      style={{
        background: "#fff",
        padding: "24px",
        borderRadius: "16px",
        boxShadow: "0 2px 12px rgba(0,0,0,0.06)",
      }}
    >
      <div
        style={{ color: "#D4A843", marginBottom: "12px", fontSize: "1.1rem" }}
      >
        {"★".repeat(rating)}
        {"☆".repeat(5 - rating)}
      </div>
      <p style={{ fontStyle: "italic", marginBottom: "16px", lineHeight: 1.6 }}>
        "{quote}"
      </p>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: "0.85rem",
        }}
      >
        <div>
          <div style={{ fontWeight: 600 }}>{author}</div>
          <div style={{ color: "#6B6259" }}>{role}</div>
        </div>
        <div style={{ color: "#999" }}>{date}</div>
      </div>
    </div>
  ),
};