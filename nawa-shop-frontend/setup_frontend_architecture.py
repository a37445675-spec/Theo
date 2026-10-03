"""
Échafaudage de l'architecture Headless CMS - Frontend React.
Crée les contextes, hooks et composants pour consommer l'API du CMS.

Usage : python setup_frontend_architecture.py
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")


# === Fichiers à créer ===
FILES = {
    # ===== Contextes =====
    "context/ThemeContext.jsx": '''import { createContext, useContext, useEffect, useState } from "react";

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(null);

  // Charge le design system depuis l'API
  useEffect(() => {
    fetch("/api/v1/design-system/")
      .then((res) => res.json())
      .then((data) => {
        const config = Array.isArray(data) ? data[0] : data;
        setTheme(config);
        applyTheme(config);
      })
      .catch((err) => console.warn("Erreur chargement design system:", err));
  }, []);

  // Applique les variables CSS dynamiquement
  const applyTheme = (config) => {
    if (!config) return;
    const root = document.documentElement;
    const map = {
      "--color-primary": config.color_primary,
      "--color-secondary": config.color_secondary,
      "--color-bg": config.color_background,
      "--color-text": config.color_text,
      "--color-accent": config.color_accent,
      "--color-error": config.color_error,
      "--color-success": config.color_success,
      "--font-heading": config.font_heading,
      "--font-body": config.font_body,
      "--font-size-base": config.font_size_base,
      "--radius": config.border_radius,
      "--button-radius": config.button_radius,
      "--shadow-sm": config.shadow_sm,
      "--shadow-md": config.shadow_md,
      "--shadow-lg": config.shadow_lg,
    };
    Object.entries(map).forEach(([key, value]) => {
      if (value) root.style.setProperty(key, value);
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
''',

    "context/SiteConfigContext.jsx": '''import { createContext, useContext, useEffect, useState } from "react";

const SiteConfigContext = createContext(null);

export function SiteConfigProvider({ children }) {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Appel unique pour récupérer toute la config du site
    fetch("/api/v1/site-config/")
      .then((res) => res.json())
      .then((data) => setConfig(data))
      .catch((err) => console.warn("Erreur chargement config site:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <SiteConfigContext.Provider value={{ config, loading }}>
      {children}
    </SiteConfigContext.Provider>
  );
}

export function useSiteConfig() {
  return useContext(SiteConfigContext);
}
''',

    "context/FeatureFlagsContext.jsx": '''import { createContext, useContext, useEffect, useState } from "react";

const FeatureFlagsContext = createContext({});

export function FeatureFlagsProvider({ children }) {
  const [flags, setFlags] = useState({});

  useEffect(() => {
    fetch("/api/v1/feature-flags/")
      .then((res) => res.json())
      .then((data) => {
        const map = {};
        (Array.isArray(data) ? data : data.results || []).forEach((flag) => {
          map[flag.code] = flag.is_enabled;
        });
        setFlags(map);
      })
      .catch((err) => console.warn("Erreur chargement feature flags:", err));
  }, []);

  return (
    <FeatureFlagsContext.Provider value={flags}>
      {children}
    </FeatureFlagsContext.Provider>
  );
}

export function useFeatureFlags() {
  return useContext(FeatureFlagsContext);
}

export function useFeatureFlag(code) {
  const flags = useContext(FeatureFlagsContext);
  return flags[code] === true;
}
''',

    "context/TranslationContext.jsx": '''import { createContext, useContext, useEffect, useState } from "react";

const TranslationContext = createContext({});

export function TranslationProvider({ children, locale = "fr" }) {
  const [translations, setTranslations] = useState({});

  useEffect(() => {
    fetch(`/api/v1/translations/?lang=${locale}`)
      .then((res) => res.json())
      .then((data) => {
        const map = {};
        (Array.isArray(data) ? data : data.results || []).forEach((t) => {
          map[t.key] = t[`value_${locale}`] || t.value_fr || t.key;
        });
        setTranslations(map);
      })
      .catch((err) => console.warn("Erreur chargement traductions:", err));
  }, [locale]);

  return (
    <TranslationContext.Provider value={translations}>
      {children}
    </TranslationContext.Provider>
  );
}

export function useTranslation() {
  const translations = useContext(TranslationContext);
  return {
    t: (key, fallback) => translations[key] || fallback || key,
    locale: "fr",
  };
}
''',

    # ===== Hooks =====
    "hooks/useApi.js": '''import { useState, useEffect } from "react";

/**
 * Hook générique pour appeler une API.
 * Usage : const { data, loading, error, refetch } = useApi("/api/v1/products/");
 */
export function useApi(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = () => {
    setLoading(true);
    fetch(url, options)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json) => setData(json))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line
  }, [url]);

  return { data, loading, error, refetch: fetchData };
}
''',

    # ===== Composants =====
    "components/DynamicMenu.jsx": '''import { Link } from "react-router-dom";
import { useApi } from "../hooks/useApi";

/**
 * Menu dynamique piloté par l'API.
 * Usage : <DynamicMenu location="header" />
 */
export default function DynamicMenu({ location = "header" }) {
  const { data: menus, loading } = useApi(`/api/v1/navigation/menus/?location=${location}`);

  if (loading || !menus) return null;

  const menu = Array.isArray(menus) ? menus[0] : menus;

  const renderItem = (item) => (
    <li key={item.id} className="menu-item">
      <Link to={item.url} target={item.open_in_new_tab ? "_blank" : undefined}>
        {item.icon && <img src={item.icon} alt="" className="menu-icon" />}
        {item.label}
      </Link>
      {item.children?.length > 0 && (
        <ul className="submenu">
          {item.children.map(renderItem)}
        </ul>
      )}
    </li>
  );

  return (
    <nav className={`dynamic-menu dynamic-menu-${location}`}>
      <ul>{menu?.items?.map(renderItem)}</ul>
    </nav>
  );
}
''',

    "components/AnnouncementBar.jsx": '''import { useState, useEffect } from "react";
import { useApi } from "../hooks/useApi";

/**
 * Bannière d'annonce affichée en haut du site.
 */
export default function AnnouncementBar({ position = "top_bar" }) {
  const { data: announcements } = useApi(
    `/api/v1/announcements/?position=${position}&is_active=true`
  );
  const [dismissed, setDismissed] = useState(false);

  if (dismissed || !announcements || announcements.length === 0) return null;

  const ann = Array.isArray(announcements) ? announcements[0] : announcements;

  return (
    <div
      className="announcement-bar"
      style={{ backgroundColor: ann.background_color, color: ann.text_color }}
    >
      <span>{ann.message}</span>
      {ann.link && (
        <a href={ann.link} className="announcement-link">
          {ann.link_label}
        </a>
      )}
      <button
        className="announcement-close"
        onClick={() => setDismissed(true)}
        aria-label="Fermer"
      >
        ×
      </button>
    </div>
  );
}
''',

    "components/DynamicPageRenderer.jsx": '''import { useApi } from "../hooks/useApi";

// Registre des composants de blocs disponibles
const BLOCK_COMPONENTS = {
  // hero: HeroBlock,
  // product_grid: ProductGridBlock,
  // blog_list: BlogListBlock,
  // banner: BannerBlock,
  // cta: CtaBlock,
  // text: TextBlock,
};

/**
 * Rend une page dynamique en boucle sur ses blocs.
 * Usage : <DynamicPageRenderer templateId={1} />
 */
export default function DynamicPageRenderer({ templateId }) {
  const { data: page, loading, error } = useApi(`/api/v1/cms/page-templates/${templateId}/`);

  if (loading) return <div className="page-loading">Chargement...</div>;
  if (error) return <div className="page-error">Erreur : {error}</div>;
  if (!page) return null;

  const blocks = (page.blocks || [])
    .filter((b) => b.is_visible)
    .sort((a, b) => a.order - b.order);

  return (
    <div className="dynamic-page">
      {blocks.map((block) => {
        const Component = BLOCK_COMPONENTS[block.block_type];
        return (
          <section key={block.id} className={`block block-${block.block_type}`}>
            {block.title && (
              <div className="container section-header">
                <h2 className="section-title">{block.title}</h2>
                {block.subtitle && <p className="section-subtitle">{block.subtitle}</p>}
              </div>
            )}
            {Component ? (
              <Component config={block.config} />
            ) : (
              <div className="container block-placeholder">
                Bloc de type <code>{block.block_type}</code> non implémenté.
              </div>
            )}
          </section>
        );
      })}
    </div>
  );
}
''',

    # ===== Utilitaires =====
    "utils/api.js": '''/**
 * Client API centralisé.
 * Ajoute automatiquement le token d'authentification si présent.
 */
const API_BASE = "/api/v1";

export async function apiCall(endpoint, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `Erreur HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  get: (url) => apiCall(url),
  post: (url, data) => apiCall(url, { method: "POST", body: JSON.stringify(data) }),
  put: (url, data) => apiCall(url, { method: "PUT", body: JSON.stringify(data) }),
  patch: (url, data) => apiCall(url, { method: "PATCH", body: JSON.stringify(data) }),
  delete: (url) => apiCall(url, { method: "DELETE" }),
};
''',
}


def create_file(relative_path, content):
    """Crée un fichier s'il n'existe pas."""
    full_path = os.path.join(SRC_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    if os.path.exists(full_path):
        print(f"  [EXISTE] src/{relative_path}")
        return False

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [CRÉÉ] src/{relative_path}")
    return True


def create_css_file():
    """Ajoute les styles CSS pour les composants dynamiques."""
    css_candidates = [
        os.path.join(SRC_DIR, "index.css"),
        os.path.join(SRC_DIR, "App.css"),
        os.path.join(SRC_DIR, "styles", "global.css"),
    ]
    css_content = """
/* ===== Composants dynamiques CMS ===== */
.dynamic-menu ul { list-style: none; display: flex; gap: 1.5rem; padding: 0; margin: 0; }
.dynamic-menu a { display: flex; align-items: center; gap: 0.5rem; text-decoration: none; color: inherit; }
.menu-icon { width: 18px; height: 18px; object-fit: contain; }
.submenu { position: absolute; background: white; box-shadow: var(--shadow-md); border-radius: var(--radius); padding: 1rem; }

.announcement-bar {
  display: flex; align-items: center; justify-content: center; gap: 1rem;
  padding: 0.75rem 1rem; font-size: 0.9rem; position: relative;
}
.announcement-link { text-decoration: underline; font-weight: 600; }
.announcement-close {
  position: absolute; right: 1rem; background: none; border: none;
  cursor: pointer; font-size: 1.25rem; color: inherit;
}

.section-header { text-align: center; margin-bottom: 2rem; }
.section-title { font-family: var(--font-heading, serif); font-size: 2rem; margin: 0 0 0.5rem; }
.section-subtitle { color: #666; font-size: 1.1rem; margin: 0; }

.page-loading, .page-error, .block-placeholder {
  padding: 3rem; text-align: center; color: #888;
}
"""
    for path in css_candidates:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing = f.read()
            if ".announcement-bar" in existing:
                print("  [INFO] Styles CSS déjà présents.")
                return
            with open(path, "a", encoding="utf-8") as f:
                f.write(css_content)
            print(f"  [OK] Styles ajoutés à {os.path.relpath(path, BASE_DIR)}")
            return
    print("  [ATTENTION] Aucun fichier CSS trouvé. Ajoutez les styles manuellement.")


def main():
    print("=" * 60)
    print("  ÉCHAFAUDAGE CMS HEADLESS - FRONTEND")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"\n  [ERREUR] Dossier src/ introuvable dans {BASE_DIR}")
        print("  Êtes-vous bien à la racine du projet frontend ?")
        return

    print("\n1. Création des contextes, hooks, composants et utilitaires...")
    created = 0
    for path, content in FILES.items():
        if create_file(path, content):
            created += 1
    print(f"  → {created} fichier(s) créé(s).")

    print("\n2. Ajout des styles CSS...")
    create_css_file()

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nProchaines étapes :")
    print("  1. Enveloppez votre App avec les Providers dans App.jsx :")
    print("     <SiteConfigProvider>")
    print("       <ThemeProvider>")
    print("         <FeatureFlagsProvider>")
    print("           <TranslationProvider>")
    print("             <App />")
    print("           </TranslationProvider>")
    print("         </FeatureFlagsProvider>")
    print("       </ThemeProvider>")
    print("     </SiteConfigProvider>")
    print("  2. Remplacez vos menus codés en dur par <DynamicMenu />")
    print("  3. Ajoutez <AnnouncementBar /> en haut de votre layout")


if __name__ == "__main__":
    main()