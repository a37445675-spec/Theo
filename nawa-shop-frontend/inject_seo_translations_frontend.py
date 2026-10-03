"""
Injection automatique des modules SEO et Traductions - Frontend React.

Prérequis : installer react-helmet-async
  npm install react-helmet-async

Usage : python inject_seo_translations_frontend.py
"""
import os
import re
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")


# ============================================================
#                    SEO - FICHIERS
# ============================================================

SEO_HEAD_JSX = '''import { Helmet } from "react-helmet-async";

/**
 * Composant SEO : injecte toutes les balises méta dans le <head>.
 *
 * Usage :
 *   <SeoHead
 *     title="Boutique Cosmétiques"
 *     description="Découvrez notre sélection..."
 *     image="/media/seo/og/cosmetiques.jpg"
 *     url="/boutique/cosmetiques"
 *     type="website"
 *   />
 *
 * Ou depuis une réponse API :
 *   <SeoHead {...mapSeoFromApi(seoData)} />
 */
export default function SeoHead({
  title,
  description,
  keywords,
  image,
  url,
  type = "website",
  robots = "index,follow",
  canonical,
  structuredData,
  siteName = "NAWA",
}) {
  const siteUrl = typeof window !== "undefined" ? window.location.origin : "";
  const fullUrl = url ? `${siteUrl}${url}` : (typeof window !== "undefined" ? window.location.href : "");
  const fullImage = image
    ? (image.startsWith("http") ? image : `${siteUrl}${image}`)
    : null;

  const finalTitle = title ? `${title} — ${siteName}` : siteName;
  const finalDesc = description || "La beauté d'Afrique, sublimée. Cosmétiques naturels, mode, chaussures et électroménager.";

  return (
    <Helmet>
      {/* Titre et description */}
      <title>{finalTitle}</title>
      <meta name="description" content={finalDesc} />
      {keywords && <meta name="keywords" content={keywords} />}

      {/* Robots */}
      <meta name="robots" content={robots} />

      {/* Canonique */}
      {canonical && <link rel="canonical" href={canonical} />}
      {!canonical && fullUrl && <link rel="canonical" href={fullUrl} />}

      {/* Open Graph (Facebook, LinkedIn, WhatsApp) */}
      <meta property="og:type" content={type} />
      <meta property="og:title" content={finalTitle} />
      <meta property="og:description" content={finalDesc} />
      {fullUrl && <meta property="og:url" content={fullUrl} />}
      {fullImage && <meta property="og:image" content={fullImage} />}
      <meta property="og:site_name" content={siteName} />
      <meta property="og:locale" content="fr_FR" />

      {/* Twitter / X */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={finalTitle} />
      <meta name="twitter:description" content={finalDesc} />
      {fullImage && <meta name="twitter:image" content={fullImage} />}

      {/* JSON-LD (données structurées) */}
      {structuredData && Object.keys(structuredData).length > 0 && (
        <script type="application/ld+json">
          {JSON.stringify(structuredData)}
        </script>
      )}
    </Helmet>
  );
}

/**
 * Utilitaire : convertit une réponse API SEO en props pour <SeoHead />.
 */
export function mapSeoFromApi(seo) {
  if (!seo) return {};
  return {
    title: seo.meta_title || seo.og_title || undefined,
    description: seo.meta_description || seo.og_description || undefined,
    keywords: seo.meta_keywords || undefined,
    image: seo.og_image_url || undefined,
    type: seo.og_type || "website",
    robots: seo.robots || "index,follow",
    canonical: seo.canonical_url || undefined,
    structuredData: seo.structured_data || undefined,
  };
}
'''


# ============================================================
#                 TRADUCTIONS - FICHIERS
# ============================================================

TRANSLATION_CONTEXT_JSX = '''import { createContext, useContext, useEffect, useState, useCallback } from "react";

const TranslationContext = createContext(null);

const DEFAULT_LOCALE = "fr";
const SUPPORTED_LOCALES = ["fr", "en"];

export function TranslationProvider({ children }) {
  const [locale, setLocaleState] = useState(() => {
    return localStorage.getItem("nawa_locale") || DEFAULT_LOCALE;
  });
  const [translations, setTranslations] = useState({});
  const [loading, setLoading] = useState(true);

  // Charge les traductions pour la langue courante
  useEffect(() => {
    setLoading(true);
    fetch(`/api/v1/translations/?lang=${locale}`)
      .then((res) => (res.ok ? res.json() : {}))
      .then((data) => setTranslations(data))
      .catch((err) => console.warn("Erreur chargement traductions:", err))
      .finally(() => setLoading(false));
  }, [locale]);

  // Change la langue (persistée dans localStorage)
  const setLocale = useCallback((newLocale) => {
    if (!SUPPORTED_LOCALES.includes(newLocale)) return;
    localStorage.setItem("nawa_locale", newLocale);
    document.documentElement.lang = newLocale;
    setLocaleState(newLocale);
  }, []);

  /**
   * Fonction de traduction : t("cart.empty.title", "Fallback")
   */
  const t = useCallback(
    (key, fallback) => translations[key] || fallback || key,
    [translations]
  );

  return (
    <TranslationContext.Provider
      value={{ t, locale, setLocale, loading, supportedLocales: SUPPORTED_LOCALES }}
    >
      {children}
    </TranslationContext.Provider>
  );
}

export function useTranslation() {
  const ctx = useContext(TranslationContext);
  if (!ctx) {
    throw new Error("useTranslation doit être utilisé dans un TranslationProvider");
  }
  return ctx;
}
'''


LANGUAGE_SWITCHER_JSX = '''import { useTranslation } from "../context/TranslationContext";

/**
 * Sélecteur de langue : affiche les langues disponibles.
 * Usage : <LanguageSwitcher />
 */
export default function LanguageSwitcher({ className = "" }) {
  const { locale, setLocale, supportedLocales } = useTranslation();

  const LABELS = { fr: "FR", en: "EN" };

  return (
    <div className={`language-switcher ${className}`}>
      {supportedLocales.map((lang) => (
        <button
          key={lang}
          className={`lang-btn ${lang === locale ? "active" : ""}`}
          onClick={() => setLocale(lang)}
          aria-label={`Changer en ${lang}`}
        >
          {LABELS[lang] || lang.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
'''


# ============================================================
#                       UTILITAIRES
# ============================================================

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    label = os.path.relpath(path, BASE_DIR)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return
        shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")


def install_helmet():
    """Installe react-helmet-async si nécessaire."""
    package_json = os.path.join(BASE_DIR, "package.json")
    if not os.path.exists(package_json):
        print("  [ATTENTION] package.json introuvable.")
        return
    with open(package_json, "r", encoding="utf-8") as f:
        if "react-helmet-async" in f.read():
            print("  [SKIP] react-helmet-async déjà installé")
            return
    print("  → Installation de react-helmet-async...")
    try:
        subprocess.run(
            ["npm", "install", "react-helmet-async"],
            cwd=BASE_DIR, check=True, shell=True
        )
        print("  [OK] react-helmet-async installé")
    except subprocess.CalledProcessError:
        print("  [ATTENTION] Échec npm install. Lancez manuellement : npm install react-helmet-async")


def inject_providers_in_app():
    """Enveloppe App.jsx avec HelmetProvider + TranslationProvider."""
    for name in ["App.jsx", "App.js"]:
        app_path = os.path.join(SRC_DIR, name)
        if os.path.exists(app_path):
            break
    else:
        print("  [ATTENTION] App.jsx introuvable.")
        return

    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "HelmetProvider" in content and "TranslationProvider" in content:
        print("  [SKIP] providers déjà présents dans App.jsx")
        return

    shutil.copy2(app_path, app_path + ".bak")

    # Import HelmetProvider
    if "HelmetProvider" not in content:
        content = 'import { HelmetProvider } from "react-helmet-async";\n' + content

    # Import TranslationProvider
    if "TranslationProvider" not in content:
        content = 'import { TranslationProvider } from "./context/TranslationContext";\n' + content

    # Ajouter HelmetProvider en plus externe
    m = re.search(r"return\s*\(\s*(<[A-Za-z]+)", content)
    if m:
        content = content.replace(
            m.group(1),
            f"<HelmetProvider>\n      {m.group(1)}",
            1,
        )
        # Trouver la dernière parenthèse de fermeture
        last = content.rfind(")")
        if last != -1:
            content = content[:last] + "    </HelmetProvider>\n  " + content[last:]

    # Ajouter TranslationProvider à l'intérieur de ThemeProvider
    if "<ThemeProvider>" in content and "<TranslationProvider>" not in content:
        content = content.replace(
            "<ThemeProvider>",
            "<ThemeProvider>\n        <TranslationProvider>",
            1,
        )
        content = content.replace(
            "</ThemeProvider>",
            "</TranslationProvider>\n      </ThemeProvider>",
            1,
        )

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {name} mis à jour")


def append_css():
    css_content = """
/* ===== Sélecteur de langue ===== */
.language-switcher {
  display: inline-flex; gap: 4px;
  border: 1px solid var(--color-text-muted, #ccc);
  border-radius: 999px; padding: 2px;
}
.lang-btn {
  background: transparent; border: none; cursor: pointer;
  padding: 4px 10px; border-radius: 999px;
  font-size: 12px; font-weight: 600;
  color: var(--color-text-muted, #666);
  transition: all 0.2s;
}
.lang-btn.active {
  background: var(--color-primary, #C1652F);
  color: #fff;
}
"""
    for path in [
        os.path.join(SRC_DIR, "index.css"),
        os.path.join(SRC_DIR, "App.css"),
    ]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                if "language-switcher" in f.read():
                    print(f"  [SKIP] styles déjà dans {os.path.basename(path)}")
                    return
            with open(path, "a", encoding="utf-8") as f:
                f.write(css_content)
            print(f"  [OK] styles ajoutés à {os.path.basename(path)}")
            return


def main():
    print("=" * 60)
    print("  INJECTION SEO + TRADUCTIONS - FRONTEND")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable dans {BASE_DIR}")
        return

    print("\n1. Installation des dépendances...")
    install_helmet()

    print("\n2. Création du composant SeoHead...")
    write_file(os.path.join(SRC_DIR, "components", "SeoHead.jsx"), SEO_HEAD_JSX)

    print("\n3. Création du TranslationContext...")
    write_file(os.path.join(SRC_DIR, "context", "TranslationContext.jsx"), TRANSLATION_CONTEXT_JSX)

    print("\n4. Création du LanguageSwitcher...")
    write_file(os.path.join(SRC_DIR, "components", "LanguageSwitcher.jsx"), LANGUAGE_SWITCHER_JSX)

    print("\n5. Injection des providers dans App.jsx...")
    inject_providers_in_app()

    print("\n6. Styles CSS...")
    append_css()

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nUtilisation :")
    print('  import SeoHead from "./components/SeoHead";')
    print('  <SeoHead title="Boutique" description="..." />')
    print()
    print('  import { useTranslation } from "./context/TranslationContext";')
    print('  const { t, locale, setLocale } = useTranslation();')
    print('  <h1>{t("cart.empty.title")}</h1>')
    print()
    print("  Ajoutez <LanguageSwitcher /> dans votre Header.")


if __name__ == "__main__":
    main()