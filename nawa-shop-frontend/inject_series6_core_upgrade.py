"""
Série 6 — Upgrade Core.
Remplace SliderPro, GridContainer, Container, FlexContainer par des versions
complètes avec toutes les fonctionnalités Elementor.

Usage : python inject_series6_core_upgrade.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
WIDGETS_DIR = os.path.join(SRC_DIR, "puck", "widgets")
CONFIG_PATH = os.path.join(SRC_DIR, "puck", "config.jsx")


# ============================================================
#              UPGRADED CORE WIDGETS
# ============================================================

CORE_UPGRADE_JSX = '''/**
 * Série 6 — Core Upgrade : Slider, Grid, Container, Flexbox.
 * Versions complètes avec toutes les fonctionnalités Elementor.
 * Noms identiques aux anciens (remplacement direct).
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
  return String(text || "").split("\\n").map((s) => s.trim()).filter(Boolean);
}

/**
 * Parse les styles per-item : "index:grow,shrink,basis,order,align"
 * Ex: "1:1,0,auto,0,auto\\n2:2,1,200px,-1,center"
 */
function parsePerItemStyles(text) {
  const result = {};
  splitLines(text).forEach((line) => {
    const [idx, styles] = line.split(":");
    if (!idx || !styles) return;
    const [grow, shrink, basis, order, align] = styles.split(",").map((s) => s.trim());
    result[Number(idx)] = { grow, shrink, basis, order, align };
  });
  return result;
}


// ============================================================
//  SLIDER PRO V2 — Complet Elementor-like
// ============================================================

export const SliderPro = {
  fields: {
    slideCount: { type: "number", label: "Nombre de slides", defaultValue: 3 },

    // === Layout ===
    orientation: {
      type: "select", label: "Orientation",
      options: [
        { label: "Horizontal", value: "horizontal" },
        { label: "Vertical", value: "vertical" },
      ],
    },
    effect: {
      type: "select", label: "Effet",
      options: [
        { label: "Glissement", value: "slide" },
        { label: "Fondu", value: "fade" },
        { label: "Coverflow 3D", value: "coverflow" },
      ],
    },
    slidesPerView: {
      type: "select", label: "Slides visibles",
      options: [
        { label: "1 (plein écran)", value: "1" },
        { label: "1.15 (peek)", value: "1.15" },
        { label: "1.5", value: "1.5" },
        { label: "2", value: "2" },
      ],
    },
    gap: { type: "text", label: "Espacement entre slides", defaultValue: "0px" },

    // === Navigation ===
    showArrows: {
      type: "radio", label: "Flèches",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    arrowPosition: {
      type: "select", label: "Position flèches",
      options: [
        { label: "Centrées", value: "center" },
        { label: "Bas droite", value: "bottom-right" },
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
    arrowPrevIcon: { type: "text", label: "Icône précédent", defaultValue: "‹" },
    arrowNextIcon: { type: "text", label: "Icône suivant", defaultValue: "›" },

    showDots: {
      type: "radio", label: "Dots",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    paginationPosition: {
      type: "select", label: "Position dots",
      options: [
        { label: "Bas", value: "bottom" },
        { label: "Haut", value: "top" },
        { label: "Extérieur bas", value: "outside-bottom" },
      ],
    },

    // === Miniatures ===
    showThumbnails: {
      type: "radio", label: "Miniatures de navigation",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    thumbnailHeight: { type: "text", label: "Hauteur miniatures", defaultValue: "60px" },

    // === Play/Pause ===
    showPlayPause: {
      type: "radio", label: "Bouton play/pause visible",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },

    // === Autoplay ===
    autoPlay: {
      type: "radio", label: "Lecture automatique",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    autoPlayInterval: { type: "number", label: "Intervalle (ms)", defaultValue: 5000 },
    pauseOnHover: {
      type: "radio", label: "Pause au survol",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    showProgress: {
      type: "radio", label: "Barre de progression",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },

    // === Dimensions ===
    heightDesktop: { type: "text", label: "Hauteur (desktop)", defaultValue: "500px" },
    heightTablet: { type: "text", label: "Hauteur (tablette)", defaultValue: "400px" },
    heightMobile: { type: "text", label: "Hauteur (mobile)", defaultValue: "300px" },
    borderRadius: { type: "text", label: "Arrondi", defaultValue: "16px" },
    transitionDuration: { type: "text", label: "Durée transition", defaultValue: "600ms" },

    // === Navigation clavier ===
    keyboardNav: {
      type: "radio", label: "Navigation clavier",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
  },
  defaultProps: {
    slideCount: 3,
    orientation: "horizontal",
    effect: "slide",
    slidesPerView: "1",
    gap: "0px",
    showArrows: "true",
    arrowPosition: "center",
    arrowStyle: "filled",
    arrowPrevIcon: "‹",
    arrowNextIcon: "›",
    showDots: "true",
    paginationPosition: "bottom",
    showThumbnails: "false",
    thumbnailHeight: "60px",
    showPlayPause: "false",
    autoPlay: "true",
    autoPlayInterval: 5000,
    pauseOnHover: "true",
    showProgress: "true",
    heightDesktop: "500px",
    heightTablet: "400px",
    heightMobile: "300px",
    borderRadius: "16px",
    transitionDuration: "600ms",
    keyboardNav: "true",
  },
  render: (props) => {
    const id = useResponsiveId("sliderpro");
    const {
      slideCount, orientation, effect, slidesPerView, gap,
      showArrows, arrowPosition, arrowStyle, arrowPrevIcon, arrowNextIcon,
      showDots, paginationPosition,
      showThumbnails, thumbnailHeight,
      showPlayPause,
      autoPlay, autoPlayInterval, pauseOnHover, showProgress,
      heightDesktop, heightTablet, heightMobile, borderRadius, transitionDuration,
      keyboardNav,
    } = props;

    const [index, setIndex] = React.useState(0);
    const [paused, setPaused] = React.useState(false);
    const [manualPause, setManualPause] = React.useState(false);
    const [progress, setProgress] = React.useState(0);
    const count = Math.max(1, Number(slideCount) || 3);
    const shouldAuto = autoPlay === "true" && !manualPause;
    const shouldPause = pauseOnHover === "true" && paused;
    const isVertical = orientation === "vertical";
    const isCoverflow = effect === "coverflow";
    const isFade = effect === "fade";
    const perView = parseFloat(slidesPerView) || 1;
    const keyboardEnabled = keyboardNav === "true";

    React.useEffect(() => {
      if (!shouldAuto || count <= 1) return;
      if (shouldPause) return;
      const start = Date.now();
      const tick = setInterval(() => {
        const p = Math.min(1, (Date.now() - start) / Number(autoPlayInterval));
        setProgress(p);
        if (p >= 1) { setIndex((i) => (i + 1) % count); setProgress(0); }
      }, 50);
      return () => clearInterval(tick);
    }, [index, shouldAuto, shouldPause, count, autoPlayInterval]);

    React.useEffect(() => { setProgress(0); }, [index]);

    const next = () => setIndex((i) => (i + 1) % count);
    const prev = () => setIndex((i) => (i - 1 + count) % count);

    React.useEffect(() => {
      if (!keyboardEnabled) return;
      const onKey = (e) => {
        if (e.key === "ArrowRight" || e.key === "ArrowDown") next();
        if (e.key === "ArrowLeft" || e.key === "ArrowUp") prev();
      };
      window.addEventListener("keydown", onKey);
      return () => window.removeEventListener("keydown", onKey);
    }, [keyboardEnabled, count]);

    const arrowBase = {
      width: 48, height: 48, borderRadius: "50%",
      border: "none", cursor: "pointer", fontSize: "1.4rem",
      display: "flex", alignItems: "center", justifyContent: "center",
      transition: "all 0.2s", zIndex: 10,
    };
    const arrowStyles = {
      filled: { ...arrowBase, background: "rgba(0,0,0,0.55)", color: "#fff" },
      outline: { ...arrowBase, background: "rgba(255,255,255,0.9)", color: "#221B15", border: "2px solid #C1652F" },
      minimal: { ...arrowBase, background: "transparent", color: "#fff", fontSize: "2.5rem", width: 40, height: 40 },
    };
    const arrowObj = arrowStyles[arrowStyle] || arrowStyles.filled;

    const positionStyles = {
      "center": isVertical
        ? {
            prev: { position: "absolute", left: "50%", top: 16, transform: "translateX(-50%)" },
            next: { position: "absolute", left: "50%", bottom: 16, transform: "translateX(-50%)" },
          }
        : {
            prev: { position: "absolute", top: "50%", left: 16, transform: "translateY(-50%)" },
            next: { position: "absolute", top: "50%", right: 16, transform: "translateY(-50%)" },
          },
      "bottom-right": {
        prev: { position: "absolute", bottom: 16, right: 76 },
        next: { position: "absolute", bottom: 16, right: 16 },
      },
      "outside": {
        prev: { position: "absolute", top: "50%", left: -60, transform: "translateY(-50%)" },
        next: { position: "absolute", top: "50%", right: -60, transform: "translateY(-50%)" },
      },
    };
    const pos = positionStyles[arrowPosition] || positionStyles.center;

    const paginationStyles = {
      bottom: "bottom: 16px;",
      top: "top: 16px;",
      "outside-bottom": "bottom: -32px;",
    };
    const paginationStyle = paginationStyles[paginationPosition] || paginationStyles.bottom;

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
        flex-direction: ${isVertical ? "column" : "row"};
        height: 100%;
        gap: ${gap};
        transition: ${isFade || isCoverflow
          ? "none"
          : `transform ${transitionDuration} cubic-bezier(0.4, 0, 0.2, 1)`};
        transform: ${isFade || isCoverflow
          ? "none"
          : isVertical
            ? `translateY(-${index * (100 / perView)}%)`
            : `translateX(-${index * (100 / perView)}%)`};
      }
      #${id} .slider-slide {
        ${isVertical ? `min-height: calc(100% / ${perView});` : `min-width: calc(100% / ${perView});`}
        ${isVertical ? "width: 100%;" : "height: 100%;"}
        position: relative;
        opacity: ${isFade ? "0" : "1"};
        ${isFade ? `position: absolute; top: 0; left: 0; right: 0; bottom: 0; transition: opacity ${transitionDuration};` : ""}
        ${isCoverflow ? `
          transition: transform ${transitionDuration}, opacity ${transitionDuration};
          transform: scale(0.85);
          opacity: 0.5;
        ` : ""}
      }
      #${id} .slider-slide.active {
        opacity: 1;
        z-index: 2;
        ${isCoverflow ? "transform: scale(1);" : ""}
      }
      #${id} .slider-slide.adjacent {
        z-index: 1;
        ${isCoverflow ? "transform: scale(0.9); opacity: 0.7;" : ""}
      }
      #${id} .slider-arrow:hover {
        transform: ${pos.prev.transform ? pos.prev.transform + " scale(1.08)" : "scale(1.08)"};
      }
      #${id} .slider-playpause {
        position: absolute;
        top: 16px; right: 16px;
        width: 40px; height: 40px;
        border-radius: 50%;
        background: rgba(0,0,0,0.55);
        color: #fff;
        border: none;
        cursor: pointer;
        font-size: 1rem;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 11;
      }
      #${id} .slider-thumbnails {
        display: flex;
        gap: 8px;
        margin-top: 12px;
        justify-content: center;
        overflow-x: auto;
        padding-bottom: 4px;
      }
      #${id} .slider-thumb {
        height: ${thumbnailHeight};
        min-width: 80px;
        border-radius: 8px;
        overflow: hidden;
        border: 2px solid transparent;
        cursor: pointer;
        background: #f5f5f5;
        opacity: 0.6;
        transition: all 0.2s;
        padding: 0;
      }
      #${id} .slider-thumb.active {
        border-color: #C1652F;
        opacity: 1;
      }
      #${id} .slider-thumb:hover { opacity: 1; }
      @media (max-width: 1024px) {
        #${id} { height: ${heightTablet}; }
      }
      @media (max-width: 768px) {
        #${id} { height: ${heightMobile}; }
        #${id} .slider-arrow { width: 36px !important; height: 36px !important; font-size: 1rem !important; }
      }
    `;

    return (
      <div>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div
          id={id}
          onMouseEnter={() => shouldPause && setPaused(true)}
          onMouseLeave={() => shouldPause && setPaused(false)}
          tabIndex={keyboardEnabled ? 0 : -1}
        >
          <div className="slider-track">
            {Array.from({ length: count }).map((_, i) => {
              const isActive = i === index;
              const isAdjacent = Math.abs(i - index) === 1;
              return (
                <div
                  key={i}
                  className={`slider-slide ${isActive ? "active" : ""} ${isAdjacent && isCoverflow ? "adjacent" : ""}`}
                  style={{
                    zIndex: isActive ? 2 : (isAdjacent ? 1 : 0),
                    ${isFade ? "opacity: " + (isActive ? 1 : 0) + ";" : ""}
                  }}
                >
                  {puckDropZone(puck, `slide-${i}`)}
                </div>
              );
            })}
          </div>

          {showProgress === "true" && shouldAuto && (
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 3, background: "rgba(255,255,255,0.2)", zIndex: 10 }}>
              <div style={{ height: "100%", width: `${progress * 100}%`, background: "#C1652F", transition: "width 50ms linear" }} />
            </div>
          )}

          {showPlayPause === "true" && count > 1 && (
            <button
              className="slider-playpause"
              onClick={() => setManualPause(!manualPause)}
              aria-label={manualPause ? "Play" : "Pause"}
            >
              {manualPause ? "▶" : "❚❚"}
            </button>
          )}

          {showArrows === "true" && count > 1 && (
            <>
              <button className="slider-arrow" onClick={prev} style={{ ...arrowObj, ...pos.prev }} aria-label="Précédent">
                {arrowPrevIcon}
              </button>
              <button className="slider-arrow" onClick={next} style={{ ...arrowObj, ...pos.next }} aria-label="Suivant">
                {arrowNextIcon}
              </button>
            </>
          )}

          {showDots === "true" && count > 1 && (
            <div style={{ position: "absolute", left: 0, right: 0, display: "flex", justifyContent: "center", gap: 8, zIndex: 10, ...(paginationStyle.includes("bottom: 16") ? { bottom: 16 } : paginationStyle.includes("top: 16") ? { top: 16 } : { bottom: -32 }) }}>
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
                />
              ))}
            </div>
          )}
        </div>

        {showThumbnails === "true" && count > 1 && (
          <div className="slider-thumbnails" id={`${id}-thumbs`}>
            {Array.from({ length: count }).map((_, i) => (
              <button
                key={i}
                className={`slider-thumb ${i === index ? "active" : ""}`}
                onClick={() => setIndex(i)}
                aria-label={`Slide ${i + 1}`}
              >
                <span style={{ fontSize: "0.7rem", color: "#999", display: "flex", alignItems: "center", justifyContent: "center", height: "100%" }}>
                  {i + 1}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>
    );
  },
};


// ============================================================
//  GRID CONTAINER V2 — Complet Elementor-like
// ============================================================

export const GridContainer = {
  fields: {
    tag: {
      type: "select", label: "Balise",
      options: [
        { label: "div", value: "div" },
        { label: "section", value: "section" },
        { label: "main", value: "main" },
        { label: "article", value: "article" },
      ],
    },

    // === Template colonnes ===
    columnsMode: {
      type: "select", label: "Mode colonnes",
      options: [
        { label: "Nombre fixe", value: "fixed" },
        { label: "Auto-fit", value: "auto-fit" },
        { label: "Auto-fill", value: "auto-fill" },
      ],
    },
    gridTemplateColumns: { type: "text", label: "Colonnes (CSS)", defaultValue: "repeat(3, 1fr)" },
    minColumnWidth: { type: "text", label: "Largeur min (auto-fit/fill)", defaultValue: "240px" },
    gridTemplateRows: { type: "text", label: "Lignes (CSS)" },

    // === Responsive ===
    gridTemplateTablet: { type: "text", label: "Colonnes (tablette)", defaultValue: "repeat(2, 1fr)" },
    gridTemplateMobile: { type: "text", label: "Colonnes (mobile)", defaultValue: "1fr" },

    // === Zones nommées ===
    gridTemplateAreas: { type: "text", label: "Zones nommées (CSS grid-template-areas)" },

    // === Flow & Align ===
    autoFlow: {
      type: "select", label: "Auto-flow",
      options: [
        { label: "Row", value: "row" },
        { label: "Column", value: "column" },
        { label: "Row dense", value: "row dense" },
        { label: "Column dense", value: "column dense" },
      ],
    },
    justifyItems: {
      type: "select", label: "Justify items",
      options: [
        { label: "start", value: "start" },
        { label: "center", value: "center" },
        { label: "end", value: "end" },
        { label: "stretch", value: "stretch" },
      ],
    },
    alignItems: {
      type: "select", label: "Align items",
      options: [
        { label: "start", value: "start" },
        { label: "center", value: "center" },
        { label: "end", value: "end" },
        { label: "stretch", value: "stretch" },
      ],
    },
    justifyContent: {
      type: "select", label: "Justify content",
      options: [
        { label: "start", value: "start" },
        { label: "center", value: "center" },
        { label: "end", value: "end" },
        { label: "space-between", value: "space-between" },
        { label: "space-around", value: "space-around" },
        { label: "stretch", value: "stretch" },
      ],
    },
    alignContent: {
      type: "select", label: "Align content",
      options: [
        { label: "start", value: "start" },
        { label: "center", value: "center" },
        { label: "end", value: "end" },
        { label: "space-between", value: "space-between" },
        { label: "stretch", value: "stretch" },
      ],
    },

    // === Gap ===
    gap: { type: "text", label: "Gap", defaultValue: "20px" },
    rowGap: { type: "text", label: "Gap vertical" },
    columnGap: { type: "text", label: "Gap horizontal" },

    // === Placement enfants ===
    childPlacements: {
      type: "textarea", label: "Placement enfants (index:col,row — 1 par ligne, ex: 1:1/3,auto)",
      defaultValue: "",
    },

    // === Box héritage ===
    width: { type: "text", label: "Largeur" },
    maxWidth: { type: "text", label: "Max-width", defaultValue: "1200px" },
    padding: { type: "text", label: "Padding", defaultValue: "40px 20px" },
    margin: { type: "text", label: "Margin", defaultValue: "0 auto" },
    background: { type: "text", label: "Fond" },
    borderRadius: { type: "text", label: "Arrondi" },
  },
  defaultProps: {
    tag: "section",
    columnsMode: "fixed",
    gridTemplateColumns: "repeat(3, 1fr)",
    minColumnWidth: "240px",
    gridTemplateTablet: "repeat(2, 1fr)",
    gridTemplateMobile: "1fr",
    autoFlow: "row",
    justifyItems: "stretch",
    alignItems: "stretch",
    justifyContent: "stretch",
    alignContent: "stretch",
    gap: "20px",
    maxWidth: "1200px",
    padding: "40px 20px",
    margin: "0 auto",
  },
  render: (props) => {
    const id = useResponsiveId("gridpro");
    const {
      tag, columnsMode, gridTemplateColumns, minColumnWidth,
      gridTemplateRows, gridTemplateTablet, gridTemplateMobile,
      gridTemplateAreas, autoFlow, justifyItems, alignItems,
      justifyContent, alignContent, gap, rowGap, columnGap,
      childPlacements,
      width, maxWidth, padding, margin, background, borderRadius,
      puck,
    } = props;

    const Tag = tag || "div";

    let columns = gridTemplateColumns;
    if (columnsMode === "auto-fit") columns = `repeat(auto-fit, minmax(${minColumnWidth}, 1fr))`;
    if (columnsMode === "auto-fill") columns = `repeat(auto-fill, minmax(${minColumnWidth}, 1fr))`;

    // CSS placement des enfants
    const placementMap = {};
    splitLines(childPlacements).forEach((line) => {
      const [idx, pos] = line.split(":");
      if (!idx || !pos) return;
      const [col, row] = pos.split("/").map((s) => s.trim());
      placementMap[Number(idx)] = { col, row };
    });

    let childCss = "";
    Object.entries(placementMap).forEach(([idx, { col, row }]) => {
      childCss += `#${id} > *:nth-child(${idx}) {`;
      if (col) childCss += ` grid-column: ${col};`;
      if (row) childCss += ` grid-row: ${row};`;
      childCss += " }\\n";
    });

    const css = `
      #${id} {
        display: grid;
        grid-template-columns: ${columns};
        ${gridTemplateRows ? `grid-template-rows: ${gridTemplateRows};` : ""}
        ${gridTemplateAreas ? `grid-template-areas: ${gridTemplateAreas};` : ""}
        grid-auto-flow: ${autoFlow};
        justify-items: ${justifyItems};
        align-items: ${alignItems};
        justify-content: ${justifyContent};
        align-content: ${alignContent};
        gap: ${gap};
        ${rowGap ? `row-gap: ${rowGap};` : ""}
        ${columnGap ? `column-gap: ${columnGap};` : ""}
        width: ${width || "100%"};
        max-width: ${maxWidth};
        padding: ${padding};
        margin: ${margin};
        ${background ? `background: ${background};` : ""}
        ${borderRadius ? `border-radius: ${borderRadius};` : ""}
        box-sizing: border-box;
      }
      ${childCss}
      @media (max-width: 1024px) {
        #${id} { grid-template-columns: ${gridTemplateTablet}; }
      }
      @media (max-width: 768px) {
        #${id} { grid-template-columns: ${gridTemplateMobile}; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <Tag id={id}>
          {puckDropZone(puck)}
        </Tag>
      </>
    );
  },
};


// ============================================================
//  CONTAINER V2 — Complet Elementor-like
// ============================================================

export const Container = {
  fields: {
    tag: {
      type: "select", label: "Balise",
      options: [
        { label: "div", value: "div" },
        { label: "section", value: "section" },
        { label: "main", value: "main" },
        { label: "article", value: "article" },
        { label: "aside", value: "aside" },
        { label: "header", value: "header" },
        { label: "footer", value: "footer" },
      ],
    },

    // === Layout ===
    widthMode: {
      type: "select", label: "Largeur",
      options: [
        { label: "Contained (max-width)", value: "contained" },
        { label: "Full width (100%)", value: "full" },
        { label: "Boxed (custom)", value: "boxed" },
      ],
    },
    maxWidthDesktop: { type: "text", label: "Max-width (desktop)", defaultValue: "1200px" },
    maxWidthTablet: { type: "text", label: "Max-width (tablette)", defaultValue: "720px" },
    maxWidthMobile: { type: "text", label: "Max-width (mobile)", defaultValue: "100%" },
    customWidth: { type: "text", label: "Largeur custom (boxed)" },

    // === Espacement ===
    paddingDesktop: { type: "text", label: "Padding (desktop)", defaultValue: "60px 24px" },
    paddingTablet: { type: "text", label: "Padding (tablette)", defaultValue: "40px 16px" },
    paddingMobile: { type: "text", label: "Padding (mobile)", defaultValue: "24px 12px" },
    margin: { type: "text", label: "Margin", defaultValue: "0 auto" },

    // === Dimensions ===
    minHeight: { type: "text", label: "Hauteur min" },
    maxHeight: { type: "text", label: "Hauteur max" },
    aspectRatio: {
      type: "select", label: "Aspect ratio",
      options: [
        { label: "Auto", value: "auto" },
        { label: "16:9", value: "16/9" },
        { label: "4:3", value: "4/3" },
        { label: "1:1", value: "1/1" },
        { label: "21:9", value: "21/9" },
        { label: "9:16", value: "9/16" },
      ],
    },

    // === Overflow ===
    overflow: {
      type: "select", label: "Overflow",
      options: [
        { label: "Visible", value: "visible" },
        { label: "Hidden", value: "hidden" },
        { label: "Auto", value: "auto" },
        { label: "Scroll", value: "scroll" },
      ],
    },

    // === Style ===
    background: { type: "text", label: "Fond (couleur)" },
    backgroundImage: { type: "text", label: "Image de fond (URL)" },
    backgroundVideo: { type: "text", label: "Vidéo de fond (MP4 URL)" },
    parallax: {
      type: "radio", label: "Parallaxe (bg fixe)",
      options: [{ label: "Oui", value: "true" }, { label: "Non", value: "false" }],
    },
    borderRadius: { type: "text", label: "Arrondi" },
    boxShadow: { type: "text", label: "Ombre" },

    // === Position ===
    position: {
      type: "select", label: "Position",
      options: [
        { label: "static", value: "static" },
        { label: "relative", value: "relative" },
        { label: "sticky", value: "sticky" },
      ],
    },
    zIndex: { type: "text", label: "Z-index" },
  },
  defaultProps: {
    tag: "section",
    widthMode: "contained",
    maxWidthDesktop: "1200px",
    maxWidthTablet: "720px",
    maxWidthMobile: "100%",
    paddingDesktop: "60px 24px",
    paddingTablet: "40px 16px",
    paddingMobile: "24px 12px",
    margin: "0 auto",
    aspectRatio: "auto",
    overflow: "visible",
    parallax: "false",
    position: "static",
  },
  render: (props) => {
    const id = useResponsiveId("container");
    const {
      tag, widthMode, maxWidthDesktop, maxWidthTablet, maxWidthMobile,
      customWidth, paddingDesktop, paddingTablet, paddingMobile, margin,
      minHeight, maxHeight, aspectRatio, overflow,
      background, backgroundImage, backgroundVideo, parallax,
      borderRadius, boxShadow, position, zIndex,
      puck,
    } = props;

    const Tag = tag || "div";

    let maxW = "100%";
    if (widthMode === "contained") maxW = maxWidthDesktop;
    if (widthMode === "boxed") maxW = customWidth || maxWidthDesktop;
    if (widthMode === "full") maxW = "100%";

    const parallaxCss = parallax === "true" ? "background-attachment: fixed;" : "";

    const css = `
      #${id} {
        position: ${position};
        ${zIndex ? `z-index: ${zIndex};` : ""}
        max-width: ${maxW};
        ${customWidth && widthMode === "boxed" ? `width: ${customWidth};` : "width: 100%;"}
        padding: ${paddingDesktop};
        margin: ${margin};
        ${minHeight ? `min-height: ${minHeight};` : ""}
        ${maxHeight ? `max-height: ${maxHeight};` : ""}
        ${aspectRatio !== "auto" ? `aspect-ratio: ${aspectRatio};` : ""}
        overflow: ${overflow};
        ${background ? `background-color: ${background};` : ""}
        ${backgroundImage ? `background-image: url('${backgroundImage}'); background-size: cover; background-position: center;` : ""}
        ${backgroundVideo ? `background-image: url('${backgroundVideo}'); background-size: cover;` : ""}
        ${parallaxCss}
        ${borderRadius ? `border-radius: ${borderRadius};` : ""}
        ${boxShadow ? `box-shadow: ${boxShadow};` : ""}
        box-sizing: border-box;
      }
      @media (max-width: 1024px) {
        #${id} { max-width: ${widthMode === "contained" ? maxWidthTablet : maxW}; padding: ${paddingTablet}; }
      }
      @media (max-width: 768px) {
        #${id} { max-width: ${widthMode === "contained" ? maxWidthMobile : maxW}; padding: ${paddingMobile}; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <Tag id={id}>
          {backgroundVideo && (
            <video
              autoPlay loop muted playsInline
              style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", zIndex: -1 }}
            >
              <source src={backgroundVideo} type="video/mp4" />
            </video>
          )}
          {puckDropZone(puck)}
        </Tag>
      </>
    );
  },
};


// ============================================================
//  FLEX CONTAINER V2 — Complet Elementor-like
// ============================================================

export const FlexContainer = {
  fields: {
    tag: {
      type: "select", label: "Balise",
      options: [
        { label: "div", value: "div" },
        { label: "section", value: "section" },
        { label: "header", value: "header" },
        { label: "nav", value: "nav" },
        { label: "main", value: "main" },
        { label: "footer", value: "footer" },
      ],
    },

    // === Flex propriétés ===
    direction: {
      type: "select", label: "Direction (desktop)",
      options: [
        { label: "Row →", value: "row" },
        { label: "Column ↓", value: "column" },
        { label: "Row-reverse ←", value: "row-reverse" },
        { label: "Column-reverse ↑", value: "column-reverse" },
      ],
    },
    directionMobile: {
      type: "select", label: "Direction (mobile)",
      options: [
        { label: "Row →", value: "row" },
        { label: "Column ↓", value: "column" },
        { label: "Row-reverse ←", value: "row-reverse" },
        { label: "Column-reverse ↑", value: "column-reverse" },
      ],
    },
    wrap: {
      type: "select", label: "Wrap (desktop)",
      options: [
        { label: "nowrap", value: "nowrap" },
        { label: "wrap", value: "wrap" },
        { label: "wrap-reverse", value: "wrap-reverse" },
      ],
    },
    wrapMobile: {
      type: "select", label: "Wrap (mobile)",
      options: [
        { label: "nowrap", value: "nowrap" },
        { label: "wrap", value: "wrap" },
        { label: "wrap-reverse", value: "wrap-reverse" },
      ],
    },
    justify: {
      type: "select", label: "Justify-content",
      options: [
        { label: "flex-start", value: "flex-start" },
        { label: "center", value: "center" },
        { label: "flex-end", value: "flex-end" },
        { label: "space-between", value: "space-between" },
        { label: "space-around", value: "space-around" },
        { label: "space-evenly", value: "space-evenly" },
      ],
    },
    alignItems: {
      type: "select", label: "Align-items",
      options: [
        { label: "flex-start", value: "flex-start" },
        { label: "center", value: "center" },
        { label: "flex-end", value: "flex-end" },
        { label: "stretch", value: "stretch" },
        { label: "baseline", value: "baseline" },
      ],
    },
    alignContent: {
      type: "select", label: "Align-content",
      options: [
        { label: "flex-start", value: "flex-start" },
        { label: "center", value: "center" },
        { label: "flex-end", value: "flex-end" },
        { label: "space-between", value: "space-between" },
        { label: "space-around", value: "space-around" },
        { label: "stretch", value: "stretch" },
      ],
    },

    // === Gap responsive ===
    gapDesktop: { type: "text", label: "Gap (desktop)", defaultValue: "20px" },
    gapTablet: { type: "text", label: "Gap (tablette)", defaultValue: "16px" },
    gapMobile: { type: "text", label: "Gap (mobile)", defaultValue: "12px" },
    rowGap: { type: "text", label: "Row-gap (override)" },
    columnGap: { type: "text", label: "Column-gap (override)" },

    // === Per-item styles ===
    perItemStyles: {
      type: "textarea",
      label: "Styles enfants (index:grow,shrink,basis,order,align — 1 par ligne)",
      defaultValue: "",
    },

    // === Dimensions & style ===
    width: { type: "text", label: "Largeur" },
    maxWidth: { type: "text", label: "Max-width", defaultValue: "1200px" },
    minHeight: { type: "text", label: "Hauteur min" },
    padding: { type: "text", label: "Padding", defaultValue: "40px 20px" },
    margin: { type: "text", label: "Margin", defaultValue: "0 auto" },
    background: { type: "text", label: "Fond" },
    borderRadius: { type: "text", label: "Arrondi" },
    boxShadow: { type: "text", label: "Ombre" },
    overflow: {
      type: "select", label: "Overflow",
      options: [
        { label: "Visible", value: "visible" },
        { label: "Hidden", value: "hidden" },
        { label: "Auto", value: "auto" },
      ],
    },
  },
  defaultProps: {
    tag: "section",
    direction: "row",
    directionMobile: "column",
    wrap: "wrap",
    wrapMobile: "wrap",
    justify: "flex-start",
    alignItems: "stretch",
    alignContent: "stretch",
    gapDesktop: "20px",
    gapTablet: "16px",
    gapMobile: "12px",
    maxWidth: "1200px",
    padding: "40px 20px",
    margin: "0 auto",
    overflow: "visible",
  },
  render: (props) => {
    const id = useResponsiveId("flexpro");
    const {
      tag, direction, directionMobile, wrap, wrapMobile,
      justify, alignItems, alignContent,
      gapDesktop, gapTablet, gapMobile, rowGap, columnGap,
      perItemStyles,
      width, maxWidth, minHeight, padding, margin,
      background, borderRadius, boxShadow, overflow,
      puck,
    } = props;

    const Tag = tag || "div";

    const perItem = parsePerItemStyles(perItemStyles);
    let childCss = "";
    Object.entries(perItem).forEach(([idx, s]) => {
      childCss += `#${id} > *:nth-child(${idx}) {`;
      if (s.grow) childCss += ` flex-grow: ${s.grow};`;
      if (s.shrink) childCss += ` flex-shrink: ${s.shrink};`;
      if (s.basis && s.basis !== "auto") childCss += ` flex-basis: ${s.basis};`;
      if (s.order) childCss += ` order: ${s.order};`;
      if (s.align && s.align !== "auto") childCss += ` align-self: ${s.align};`;
      childCss += " }\\n";
    });

    const css = `
      #${id} {
        display: flex;
        flex-direction: ${direction};
        flex-wrap: ${wrap};
        justify-content: ${justify};
        align-items: ${alignItems};
        align-content: ${alignContent};
        gap: ${gapDesktop};
        ${rowGap ? `row-gap: ${rowGap};` : ""}
        ${columnGap ? `column-gap: ${columnGap};` : ""}
        width: ${width || "100%"};
        max-width: ${maxWidth};
        ${minHeight ? `min-height: ${minHeight};` : ""}
        padding: ${padding};
        margin: ${margin};
        ${background ? `background: ${background};` : ""}
        ${borderRadius ? `border-radius: ${borderRadius};` : ""}
        ${boxShadow ? `box-shadow: ${boxShadow};` : ""}
        overflow: ${overflow};
        box-sizing: border-box;
      }
      ${childCss}
      @media (max-width: 1024px) {
        #${id} { gap: ${gapTablet}; }
      }
      @media (max-width: 768px) {
        #${id} { flex-direction: ${directionMobile}; flex-wrap: ${wrapMobile}; gap: ${gapMobile}; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <Tag id={id}>
          {puckDropZone(puck)}
        </Tag>
      </>
    );
  },
};
'''


# ============================================================
#                    PATCH CONFIG
# ============================================================

MARKER = "/* === SERIES 6 CORE UPGRADE === */"

# Les 4 widgets à remplacer
UPGRADED = ["SliderPro", "GridContainer", "Container", "FlexContainer"]


def write_upgrade():
    os.makedirs(WIDGETS_DIR, exist_ok=True)
    path = os.path.join(WIDGETS_DIR, "widgetsCoreUpgrade.jsx")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if "export const SliderPro" in f.read() and "perItemStyles" in f.read():
                print(f"  [SKIP] widgetsCoreUpgrade.jsx existe déjà")
                return False
        shutil.copy2(path, path + ".bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(CORE_UPGRADE_JSX)
    print(f"  [OK] src/puck/widgets/widgetsCoreUpgrade.jsx créé")
    return True


def remove_names_from_import(content, names):
    """Retire des noms spécifiques de tous les imports."""
    for name in names:
        # Match dans les imports multi-lignes : "  Name,\n" ou "Name, " ou ", Name"
        content = re.sub(rf'\b{name}\s*,\s*', '', content)
        content = re.sub(rf',\s*\b{name}\b', '', content)
    return content


def update_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"  [ERREUR] config.jsx introuvable")
        return False

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER in content:
        print("  [SKIP] config.jsx déjà patché pour Série 6")
        return False

    shutil.copy2(CONFIG_PATH, CONFIG_PATH + ".before-series6.bak")
    print(f"  [BACKUP] config.jsx.before-series6.bak")

    # 1. Retirer les 4 noms des imports existants
    # (mais pas des composants, ni des catégories — on ne remplace qu'au niveau import)
    lines = content.split("\n")
    new_lines = []
    removed_count = 0

    for line in lines:
        # Détecter si c'est une ligne d'import de widgets/
        is_widget_import = "from \"./widgets/" in line or "from './widgets/" in line
        if is_widget_import:
            # Retirer les noms upgradés
            for name in UPGRADED:
                # Match exact du nom (avec virgule optionnelle)
                pattern = rf'\b{name}\b,?\s*'
                if re.search(pattern, line):
                    line = re.sub(pattern, '', line)
                    removed_count += 1
        new_lines.append(line)

    content = "\n".join(new_lines)

    # Nettoyer les lignes d'import vides
    content = re.sub(r'import\s*\{\s*\}\s*from\s*["\'][^"\']+["\'];?\s*\n', '', content)
    # Nettoyer les imports avec virgule finale orpheline
    content = re.sub(r',\s*\n(\s*)\}', r'\n\1}', content)
    content = re.sub(r'\{\s*,', '{', content)

    print(f"  [OK] {removed_count} nom(s) retiré(s) des imports")

    # 2. Ajouter le nouvel import
    imports = f'''
{MARKER}
import {{
  SliderPro, GridContainer, Container, FlexContainer,
}} from "./widgets/widgetsCoreUpgrade";
{MARKER}
'''
    content = re.sub(
        r'(import React from "react";\n)',
        r'\1' + imports,
        content,
        count=1,
    )

    print("  [OK] Import depuis widgetsCoreUpgrade ajouté")

    # 3. Vérifier que les 4 noms sont dans components
    for name in UPGRADED:
        comp_section = re.search(r'components:\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', content, re.DOTALL)
        if comp_section and name not in comp_section.group(1):
            print(f"  [ATTENTION] {name} absent de components")

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  SÉRIE 6 — UPGRADE CORE")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable")
        return

    print("\n[1/3] Création des 4 widgets upgradés...")
    write_upgrade()

    print("\n[2/3] Mise à jour de config.jsx...")
    update_config()

    print("\n[3/3] Vérification syntaxique...")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    opens = content.count("{") - content.count("}")
    parens = content.count("(") - content.count(")")
    brackets = content.count("[") - content.count("]")
    print(f"  Accolades   : {'OK' if opens == 0 else f'DÉSÉQUILIBRE ({opens:+d})'}")
    print(f"  Parenthèses : {'OK' if parens == 0 else f'DÉSÉQUILIBRE ({parens:+d})'}")
    print(f"  Crochets    : {'OK' if brackets == 0 else f'DÉSÉQUILIBRE ({brackets:+d})'}")

    print()
    print("=" * 60)
    print("  ✅ SÉRIE 6 TERMINÉE — 4 widgets upgradés")
    print("=" * 60)
    print("\nAméliorations :")
    print("  SliderPro       + Miniatures, Coverflow, Vertical, Peek, Play/Pause")
    print("  GridContainer   + Placement enfants, Zones nommées, Responsive BP")
    print("  Container       + Contained/Full, Overflow, Aspect ratio, Vidéo fond")
    print("  FlexContainer   + Per-item styles, Direction responsive")
    print()
    print("Redémarrer :")
    print("  Remove-Item -Recurse -Force node_modules\\.vite")
    print("  npm run dev")


if __name__ == "__main__":
    main()