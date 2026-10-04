"""
Fix complet du Mega Menu Header.
Remplace MegaMenuHeader.jsx par une version auto-suffisante.

Usage : python fix_mega_menu.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
COMPONENTS = os.path.join(SRC_DIR, "components")
HEADER = os.path.join(COMPONENTS, "Header.jsx")
MEGA = os.path.join(COMPONENTS, "MegaMenuHeader.jsx")
CSS = os.path.join(SRC_DIR, "index.css")


# ============================================================
#  MEGA MENU AUTO-SUFFISANT (sans dépendance contexte)
# ============================================================

MEGA_JSX = '''import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

/**
 * MegaMenu Header — auto-suffisant.
 * Fetch directement /api/v1/navigation/menus/?location=header
 * Affiche les items avec leurs enfants en dropdown au survol.
 */
export default function MegaMenuHeader() {
  const [menu, setMenu] = useState(null);
  const [loading, setLoading] = useState(true);
  const [openItem, setOpenItem] = useState(null);

  useEffect(() => {
    fetch("/api/v1/navigation/menus/?location=header")
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => {
        const list = Array.isArray(data) ? data : data.results || [];
        setMenu(list[0] || null);
      })
      .catch((err) => {
        console.warn("Mega menu indisponible:", err);
        setMenu(null);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return null;
  if (!menu || !menu.items || menu.items.length === 0) return null;

  return (
    <nav className="mega-menu-header">
      <ul className="mega-menu-list">
        {menu.items.map((item) => {
          const hasChildren = item.children && item.children.length > 0;

          return (
            <li
              key={item.id}
              className="mega-menu-item"
              onMouseEnter={() => hasChildren && setOpenItem(item.id)}
              onMouseLeave={() => setOpenItem(null)}
            >
              {item.url ? (
                <Link to={item.url} className="mega-menu-link">
                  {item.label}
                  {hasChildren && <span className="mega-arrow"> ▾</span>}
                </Link>
              ) : (
                <span className="mega-menu-link" style={{ cursor: "pointer" }}>
                  {item.label}
                  {hasChildren && <span className="mega-arrow"> ▾</span>}
                </span>
              )}

              {hasChildren && openItem === item.id && (
                <div className="mega-dropdown">
                  <div className="mega-column-title">{item.label}</div>
                  <ul className="mega-sublist">
                    {item.children.map((child) => (
                      <li key={child.id}>
                        <Link to={child.url} className="mega-sublink">
                          {child.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
'''


# ============================================================
#  CSS MEGA MENU
# ============================================================

CSS_BLOCK = """
/* ===== Méga Menu Header ===== */
.mega-menu-header {
  position: relative;
}

.mega-menu-list {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

.mega-menu-item {
  position: relative;
}

.mega-menu-link {
  display: inline-flex;
  align-items: center;
  color: var(--color-text, #221B15);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  padding: 0.5rem 0;
  transition: color 0.2s;
}

.mega-menu-link:hover {
  color: var(--color-primary, #C1652F);
}

.mega-arrow {
  font-size: 0.7rem;
  opacity: 0.6;
}

.mega-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  padding: 20px 24px;
  min-width: 240px;
  z-index: 100;
  animation: mega-fade-in 0.2s ease;
  margin-top: 4px;
}

@keyframes mega-fade-in {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.mega-column-title {
  font-weight: 700;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-primary, #C1652F);
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.mega-sublist {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mega-sublink {
  color: #221B15;
  text-decoration: none;
  font-size: 0.9rem;
  display: block;
  padding: 4px 0;
  transition: color 0.15s, padding-left 0.15s;
}

.mega-sublink:hover {
  color: var(--color-primary, #C1652F);
  padding-left: 4px;
}

@media (max-width: 900px) {
  .mega-menu-list {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .mega-dropdown {
    position: static;
    box-shadow: none;
    padding: 8px 0 8px 16px;
    margin-top: 0;
    background: transparent;
  }
}
/* ===== Fin Méga Menu ===== */
"""


# ============================================================
#  FONCTIONS
# ============================================================

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    label = os.path.relpath(path, BASE_DIR)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return False
        shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")
    return True


def ensure_header_uses_mega():
    """Vérifie que Header.jsx importe et utilise MegaMenuHeader."""
    if not os.path.exists(HEADER):
        print("  [ERREUR] Header.jsx introuvable")
        return False

    with open(HEADER, "r", encoding="utf-8") as f:
        content = f.read()

    modified = False

    # Ajouter l'import si absent
    if "MegaMenuHeader" not in content:
        if 'import DynamicMenu' in content:
            content = content.replace(
                'import DynamicMenu from "./DynamicMenu";',
                'import DynamicMenu from "./DynamicMenu";\nimport MegaMenuHeader from "./MegaMenuHeader";',
            )
        else:
            match = re.search(r'^(import\s+.*\n)', content, re.MULTILINE)
            if match:
                content = content[:match.end()] + 'import MegaMenuHeader from "./MegaMenuHeader";\n' + content[match.end():]
        modified = True
        print("  [OK] Import MegaMenuHeader ajouté")

    # Remplacer <DynamicMenu location="header" ... /> si présent
    if '<DynamicMenu location="header"' in content:
        content = re.sub(
            r'<DynamicMenu\s+location="header"[^/]*/>',
            '<MegaMenuHeader />',
            content,
        )
        modified = True
        print("  [OK] <DynamicMenu location='header'> remplacé par <MegaMenuHeader />")
    elif "<MegaMenuHeader />" not in content:
        # Chercher <nav className="main-nav"> pour insérer
        if '<nav className="main-nav' in content:
            content = re.sub(
                r'(<nav className="main-nav[^>]*>)',
                r'\1\n          <MegaMenuHeader />',
                content,
                count=1,
            )
            modified = True
            print("  [OK] <MegaMenuHeader /> inséré dans <nav>")

    if modified:
        shutil.copy2(HEADER, HEADER + ".bak")
        with open(HEADER, "w", encoding="utf-8") as f:
            f.write(content)
    else:
        print("  [SKIP] Header.jsx déjà configuré")

    return True


def append_css():
    if not os.path.exists(CSS):
        print("  [INFO] index.css introuvable, ignoré")
        return
    with open(CSS, "r", encoding="utf-8") as f:
        content = f.read()
    if ".mega-menu-header" in content:
        print("  [SKIP] CSS déjà présent")
        return
    with open(CSS, "a", encoding="utf-8") as f:
        f.write(CSS_BLOCK)
    print("  [OK] CSS ajouté")


# ============================================================
#  MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  FIX MEGA MENU HEADER")
    print("=" * 60)

    print("\n[1/3] Remplacement de MegaMenuHeader.jsx...")
    write_file(MEGA, MEGA_JSX)

    print("\n[2/3] Mise à jour de Header.jsx...")
    ensure_header_uses_mega()

    print("\n[3/3] Ajout du CSS...")
    append_css()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print("\n📋 À FAIRE MAINTENANT :")
    print("  1. Ouvrez GitHub Desktop")
    print("  2. Summary : fix: mega menu header auto-suffisant")
    print("  3. Commit to main → Push origin")
    print("  4. Attendez Railway (~3 min)")
    print()
    print("📋 PUIS : créer le menu dans l'admin Django")
    print("  https://theo-production-c85a.up.railway.app/admin/navigation/menu/")


if __name__ == "__main__":
    main()