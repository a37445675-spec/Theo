/**
 * Layout Widgets — Flexbox, Grid et Box.
 * Structure avancée type Elementor.
 */
import React from "react";

// ============================================================
//  UTILITAIRES
// ============================================================

function parseResponsive(value, fallback) {
  if (!value) return fallback;
  return value;
}

function buildBoxStyles(props) {
  const {
    padding, margin, background, backgroundImage, borderRadius, boxShadow,
    borderWidth, borderColor, borderStyle, minHeight, width, maxWidth,
    opacity, zIndex, position, top, right, bottom, left,
  } = props;

  return {
    padding: padding || undefined,
    margin: margin || undefined,
    background: background || undefined,
    backgroundImage: backgroundImage ? `url(${backgroundImage})` : undefined,
    backgroundSize: "cover",
    backgroundPosition: "center",
    borderRadius: borderRadius || undefined,
    boxShadow: boxShadow || undefined,
    border: borderWidth ? `${borderWidth} ${borderStyle || "solid"} ${borderColor || "#e5e5e5"}` : undefined,
    minHeight: minHeight || undefined,
    width: width || undefined,
    maxWidth: maxWidth || undefined,
    opacity: opacity !== "" && opacity !== undefined ? Number(opacity) : undefined,
    zIndex: zIndex ? Number(zIndex) : undefined,
    position: position && position !== "static" ? position : undefined,
    top: top || undefined,
    right: right || undefined,
    bottom: bottom || undefined,
    left: left || undefined,
    boxSizing: "border-box",
    position: position && position !== "static" ? position : undefined,
  };
}

function buildFlexStyles({
  direction, wrap, justify, alignItems, alignContent,
  gap, rowGap, columnGap,
}) {
  return {
    display: "flex",
    flexDirection: direction || "row",
    flexWrap: wrap || "nowrap",
    justifyContent: justify || "flex-start",
    alignItems: alignItems || "stretch",
    alignContent: alignContent || "stretch",
    gap: gap || undefined,
    rowGap: rowGap || undefined,
    columnGap: columnGap || undefined,
  };
}

function buildGridStyles({
  gridTemplateColumns, gridTemplateRows, autoFlow,
  justifyItems, alignItems, justifyContent, alignContent,
  gap, rowGap, columnGap,
}) {
  return {
    display: "grid",
    gridTemplateColumns: gridTemplateColumns || "repeat(2, 1fr)",
    gridTemplateRows: gridTemplateRows || undefined,
    gridAutoFlow: autoFlow || "row",
    justifyItems: justifyItems || "stretch",
    alignItems: alignItems || "stretch",
    justifyContent: justifyContent || "stretch",
    alignContent: alignContent || "stretch",
    gap: gap || undefined,
    rowGap: rowGap || undefined,
    columnGap: columnGap || undefined,
  };
}


// ============================================================
//  BOX — Conteneur simple
// ============================================================

export const Box = {
  fields: {
    // Contenu
    tag: {
      type: "select", label: "Balise HTML",
      options: [
        { label: "div", value: "div" },
        { label: "section", value: "section" },
        { label: "article", value: "article" },
        { label: "header", value: "header" },
        { label: "footer", value: "footer" },
        { label: "main", value: "main" },
        { label: "aside", value: "aside" },
        { label: "nav", value: "nav" },
      ],
    },
    // Dimension
    width: { type: "text", label: "Largeur (ex: 100%, 800px)" },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "1200px" },
    minHeight: { type: "text", label: "Hauteur min" },
    // Espacement
    padding: { type: "text", label: "Padding (ex: 40px 20px)", defaultValue: "40px 20px" },
    margin: { type: "text", label: "Margin (ex: 0 auto)" },
    // Style
    background: { type: "text", label: "Couleur de fond" },
    backgroundImage: { type: "text", label: "Image de fond (URL)" },
    borderRadius: { type: "text", label: "Arrondi (ex: 16px)" },
    boxShadow: { type: "text", label: "Ombre portée" },
    // Bordure
    borderWidth: { type: "text", label: "Épaisseur bordure" },
    borderColor: { type: "text", label: "Couleur bordure", defaultValue: "#e5e5e5" },
    borderStyle: {
      type: "select", label: "Style bordure",
      options: [
        { label: "solid", value: "solid" },
        { label: "dashed", value: "dashed" },
        { label: "dotted", value: "dotted" },
      ],
    },
    // Avancé
    opacity: { type: "text", label: "Opacité (0-1)" },
    zIndex: { type: "text", label: "Z-Index" },
    position: {
      type: "select", label: "Position",
      options: [
        { label: "static", value: "static" },
        { label: "relative", value: "relative" },
        { label: "absolute", value: "absolute" },
        { label: "sticky", value: "sticky" },
        { label: "fixed", value: "fixed" },
      ],
    },
    top: { type: "text", label: "Top" },
    right: { type: "text", label: "Right" },
    bottom: { type: "text", label: "Bottom" },
    left: { type: "text", label: "Left" },
  },
  defaultProps: {
    tag: "section",
    maxWidth: "1200px",
    padding: "40px 20px",
    margin: "0 auto",
    borderStyle: "solid",
    borderColor: "#e5e5e5",
    position: "static",
  },
  render: (props) => {
    const { tag, puck } = props;
    const Tag = tag || "div";
    const style = buildBoxStyles(props);
    return (
      <Tag style={style}>
        {puck?.DropZone ? <puck.DropZone zone="content" /> : null}
      </Tag>
    );
  },
};


// ============================================================
//  FLEX CONTAINER — Disposition flexible
// ============================================================

export const FlexContainer = {
  fields: {
    tag: {
      type: "select", label: "Balise HTML",
      options: [
        { label: "div", value: "div" },
        { label: "section", value: "section" },
        { label: "header", value: "header" },
        { label: "nav", value: "nav" },
        { label: "main", value: "main" },
        { label: "footer", value: "footer" },
      ],
    },
    // Flex propriétés
    direction: {
      type: "select", label: "Direction",
      options: [
        { label: "Ligne →", value: "row" },
        { label: "Colonne ↓", value: "column" },
        { label: "Ligne inversée ←", value: "row-reverse" },
        { label: "Colonne inversée ↑", value: "column-reverse" },
      ],
    },
    wrap: {
      type: "select", label: "Retour à la ligne",
      options: [
        { label: "Empêcher", value: "nowrap" },
        { label: "Autoriser", value: "wrap" },
        { label: "Inverser", value: "wrap-reverse" },
      ],
    },
    justify: {
      type: "select", label: "Justification (horizontal)",
      options: [
        { label: "Début", value: "flex-start" },
        { label: "Centre", value: "center" },
        { label: "Fin", value: "flex-end" },
        { label: "Espace entre", value: "space-between" },
        { label: "Espace autour", value: "space-around" },
        { label: "Espace uniforme", value: "space-evenly" },
      ],
    },
    alignItems: {
      type: "select", label: "Alignement (vertical)",
      options: [
        { label: "Début", value: "flex-start" },
        { label: "Centre", value: "center" },
        { label: "Fin", value: "flex-end" },
        { label: "Étirer", value: "stretch" },
        { label: "Baseline", value: "baseline" },
      ],
    },
    alignContent: {
      type: "select", label: "Alignement multi-lignes",
      options: [
        { label: "Début", value: "flex-start" },
        { label: "Centre", value: "center" },
        { label: "Fin", value: "flex-end" },
        { label: "Espace entre", value: "space-between" },
        { label: "Étirer", value: "stretch" },
      ],
    },
    // Espacement
    gap: { type: "text", label: "Gap global (ex: 20px)" },
    rowGap: { type: "text", label: "Gap vertical" },
    columnGap: { type: "text", label: "Gap horizontal" },
    // Dimension / Style (hérité de Box)
    width: { type: "text", label: "Largeur" },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "1200px" },
    minHeight: { type: "text", label: "Hauteur min" },
    padding: { type: "text", label: "Padding", defaultValue: "40px 20px" },
    margin: { type: "text", label: "Margin", defaultValue: "0 auto" },
    background: { type: "text", label: "Fond" },
    borderRadius: { type: "text", label: "Arrondi" },
    boxShadow: { type: "text", label: "Ombre" },
  },
  defaultProps: {
    tag: "section",
    direction: "row",
    wrap: "wrap",
    justify: "flex-start",
    alignItems: "stretch",
    alignContent: "stretch",
    gap: "20px",
    maxWidth: "1200px",
    padding: "40px 20px",
    margin: "0 auto",
  },
  render: (props) => {
    const { tag, puck } = props;
    const Tag = tag || "div";
    const flexStyles = buildFlexStyles(props);
    const boxStyles = buildBoxStyles(props);
    return (
      <Tag style={{ ...boxStyles, ...flexStyles }}>
        {puck?.DropZone ? <puck.DropZone zone="content" /> : null}
      </Tag>
    );
  },
};


// ============================================================
//  GRID CONTAINER — Disposition en grille
// ============================================================

export const GridContainer = {
  fields: {
    tag: {
      type: "select", label: "Balise HTML",
      options: [
        { label: "div", value: "div" },
        { label: "section", value: "section" },
        { label: "main", value: "main" },
        { label: "article", value: "article" },
      ],
    },
    // Grid propriétés
    gridTemplateColumns: {
      type: "text", label: "Colonnes (CSS Grid)",
      defaultValue: "repeat(3, 1fr)",
    },
    gridTemplateRows: {
      type: "text", label: "Lignes (CSS Grid)",
    },
    autoFlow: {
      type: "select", label: "Auto-flow",
      options: [
        { label: "Par ligne", value: "row" },
        { label: "Par colonne", value: "column" },
        { label: "Dense ligne", value: "row dense" },
        { label: "Dense colonne", value: "column dense" },
      ],
    },
    justifyItems: {
      type: "select", label: "Justification cellules",
      options: [
        { label: "Début", value: "start" },
        { label: "Centre", value: "center" },
        { label: "Fin", value: "end" },
        { label: "Étirer", value: "stretch" },
      ],
    },
    alignItems: {
      type: "select", label: "Alignement cellules",
      options: [
        { label: "Début", value: "start" },
        { label: "Centre", value: "center" },
        { label: "Fin", value: "end" },
        { label: "Étirer", value: "stretch" },
      ],
    },
    justifyContent: {
      type: "select", label: "Justification grille",
      options: [
        { label: "Début", value: "start" },
        { label: "Centre", value: "center" },
        { label: "Fin", value: "end" },
        { label: "Espace entre", value: "space-between" },
        { label: "Espace autour", value: "space-around" },
        { label: "Étirer", value: "stretch" },
      ],
    },
    alignContent: {
      type: "select", label: "Alignement grille",
      options: [
        { label: "Début", value: "start" },
        { label: "Centre", value: "center" },
        { label: "Fin", value: "end" },
        { label: "Espace entre", value: "space-between" },
        { label: "Étirer", value: "stretch" },
      ],
    },
    // Espacement
    gap: { type: "text", label: "Gap global", defaultValue: "20px" },
    rowGap: { type: "text", label: "Gap vertical" },
    columnGap: { type: "text", label: "Gap horizontal" },
    // Box héritage
    width: { type: "text", label: "Largeur" },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "1200px" },
    minHeight: { type: "text", label: "Hauteur min" },
    padding: { type: "text", label: "Padding", defaultValue: "40px 20px" },
    margin: { type: "text", label: "Margin", defaultValue: "0 auto" },
    background: { type: "text", label: "Fond" },
    borderRadius: { type: "text", label: "Arrondi" },
  },
  defaultProps: {
    tag: "section",
    gridTemplateColumns: "repeat(3, 1fr)",
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
    const { tag, puck } = props;
    const Tag = tag || "div";
    const gridStyles = buildGridStyles(props);
    const boxStyles = buildBoxStyles(props);
    return (
      <Tag style={{ ...boxStyles, ...gridStyles }}>
        {puck?.DropZone ? <puck.DropZone zone="content" /> : null}
      </Tag>
    );
  },
};


// ============================================================
//  COLUMNS PRESET — 2, 3 ou 4 colonnes
// ============================================================

export const ColumnsPreset = {
  fields: {
    count: {
      type: "select", label: "Nombre de colonnes",
      options: [
        { label: "2 colonnes", value: "2" },
        { label: "3 colonnes", value: "3" },
        { label: "4 colonnes", value: "4" },
        { label: "1/3 + 2/3", value: "1-2" },
        { label: "2/3 + 1/3", value: "2-1" },
        { label: "1/4 + 1/2 + 1/4", value: "1-2-1" },
      ],
    },
    gap: { type: "text", label: "Espacement", defaultValue: "24px" },
    padding: { type: "text", label: "Padding", defaultValue: "40px 20px" },
    maxWidth: { type: "text", label: "Largeur max", defaultValue: "1200px" },
    background: { type: "text", label: "Fond" },
  },
  defaultProps: {
    count: "2",
    gap: "24px",
    padding: "40px 20px",
    maxWidth: "1200px",
  },
  render: ({ count, gap, padding, maxWidth, background, puck }) => {
    const layout = count || "2";
    const cols = layout.includes("-") ? layout.split("-") : [layout];
    const template = cols.length > 1
      ? cols.map((n) => `${n}fr`).join(" ")
      : `repeat(${cols[0]}, 1fr)`;

    return (
      <section style={{
        padding,
        maxWidth,
        margin: "0 auto",
        background: background || undefined,
      }}>
        <div style={{
          display: "grid",
          gridTemplateColumns: template,
          gap,
        }}>
          {cols.map((_, i) => (
            <div key={i}>
              {puck?.DropZone ? <puck.DropZone zone={`col-${i}`} /> : null}
            </div>
          ))}
        </div>
      </section>
    );
  },
};
