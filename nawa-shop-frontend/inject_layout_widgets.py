"""
Ajoute les widgets de layout avancés : Box, FlexContainer, GridContainer.

Usage : python inject_layout_widgets.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
WIDGETS_DIR = os.path.join(SRC_DIR, "puck", "widgets")
CONFIG_PATH = os.path.join(SRC_DIR, "puck", "config.jsx")


# ============================================================
#              LAYOUT WIDGETS
# ============================================================

LAYOUT_WIDGETS = '''/**
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
'''


# ============================================================
#                    PATCH DU CONFIG
# ============================================================

MARKER = "/* === LAYOUT WIDGETS === */"


def write_layout_widgets():
    os.makedirs(WIDGETS_DIR, exist_ok=True)
    path = os.path.join(WIDGETS_DIR, "layoutWidgets.jsx")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if "export const FlexContainer" in f.read():
                print(f"  [SKIP] layoutWidgets.jsx existe déjà")
                return False
        shutil.copy2(path, path + ".bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(LAYOUT_WIDGETS)
    print(f"  [OK] src/puck/widgets/layoutWidgets.jsx créé")
    return True


def update_config():
    if not os.path.exists(CONFIG_PATH):
        print(f"  [ERREUR] config.jsx introuvable")
        return False

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if MARKER in content:
        print("  [SKIP] config.jsx déjà patché pour les layouts")
        return False

    shutil.copy2(CONFIG_PATH, CONFIG_PATH + ".before-layout.bak")
    print(f"  [BACKUP] config.jsx.before-layout.bak")

    # 1. Ajouter les imports après React
    imports = f'''
{MARKER}
import {{
  Box, FlexContainer, GridContainer, ColumnsPreset,
}} from "./widgets/layoutWidgets";
{MARKER}
'''
    content = re.sub(
        r'(import React from "react";\n)',
        r'\1' + imports,
        content,
        count=1,
    )

    # 2. Ajouter les composants dans components
    new_components = (
        "    // === Layout avancé ===\n"
        "    Box, FlexContainer, GridContainer, ColumnsPreset,\n"
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
        print("  [OK] Composants ajoutés dans puckConfig.components")

    # 3. Ajouter la catégorie "layout"
    new_categories = (
        '    layout: { title: "Layout", components: [\n'
        '      "Box", "FlexContainer", "GridContainer", "ColumnsPreset",\n'
        '    ]},\n'
    )

    cat_pattern = re.compile(r'(categories:\s*\{)(.*?)(\n\s*\},)', re.DOTALL)
    cat_match = cat_pattern.search(content)
    if cat_match:
        content = (
            content[: cat_match.start(2)] + "\n" + new_categories
            + cat_match.group(2) + content[cat_match.start(3):]
        )
        print("  [OK] Catégorie 'Layout' ajoutée")

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  AJOUT DES LAYOUTS AVANCÉS")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable")
        return

    print("\n[1/2] Création de layoutWidgets.jsx...")
    write_layout_widgets()

    print("\n[2/2] Mise à jour de config.jsx...")
    update_config()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print("\n4 widgets ajoutés dans la catégorie 'Layout' :")
    print("  • Box             — Conteneur simple (padding, bg, bordure)")
    print("  • FlexContainer   — Disposition flexible 1 axe")
    print("  • GridContainer   — Disposition en grille N×M")
    print("  • ColumnsPreset   — Raccourci 2/3/4 colonnes")
    print()
    print("Étapes suivantes :")
    print("  1. Remove-Item -Recurse -Force node_modules\\.vite")
    print("  2. npm run dev")


if __name__ == "__main__":
    main()