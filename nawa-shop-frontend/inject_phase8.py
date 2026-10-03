"""
Phase 8 — Widgets Média & Interactifs (14 widgets).
Installe les dépendances, crée les widgets, met à jour la config Puck.

Usage : python inject_phase8.py
"""
import os
import re
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
WIDGETS_DIR = os.path.join(SRC_DIR, "puck", "widgets")


# ============================================================
#              WIDGETS MÉDIA (5)
# ============================================================

MEDIA_WIDGETS_JSX = '''/**
 * Phase 8 — Widgets Média (5 composants).
 * Carrousels, diapositives, playlists vidéo.
 */
import React from "react";

// ============================================================
//  UTILITAIRES PARTAGÉS
// ============================================================

function useAutoSlide(length, interval, enabled) {
  const [index, setIndex] = React.useState(0);
  React.useEffect(() => {
    if (!enabled || length <= 1) return;
    const id = setInterval(() => setIndex((i) => (i + 1) % length), interval);
    return () => clearInterval(id);
  }, [length, interval, enabled]);
  return [index, setIndex];
}

function splitLines(text) {
  return String(text || "").split("\\n").map((s) => s.trim()).filter(Boolean);
}

// ============================================================
//  CAROUSEL LOOP — Boucle infinie
// ============================================================

export const CarouselLoop = {
  fields: {
    images: { type: "textarea", label: "URLs (1 par ligne)" },
    interval: { type: "number", label: "Intervalle (ms)", defaultValue: 3000 },
    height: { type: "text", label: "Hauteur", defaultValue: "360px" },
    showDots: {
      type: "radio", label: "Afficher les points",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    images: "/fallbacks/hero-fallback.jpg\\n/fallbacks/blog-fallback.jpg\\n/fallbacks/product-fallback.jpg",
    interval: 3000, height: "360px", showDots: "true",
  },
  render: ({ images, interval, height, showDots }) => {
    const list = splitLines(images);
    const [index, setIndex] = useAutoSlide(list.length, interval, true);
    if (!list.length) return null;

    return (
      <div style={{ position: "relative", height, overflow: "hidden", borderRadius: "16px" }}>
        {/* Piste de slides */}
        <div style={{
          display: "flex",
          transform: `translateX(-${index * 100}%)`,
          transition: "transform 0.6s ease-in-out",
          height: "100%",
        }}>
          {list.map((url, i) => (
            <img
              key={i}
              src={url}
              alt=""
              style={{
                minWidth: "100%",
                height: "100%",
                objectFit: "cover",
              }}
            />
          ))}
        </div>

        {/* Navigation manuelle */}
        <button
          onClick={() => setIndex((index - 1 + list.length) % list.length)}
          style={navBtnStyle("left")}
        >
          ‹
        </button>
        <button
          onClick={() => setIndex((index + 1) % list.length)}
          style={navBtnStyle("right")}
        >
          ›
        </button>

        {/* Points indicateurs */}
        {showDots === "true" && (
          <div style={{
            position: "absolute", bottom: 16, left: 0, right: 0,
            display: "flex", justifyContent: "center", gap: "8px",
          }}>
            {list.map((_, i) => (
              <button
                key={i}
                onClick={() => setIndex(i)}
                style={{
                  width: i === index ? "24px" : "8px",
                  height: "8px",
                  borderRadius: "999px",
                  border: "none",
                  background: i === index ? "#C1652F" : "rgba(255,255,255,0.6)",
                  cursor: "pointer",
                  transition: "all 0.3s",
                }}
              />
            ))}
          </div>
        )}
      </div>
    );
  },
};

function navBtnStyle(side) {
  return {
    position: "absolute", top: "50%", [side]: 12,
    transform: "translateY(-50%)",
    width: 44, height: 44, borderRadius: "50%",
    background: "rgba(0,0,0,0.5)", color: "#fff",
    border: "none", cursor: "pointer", fontSize: "1.5rem",
    display: "flex", alignItems: "center", justifyContent: "center",
  };
}

// ============================================================
//  CAROUSEL MEDIA — Photo + Vidéo
// ============================================================

export const CarouselMedia = {
  fields: {
    items: {
      type: "textarea",
      label: "Médias (type|url, un par ligne)",
      defaultValue: "image|/fallbacks/hero-fallback.jpg\\nvideo|https://www.youtube.com/embed/dQw4w9WgXcQ\\nimage|/fallbacks/blog-fallback.jpg",
    },
    height: { type: "text", label: "Hauteur", defaultValue: "400px" },
  },
  defaultProps: {
    items: "image|/fallbacks/hero-fallback.jpg\\nvideo|https://www.youtube.com/embed/dQw4w9WgXcQ\\nimage|/fallbacks/blog-fallback.jpg",
    height: "400px",
  },
  render: ({ items, height }) => {
    const list = splitLines(items).map((line) => {
      const [type, ...urlParts] = line.split("|");
      return { type: type.trim(), url: urlParts.join("|").trim() };
    });
    const [index, setIndex] = useAutoSlide(list.length, 5000, true);
    if (!list.length) return null;

    const current = list[index];

    return (
      <div style={{ position: "relative", height, borderRadius: "16px", overflow: "hidden", background: "#000" }}>
        {current.type === "video" ? (
          <iframe
            src={current.url}
            title="Vidéo"
            allowFullScreen
            style={{ width: "100%", height: "100%", border: "none" }}
          />
        ) : (
          <img src={current.url} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        )}
        <div style={{
          position: "absolute", bottom: 12, left: 0, right: 0,
          display: "flex", justifyContent: "center", gap: "6px",
        }}>
          {list.map((_, i) => (
            <button
              key={i}
              onClick={() => setIndex(i)}
              style={{
                width: i === index ? "20px" : "8px", height: "8px",
                borderRadius: "999px", border: "none",
                background: i === index ? "#C1652F" : "rgba(255,255,255,0.6)",
                cursor: "pointer", transition: "all 0.3s",
              }}
            />
          ))}
        </div>
      </div>
    );
  },
};

// ============================================================
//  CAROUSEL NESTED — Carrousel imbriqué
// ============================================================

export const CarouselNested = {
  fields: {
    groups: {
      type: "textarea",
      label: "Groupes (titre|url1,url2,url3 — un par ligne)",
      defaultValue: "Cosmétiques|/fallbacks/product-fallback.jpg,/fallbacks/blog-fallback.jpg\\nMode|/fallbacks/hero-fallback.jpg,/fallbacks/product-fallback.jpg",
    },
    height: { type: "text", label: "Hauteur", defaultValue: "280px" },
  },
  defaultProps: {
    groups: "Cosmétiques|/fallbacks/product-fallback.jpg,/fallbacks/blog-fallback.jpg\\nMode|/fallbacks/hero-fallback.jpg,/fallbacks/product-fallback.jpg",
    height: "280px",
  },
  render: ({ groups, height }) => {
    const parsed = splitLines(groups).map((line) => {
      const [title, urls] = line.split("|");
      return { title: title.trim(), urls: urls.split(",").map((u) => u.trim()) };
    });
    const [groupIndex, setGroupIndex] = React.useState(0);
    const [imgIndex, setImgIndex] = React.useState(0);

    React.useEffect(() => {
      const g = parsed[groupIndex];
      if (!g) return;
      const id = setInterval(() => {
        setImgIndex((i) => (i + 1) % g.urls.length);
      }, 2500);
      return () => clearInterval(id);
    }, [groupIndex, parsed]);

    if (!parsed.length) return null;
    const current = parsed[groupIndex];

    return (
      <div style={{ height }}>
        <div style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
          {parsed.map((g, i) => (
            <button
              key={i}
              onClick={() => { setGroupIndex(i); setImgIndex(0); }}
              style={{
                padding: "6px 16px", borderRadius: "999px",
                border: "none", cursor: "pointer",
                background: i === groupIndex ? "#C1652F" : "#eee",
                color: i === groupIndex ? "#fff" : "#221B15",
                fontWeight: 600, fontSize: "0.85rem",
              }}
            >
              {g.title}
            </button>
          ))}
        </div>
        <div style={{ position: "relative", height: "calc(100% - 50px)", borderRadius: "16px", overflow: "hidden" }}>
          <img
            src={current.urls[imgIndex]}
            alt={current.title}
            style={{ width: "100%", height: "100%", objectFit: "cover", transition: "opacity 0.4s" }}
          />
        </div>
      </div>
    );
  },
};

// ============================================================
//  SLIDES — Diapositives avec transitions
// ============================================================

export const Slides = {
  fields: {
    slides: {
      type: "textarea",
      label: "Slides (titre|sous-titre|url|bg — un par ligne)",
      defaultValue: "Bienvenue chez NAWA|La beauté d'Afrique sublimée|/boutique|/fallbacks/hero-fallback.jpg\\nNouvelle collection|Découvrez nos nouveautés|/boutique/vetements|/fallbacks/blog-fallback.jpg",
    },
    height: { type: "text", label: "Hauteur", defaultValue: "500px" },
    autoPlay: {
      type: "radio", label: "Défilement auto",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    slides: "Bienvenue chez NAWA|La beauté d'Afrique sublimée|/boutique|/fallbacks/hero-fallback.jpg\\nNouvelle collection|Découvrez nos nouveautés|/boutique/vetements|/fallbacks/blog-fallback.jpg",
    height: "500px", autoPlay: "true",
  },
  render: ({ slides, height, autoPlay }) => {
    const list = splitLines(slides).map((line) => {
      const [title, subtitle, url, bg] = line.split("|").map((s) => s.trim());
      return { title, subtitle, url, bg };
    });
    const [index, setIndex] = useAutoSlide(list.length, 5000, autoPlay === "true");
    if (!list.length) return null;

    const current = list[index];

    return (
      <div style={{ position: "relative", height, borderRadius: "16px", overflow: "hidden" }}>
        <img
          src={current.bg}
          alt=""
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }}
        />
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to right, rgba(0,0,0,0.6), rgba(0,0,0,0.2))" }} />
        <div style={{
          position: "relative", height: "100%", display: "flex",
          flexDirection: "column", justifyContent: "center",
          padding: "0 8%", color: "#fff",
        }}>
          <h2 style={{ fontSize: "2.5rem", marginBottom: "1rem", color: "#fff" }}>
            {current.title}
          </h2>
          <p style={{ fontSize: "1.2rem", marginBottom: "2rem", opacity: 0.9 }}>
            {current.subtitle}
          </p>
          <a href={current.url} className="btn btn-primary btn-lg" style={{ alignSelf: "flex-start" }}>
            Découvrir
          </a>
        </div>
      </div>
    );
  },
};

// ============================================================
//  VIDEO PLAYLIST — Liste de lecture vidéo
// ============================================================

export const VideoPlaylist = {
  fields: {
    videos: {
      type: "textarea",
      label: "Vidéos (titre|url — un par ligne)",
      defaultValue: "Présentation|https://www.youtube.com/embed/dQw4w9WgXcQ\\nTutoriel|https://www.youtube.com/embed/dQw4w9WgXcQ",
    },
  },
  defaultProps: {
    videos: "Présentation|https://www.youtube.com/embed/dQw4w9WgXcQ\\nTutoriel|https://www.youtube.com/embed/dQw4w9WgXcQ",
  },
  render: ({ videos }) => {
    const list = splitLines(videos).map((line) => {
      const [title, ...urlParts] = line.split("|");
      return { title: title.trim(), url: urlParts.join("|").trim() };
    });
    const [active, setActive] = React.useState(0);
    if (!list.length) return null;

    return (
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "16px" }}>
        <iframe
          src={list[active].url}
          title={list[active].title}
          allowFullScreen
          style={{ width: "100%", aspectRatio: "16/9", border: "none", borderRadius: "12px" }}
        />
        <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
          {list.map((v, i) => (
            <button
              key={i}
              onClick={() => setActive(i)}
              style={{
                padding: "12px 16px", textAlign: "left",
                borderRadius: "8px", border: "none", cursor: "pointer",
                background: i === active ? "#C1652F" : "#f5f5f5",
                color: i === active ? "#fff" : "#221B15",
                fontWeight: i === active ? 600 : 400,
                fontSize: "0.9rem",
              }}
            >
              ▶ {v.title}
            </button>
          ))}
        </div>
      </div>
    );
  },
};
'''


# ============================================================
#              WIDGETS INTERACTIFS (9)
# ============================================================

INTERACTIVE_WIDGETS_JSX = '''/**
 * Phase 8 — Widgets Interactifs (9 composants).
 * Témoignages, Lottie, Hotspot, Compteurs, Portfolio...
 */
import React from "react";
import Lottie from "lottie-react";

function splitLines(text) {
  return String(text || "").split("\\n").map((s) => s.trim()).filter(Boolean);
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
      ([entry]) => { if (entry.isIntersecting) setVisible(true); },
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
      defaultValue: "Excellent service !|Fatou D.|Cliente fidèle\\nProduits de qualité|Aminata K.|Cliente\\nLivraison rapide|Ibrahim S.|Client",
    },
    autoPlay: {
      type: "radio", label: "Auto",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    testimonials: "Excellent service !|Fatou D.|Cliente fidèle\\nProduits de qualité|Aminata K.|Cliente\\nLivraison rapide|Ibrahim S.|Client",
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
      <div style={{ textAlign: "center", padding: "40px 24px", background: "#F7F0E4", borderRadius: "24px" }}>
        <div style={{ fontSize: "2.5rem", color: "#C1652F", marginBottom: "16px" }}>"</div>
        <p style={{ fontSize: "1.25rem", fontStyle: "italic", marginBottom: "24px", maxWidth: "700px", marginLeft: "auto", marginRight: "auto" }}>
          {t.quote}
        </p>
        <div style={{ fontWeight: 600 }}>{t.author}</div>
        <div style={{ color: "#6B6259", fontSize: "0.9rem" }}>{t.role}</div>
        <div style={{ display: "flex", justifyContent: "center", gap: "8px", marginTop: "24px" }}>
          {list.map((_, i) => (
            <button
              key={i}
              onClick={() => setIndex(i)}
              style={{
                width: i === index ? "24px" : "8px", height: "8px",
                borderRadius: "999px", border: "none",
                background: i === index ? "#C1652F" : "#ccc",
                cursor: "pointer", transition: "all 0.3s",
              }}
            />
          ))}
        </div>
      </div>
    );
  },
};

// ============================================================
//  LOTTIE — Animation Lottie
// ============================================================

export const LottieWidget = {
  fields: {
    url: { type: "text", label: "URL du fichier .json Lottie" },
    height: { type: "text", label: "Hauteur", defaultValue: "300px" },
    loop: {
      type: "radio", label: "Boucle",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    caption: { type: "text", label: "Légende (optionnel)" },
  },
  defaultProps: {
    url: "https://assets10.lottiefiles.com/packages/lf20_puciaact.json",
    height: "300px", loop: "true", caption: "",
  },
  render: ({ url, height, loop, caption }) => {
    const [animationData, setAnimationData] = React.useState(null);
    const [error, setError] = React.useState(null);

    React.useEffect(() => {
      if (!url) return;
      fetch(url)
        .then((res) => res.json())
        .then(setAnimationData)
        .catch((err) => setError(err.message));
    }, [url]);

    if (error) {
      return (
        <div style={{ height, background: "#f5f5f5", borderRadius: "12px", display: "flex", alignItems: "center", justifyContent: "center", color: "#999" }}>
          Impossible de charger l'animation Lottie
        </div>
      );
    }

    if (!animationData) {
      return (
        <div style={{ height, background: "#f5f5f5", borderRadius: "12px", display: "flex", alignItems: "center", justifyContent: "center", color: "#999" }}>
          Chargement de l'animation...
        </div>
      );
    }

    return (
      <div style={{ textAlign: "center" }}>
        <div style={{ height }}>
          <Lottie animationData={animationData} loop={loop === "true"} style={{ height: "100%" }} />
        </div>
        {caption && <p style={{ marginTop: "12px", color: "#6B6259" }}>{caption}</p>}
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
      defaultValue: "30|40|Beurre de karité|Hydratation intense\\n70|60|Huile de baobab|Régénération",
    },
  },
  defaultProps: {
    image: "/fallbacks/hero-fallback.jpg",
    hotspots: "30|40|Beurre de karité|Hydratation intense\\n70|60|Huile de baobab|Régénération",
  },
  render: ({ image, hotspots }) => {
    const points = splitLines(hotspots).map((line) => {
      const [x, y, title, ...descParts] = line.split("|").map((s) => s.trim());
      return { x: Number(x), y: Number(y), title, description: descParts.join("|") };
    });
    const [active, setActive] = React.useState(null);

    return (
      <div style={{ position: "relative", borderRadius: "16px", overflow: "hidden" }}>
        <img src={image} alt="" style={{ width: "100%", display: "block" }} />
        {points.map((p, i) => (
          <div key={i}>
            <button
              onMouseEnter={() => setActive(i)}
              onMouseLeave={() => setActive(null)}
              onClick={() => setActive(active === i ? null : i)}
              style={{
                position: "absolute",
                left: `${p.x}%`, top: `${p.y}%`,
                transform: "translate(-50%, -50%)",
                width: 32, height: 32, borderRadius: "50%",
                background: "#C1652F", color: "#fff",
                border: "3px solid #fff", cursor: "pointer",
                boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
                fontSize: "1rem", fontWeight: 700,
                display: "flex", alignItems: "center", justifyContent: "center",
              }}
            >
              +
            </button>
            {active === i && (
              <div style={{
                position: "absolute",
                left: `${p.x}%`, top: `${p.y}%`,
                transform: "translate(-50%, calc(-100% - 20px))",
                background: "#fff", padding: "12px 16px",
                borderRadius: "8px", boxShadow: "0 4px 16px rgba(0,0,0,0.15)",
                minWidth: 200, zIndex: 10, pointerEvents: "none",
              }}>
                <div style={{ fontWeight: 600, marginBottom: "4px" }}>{p.title}</div>
                <div style={{ fontSize: "0.85rem", color: "#6B6259" }}>{p.description}</div>
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
      defaultValue: "1|Introduction|#intro\\n2|Fonctionnalités|#features\\n2|Tarifs|#pricing\\n1|FAQ|#faq",
    },
    title: { type: "text", label: "Titre", defaultValue: "Sommaire" },
  },
  defaultProps: {
    items: "1|Introduction|#intro\\n2|Fonctionnalités|#features\\n2|Tarifs|#pricing\\n1|FAQ|#faq",
    title: "Sommaire",
  },
  render: ({ items, title }) => {
    const list = splitLines(items).map((line) => {
      const [level, text, anchor] = line.split("|").map((s) => s.trim());
      return { level: Number(level), text, anchor };
    });

    return (
      <nav style={{ background: "#F7F0E4", padding: "24px", borderRadius: "16px" }}>
        <div style={{ fontWeight: 700, marginBottom: "16px", fontSize: "1.1rem" }}>{title}</div>
        <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
          {list.map((item, i) => (
            <li key={i} style={{ paddingLeft: `${(item.level - 1) * 20}px`, marginBottom: "8px" }}>
              <a href={item.anchor} style={{ color: "#221B15", textDecoration: "none", fontSize: "0.95rem" }}>
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
    value: 1250, label: "Clients satisfaits", suffix: "+",
    duration: 2000, color: "#C1652F",
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
        <div style={{ fontSize: "3rem", fontWeight: 800, color, lineHeight: 1 }}>
          {count.toLocaleString("fr-FR")}{suffix}
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
    total: { type: "number", label: "Nombre total d'avis", defaultValue: 128 },
    distribution: {
      type: "textarea",
      label: "Répartition (étoiles|pourcentage — un par ligne)",
      defaultValue: "5|70\\n4|20\\n3|6\\n2|3\\n1|1",
    },
  },
  defaultProps: {
    average: 4.5, total: 128,
    distribution: "5|70\\n4|20\\n3|6\\n2|3\\n1|1",
  },
  render: ({ average, total, distribution }) => {
    const rows = splitLines(distribution).map((line) => {
      const [stars, pct] = line.split("|").map((s) => Number(s.trim()));
      return { stars, pct };
    });

    return (
      <div style={{ display: "flex", gap: "32px", alignItems: "center", flexWrap: "wrap" }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "3rem", fontWeight: 700, color: "#C1652F" }}>
            {average.toFixed(1)}
          </div>
          <div style={{ color: "#D4A843", fontSize: "1.3rem" }}>
            {"★".repeat(Math.round(average))}{"☆".repeat(5 - Math.round(average))}
          </div>
          <div style={{ color: "#6B6259", fontSize: "0.85rem", marginTop: "4px" }}>
            {total} avis
          </div>
        </div>
        <div style={{ flex: 1, minWidth: 200 }}>
          {rows.map((r, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
              <span style={{ fontSize: "0.85rem", width: 40 }}>{r.stars} ★</span>
              <div style={{ flex: 1, height: 8, background: "#eee", borderRadius: "999px", overflow: "hidden" }}>
                <div style={{ height: "100%", width: `${r.pct}%`, background: "#D4A843" }} />
              </div>
              <span style={{ fontSize: "0.8rem", color: "#6B6259", width: 32, textAlign: "right" }}>
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
    code: "function greet(name) {\\n  return `Bonjour ${name} !`;\\n}",
    language: "javascript", filename: "example.js",
  },
  render: ({ code, language, filename }) => (
    <div style={{ background: "#1E293B", borderRadius: "12px", overflow: "hidden" }}>
      {filename && (
        <div style={{ background: "#0F172A", color: "#94A3B8", padding: "10px 16px", fontSize: "0.85rem", fontFamily: "monospace" }}>
          {filename}
        </div>
      )}
      <pre style={{
        margin: 0, padding: "20px",
        color: "#E2E8F0", fontFamily: "Consolas, Monaco, monospace",
        fontSize: "0.9rem", overflowX: "auto", lineHeight: 1.6,
      }}>
        <code>{code}</code>
      </pre>
      <div style={{ padding: "8px 16px", background: "#0F172A", color: "#64748B", fontSize: "0.75rem", textAlign: "right" }}>
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
      defaultValue: "Karité bio|Cosmétiques|/fallbacks/product-fallback.jpg\\nRobe wax|Mode|/fallbacks/blog-fallback.jpg\\nSérum éclat|Cosmétiques|/fallbacks/hero-fallback.jpg",
    },
  },
  defaultProps: {
    items: "Karité bio|Cosmétiques|/fallbacks/product-fallback.jpg\\nRobe wax|Mode|/fallbacks/blog-fallback.jpg\\nSérum éclat|Cosmétiques|/fallbacks/hero-fallback.jpg",
  },
  render: ({ items }) => {
    const list = splitLines(items).map((line) => {
      const [title, category, image] = line.split("|").map((s) => s.trim());
      return { title, category, image };
    });
    const categories = ["Tout", ...new Set(list.map((i) => i.category))];
    const [filter, setFilter] = React.useState("Tout");

    const filtered = filter === "Tout" ? list : list.filter((i) => i.category === filter);

    return (
      <div>
        <div style={{ display: "flex", gap: "8px", marginBottom: "20px", flexWrap: "wrap" }}>
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setFilter(c)}
              style={{
                padding: "8px 18px", borderRadius: "999px",
                border: "none", cursor: "pointer",
                background: c === filter ? "#C1652F" : "#f0f0f0",
                color: c === filter ? "#fff" : "#221B15",
                fontWeight: 600, fontSize: "0.85rem",
              }}
            >
              {c}
            </button>
          ))}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "16px" }}>
          {filtered.map((item, i) => (
            <div key={i} style={{ position: "relative", borderRadius: "12px", overflow: "hidden", aspectRatio: "1/1" }}>
              <img src={item.image} alt={item.title} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              <div style={{
                position: "absolute", inset: 0,
                background: "linear-gradient(to top, rgba(0,0,0,0.7), transparent 50%)",
                display: "flex", flexDirection: "column", justifyContent: "flex-end",
                padding: "16px", color: "#fff",
              }}>
                <div style={{ fontSize: "0.75rem", opacity: 0.8 }}>{item.category}</div>
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
    author: "Fatou Diallo", role: "Cliente vérifiée",
    rating: 5, date: "Mars 2026",
  },
  render: ({ quote, author, role, rating, date }) => (
    <div style={{ background: "#fff", padding: "24px", borderRadius: "16px", boxShadow: "0 2px 12px rgba(0,0,0,0.06)" }}>
      <div style={{ color: "#D4A843", marginBottom: "12px", fontSize: "1.1rem" }}>
        {"★".repeat(rating)}{"☆".repeat(5 - rating)}
      </div>
      <p style={{ fontStyle: "italic", marginBottom: "16px", lineHeight: 1.6 }}>"{quote}"</p>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.85rem" }}>
        <div>
          <div style={{ fontWeight: 600 }}>{author}</div>
          <div style={{ color: "#6B6259" }}>{role}</div>
        </div>
        <div style={{ color: "#999" }}>{date}</div>
      </div>
    </div>
  ),
};
'''


# ============================================================
#              MISE À JOUR DU CONFIG PUCK
# ============================================================

CONFIG_PATCH_MARKER = "/* === PHASE 8 WIDGETS === */"


def install_lottie():
    pkg = os.path.join(BASE_DIR, "package.json")
    if not os.path.exists(pkg):
        print("  [ATTENTION] package.json introuvable.")
        return
    with open(pkg, "r", encoding="utf-8") as f:
        if "lottie-react" in f.read():
            print("  [SKIP] lottie-react déjà installé")
            return
    print("  → npm install lottie-react")
    try:
        subprocess.run(["npm", "install", "lottie-react"], cwd=BASE_DIR, check=True, shell=True)
        print("  [OK] lottie-react installé")
    except subprocess.CalledProcessError:
        print("  [ATTENTION] Lancez manuellement : npm install lottie-react")


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
    """Importe et enregistre les 14 widgets dans le puckConfig existant."""
    config_path = os.path.join(SRC_DIR, "puck", "config.jsx")
    if not os.path.exists(config_path):
        print("  [ERREUR] config.jsx introuvable.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()

    if CONFIG_PATCH_MARKER in content:
        print("  [SKIP] config.jsx déjà patché Phase 8")
        return

    shutil.copy2(config_path, config_path + ".bak")
    print(f"  [BACKUP] {os.path.relpath(config_path, BASE_DIR)}.bak")

    # 1. Ajouter les imports
    imports = (
        f"\n{CONFIG_PATCH_MARKER}\n"
        'import {\n'
        '  CarouselLoop, CarouselMedia, CarouselNested, Slides, VideoPlaylist,\n'
        '} from "./widgets/mediaWidgets";\n'
        'import {\n'
        '  TestimonialCarousel, LottieWidget, Hotspot, TableOfContents,\n'
        '  Counter, ProgressReview, CodeHighlight, Portfolio, Review,\n'
        '} from "./widgets/interactiveWidgets";\n'
        f"{CONFIG_PATCH_MARKER}\n"
    )

    # Insérer après le premier import React
    content = re.sub(
        r'(import React from "react";\n)',
        r'\1' + imports,
        content,
        count=1,
    )

    # 2. Ajouter les widgets dans components
    new_components = (
        "    // === Phase 8 : Média ===\n"
        "    CarouselLoop, CarouselMedia, CarouselNested, Slides, VideoPlaylist,\n"
        "    // === Phase 8 : Interactif ===\n"
        "    TestimonialCarousel, LottieWidget, Hotspot, TableOfContents,\n"
        "    Counter, ProgressReview, CodeHighlight, Portfolio, Review,\n"
    )

    # Trouver la fermeture de "components: {"
    components_pattern = re.compile(
        r'(components:\s*\{)(.*?)(\n\s*\},\s*\n\s*categories:)',
        re.DOTALL,
    )
    match = components_pattern.search(content)
    if match:
        content = content[:match.start(2)] + "\n" + new_components + match.group(2).rstrip() + "\n  " + content[match.start(3):]
    else:
        print("  [ATTENTION] Structure 'components: {' non standard.")
        print("  → Ajoutez les widgets manuellement dans puckConfig.components")

    # 3. Ajouter une catégorie "media-advanced" et "interactive-advanced"
    new_categories = (
        '    mediaAdvanced: { title: "Média avancé", components: [\n'
        '      "CarouselLoop", "CarouselMedia", "CarouselNested", "Slides",\n'
        '      "VideoPlaylist", "LottieWidget", "Hotspot", "Portfolio",\n'
        '    ]},\n'
        '    interactiveAdvanced: { title: "Interactif avancé", components: [\n'
        '      "TestimonialCarousel", "TableOfContents", "Counter",\n'
        '      "ProgressReview", "CodeHighlight", "Review",\n'
        '    ]},\n'
    )

    cat_pattern = re.compile(
        r'(categories:\s*\{)(.*?)(\n\s*\},)',
        re.DOTALL,
    )
    cat_match = cat_pattern.search(content)
    if cat_match:
        content = content[:cat_match.start(2)] + "\n" + new_categories + cat_match.group(2) + content[cat_match.start(3):]

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] config.jsx patché (14 widgets + 2 catégories)")


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  PHASE 8 — WIDGETS MÉDIA & INTERACTIFS")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable dans {BASE_DIR}")
        return

    print("\n[1/4] Installation de lottie-react...")
    install_lottie()

    print("\n[2/4] Création des widgets média (5)...")
    write_file(os.path.join(WIDGETS_DIR, "mediaWidgets.jsx"), MEDIA_WIDGETS_JSX)

    print("\n[3/4] Création des widgets interactifs (9)...")
    write_file(os.path.join(WIDGETS_DIR, "interactiveWidgets.jsx"), INTERACTIVE_WIDGETS_JSX)

    print("\n[4/4] Mise à jour de puckConfig...")
    update_config()

    print("\n" + "=" * 60)
    print("  ✅ PHASE 8 — 14 WIDGETS AJOUTÉS")
    print("=" * 60)
    print("\nWidgets Média :")
    print("  CarouselLoop       — Carrousel en boucle infinie")
    print("  CarouselMedia      — Photo + Vidéo")
    print("  CarouselNested     — Carrousel imbriqué")
    print("  Slides             — Diapositives avec transitions")
    print("  VideoPlaylist      — Liste de lecture vidéo")
    print("\nWidgets Interactifs :")
    print("  TestimonialCarousel — Témoignages en carrousel")
    print("  LottieWidget        — Animation Lottie")
    print("  Hotspot             — Image avec points cliquables")
    print("  TableOfContents     — Sommaire automatique")
    print("  Counter             — Compteur animé au scroll")
    print("  ProgressReview      — Suivi des avis")
    print("  CodeHighlight       — Code coloré")
    print("  Portfolio           — Grille filtrable")
    print("  Review              — Bloc avis unique")


if __name__ == "__main__":
    main()
