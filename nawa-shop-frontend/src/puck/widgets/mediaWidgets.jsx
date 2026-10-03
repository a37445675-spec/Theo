/**
 * Phase 8 — Widgets Média (5 composants).
 * Carrousels, diapositives, playlists vidéo.
 */
import { apiFetch } from "../../utils/apiClient";
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
  return String(text || "").split("\n").map((s) => s.trim()).filter(Boolean);
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
    images: "/fallbacks/hero-fallback.jpg\n/fallbacks/blog-fallback.jpg\n/fallbacks/product-fallback.jpg",
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
      defaultValue: "image|/fallbacks/hero-fallback.jpg\nvideo|https://www.youtube.com/embed/dQw4w9WgXcQ\nimage|/fallbacks/blog-fallback.jpg",
    },
    height: { type: "text", label: "Hauteur", defaultValue: "400px" },
  },
  defaultProps: {
    items: "image|/fallbacks/hero-fallback.jpg\nvideo|https://www.youtube.com/embed/dQw4w9WgXcQ\nimage|/fallbacks/blog-fallback.jpg",
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
      defaultValue: "Cosmétiques|/fallbacks/product-fallback.jpg,/fallbacks/blog-fallback.jpg\nMode|/fallbacks/hero-fallback.jpg,/fallbacks/product-fallback.jpg",
    },
    height: { type: "text", label: "Hauteur", defaultValue: "280px" },
  },
  defaultProps: {
    groups: "Cosmétiques|/fallbacks/product-fallback.jpg,/fallbacks/blog-fallback.jpg\nMode|/fallbacks/hero-fallback.jpg,/fallbacks/product-fallback.jpg",
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
      defaultValue: "Bienvenue chez NAWA|La beauté d'Afrique sublimée|/boutique|/fallbacks/hero-fallback.jpg\nNouvelle collection|Découvrez nos nouveautés|/boutique/vetements|/fallbacks/blog-fallback.jpg",
    },
    height: { type: "text", label: "Hauteur", defaultValue: "500px" },
    autoPlay: {
      type: "radio", label: "Défilement auto",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    slides: "Bienvenue chez NAWA|La beauté d'Afrique sublimée|/boutique|/fallbacks/hero-fallback.jpg\nNouvelle collection|Découvrez nos nouveautés|/boutique/vetements|/fallbacks/blog-fallback.jpg",
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
      defaultValue: "Présentation|https://www.youtube.com/embed/dQw4w9WgXcQ\nTutoriel|https://www.youtube.com/embed/dQw4w9WgXcQ",
    },
  },
  defaultProps: {
    videos: "Présentation|https://www.youtube.com/embed/dQw4w9WgXcQ\nTutoriel|https://www.youtube.com/embed/dQw4w9WgXcQ",
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
