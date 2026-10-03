/**
 * Hook responsive — génère du CSS scopé avec media queries.
 *
 * Permet à chaque instance de widget de définir des styles différents
 * pour Desktop, Tablette et Mobile sans collision entre instances.
 */
import { useMemo } from "react";

/**
 * Breakpoints standards (alignés sur Tailwind)
 *   - Mobile  : < 768px
 *   - Tablet  : 768px → 1024px
 *   - Desktop : >= 1024px
 */
export const BREAKPOINTS = {
  mobile: 768,
  tablet: 1024,
};

let instanceCounter = 0;

/**
 * Génère un ID unique et stable par instance de widget.
 */
export function useResponsiveId(prefix = "na") {
  return useMemo(() => {
    instanceCounter += 1;
    return `${prefix}-${Date.now().toString(36)}-${instanceCounter}`;
  }, [prefix]);
}

/**
 * Construit un bloc CSS scopé avec ses media queries.
 *
 * Usage :
 *   const css = buildResponsiveCss(id, {
 *     desktop: { padding: "40px" },
 *     tablet:  { padding: "24px" },
 *     mobile:  { padding: "16px" },
 *   });
 */
export function buildResponsiveCss(id, styles) {
  const toCss = (obj) =>
    Object.entries(obj || {})
      .filter(([, v]) => v !== undefined && v !== null && v !== "")
      .map(([k, v]) => `${camelToKebab(k)}: ${v};`)
      .join(" ");

  const desktopCss = toCss(styles.desktop);
  const tabletCss = toCss(styles.tablet);
  const mobileCss = toCss(styles.mobile);

  let css = "";
  if (desktopCss) {
    css += `#${id} { ${desktopCss} }\n`;
  }
  if (tabletCss) {
    css += `@media (max-width: ${BREAKPOINTS.tablet}px) { #${id} { ${tabletCss} } }\n`;
  }
  if (mobileCss) {
    css += `@media (max-width: ${BREAKPOINTS.mobile}px) { #${id} { ${mobileCss} } }\n`;
  }
  return css;
}

function camelToKebab(str) {
  return str.replace(/[A-Z]/g, (m) => "-" + m.toLowerCase());
}

/**
 * Composant qui injecte le CSS scopé dans le DOM.
 */
export function ResponsiveStyle({ id, styles }) {
  const css = buildResponsiveCss(id, styles);
  if (!css) return null;
  return <style dangerouslySetInnerHTML={{ __html: css }} />;
}
