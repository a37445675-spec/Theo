"""
Ajoute 8 widgets avancés responsive : Masonry, Marquee, Cascade,
Repeater, Modal, Drawer, Portal, Mask.

Usage : python inject_advanced_widgets.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
WIDGETS_DIR = os.path.join(SRC_DIR, "puck", "widgets")
CONFIG_PATH = os.path.join(SRC_DIR, "puck", "config.jsx")


# ============================================================
#              WIDGETS AVANCÉS
# ============================================================

ADVANCED_WIDGETS = '''/**
 * Widgets avancés — Masonry, Marquee, Cascade, Repeater,
 * Modal, Drawer, Portal, Mask.
 * Tous responsive (Desktop / Tablet / Mobile).
 */
import React from "react";
import { useResponsiveId, ResponsiveStyle } from "../hooks/useResponsive";


// ============================================================
//  HELPERS
// ============================================================

function puckDropZone(puck, zone = "content") {
  if (!puck) return null;
  if (puck.DropZone) return <puck.DropZone zone={zone} />;
  if (puck.renderDropZone) return puck.renderDropZone({ zone });
  return null;
}

// Intersection Observer hook (pour Cascade)
function useInViewOnce(options = {}) {
  const ref = React.useRef(null);
  const [visible, setVisible] = React.useState(false);

  React.useEffect(() => {
    if (!ref.current || visible) return;
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setVisible(true); },
      { threshold: 0.15, ...options }
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [visible, options]);

  return [ref, visible];
}


// ============================================================
//  MASONRY — Galerie en colonnes
// ============================================================

export const Masonry = {
  fields: {
    columnsDesktop: { type: "number", label: "Colonnes (desktop)", defaultValue: 3 },
    columnsTablet: { type: "number", label: "Colonnes (tablette)", defaultValue: 2 },
    columnsMobile: { type: "number", label: "Colonnes (mobile)", defaultValue: 1 },
    gapDesktop: { type: "text", label: "Gap (desktop)", defaultValue: "16px" },
    gapMobile: { type: "text", label: "Gap (mobile)", defaultValue: "8px" },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "1200px" },
  },
  defaultProps: {
    columnsDesktop: 3,
    columnsTablet: 2,
    columnsMobile: 1,
    gapDesktop: "16px",
    gapMobile: "8px",
    maxWidth: "1200px",
  },
  render: (props) => {
    const { puck, columnsDesktop, columnsTablet, columnsMobile,
            gapDesktop, gapMobile, maxWidth } = props;
    const id = useResponsiveId("masonry");

    const css = `
      #${id} {
        column-count: ${columnsDesktop};
        column-gap: ${gapDesktop};
        max-width: ${maxWidth};
        margin: 0 auto;
        width: 100%;
      }
      #${id} > * {
        break-inside: avoid;
        margin-bottom: ${gapDesktop};
        display: block;
        width: 100%;
      }
      @media (max-width: 1024px) {
        #${id} { column-count: ${columnsTablet}; }
      }
      @media (max-width: 768px) {
        #${id} { column-count: ${columnsMobile}; column-gap: ${gapMobile}; }
        #${id} > * { margin-bottom: ${gapMobile}; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {puckDropZone(puck)}
        </div>
      </>
    );
  },
};


// ============================================================
//  MARQUEE — Défilement horizontal infini
// ============================================================

export const Marquee = {
  fields: {
    text: { type: "text", label: "Texte / HTML", defaultValue: "✨ Livraison offerte dès 49€ · Nouvelle collection disponible · " },
    speedDesktop: { type: "number", label: "Vitesse (desktop, sec)", defaultValue: 30 },
    speedMobile: { type: "number", label: "Vitesse (mobile, sec)", defaultValue: 20 },
    direction: {
      type: "select", label: "Direction",
      options: [
        { label: "Gauche →", value: "normal" },
        { label: "Droite ←", value: "reverse" },
      ],
    },
    background: { type: "text", label: "Fond", defaultValue: "#221B15" },
    textColor: { type: "text", label: "Couleur texte", defaultValue: "#D4A843" },
    padding: { type: "text", label: "Padding", defaultValue: "16px 0" },
    fontSize: { type: "text", label: "Taille police", defaultValue: "1rem" },
    pauseOnHover: {
      type: "radio", label: "Pause au survol",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
  },
  defaultProps: {
    text: "✨ Livraison offerte dès 49€ · Nouvelle collection disponible · ",
    speedDesktop: 30,
    speedMobile: 20,
    direction: "normal",
    background: "#221B15",
    textColor: "#D4A843",
    padding: "16px 0",
    fontSize: "1rem",
    pauseOnHover: "true",
  },
  render: (props) => {
    const { text, speedDesktop, speedMobile, direction, background,
            textColor, padding, fontSize, pauseOnHover } = props;
    const id = useResponsiveId("marquee");
    const content = (text || "").repeat(20);

    const css = `
      #${id} {
        background: ${background};
        color: ${textColor};
        padding: ${padding};
        overflow: hidden;
        white-space: nowrap;
        width: 100%;
      }
      #${id} .marquee-track {
        display: inline-block;
        animation: marquee-scroll-${id} ${speedDesktop}s linear infinite;
        animation-direction: ${direction};
        font-size: ${fontSize};
      }
      ${pauseOnHover === "true" ? `#${id}:hover .marquee-track { animation-play-state: paused; }` : ""}
      @keyframes marquee-scroll-${id} {
        0% { transform: translateX(0); }
        100% { transform: translateX(-50%); }
      }
      @media (max-width: 768px) {
        #${id} .marquee-track { animation-duration: ${speedMobile}s; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <div className="marquee-track">
            {content}
            {content}
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  CASCADE — Révélation au scroll
// ============================================================

export const Cascade = {
  fields: {
    animation: {
      type: "select", label: "Animation",
      options: [
        { label: "Fondu", value: "fade" },
        { label: "Monte", value: "slide-up" },
        { label: "Descend", value: "slide-down" },
        { label: "Vient de la gauche", value: "slide-left" },
        { label: "Vient de la droite", value: "slide-right" },
        { label: "Zoom", value: "zoom" },
      ],
    },
    duration: { type: "text", label: "Durée (ex: 0.8s)", defaultValue: "0.8s" },
    delay: { type: "text", label: "Délai (ex: 0s)", defaultValue: "0s" },
    threshold: { type: "number", label: "Seuil de déclenchement (0-1)", defaultValue: 0.15 },
    distance: { type: "text", label: "Distance (ex: 40px)", defaultValue: "40px" },
  },
  defaultProps: {
    animation: "slide-up",
    duration: "0.8s",
    delay: "0s",
    threshold: 0.15,
    distance: "40px",
  },
  render: (props) => {
    const { puck, animation, duration, delay, threshold, distance } = props;
    const id = useResponsiveId("cascade");
    const [ref, visible] = useInViewOnce({ threshold: Number(threshold) });

    const transforms = {
      "fade": "none",
      "slide-up": `translateY(${distance})`,
      "slide-down": `translateY(-${distance})`,
      "slide-left": `translateX(${distance})`,
      "slide-right": `translateX(-${distance})`,
      "zoom": "scale(0.9)",
    };
    const initialTransform = transforms[animation] || "none";
    const initialOpacity = animation === "fade" ? "0" : "0";

    const css = `
      #${id} {
        opacity: ${visible ? "1" : initialOpacity};
        transform: ${visible ? "none" : initialTransform};
        transition: opacity ${duration} ease ${delay}, transform ${duration} ease ${delay};
        will-change: opacity, transform;
      }
      @media (prefers-reduced-motion: reduce) {
        #${id} {
          opacity: 1;
          transform: none;
          transition: none;
        }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id} ref={ref}>
          {puckDropZone(puck)}
        </div>
      </>
    );
  },
};


// ============================================================
//  REPEATER — Contenu répété N fois
// ============================================================

export const Repeater = {
  fields: {
    countDesktop: { type: "number", label: "Nombre (desktop)", defaultValue: 3 },
    countTablet: { type: "number", label: "Nombre (tablette)", defaultValue: 2 },
    countMobile: { type: "number", label: "Nombre (mobile)", defaultValue: 1 },
    columnsDesktop: { type: "number", label: "Colonnes (desktop)", defaultValue: 3 },
    columnsMobile: { type: "number", label: "Colonnes (mobile)", defaultValue: 1 },
    gap: { type: "text", label: "Gap", defaultValue: "20px" },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "1200px" },
  },
  defaultProps: {
    countDesktop: 3,
    countTablet: 2,
    countMobile: 1,
    columnsDesktop: 3,
    columnsMobile: 1,
    gap: "20px",
    maxWidth: "1200px",
  },
  render: (props) => {
    const { puck, countDesktop, countTablet, countMobile,
            columnsDesktop, columnsMobile, gap, maxWidth } = props;
    const id = useResponsiveId("repeater");

    const css = `
      #${id} {
        display: grid;
        grid-template-columns: repeat(${columnsDesktop}, 1fr);
        gap: ${gap};
        max-width: ${maxWidth};
        margin: 0 auto;
        width: 100%;
      }
      @media (max-width: 1024px) {
        #${id} { grid-template-columns: repeat(${Math.min(columnsDesktop, 2)}, 1fr); }
        #${id} > .repeater-item:nth-child(n+${Number(countTablet) + 1}) { display: none; }
      }
      @media (max-width: 768px) {
        #${id} { grid-template-columns: repeat(${columnsMobile}, 1fr); }
        #${id} > .repeater-item:nth-child(n+${Number(countMobile) + 1}) { display: none; }
        #${id} > .repeater-item:nth-child(-n+${Number(countTablet)}) { display: block; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          {Array.from({ length: Math.max(countDesktop, countTablet, countMobile) }).map((_, i) => (
            <div key={i} className="repeater-item">
              {puckDropZone(puck, `item-${i}`)}
            </div>
          ))}
        </div>
      </>
    );
  },
};


// ============================================================
//  MODAL — Fenêtre modale
// ============================================================

export const Modal = {
  fields: {
    triggerLabel: { type: "text", label: "Texte du bouton", defaultValue: "Ouvrir" },
    triggerStyle: {
      type: "select", label: "Style du bouton",
      options: [
        { label: "Primaire", value: "primary" },
        { label: "Ghost", value: "ghost" },
      ],
    },
    title: { type: "text", label: "Titre", defaultValue: "Détails" },
    sizeDesktop: { type: "text", label: "Largeur (desktop)", defaultValue: "600px" },
    sizeMobile: { type: "text", label: "Largeur (mobile)", defaultValue: "92vw" },
    closeOnOverlay: {
      type: "radio", label: "Fermer au clic extérieur",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    maxHeight: { type: "text", label: "Hauteur max", defaultValue: "85vh" },
  },
  defaultProps: {
    triggerLabel: "Ouvrir",
    triggerStyle: "primary",
    title: "Détails",
    sizeDesktop: "600px",
    sizeMobile: "92vw",
    closeOnOverlay: "true",
    maxHeight: "85vh",
  },
  render: (props) => {
    const { puck, triggerLabel, triggerStyle, title, sizeDesktop,
            sizeMobile, closeOnOverlay, maxHeight } = props;
    const [open, setOpen] = React.useState(false);
    const id = useResponsiveId("modal");

    React.useEffect(() => {
      if (open) {
        document.body.style.overflow = "hidden";
        return () => { document.body.style.overflow = ""; };
      }
    }, [open]);

    const css = `
      #${id} .modal-overlay {
        position: fixed; inset: 0;
        background: rgba(0, 0, 0, 0.6);
        display: flex; align-items: center; justify-content: center;
        z-index: 9999; padding: 20px;
      }
      #${id} .modal-box {
        background: #fff;
        width: ${sizeDesktop};
        max-height: ${maxHeight};
        overflow-y: auto;
        border-radius: 16px;
        padding: 32px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        position: relative;
      }
      #${id} .modal-close {
        position: absolute; top: 12px; right: 16px;
        background: none; border: none;
        font-size: 1.75rem; cursor: pointer;
        color: #6B6259;
      }
      @media (max-width: 768px) {
        #${id} .modal-box { width: ${sizeMobile}; padding: 20px; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <button
            onClick={() => setOpen(true)}
            className={triggerStyle === "primary" ? "btn btn-primary" : "btn btn-ghost"}
          >
            {triggerLabel}
          </button>
          {open && (
            <div
              className="modal-overlay"
              onClick={() => closeOnOverlay === "true" && setOpen(false)}
            >
              <div className="modal-box" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={() => setOpen(false)}>×</button>
                {title && <h2 style={{ marginBottom: "16px" }}>{title}</h2>}
                {puckDropZone(puck)}
              </div>
            </div>
          )}
        </div>
      </>
    );
  },
};


// ============================================================
//  DRAWER — Tiroir latéral
// ============================================================

export const Drawer = {
  fields: {
    triggerLabel: { type: "text", label: "Texte du bouton", defaultValue: "Ouvrir" },
    position: {
      type: "select", label: "Position",
      options: [
        { label: "Droite", value: "right" },
        { label: "Gauche", value: "left" },
        { label: "Haut", value: "top" },
        { label: "Bas", value: "bottom" },
      ],
    },
    sizeDesktop: { type: "text", label: "Taille (desktop)", defaultValue: "400px" },
    sizeMobile: { type: "text", label: "Taille (mobile)", defaultValue: "85vw" },
    background: { type: "text", label: "Fond", defaultValue: "#F7F0E4" },
    title: { type: "text", label: "Titre", defaultValue: "" },
  },
  defaultProps: {
    triggerLabel: "Ouvrir",
    position: "right",
    sizeDesktop: "400px",
    sizeMobile: "85vw",
    background: "#F7F0E4",
    title: "",
  },
  render: (props) => {
    const { puck, triggerLabel, position, sizeDesktop, sizeMobile, background, title } = props;
    const [open, setOpen] = React.useState(false);
    const id = useResponsiveId("drawer");
    const isVertical = position === "top" || position === "bottom";

    const css = `
      #${id} .drawer-overlay {
        position: fixed; inset: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 9999;
      }
      #${id} .drawer-panel {
        position: fixed;
        background: ${background};
        z-index: 10000;
        padding: 32px;
        overflow-y: auto;
        box-shadow: 0 0 40px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s ease;
        ${position === "right" ? `top: 0; right: 0; bottom: 0; width: ${sizeDesktop};` : ""}
        ${position === "left" ? `top: 0; left: 0; bottom: 0; width: ${sizeDesktop};` : ""}
        ${position === "top" ? `top: 0; left: 0; right: 0; height: ${sizeDesktop};` : ""}
        ${position === "bottom" ? `bottom: 0; left: 0; right: 0; height: ${sizeDesktop};` : ""}
      }
      #${id} .drawer-close {
        position: absolute; top: 12px; right: 16px;
        background: none; border: none;
        font-size: 1.75rem; cursor: pointer;
      }
      @media (max-width: 768px) {
        #${id} .drawer-panel {
          ${isVertical
            ? `height: ${sizeMobile};`
            : `width: ${sizeMobile};`}
        }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <button className="btn btn-primary" onClick={() => setOpen(true)}>
            {triggerLabel}
          </button>
          {open && (
            <>
              <div className="drawer-overlay" onClick={() => setOpen(false)} />
              <div className="drawer-panel">
                <button className="drawer-close" onClick={() => setOpen(false)}>×</button>
                {title && <h2 style={{ marginBottom: "16px" }}>{title}</h2>}
                {puckDropZone(puck)}
              </div>
            </>
          )}
        </div>
      </>
    );
  },
};


// ============================================================
//  PORTAL — Injection dans un sélecteur distant
// ============================================================

export const Portal = {
  fields: {
    targetSelector: {
      type: "text", label: "Sélecteur CSS cible",
      defaultValue: "#portal-target",
    },
    fallbackMessage: {
      type: "text", label: "Message si cible absente",
      defaultValue: "Zone cible introuvable",
    },
    showInEditor: {
      type: "radio", label: "Afficher dans l'éditeur",
      options: [
        { label: "Oui (preview)", value: "true" },
        { label: "Non (rendu public seulement)", value: "false" },
      ],
    },
  },
  defaultProps: {
    targetSelector: "#portal-target",
    fallbackMessage: "Zone cible introuvable",
    showInEditor: "true",
  },
  render: (props) => {
    const { puck, targetSelector, fallbackMessage, showInEditor } = props;
    const id = useResponsiveId("portal");
    const [target, setTarget] = React.useState(null);
    const [checked, setChecked] = React.useState(false);

    // Dans Puck editor, on affiche en placeholder
    const isEditor = typeof window !== "undefined" && window.location.pathname.includes("/builder");

    React.useEffect(() => {
      if (isEditor && showInEditor === "true") {
        setChecked(true);
        return;
      }
      const el = document.querySelector(targetSelector);
      setTarget(el);
      setChecked(true);
    }, [targetSelector, isEditor, showInEditor]);

    if (isEditor && showInEditor === "true") {
      return (
        <div
          id={id}
          style={{
            padding: "20px",
            border: "2px dashed #C1652F",
            borderRadius: "12px",
            background: "#FEF6F0",
            textAlign: "center",
            color: "#C1652F",
            fontSize: "0.9rem",
          }}
        >
          📤 Portal vers <code>{targetSelector}</code>
          <div style={{ marginTop: "12px" }}>{puckDropZone(puck)}</div>
        </div>
      );
    }

    if (!checked) return null;
    if (!target) {
      return (
        <div style={{ padding: "12px", background: "#FEE2E2", color: "#991B1B", borderRadius: "8px", fontSize: "0.85rem" }}>
          ⚠ {fallbackMessage} ({targetSelector})
        </div>
      );
    }

    return null; // Le contenu est injecté via DOM
  },
};


// ============================================================
//  MASK — Section avec masque SVG
// ============================================================

export const Mask = {
  fields: {
    backgroundColor: { type: "text", label: "Couleur de fond", defaultValue: "#F7F0E4" },
    maskType: {
      type: "select", label: "Type de masque",
      options: [
        { label: "Vague bas", value: "wave-bottom" },
        { label: "Vague haut", value: "wave-top" },
        { label: "Inclinaison bas", value: "slant-bottom" },
        { label: "Montagne", value: "mountain" },
      ],
    },
    heightDesktop: { type: "text", label: "Hauteur (desktop)", defaultValue: "600px" },
    heightMobile: { type: "text", label: "Hauteur (mobile)", defaultValue: "400px" },
    paddingDesktop: { type: "text", label: "Padding (desktop)", defaultValue: "80px 40px" },
    paddingMobile: { type: "text", label: "Padding (mobile)", defaultValue: "40px 16px" },
    overlayOpacity: { type: "text", label: "Opacité overlay", defaultValue: "0.3" },
    overlayColor: { type: "text", label: "Couleur overlay", defaultValue: "#000000" },
    contentPosition: {
      type: "select", label: "Position contenu",
      options: [
        { label: "Centre", value: "center" },
        { label: "Gauche", value: "flex-start" },
      ],
    },
  },
  defaultProps: {
    backgroundColor: "#F7F0E4",
    maskType: "wave-bottom",
    heightDesktop: "600px",
    heightMobile: "400px",
    paddingDesktop: "80px 40px",
    paddingMobile: "40px 16px",
    overlayOpacity: "0.3",
    overlayColor: "#000000",
    contentPosition: "center",
  },
  render: (props) => {
    const { puck, backgroundColor, maskType, heightDesktop, heightMobile,
            paddingDesktop, paddingMobile, overlayOpacity, overlayColor, contentPosition } = props;
    const id = useResponsiveId("mask");

    const masks = {
      "wave-bottom": `M0,160 C320,300 420,100 720,150 C1020,200 1280,60 1440,120 L1440,400 L0,400 Z`,
      "wave-top": `M0,0 L0,240 C320,100 420,300 720,250 C1020,200 1280,340 1440,280 L1440,0 Z`,
      "slant-bottom": `M0,0 L1440,0 L1440,320 L0,400 Z`,
      "mountain": `M0,400 L0,200 L360,80 L720,240 L1080,60 L1440,220 L1440,400 Z`,
    };

    const isBottom = maskType.endsWith("bottom") || maskType === "mountain";
    const isSlant = maskType === "slant-bottom";
    const path = masks[maskType] || masks["wave-bottom"];
    const svgViewBox = isSlant ? "0 0 1440 400" : "0 0 1440 400";

    const css = `
      #${id} {
        position: relative;
        background-color: ${backgroundColor};
        min-height: ${heightDesktop};
        padding: ${paddingDesktop};
        overflow: hidden;
        width: 100%;
        box-sizing: border-box;
      }
      #${id} .mask-svg {
        position: absolute;
        ${isBottom ? "bottom: -1px;" : "top: -1px;"}
        left: 0;
        width: 100%;
        height: auto;
        z-index: 2;
        display: block;
      }
      #${id} .mask-content {
        position: relative;
        z-index: 1;
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: ${contentPosition === "center" ? "center" : "flex-start"};
        text-align: ${contentPosition === "center" ? "center" : "left"};
        min-height: inherit;
      }
      #${id} .mask-overlay {
        position: absolute;
        inset: 0;
        background: ${overlayColor};
        opacity: ${overlayOpacity};
        z-index: 0;
      }
      @media (max-width: 768px) {
        #${id} { min-height: ${heightMobile}; padding: ${paddingMobile}; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <section id={id}>
          <div className="mask-overlay" />
          <div className="mask-content">
            {puckDropZone(puck)}
          </div>
          <svg
            className="mask-svg"
            viewBox={svgViewBox}
            xmlns="http://www.w3.org/2000/svg"
            preserveAspectRatio="none"
            style={isBottom ? undefined : { transform: "scaleY(-1)" }}
          >
            <path d={path} fill={backgroundColor} />
          </svg>
        </section>
      </>
    );
  },
};
'''


# ============================================================
#                    PATCH CONFIG
# ============================================================

MARKER = "/* === ADVANCED WIDGETS === */"


def write_widgets():
    os.makedirs(WIDGETS_DIR, exist_ok=True)
    path = os.path.join(WIDGETS_DIR, "advancedWidgets.jsx")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if "export const Masonry" in f.read():
                print(f"  [SKIP] advancedWidgets.jsx existe déjà")
                return False
        shutil.copy2(path, path + ".bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(ADVANCED_WIDGETS)
    print(f"  [OK] src/puck/widgets/advancedWidgets.jsx créé")
    return True


def update_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"  [ERREUR] config.jsx introuvable")
        return False

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER in content:
        print("  [SKIP] config.jsx déjà patché pour les widgets avancés")
        return False

    shutil.copy2(CONFIG_PATH, CONFIG_PATH + ".before-advanced.bak")
    print(f"  [BACKUP] config.jsx.before-advanced.bak")

    # 1. Imports
    imports = f'''
{MARKER}
import {{
  Masonry, Marquee, Cascade, Repeater,
  Modal, Drawer, Portal, Mask,
}} from "./widgets/advancedWidgets";
{MARKER}
'''
    content = re.sub(
        r'(import React from "react";\n)',
        r'\1' + imports,
        content,
        count=1,
    )

    # 2. Composants
    new_components = (
        "    // === Widgets avancés ===\n"
        "    Masonry, Marquee, Cascade, Repeater,\n"
        "    Modal, Drawer, Portal, Mask,\n"
    )

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
        print("  [OK] 8 composants ajoutés")

    # 3. Catégorie
    new_categories = (
        '    advancedLayout: { title: "Avancé", components: [\n'
        '      "Masonry", "Marquee", "Cascade", "Repeater",\n'
        '      "Modal", "Drawer", "Portal", "Mask",\n'
        '    ]},\n'
    )

    cat_pattern = re.compile(r'(categories:\s*\{)(.*?)(\n\s*\},)', re.DOTALL)
    cat_match = cat_pattern.search(content)
    if cat_match:
        content = (
            content[: cat_match.start(2)] + "\n" + new_categories
            + cat_match.group(2) + content[cat_match.start(3):]
        )
        print("  [OK] Catégorie 'Avancé' ajoutée")

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  AJOUT DES WIDGETS AVANCÉS")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable")
        return

    print("\n[1/2] Création des 8 widgets...")
    write_widgets()

    print("\n[2/2] Mise à jour de config.jsx...")
    update_config()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ — 8 widgets avancés ajoutés")
    print("=" * 60)
    print("\nWidgets :")
    print("  • Masonry   — Galerie en colonnes décalées")
    print("  • Marquee   — Défilement horizontal infini")
    print("  • Cascade   — Révélation au scroll")
    print("  • Repeater  — Contenu répété N fois")
    print("  • Modal     — Fenêtre modale")
    print("  • Drawer    — Tiroir latéral (4 positions)")
    print("  • Portal    — Injection dans un sélecteur distant")
    print("  • Mask      — Section avec masque SVG")
    print()
    print("Redémarrer :")
    print("  Remove-Item -Recurse -Force node_modules\\.vite")
    print("  npm run dev")


if __name__ == "__main__":
    main()