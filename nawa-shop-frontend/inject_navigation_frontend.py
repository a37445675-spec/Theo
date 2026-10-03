"""
Injection automatique du module Navigation - Frontend React.
Crée les composants DynamicMenu et DynamicFooter.

Usage : python inject_navigation_frontend.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")


# ============ FICHIERS ============

NAVIGATION_CONTEXT_JSX = '''import { createContext, useContext, useEffect, useState } from "react";

const NavigationContext = createContext(null);

export function NavigationProvider({ children }) {
  const [menus, setMenus] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/navigation/menus/")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        // L'API peut renvoyer une liste ou un objet paginé
        const list = Array.isArray(data) ? data : (data.results || []);
        // Index par emplacement (header, footer, mobile)
        const byLocation = {};
        list.forEach((menu) => {
          if (!byLocation[menu.location]) {
            byLocation[menu.location] = menu;
          }
        });
        setMenus(byLocation);
      })
      .catch((err) => console.warn("Erreur chargement navigation:", err))
      .finally(() => setLoading(false));
  }, []);

  const getMenu = (location) => menus[location] || null;

  return (
    <NavigationContext.Provider value={{ menus, getMenu, loading }}>
      {children}
    </NavigationContext.Provider>
  );
}

export function useNavigation() {
  const ctx = useContext(NavigationContext);
  if (!ctx) throw new Error("useNavigation doit être utilisé dans un NavigationProvider");
  return ctx;
}
'''

DYNAMIC_MENU_JSX = '''import { Link, NavLink } from "react-router-dom";
import { useNavigation } from "../context/NavigationContext";

/**
 * Menu dynamique piloté par le CMS.
 *
 * Usage :
 *   <DynamicMenu location="header" className="main-nav" />
 *   <DynamicMenu location="footer" className="footer-nav" />
 */
export default function DynamicMenu({ location = "header", className = "" }) {
  const { getMenu, loading } = useNavigation();
  const menu = getMenu(location);

  if (loading) return null;
  if (!menu || !menu.items || menu.items.length === 0) return null;

  const renderItem = (item) => {
    const linkClass = location === "header" ? "nav-link" : "footer-link";
    const isExternal = item.url?.startsWith("http");
    const isInternal = item.url?.startsWith("/");

    const content = (
      <>
        {item.icon_url && (
          <img src={item.icon_url} alt="" className="menu-icon" loading="lazy" />
        )}
        <span>{item.label}</span>
        {item.badge_text && (
          <span
            className="menu-badge"
            style={{ backgroundColor: item.badge_color || "#C1652F" }}
          >
            {item.badge_text}
          </span>
        )}
      </>
    );

    const targetAttr = item.target === "_blank" ? "_blank" : undefined;
    const relAttr = item.target === "_blank" ? "noopener noreferrer" : undefined;

    return (
      <li key={item.id} className="menu-item">
        {isExternal ? (
          <a href={item.url} className={linkClass} target={targetAttr} rel={relAttr}>
            {content}
          </a>
        ) : isInternal ? (
          location === "header" ? (
            <NavLink
              to={item.url}
              end
              className={({ isActive }) => `${linkClass}${isActive ? " active" : ""}`}
              target={targetAttr}
              rel={relAttr}
            >
              {content}
            </NavLink>
          ) : (
            <Link to={item.url} className={linkClass} target={targetAttr} rel={relAttr}>
              {content}
            </Link>
          )
        ) : (
          <span className={linkClass}>{content}</span>
        )}

        {item.children && item.children.length > 0 && (
          <ul className="submenu">
            {item.children.map((child) => (
              <li key={child.id} className="submenu-item">
                <Link to={child.url} className="submenu-link">
                  {child.label}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </li>
    );
  };

  return (
    <ul className={className}>
      {menu.items.map(renderItem)}
    </ul>
  );
}
'''

DYNAMIC_FOOTER_JSX = '''import { useNavigation } from "../context/NavigationContext";
import DynamicMenu from "./DynamicMenu";

/**
 * Pied de page dynamique piloté par le CMS.
 * Affiche le menu de location "footer".
 */
export default function DynamicFooter() {
  const { getMenu, loading } = useNavigation();
  const menu = getMenu("footer");

  if (loading) return null;

  return (
    <footer className="site-footer">
      <div className="container footer-inner">
        <div className="footer-brand">
          <h3>NAWA</h3>
          <p>La beauté d'Afrique, sublimée.</p>
        </div>

        {menu && menu.items && menu.items.length > 0 && (
          <nav className="footer-nav-wrapper">
            <h4>Informations</h4>
            <DynamicMenu location="footer" className="footer-nav" />
          </nav>
        )}

        <div className="footer-copyright">
          <p>© {new Date().getFullYear()} NAWA Commerce. Tous droits réservés.</p>
        </div>
      </div>
    </footer>
  );
}
'''


CSS_STYLES = """
/* ===== Navigation dynamique (CMS) ===== */
.menu-item { position: relative; }
.menu-item a { display: inline-flex; align-items: center; gap: 0.4rem; }
.menu-icon { width: 18px; height: 18px; object-fit: contain; }
.menu-badge {
  color: #fff; font-size: 10px; padding: 2px 6px;
  border-radius: 999px; font-weight: 600; margin-left: 4px;
  text-transform: uppercase; letter-spacing: 0.03em;
}
.submenu {
  position: absolute; top: 100%; left: 0;
  background: var(--color-surface, #fff);
  box-shadow: var(--shadow-md, 0 4px 12px rgba(0,0,0,0.1));
  border-radius: var(--radius, 16px);
  padding: 0.75rem 1rem; min-width: 200px;
  list-style: none; margin: 0;
  opacity: 0; visibility: hidden; transform: translateY(8px);
  transition: opacity 0.2s, transform 0.2s, visibility 0.2s;
  z-index: 100;
}
.menu-item:hover .submenu { opacity: 1; visibility: visible; transform: translateY(0); }
.submenu-item { padding: 0.4rem 0; }
.submenu-link { color: var(--color-text, #221B15); text-decoration: none; }
.submenu-link:hover { color: var(--color-primary, #C1652F); }
.site-footer { background: var(--color-secondary, #2F4A3C); color: #F7F0E4; padding: 3rem 0 1.5rem; margin-top: 4rem; }
.footer-inner { display: flex; flex-direction: column; gap: 2rem; }
.footer-brand h3 { font-family: var(--font-heading, serif); font-size: 1.75rem; margin: 0 0 0.5rem; }
.footer-nav { list-style: none; padding: 0; margin: 0; display: flex; flex-wrap: wrap; gap: 1rem 1.5rem; }
.footer-link { color: #F7F0E4; text-decoration: none; opacity: 0.85; }
.footer-link:hover { opacity: 1; color: var(--color-accent, #D4A843); }
.footer-copyright { border-top: 1px solid rgba(255,255,255,0.15); padding-top: 1.5rem; text-align: center; opacity: 0.7; font-size: 0.9rem; }
"""


# ============ FONCTIONS ============

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_file(path, content):
    ensure_dir(os.path.dirname(path))
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


def append_css():
    candidates = [
        os.path.join(SRC_DIR, "index.css"),
        os.path.join(SRC_DIR, "App.css"),
        os.path.join(SRC_DIR, "styles", "global.css"),
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing = f.read()
            if ".menu-badge" in existing:
                print(f"  [SKIP] styles déjà dans {os.path.relpath(path, BASE_DIR)}")
                return
            shutil.copy2(path, path + ".bak")
            with open(path, "a", encoding="utf-8") as f:
                f.write(CSS_STYLES)
            print(f"  [OK] styles ajoutés à {os.path.relpath(path, BASE_DIR)}")
            return
    print("  [ATTENTION] Aucun CSS trouvé. Ajoutez les styles manuellement.")


def inject_provider_in_app():
    """Enveloppe App.jsx avec NavigationProvider."""
    for app_file in ["App.jsx", "App.js"]:
        app_path = os.path.join(SRC_DIR, app_file)
        if os.path.exists(app_path):
            break
    else:
        print("  [ATTENTION] App.jsx introuvable.")
        return

    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "NavigationProvider" in content:
        print(f"  [SKIP] NavigationProvider déjà dans {app_file}")
        return

    shutil.copy2(app_path, app_path + ".bak")

    # Import
    import_line = 'import { NavigationProvider } from "./context/NavigationContext";\n'
    if content.lstrip().startswith("import"):
        content = import_line + content
    else:
        content = import_line + content

    # Envelopper
    if "<ThemeProvider>" in content:
        content = content.replace(
            "<ThemeProvider>",
            "<ThemeProvider>\n        <NavigationProvider>",
            1,
        )
        content = content.replace(
            "</ThemeProvider>",
            "</NavigationProvider>\n      </ThemeProvider>",
            1,
        )
        print(f"  [OK] NavigationProvider imbriqué dans ThemeProvider")
    else:
        # Fallback : envelopper le premier <Router> ou le return
        print(f"  [ATTENTION] Enveloppez manuellement App avec <NavigationProvider>")

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {app_file} mis à jour")


def main():
    print("=" * 60)
    print("  INJECTION NAVIGATION - FRONTEND")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"\n  [ERREUR] src/ introuvable dans {BASE_DIR}")
        return

    print("\n1. Création du NavigationContext...")
    write_file(os.path.join(SRC_DIR, "context", "NavigationContext.jsx"), NAVIGATION_CONTEXT_JSX)

    print("\n2. Création des composants DynamicMenu et DynamicFooter...")
    write_file(os.path.join(SRC_DIR, "components", "DynamicMenu.jsx"), DYNAMIC_MENU_JSX)
    write_file(os.path.join(SRC_DIR, "components", "DynamicFooter.jsx"), DYNAMIC_FOOTER_JSX)

    print("\n3. Injection des styles CSS...")
    append_css()

    print("\n4. Enveloppement de l'App avec NavigationProvider...")
    inject_provider_in_app()

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nProchaines étapes MANUELLES dans Header.jsx et Footer.jsx :")
    print("  - Remplacez le <nav> codé en dur par <DynamicMenu location=\"header\" />")
    print("  - Remplacez le <footer> codé en dur par <DynamicFooter />")
    print("\nVérifiez dans le navigateur que les menus s'affichent.")


if __name__ == "__main__":
    main()