/**
 * Widgets de structure responsive — Desktop / Tablet / Mobile.
 * Chaque widget accepte des propriétés distinctes par breakpoint.
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

function pickResponsive(prop, prefix = "") {
  // Aide à extraire les champs responsive : padding, paddingTablet, paddingMobile
  return {
    desktop: prop,
    tablet: prop ? undefined : undefined,
  };
}


// ============================================================
//  CONTAINER — Wrapper max-width
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
    maxWidthDesktop: { type: "text", label: "Max-width (desktop)", defaultValue: "1200px" },
    maxWidthTablet: { type: "text", label: "Max-width (tablette)", defaultValue: "720px" },
    maxWidthMobile: { type: "text", label: "Max-width (mobile)", defaultValue: "100%" },

    paddingDesktop: { type: "text", label: "Padding (desktop)", defaultValue: "60px 24px" },
    paddingTablet: { type: "text", label: "Padding (tablette)", defaultValue: "40px 16px" },
    paddingMobile: { type: "text", label: "Padding (mobile)", defaultValue: "24px 12px" },

    margin: { type: "text", label: "Margin (auto pour centrer)", defaultValue: "0 auto" },
    background: { type: "text", label: "Fond" },
    borderRadius: { type: "text", label: "Arrondi" },
  },
  defaultProps: {
    tag: "section",
    maxWidthDesktop: "1200px",
    maxWidthTablet: "720px",
    maxWidthMobile: "100%",
    paddingDesktop: "60px 24px",
    paddingTablet: "40px 16px",
    paddingMobile: "24px 12px",
    margin: "0 auto",
  },
  render: (props) => {
    const { tag, puck, maxWidthDesktop, maxWidthTablet, maxWidthMobile,
            paddingDesktop, paddingTablet, paddingMobile, margin, background, borderRadius } = props;
    const Tag = tag || "div";
    const id = useResponsiveId("container");

    return (
      <>
        <ResponsiveStyle
          id={id}
          styles={{
            desktop: {
              maxWidth: maxWidthDesktop,
              padding: paddingDesktop,
              margin,
              background,
              borderRadius,
              boxSizing: "border-box",
              width: "100%",
            },
            tablet: { maxWidth: maxWidthTablet, padding: paddingTablet },
            mobile: { maxWidth: maxWidthMobile, padding: paddingMobile },
          }}
        />
        <Tag id={id} style={{ margin: "0 auto" }}>
          {puckDropZone(puck)}
        </Tag>
      </>
    );
  },
};


// ============================================================
//  STACK — Empilement vertical
// ============================================================

export const Stack = {
  fields: {
    tag: {
      type: "select", label: "Balise",
      options: [
        { label: "div", value: "div" },
        { label: "section", value: "section" },
        { label: "article", value: "article" },
        { label: "nav", value: "nav" },
      ],
    },
    gapDesktop: { type: "text", label: "Gap (desktop)", defaultValue: "24px" },
    gapTablet: { type: "text", label: "Gap (tablette)", defaultValue: "16px" },
    gapMobile: { type: "text", label: "Gap (mobile)", defaultValue: "12px" },

    alignItemsDesktop: {
      type: "select", label: "Alignement (desktop)",
      options: [
        { label: "Début", value: "flex-start" },
        { label: "Centre", value: "center" },
        { label: "Fin", value: "flex-end" },
        { label: "Étirer", value: "stretch" },
      ],
    },
    alignItemsMobile: {
      type: "select", label: "Alignement (mobile)",
      options: [
        { label: "Début", value: "flex-start" },
        { label: "Centre", value: "center" },
        { label: "Fin", value: "flex-end" },
        { label: "Étirer", value: "stretch" },
      ],
    },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "1200px" },
    padding: { type: "text", label: "Padding", defaultValue: "24px" },
  },
  defaultProps: {
    tag: "div",
    gapDesktop: "24px",
    gapTablet: "16px",
    gapMobile: "12px",
    alignItemsDesktop: "stretch",
    alignItemsMobile: "stretch",
    maxWidth: "1200px",
    padding: "24px",
  },
  render: (props) => {
    const { tag, puck, gapDesktop, gapTablet, gapMobile,
            alignItemsDesktop, alignItemsMobile, maxWidth, padding } = props;
    const Tag = tag || "div";
    const id = useResponsiveId("stack");

    return (
      <>
        <ResponsiveStyle
          id={id}
          styles={{
            desktop: {
              display: "flex", flexDirection: "column",
              gap: gapDesktop, alignItems: alignItemsDesktop,
              maxWidth, margin: "0 auto", padding, boxSizing: "border-box", width: "100%",
            },
            tablet: { gap: gapTablet },
            mobile: { gap: gapMobile, alignItems: alignItemsMobile },
          }}
        />
        <Tag id={id}>
          {puckDropZone(puck)}
        </Tag>
      </>
    );
  },
};


// ============================================================
//  CLUSTER — Groupe horizontal wrap
// ============================================================

export const Cluster = {
  fields: {
    gapDesktop: { type: "text", label: "Gap (desktop)", defaultValue: "16px" },
    gapMobile: { type: "text", label: "Gap (mobile)", defaultValue: "8px" },
    justifyDesktop: {
      type: "select", label: "Justification (desktop)",
      options: [
        { label: "Début", value: "flex-start" },
        { label: "Centre", value: "center" },
        { label: "Fin", value: "flex-end" },
        { label: "Espace entre", value: "space-between" },
        { label: "Espace autour", value: "space-around" },
      ],
    },
    justifyMobile: {
      type: "select", label: "Justification (mobile)",
      options: [
        { label: "Début", value: "flex-start" },
        { label: "Centre", value: "center" },
        { label: "Espace entre", value: "space-between" },
      ],
    },
    alignItems: {
      type: "select", label: "Alignement",
      options: [
        { label: "Début", value: "flex-start" },
        { label: "Centre", value: "center" },
        { label: "Fin", value: "flex-end" },
        { label: "Étirer", value: "stretch" },
      ],
    },
    wrap: {
      type: "select", label: "Retour ligne",
      options: [
        { label: "Autoriser", value: "wrap" },
        { label: "Empêcher", value: "nowrap" },
      ],
    },
  },
  defaultProps: {
    gapDesktop: "16px",
    gapMobile: "8px",
    justifyDesktop: "flex-start",
    justifyMobile: "flex-start",
    alignItems: "center",
    wrap: "wrap",
  },
  render: (props) => {
    const { puck, gapDesktop, gapMobile, justifyDesktop, justifyMobile, alignItems, wrap } = props;
    const id = useResponsiveId("cluster");

    return (
      <>
        <ResponsiveStyle
          id={id}
          styles={{
            desktop: {
              display: "flex", flexWrap: wrap, gap: gapDesktop,
              justifyContent: justifyDesktop, alignItems,
            },
            mobile: { gap: gapMobile, justifyContent: justifyMobile },
          }}
        />
        <div id={id}>
          {puckDropZone(puck)}
        </div>
      </>
    );
  },
};


// ============================================================
//  SIDEBAR — 2 colonnes avec aside
// ============================================================

export const Sidebar = {
  fields: {
    sidebarWidthDesktop: { type: "text", label: "Largeur sidebar (desktop)", defaultValue: "300px" },
    sidebarWidthTablet: { type: "text", label: "Largeur sidebar (tablette)", defaultValue: "240px" },
    sidebarPosition: {
      type: "select", label: "Position sidebar",
      options: [
        { label: "Gauche", value: "left" },
        { label: "Droite", value: "right" },
      ],
    },
    gapDesktop: { type: "text", label: "Gap (desktop)", defaultValue: "32px" },
    gapMobile: { type: "text", label: "Gap (mobile)", defaultValue: "16px" },
    stackOnMobile: {
      type: "radio", label: "Empiler sur mobile",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "1200px" },
    padding: { type: "text", label: "Padding", defaultValue: "24px" },
  },
  defaultProps: {
    sidebarWidthDesktop: "300px",
    sidebarWidthTablet: "240px",
    sidebarPosition: "right",
    gapDesktop: "32px",
    gapMobile: "16px",
    stackOnMobile: "true",
    maxWidth: "1200px",
    padding: "24px",
  },
  render: (props) => {
    const { puck, sidebarWidthDesktop, sidebarWidthTablet, sidebarPosition,
            gapDesktop, gapMobile, stackOnMobile, maxWidth, padding } = props;
    const id = useResponsiveId("sidebar");
    const isLeft = sidebarPosition === "left";
    const stack = stackOnMobile === "true";

    return (
      <>
        <ResponsiveStyle
          id={id}
          styles={{
            desktop: {
              display: "grid",
              gridTemplateColumns: isLeft
                ? `${sidebarWidthDesktop} 1fr`
                : `1fr ${sidebarWidthDesktop}`,
              gap: gapDesktop, maxWidth, margin: "0 auto",
              padding, boxSizing: "border-box", width: "100%",
            },
            tablet: {
              gridTemplateColumns: isLeft
                ? `${sidebarWidthTablet} 1fr`
                : `1fr ${sidebarWidthTablet}`,
            },
            mobile: stack
              ? { gridTemplateColumns: "1fr", gap: gapMobile }
              : { gap: gapMobile },
          }}
        />
        <div id={id}>
          {isLeft ? (
            <>
              <aside>{puckDropZone(puck, "sidebar")}</aside>
              <main>{puckDropZone(puck, "main")}</main>
            </>
          ) : (
            <>
              <main>{puckDropZone(puck, "main")}</main>
              <aside>{puckDropZone(puck, "sidebar")}</aside>
            </>
          )}
        </div>
      </>
    );
  },
};


// ============================================================
//  SPLIT — 2 colonnes 50/50
// ============================================================

export const Split = {
  fields: {
    ratioDesktop: {
      type: "select", label: "Ratio (desktop)",
      options: [
        { label: "50/50", value: "1fr 1fr" },
        { label: "60/40", value: "3fr 2fr" },
        { label: "40/60", value: "2fr 3fr" },
        { label: "70/30", value: "7fr 3fr" },
        { label: "30/70", value: "3fr 7fr" },
      ],
    },
    gapDesktop: { type: "text", label: "Gap (desktop)", defaultValue: "32px" },
    gapMobile: { type: "text", label: "Gap (mobile)", defaultValue: "16px" },
    stackOnMobile: {
      type: "radio", label: "Empiler sur mobile",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "1200px" },
    padding: { type: "text", label: "Padding", defaultValue: "40px 24px" },
  },
  defaultProps: {
    ratioDesktop: "1fr 1fr",
    gapDesktop: "32px",
    gapMobile: "16px",
    stackOnMobile: "true",
    maxWidth: "1200px",
    padding: "40px 24px",
  },
  render: (props) => {
    const { puck, ratioDesktop, gapDesktop, gapMobile, stackOnMobile, maxWidth, padding } = props;
    const id = useResponsiveId("split");
    const stack = stackOnMobile === "true";

    return (
      <>
        <ResponsiveStyle
          id={id}
          styles={{
            desktop: {
              display: "grid", gridTemplateColumns: ratioDesktop,
              gap: gapDesktop, maxWidth, margin: "0 auto",
              padding, boxSizing: "border-box", width: "100%",
            },
            tablet: { gridTemplateColumns: "1fr 1fr" },
            mobile: stack
              ? { gridTemplateColumns: "1fr", gap: gapMobile }
              : { gap: gapMobile },
          }}
        />
        <div id={id}>
          <div>{puckDropZone(puck, "left")}</div>
          <div>{puckDropZone(puck, "right")}</div>
        </div>
      </>
    );
  },
};


// ============================================================
//  SECTION OVERLAY — Section avec image + overlay
// ============================================================

export const SectionOverlay = {
  fields: {
    backgroundImage: { type: "text", label: "Image de fond (URL)" },
    overlayColor: { type: "text", label: "Couleur overlay", defaultValue: "#000000" },
    overlayOpacityDesktop: { type: "text", label: "Opacité overlay (desktop)", defaultValue: "0.4" },
    overlayOpacityMobile: { type: "text", label: "Opacité overlay (mobile)", defaultValue: "0.6" },
    heightDesktop: { type: "text", label: "Hauteur (desktop)", defaultValue: "500px" },
    heightTablet: { type: "text", label: "Hauteur (tablette)", defaultValue: "400px" },
    heightMobile: { type: "text", label: "Hauteur (mobile)", defaultValue: "auto" },
    paddingDesktop: { type: "text", label: "Padding (desktop)", defaultValue: "80px 24px" },
    paddingMobile: { type: "text", label: "Padding (mobile)", defaultValue: "40px 16px" },
    contentPosition: {
      type: "select", label: "Position contenu",
      options: [
        { label: "Centre", value: "center" },
        { label: "Gauche", value: "flex-start" },
        { label: "Droite", value: "flex-end" },
      ],
    },
    contentVertical: {
      type: "select", label: "Alignement vertical",
      options: [
        { label: "Centre", value: "center" },
        { label: "Haut", value: "flex-start" },
        { label: "Bas", value: "flex-end" },
      ],
    },
    textColor: { type: "text", label: "Couleur du texte", defaultValue: "#FFFFFF" },
  },
  defaultProps: {
    backgroundImage: "/fallbacks/hero-fallback.jpg",
    overlayColor: "#000000",
    overlayOpacityDesktop: "0.4",
    overlayOpacityMobile: "0.6",
    heightDesktop: "500px",
    heightTablet: "400px",
    heightMobile: "auto",
    paddingDesktop: "80px 24px",
    paddingMobile: "40px 16px",
    contentPosition: "center",
    contentVertical: "center",
    textColor: "#FFFFFF",
  },
  render: (props) => {
    const { puck, backgroundImage, overlayColor, overlayOpacityDesktop,
            overlayOpacityMobile, heightDesktop, heightTablet, heightMobile,
            paddingDesktop, paddingMobile, contentPosition, contentVertical, textColor } = props;
    const id = useResponsiveId("overlay");

    const overlayCss = `
      #${id} { position: relative; min-height: ${heightDesktop}; padding: ${paddingDesktop}; }
      #${id}::before { content: ""; position: absolute; inset: 0; background-color: ${overlayColor}; opacity: ${overlayOpacityDesktop}; z-index: 1; }
      #${id} .overlay-bg { position: absolute; inset: 0; background-image: url('${backgroundImage || ""}'); background-size: cover; background-position: center; z-index: 0; }
      #${id} .overlay-content { position: relative; z-index: 2; display: flex; flex-direction: column; justify-content: ${contentVertical}; align-items: ${contentPosition === "center" ? "center" : "flex-start"}; text-align: ${contentPosition === "center" ? "center" : "left"}; min-height: inherit; color: ${textColor}; }
      @media (max-width: 1024px) { #${id} { min-height: ${heightTablet}; } }
      @media (max-width: 768px) { #${id} { min-height: ${heightMobile}; padding: ${paddingMobile}; } #${id}::before { opacity: ${overlayOpacityMobile}; } }
    `;

    return (
      <section id={id} style={{ position: "relative", overflow: "hidden", width: "100%" }}>
        <style dangerouslySetInnerHTML={{ __html: overlayCss }} />
        <div className="overlay-bg" />
        <div className="overlay-content">
          {puckDropZone(puck)}
        </div>
      </section>
    );
  },
};


// ============================================================
//  CARD — Carte avec header/body/footer
// ============================================================

export const Card = {
  fields: {
    background: { type: "text", label: "Fond", defaultValue: "#FFFFFF" },
    borderRadius: { type: "text", label: "Arrondi", defaultValue: "16px" },
    boxShadow: { type: "text", label: "Ombre", defaultValue: "0 4px 12px rgba(0,0,0,0.08)" },
    paddingDesktop: { type: "text", label: "Padding (desktop)", defaultValue: "24px" },
    paddingMobile: { type: "text", label: "Padding (mobile)", defaultValue: "16px" },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "100%" },
    minHeight: { type: "text", label: "Hauteur min" },
    borderWidth: { type: "text", label: "Épaisseur bordure" },
    borderColor: { type: "text", label: "Couleur bordure", defaultValue: "#e5e5e5" },
    hoverLift: {
      type: "radio", label: "Effet au survol",
      options: [
        { label: "Aucun", value: "false" },
        { label: "Légère élévation", value: "true" },
      ],
    },
  },
  defaultProps: {
    background: "#FFFFFF",
    borderRadius: "16px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
    paddingDesktop: "24px",
    paddingMobile: "16px",
    maxWidth: "100%",
    borderColor: "#e5e5e5",
    hoverLift: "false",
  },
  render: (props) => {
    const { puck, background, borderRadius, boxShadow, paddingDesktop, paddingMobile,
            maxWidth, minHeight, borderWidth, borderColor, hoverLift } = props;
    const id = useResponsiveId("card");

    const hoverCss = hoverLift === "true"
      ? `#${id} { transition: transform 0.2s, box-shadow 0.2s; } #${id}:hover { transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0,0,0,0.12); }`
      : "";

    const cardCss = `
      #${id} {
        background: ${background};
        border-radius: ${borderRadius};
        box-shadow: ${boxShadow};
        padding: ${paddingDesktop};
        max-width: ${maxWidth};
        min-height: ${minHeight || "auto"};
        border: ${borderWidth ? `${borderWidth} solid ${borderColor}` : "none"};
        box-sizing: border-box;
        width: 100%;
      }
      @media (max-width: 768px) { #${id} { padding: ${paddingMobile}; } }
      ${hoverCss}
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: cardCss }} />
        <div id={id}>
          {puckDropZone(puck)}
        </div>
      </>
    );
  },
};


// ============================================================
//  STICKY CONTAINER
// ============================================================

export const StickyContainer = {
  fields: {
    top: { type: "text", label: "Position (top)", defaultValue: "20px" },
    zIndex: { type: "text", label: "Z-index", defaultValue: "10" },
    background: { type: "text", label: "Fond", defaultValue: "transparent" },
    padding: { type: "text", label: "Padding", defaultValue: "0" },
    disableOnMobile: {
      type: "radio", label: "Désactiver sur mobile",
      options: [
        { label: "Oui", value: "true" },
        { label: "Non", value: "false" },
      ],
    },
  },
  defaultProps: {
    top: "20px",
    zIndex: "10",
    background: "transparent",
    padding: "0",
    disableOnMobile: "true",
  },
  render: (props) => {
    const { puck, top, zIndex, background, padding, disableOnMobile } = props;
    const id = useResponsiveId("sticky");
    const disable = disableOnMobile === "true";

    const stickyCss = `
      #${id} { position: sticky; top: ${top}; z-index: ${zIndex}; background: ${background}; padding: ${padding}; }
      ${disable ? `@media (max-width: 768px) { #${id} { position: static; } }` : ""}
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: stickyCss }} />
        <div id={id}>
          {puckDropZone(puck)}
        </div>
      </>
    );
  },
};


// ============================================================
//  TABS VERTICAL — Onglets verticaux
// ============================================================

export const TabsVertical = {
  fields: {
    tabLabels: {
      type: "textarea", label: "Onglets (1 par ligne)",
      defaultValue: "Présentation\nCaractéristiques\nAvis",
    },
    tabsWidthDesktop: { type: "text", label: "Largeur onglets (desktop)", defaultValue: "200px" },
    gap: { type: "text", label: "Gap", defaultValue: "24px" },
    activeColor: { type: "text", label: "Couleur active", defaultValue: "#C1652F" },
    inactiveColor: { type: "text", label: "Couleur inactive", defaultValue: "#6B6259" },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "1000px" },
    mobileLayout: {
      type: "select", label: "Sur mobile",
      options: [
        { label: "Onglets horizontaux", value: "horizontal" },
        { label: "Onglets empilés", value: "stacked" },
      ],
    },
  },
  defaultProps: {
    tabLabels: "Présentation\nCaractéristiques\nAvis",
    tabsWidthDesktop: "200px",
    gap: "24px",
    activeColor: "#C1652F",
    inactiveColor: "#6B6259",
    maxWidth: "1000px",
    mobileLayout: "horizontal",
  },
  render: (props) => {
    const { puck, tabLabels, tabsWidthDesktop, gap, activeColor, inactiveColor, maxWidth, mobileLayout } = props;
    const [active, setActive] = React.useState(0);
    const tabs = String(tabLabels || "").split("\n").filter(Boolean);
    const id = useResponsiveId("tabsvert");

    const css = `
      #${id} { display: grid; grid-template-columns: ${tabsWidthDesktop} 1fr; gap: ${gap}; max-width: ${maxWidth}; margin: 0 auto; }
      #${id} .tabs-list { display: flex; flex-direction: column; gap: 8px; }
      #${id} .tab-btn { padding: 12px 16px; text-align: left; background: transparent; border: none; border-left: 3px solid transparent; cursor: pointer; font-weight: 500; transition: all 0.2s; }
      #${id} .tab-btn.active { border-left-color: ${activeColor}; color: ${activeColor}; font-weight: 700; }
      #${id} .tab-btn:not(.active) { color: ${inactiveColor}; }
      @media (max-width: 768px) {
        #${id} { grid-template-columns: 1fr; }
        #${id} .tabs-list { flex-direction: ${mobileLayout === "horizontal" ? "row" : "column"}; overflow-x: ${mobileLayout === "horizontal" ? "auto" : "visible"}; }
      }
    `;

    return (
      <>
        <style dangerouslySetInnerHTML={{ __html: css }} />
        <div id={id}>
          <div className="tabs-list">
            {tabs.map((label, i) => (
              <button
                key={i}
                className={`tab-btn ${active === i ? "active" : ""}`}
                onClick={() => setActive(i)}
                style={{ color: active === i ? activeColor : inactiveColor }}
              >
                {label}
              </button>
            ))}
          </div>
          <div>
            {puckDropZone(puck, `tab-${active}`)}
          </div>
        </div>
      </>
    );
  },
};


// ============================================================
//  ACCORDION CONTAINER — Sections repliables
// ============================================================

export const AccordionContainer = {
  fields: {
    sectionTitles: {
      type: "textarea", label: "Titres des sections (1 par ligne)",
      defaultValue: "Section 1\nSection 2\nSection 3",
    },
    openByDefault: {
      type: "select", label: "Ouvert par défaut",
      options: [
        { label: "Toutes fermées", value: "none" },
        { label: "Première ouverte", value: "first" },
        { label: "Toutes ouvertes", value: "all" },
      ],
    },
    borderColor: { type: "text", label: "Couleur bordure", defaultValue: "#e5e5e5" },
    accentColor: { type: "text", label: "Couleur accent", defaultValue: "#C1652F" },
    padding: { type: "text", label: "Padding section", defaultValue: "16px 20px" },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "100%" },
  },
  defaultProps: {
    sectionTitles: "Section 1\nSection 2\nSection 3",
    openByDefault: "first",
    borderColor: "#e5e5e5",
    accentColor: "#C1652F",
    padding: "16px 20px",
    maxWidth: "100%",
  },
  render: (props) => {
    const { puck, sectionTitles, openByDefault, borderColor, accentColor, padding, maxWidth } = props;
    const sections = String(sectionTitles || "").split("\n").filter(Boolean);

    const [openSet, setOpenSet] = React.useState(() => {
      const s = new Set();
      if (openByDefault === "all") {
        sections.forEach((_, i) => s.add(i));
      } else if (openByDefault === "first") {
        s.add(0);
      }
      return s;
    });

    const toggle = (i) => {
      const s = new Set(openSet);
      s.has(i) ? s.delete(i) : s.add(i);
      setOpenSet(s);
    };

    return (
      <div style={{ maxWidth, margin: "0 auto", width: "100%" }}>
        {sections.map((title, i) => {
          const isOpen = openSet.has(i);
          return (
            <div key={i} style={{ borderBottom: `1px solid ${borderColor}` }}>
              <button
                onClick={() => toggle(i)}
                style={{
                  width: "100%", padding, background: "transparent",
                  border: "none", cursor: "pointer", textAlign: "left",
                  fontWeight: 600, fontSize: "1rem",
                  color: isOpen ? accentColor : "inherit",
                  display: "flex", justifyContent: "space-between",
                }}
              >
                {title}
                <span>{isOpen ? "−" : "+"}</span>
              </button>
              {isOpen && (
                <div style={{ padding: `0 ${padding.split(" ")[1] || "20px"} 16px` }}>
                  {puckDropZone(puck, `section-${i}`)}
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  },
};
