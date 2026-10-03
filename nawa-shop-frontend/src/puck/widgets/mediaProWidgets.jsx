/**
 * Widgets média avancés — noms uniques pour éviter tout conflit.
 *  - SliderPro         : Slider avec flèches gauche/droite
 *  - GalleryLightbox   : Galerie avec visionneuse plein écran
 *  - VideoPlayerCustom : Lecteur vidéo HTML5 avec contrôles custom
 */
import React from "react";
import { useResponsiveId } from "../hooks/useResponsive";


// ============================================================
//  HELPERS
// ============================================================

function puckDropZone(puck, zone = "content") {
  if (!puck) return null;
  if (puck.DropZone) return <puck.DropZone zone={zone} />;
  if (puck.renderDropZone) return puck.renderDropZone({ zone });
  return null;
}

function splitLines(text) {
  return String(text || "").split("\n").map((s) => s.trim()).filter(Boolean);
}


// ============================================================
//  SLIDER PRO — Slider avec flèches gauche/droite
// ============================================================

export const SliderPro = {
  fields: {
    slideCount: { type: "number", label: "Nombre de slides", defaultValue: 3 },

    // Navigation
    showArrows: {
      type: "radio", label: "Afficher les flèches",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    arrowPosition: {
      type: "select", label: "Position flèches",
      options: [
        { label: "Centrées verticalement", value: "center" },
        { label: "En bas à droite", value: "bottom-right" },
        { label: "Extérieur", value: "outside" },
      ],
    },
    arrowStyle: {
      type: "select", label: "Style flèches",
      options: [
        { label: "Cercles pleins", value: "filled" },
        { label: "Contour", value: "outline" },
        { label: "Minimal", value: "minimal" },
      ],
    },
    showDots: {
      type: "radio", label: "Afficher les points",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    showProgress: {
      type: "radio", label: "Barre de progression",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },

    // Autoplay
    autoPlay: {
      type: "radio", label: "Lecture automatique",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    autoPlayInterval: { type: "number", label: "Intervalle (ms)", defaultValue: 5000 },
    pauseOnHover: {
      type: "radio", label: "Pause au survol",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },

    // Layout
    heightDesktop: { type: "text", label: "Hauteur (desktop)", defaultValue: "500px" },
    heightTablet: { type: "text", label: "Hauteur (tablette)", defaultValue: "400px" },
    heightMobile: { type: "text", label: "Hauteur (mobile)", defaultValue: "300px" },
    borderRadius: { type: "text", label: "Arrondi", defaultValue: "16px" },
    transition: {
      type: "select", label: "Transition",
      options: [
        { label: "Glissement", value: "slide" },
        { label: "Fondu", value: "fade" },
      ],
    },
    transitionDuration: { type: "text", label: "Durée transition", defaultValue: "600ms" },
  },
  defaultProps: {
    slideCount: 3,
    showArrows: "true",
    arrowPosition: "center",
    arrowStyle: "filled",
    showDots: "true",
    showProgress: "true",
    autoPlay: "true",
    autoPlayInterval: 5000,
    pauseOnHover: "true",
    heightDesktop: "500px",
    heightTablet: "400px",
    heightMobile: "300px",
    borderRadius: "16px",
    transition: "slide",
    transitionDuration: "600ms",
  },
  render: (props) => {
    const { puck, slideCount, showArrows, arrowPosition, arrowStyle,
            showDots, showProgress, autoPlay, autoPlayInterval, pauseOnHover,
            heightDesktop, heightTablet, heightMobile, borderRadius,
            transition, transitionDuration } = props;

    const id = useResponsiveId("sliderpro");
    const [index, setIndex] = React.useState(0);
    const [paused, setPaused] = React.useState(false);
    const [progress, setProgress] = React.useState(0);
    const count = Math.max(1, Number(slideCount) || 3);
    const shouldAuto = autoPlay === "true";
    const shouldPause = pauseOnHover === "true";

    // Autoplay + progress
    React.useEffect(() => {
      if (!shouldAuto || count <= 1) return;
      if (shouldPause && paused) return;

      const start = Date.now();
      const tick = setInterval(() => {
        const p = Math.min(1, (Date.now() - start) / autoPlayInterval);
        setProgress(p);
        if (p >= 1) {
          setIndex((i) => (i + 1) % count);
          setProgress(0);
        }
      }, 50);

      return () => clearInterval(tick);
    }, [index, shouldAuto, shouldPause, paused, count, autoPlayInterval]);

    // Reset progress on manual change
    React.useEffect(() => { setProgress(0); }, [index]);

    const next = () => setIndex((i) => (i + 1) % count);
    const prev = () => setIndex((i) => (i - 1 + count) % count);

    // Styles arrow selon le type
    const arrowBase = {
      width: 48, height: 48, borderRadius: "50%",
      border: "none", cursor: "pointer", fontSize: "1.4rem",
      display: "flex", alignItems: "center", justifyContent: "center",
      transition: "all 0.2s",
      zIndex: 10,
    };
    const arrowStyles = {
      filled: { ...arrowBase, background: "rgba(0,0,0,0.55)", color: "#fff" },
      outline: { ...arrowBase, background: "rgba(255,255,255,0.9)", color: "#221B15", border: "2px solid #C1652F" },
      minimal: { ...arrowBase, background: "transparent", color: "#fff", fontSize: "2.5rem", width: 40, height: 40 },
    };
    const arrowStyleObj = arrowStyles[arrowStyle] || arrowStyles.filled;

    const positionStyles = {
      "center": {
        left: { position: "absolute", top: "50%", left: 16, transform: "translateY(-50%)" },
        right: { position: "absolute", top: "50%", right: 16, transform: "translateY(-50%)" },
      },
      "bottom-right": {
        left: { position: "absolute", bottom: 16, right: 76 },
        right: { position: "absolute", bottom: 16, right: 16 },
      },
      "outside": {
        left: { position: "absolute", top: "50%", left: -60, transform: "translateY(-50%)" },
        right: { position: "absolute", top: "50%", right: -60, transform: "translateY(-50%)" },
      },
    };
    const pos = positionStyles[arrowPosition] || positionStyles.center;

    const css = `
      #${id} {
        position: relative;
        height: ${heightDesktop};
        border-radius: ${borderRadius};
        overflow: hidden;
        width: 100%;
      }
      #${id} .slider-track {
        display: flex;
        height: 100%;
        transition: ${transition === "slide"
          ? `transform ${transitionDuration} cubic-bezier(0.4, 0, 0.2, 1)`
          : "none"};
        transform: ${transition === "slide" ? `translateX(-${index * 100}%)` : "none"};
      }
      #${id} .slider-slide {
        min-width: 100%;
        height: 100%;
        position: relative;
        opacity: ${transition === "fade" ? "0" : "1"};
        ${transition === "fade" ? `position: absolute; top: 0; left: 0; right: 0; bottom: 0; transition: opacity ${transitionDuration};` : ""}
      }
      #${id} .slider-slide.active {
        opacity: 1;
        z-index: 1;
      }
      #${id} .slider-arrow:hover {
        transform: translateY(-50%) scale(1.08);
      }
      @media (max-width: 1024px) {
        #${id} { height: ${heightTablet}; }
      }
      @media (max-width: 768px) {
        #${id} { height: ${heightMobile}; }
        #${id} .slider-arrow { width: 36px !important; height: 36px !important; font-size: 1rem !important; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div
          id={id}
          onMouseEnter={() => shouldPause && setPaused(true)}
          onMouseLeave={() => shouldPause && setPaused(false)}
        >
          <div className="slider-track">
            {Array.from({ length: count }).map((_, i) => (
              <div
                key={i}
                className={`slider-slide ${i === index ? "active" : ""}`}
                style={{ zIndex: i === index ? 1 : 0 }}
              >
                {puckDropZone(puck, `slide-${i}`)}
              </div>
            ))}
          </div>

          {/* Barre de progression */}
          {showProgress === "true" && shouldAuto && (
            <div style={{
              position: "absolute", top: 0, left: 0, right: 0,
              height: 3, background: "rgba(255,255,255,0.2)", zIndex: 10,
            }}>
              <div style={{
                height: "100%", width: `${progress * 100}%`,
                background: "#C1652F", transition: "width 50ms linear",
              }} />
            </div>
          )}

          {/* Flèches */}
          {showArrows === "true" && count > 1 && (
            <>
              <button
                className="slider-arrow"
                onClick={prev}
                style={{ ...arrowStyleObj, ...pos.left }}
                aria-label="Slide précédent"
              >
                ‹
              </button>
              <button
                className="slider-arrow"
                onClick={next}
                style={{ ...arrowStyleObj, ...pos.right }}
                aria-label="Slide suivant"
              >
                ›
              </button>
            </>
          )}

          {/* Points */}
          {showDots === "true" && count > 1 && (
            <div style={{
              position: "absolute", bottom: 16, left: 0, right: 0,
              display: "flex", justifyContent: "center", gap: 8, zIndex: 10,
            }}>
              {Array.from({ length: count }).map((_, i) => (
                <button
                  key={i}
                  onClick={() => setIndex(i)}
                  style={{
                    width: i === index ? 24 : 8, height: 8,
                    borderRadius: 999, border: "none",
                    background: i === index ? "#C1652F" : "rgba(255,255,255,0.6)",
                    cursor: "pointer", transition: "all 0.3s",
                  }}
                  aria-label={`Aller au slide ${i + 1}`}
                />
              ))}
            </div>
          )}
        </div>
      </>
    );
  },
};


// ============================================================
//  GALLERY LIGHTBOX — Galerie avec visionneuse
// ============================================================

export const GalleryLightbox = {
  fields: {
    images: {
      type: "textarea",
      label: "Images (URL|titre, une par ligne)",
      defaultValue: "/fallbacks/product-fallback.jpg|Produit 1\n/fallbacks/blog-fallback.jpg|Article 2\n/fallbacks/hero-fallback.jpg|Hero 3",
    },
    columnsDesktop: { type: "number", label: "Colonnes (desktop)", defaultValue: 3 },
    columnsTablet: { type: "number", label: "Colonnes (tablette)", defaultValue: 2 },
    columnsMobile: { type: "number", label: "Colonnes (mobile)", defaultValue: 1 },
    gap: { type: "text", label: "Espacement", defaultValue: "12px" },
    ratio: {
      type: "select", label: "Ratio",
      options: [
        { label: "Carré 1:1", value: "1/1" },
        { label: "Paysage 16:9", value: "16/9" },
        { label: "Portrait 4:5", value: "4/5" },
        { label: "Original", value: "auto" },
      ],
    },
    borderRadius: { type: "text", label: "Arrondi", defaultValue: "12px" },
    hoverEffect: {
      type: "select", label: "Effet au survol",
      options: [
        { label: "Aucun", value: "none" },
        { label: "Zoom", value: "zoom" },
        { label: "Overlay foncé", value: "darken" },
        { label: "Icône loupe", value: "icon" },
      ],
    },
    showCaptions: {
      type: "radio", label: "Afficher les titres",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
  },
  defaultProps: {
    images: "/fallbacks/product-fallback.jpg|Produit 1\n/fallbacks/blog-fallback.jpg|Article 2\n/fallbacks/hero-fallback.jpg|Hero 3",
    columnsDesktop: 3,
    columnsTablet: 2,
    columnsMobile: 1,
    gap: "12px",
    ratio: "1/1",
    borderRadius: "12px",
    hoverEffect: "zoom",
    showCaptions: "true",
  },
  render: (props) => {
    const { images, columnsDesktop, columnsTablet, columnsMobile,
            gap, ratio, borderRadius, hoverEffect, showCaptions } = props;

    const id = useResponsiveId("gallerylb");
    const [lightboxIndex, setLightboxIndex] = React.useState(null);

    const items = splitLines(images).map((line) => {
      const [url, ...titleParts] = line.split("|");
      return { url: url.trim(), title: titleParts.join("|").trim() };
    });

    const openLightbox = (i) => setLightboxIndex(i);
    const closeLightbox = () => setLightboxIndex(null);
    const nextImage = () => setLightboxIndex((i) => (i + 1) % items.length);
    const prevImage = () => setLightboxIndex((i) => (i - 1 + items.length) % items.length);

    // Keyboard nav + body scroll lock
    React.useEffect(() => {
      if (lightboxIndex === null) return;
      const onKey = (e) => {
        if (e.key === "Escape") closeLightbox();
        if (e.key === "ArrowRight") nextImage();
        if (e.key === "ArrowLeft") prevImage();
      };
      window.addEventListener("keydown", onKey);
      document.body.style.overflow = "hidden";
      return () => {
        window.removeEventListener("keydown", onKey);
        document.body.style.overflow = "";
      };
    }, [lightboxIndex]);

    const hoverCss = {
      zoom: `#${id} .gallery-item:hover .gallery-img { transform: scale(1.08); }`,
      darken: `#${id} .gallery-item:hover .gallery-img { filter: brightness(0.7); }`,
      icon: `#${id} .gallery-item:hover .gallery-icon { opacity: 1; }`,
      none: "",
    }[hoverEffect] || "";

    const css = `
      #${id} {
        display: grid;
        grid-template-columns: repeat(${columnsDesktop}, 1fr);
        gap: ${gap};
        width: 100%;
      }
      #${id} .gallery-item {
        position: relative;
        border-radius: ${borderRadius};
        overflow: hidden;
        cursor: pointer;
        aspect-ratio: ${ratio === "auto" ? "auto" : ratio};
        background: #f5f5f5;
      }
      #${id} .gallery-img {
        width: 100%; height: 100%;
        object-fit: cover;
        transition: transform 0.4s, filter 0.4s;
        display: block;
      }
      #${id} .gallery-caption {
        position: absolute; bottom: 0; left: 0; right: 0;
        padding: 12px; color: #fff;
        background: linear-gradient(to top, rgba(0,0,0,0.7), transparent);
        font-size: 0.85rem;
      }
      #${id} .gallery-icon {
        position: absolute; inset: 0;
        display: flex; align-items: center; justify-content: center;
        font-size: 2rem; color: #fff;
        opacity: 0; transition: opacity 0.3s;
        background: rgba(0, 0, 0, 0.3);
      }
      #${id} .lightbox-overlay {
        position: fixed; inset: 0;
        background: rgba(0, 0, 0, 0.95);
        z-index: 99999;
        display: flex; align-items: center; justify-content: center;
        padding: 40px;
      }
      #${id} .lightbox-image {
        max-width: 90vw; max-height: 85vh;
        object-fit: contain;
        border-radius: 8px;
      }
      #${id} .lightbox-close {
        position: fixed; top: 20px; right: 24px;
        background: rgba(255, 255, 255, 0.15); border: none;
        color: #fff; width: 44px; height: 44px;
        border-radius: 50%; font-size: 1.5rem;
        cursor: pointer; display: flex;
        align-items: center; justify-content: center;
      }
      #${id} .lightbox-nav {
        position: fixed; top: 50%; transform: translateY(-50%);
        background: rgba(255, 255, 255, 0.15); border: none;
        color: #fff; width: 56px; height: 56px;
        border-radius: 50%; font-size: 2rem;
        cursor: pointer; display: flex;
        align-items: center; justify-content: center;
      }
      #${id} .lightbox-nav.prev { left: 20px; }
      #${id} .lightbox-nav.next { right: 20px; }
      #${id} .lightbox-counter {
        position: fixed; bottom: 20px; left: 50%;
        transform: translateX(-50%);
        color: #fff; font-size: 0.9rem;
        background: rgba(0, 0, 0, 0.5);
        padding: 6px 16px; border-radius: 999px;
      }
      ${hoverCss}
      @media (max-width: 1024px) {
        #${id} { grid-template-columns: repeat(${columnsTablet}, 1fr); }
      }
      @media (max-width: 768px) {
        #${id} { grid-template-columns: repeat(${columnsMobile}, 1fr); }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {items.map((item, i) => (
            <div key={i} className="gallery-item" onClick={() => openLightbox(i)}>
              <img src={item.url} alt={item.title} className="gallery-img" loading="lazy" />
              {showCaptions === "true" && item.title && (
                <div className="gallery-caption">{item.title}</div>
              )}
              {hoverEffect === "icon" && (
                <div className="gallery-icon">🔍</div>
              )}
            </div>
          ))}

          {/* Lightbox */}
          {lightboxIndex !== null && (
            <div className="lightbox-overlay" onClick={closeLightbox}>
              <img
                src={items[lightboxIndex].url}
                alt={items[lightboxIndex].title}
                className="lightbox-image"
                onClick={(e) => e.stopPropagation()}
              />
              <button className="lightbox-close" onClick={closeLightbox}>×</button>
              {items.length > 1 && (
                <>
                  <button
                    className="lightbox-nav prev"
                    onClick={(e) => { e.stopPropagation(); prevImage(); }}
                  >‹</button>
                  <button
                    className="lightbox-nav next"
                    onClick={(e) => { e.stopPropagation(); nextImage(); }}
                  >›</button>
                </>
              )}
              <div className="lightbox-counter">
                {lightboxIndex + 1} / {items.length}
              </div>
            </div>
          )}
        </div>
      </>
    );
  },
};


// ============================================================
//  VIDEO PLAYER CUSTOM — Player HTML5 avec contrôles custom
// ============================================================

export const VideoPlayerCustom = {
  fields: {
    src: { type: "text", label: "URL de la vidéo (MP4/WebM)" },
    poster: { type: "text", label: "Image de couverture (URL)" },
    ratio: {
      type: "select", label: "Ratio",
      options: [
        { label: "16:9", value: "16/9" },
        { label: "4:3", value: "4/3" },
        { label: "21:9", value: "21/9" },
        { label: "1:1", value: "1/1" },
      ],
    },
    autoplay: {
      type: "radio", label: "Lecture auto",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    loop: {
      type: "radio", label: "Boucle",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    muted: {
      type: "radio", label: "Muet par défaut",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    showControls: {
      type: "radio", label: "Afficher les contrôles",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    borderRadius: { type: "text", label: "Arrondi", defaultValue: "16px" },
  },
  defaultProps: {
    src: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    poster: "",
    ratio: "16/9",
    autoplay: "false",
    loop: "false",
    muted: "false",
    showControls: "true",
    accentColor: "#C1652F",
    borderRadius: "16px",
  },
  render: (props) => {
    const { src, poster, ratio, autoplay, loop, muted, showControls,
            accentColor, borderRadius } = props;

    const id = useResponsiveId("videocustom");
    const videoRef = React.useRef(null);
    const [playing, setPlaying] = React.useState(false);
    const [progress, setProgress] = React.useState(0);
    const [duration, setDuration] = React.useState(0);
    const [currentTime, setCurrentTime] = React.useState(0);
    const [volume, setVolume] = React.useState(1);
    const [showVolumeSlider, setShowVolumeSlider] = React.useState(false);

    React.useEffect(() => {
      const v = videoRef.current;
      if (!v) return;
      const onTimeUpdate = () => {
        setCurrentTime(v.currentTime);
        setProgress(v.duration ? (v.currentTime / v.duration) * 100 : 0);
      };
      const onLoaded = () => setDuration(v.duration || 0);
      const onPlay = () => setPlaying(true);
      const onPause = () => setPlaying(false);
      v.addEventListener("timeupdate", onTimeUpdate);
      v.addEventListener("loadedmetadata", onLoaded);
      v.addEventListener("play", onPlay);
      v.addEventListener("pause", onPause);
      return () => {
        v.removeEventListener("timeupdate", onTimeUpdate);
        v.removeEventListener("loadedmetadata", onLoaded);
        v.removeEventListener("play", onPlay);
        v.removeEventListener("pause", onPause);
      };
    }, []);

    const togglePlay = () => {
      const v = videoRef.current;
      if (!v) return;
      if (v.paused) v.play();
      else v.pause();
    };

    const seek = (e) => {
      const v = videoRef.current;
      if (!v || !duration) return;
      const rect = e.currentTarget.getBoundingClientRect();
      const ratio = (e.clientX - rect.left) / rect.width;
      v.currentTime = ratio * duration;
    };

    const toggleFullscreen = () => {
      const v = videoRef.current;
      if (!v) return;
      if (v.requestFullscreen) v.requestFullscreen();
      else if (v.webkitRequestFullscreen) v.webkitRequestFullscreen();
    };

    const changeVolume = (e) => {
      const v = videoRef.current;
      if (!v) return;
      const newVol = Number(e.target.value);
      v.volume = newVol;
      setVolume(newVol);
    };

    const formatTime = (s) => {
      const m = Math.floor(s / 60);
      const sec = Math.floor(s % 60);
      return `${m}:${String(sec).padStart(2, "0")}`;
    };

    const css = `
      #${id} {
        position: relative;
        aspect-ratio: ${ratio};
        background: #000;
        border-radius: ${borderRadius};
        overflow: hidden;
        width: 100%;
      }
      #${id} video {
        width: 100%; height: 100%;
        display: block;
        object-fit: cover;
      }
      #${id} .vp-controls {
        position: absolute;
        bottom: 0; left: 0; right: 0;
        background: linear-gradient(to top, rgba(0,0,0,0.85), transparent);
        padding: 40px 16px 12px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        opacity: 0;
        transition: opacity 0.3s;
      }
      #${id}:hover .vp-controls,
      #${id} .vp-controls.always-visible { opacity: 1; }
      #${id} .vp-progress {
        height: 6px;
        background: rgba(255,255,255,0.25);
        border-radius: 999px;
        cursor: pointer;
        position: relative;
      }
      #${id} .vp-progress-fill {
        height: 100%;
        background: ${accentColor};
        border-radius: 999px;
        transition: width 0.1s;
      }
      #${id} .vp-buttons {
        display: flex;
        align-items: center;
        gap: 12px;
        color: #fff;
        font-size: 0.85rem;
      }
      #${id} .vp-btn {
        background: none;
        border: none;
        color: #fff;
        cursor: pointer;
        padding: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        transition: color 0.2s;
      }
      #${id} .vp-btn:hover {
        color: ${accentColor};
      }
      #${id} .vp-time {
        font-variant-numeric: tabular-nums;
        opacity: 0.9;
      }
      #${id} .vp-spacer {
        flex: 1;
      }
      #${id} .vp-volume-wrapper {
        position: relative;
        display: flex;
        align-items: center;
      }
      #${id} .vp-volume-slider {
        width: 0;
        opacity: 0;
        overflow: hidden;
        transition: width 0.2s, opacity 0.2s;
        margin-left: 8px;
      }
      #${id} .vp-volume-wrapper:hover .vp-volume-slider {
        width: 80px;
        opacity: 1;
      }
      #${id} .vp-volume-slider input {
        width: 80px;
        accent-color: ${accentColor};
      }
      #${id} .vp-big-play {
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: 80px; height: 80px;
        border-radius: 50%;
        background: ${accentColor};
        color: #fff;
        border: none;
        cursor: pointer;
        font-size: 2rem;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s;
      }
      #${id} .vp-big-play:hover {
        transform: translate(-50%, -50%) scale(1.08);
      }
      @media (max-width: 768px) {
        #${id} .vp-big-play { width: 60px; height: 60px; font-size: 1.5rem; }
        #${id} .vp-controls { opacity: 1; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <video
            ref={videoRef}
            src={src}
            poster={poster || undefined}
            autoPlay={autoplay === "true"}
            loop={loop === "true"}
            muted={muted === "true"}
            playsInline
            onClick={togglePlay}
          />

          {/* Gros bouton play central */}
          {!playing && (
            <button className="vp-big-play" onClick={togglePlay} aria-label="Lecture">
              ▶
            </button>
          )}

          {/* Contrôles custom */}
          {showControls === "true" && (
            <div className="vp-controls">
              <div className="vp-progress" onClick={seek}>
                <div className="vp-progress-fill" style={{ width: `${progress}%` }} />
              </div>
              <div className="vp-buttons">
                <button className="vp-btn" onClick={togglePlay} aria-label={playing ? "Pause" : "Lecture"}>
                  {playing ? "❚❚" : "▶"}
                </button>
                <span className="vp-time">{formatTime(currentTime)} / {formatTime(duration)}</span>
                <div className="vp-spacer" />
                <div className="vp-volume-wrapper">
                  <button className="vp-btn" onClick={() => setShowVolumeSlider(!showVolumeSlider)} aria-label="Volume">
                    {volume === 0 ? "🔇" : volume < 0.5 ? "🔉" : "🔊"}
                  </button>
                  <div className="vp-volume-slider">
                    <input
                      type="range"
                      min="0" max="1" step="0.05"
                      value={volume}
                      onChange={changeVolume}
                    />
                  </div>
                </div>
                <button className="vp-btn" onClick={toggleFullscreen} aria-label="Plein écran">
                  ⛶
                </button>
              </div>
            </div>
          )}
        </div>
      </>
    );
  },
};
