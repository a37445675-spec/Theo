"""
Setup automatique du Méga Menu Header pour NAWA.
Crée le composant, modifie le Header, ajoute le CSS.

Usage : python setup_mega_menu.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
COMPONENTS_DIR = os.path.join(SRC_DIR, "components")
HEADER_PATH = os.path.join(COMPONENTS_DIR, "Header.jsx")
CSS_PATH = os.path.join(SRC_DIR, "index.css")
MEGA_PATH = os.path.join(COMPONENTS_DIR, "MegaMenuHeader.jsx")


# ============================================================
#  COMPOSANT MEGA MENU
# ============================================================

MEGA_MENU_JSX = '''import { useState } from "react";
import { Link } from "react-router-dom";
import { useNavigation } from "../context/NavigationContext";

/**
 * MegaMenu avec colonnes pour le Header.
 * Lit le menu de location="header" et affiche les items parents
 * avec leurs enfants en colonnes déroulantes.
 */
export default function MegaMenuHeader() {
  const { getMenu, loading } = useNavigation();
  const [openItem, setOpenItem] = useState(null);
  const menu = getMenu("header");

  if (loading || !menu || !menu.items || menu.items.length === 0) return null;

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
                  {hasChildren && <span className="mega-arrow">▾</span>}
                </Link>
              ) : (
                <span className="mega-menu-link">
                  {item.label}
                  {hasChildren && <span className="mega-arrow">▾</span>}
                </span>
              )}

              {hasChildren && openItem === item.id && (
                <div className="mega-dropdown">
                  <div className="mega-dropdown-inner">
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
#  CSS
# ============================================================

CSS_BLOCK = """
/* ===== Méga Menu Header (CMS) ===== */
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
  gap: 0.25rem;
  color: var(--color-text, #221B15);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.95rem;
  padding: 0.5rem 0;
  cursor: pointer;
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
  left: 50%;
  transform: translateX(-50%);
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  padding: 24px 32px;
  min-width: 220px;
  z-index: 100;
  animation: mega-fade-in 0.2s ease;
  margin-top: 8px;
}

@keyframes mega-fade-in {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

.mega-column-title {
  font-weight: 700;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-primary, #C1652F);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.mega-sublist {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mega-sublink {
  color: #221B15;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.15s, padding-left 0.15s;
  display: block;
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
    transform: none;
    box-shadow: none;
    padding: 8px 0 8px 16px;
    margin-top: 0;
    background: transparent;
  }
  .mega-column-title {
    border-bottom: none;
    padding-bottom: 0;
  }
}
/* ===== Fin Méga Menu ===== */
"""


# ============================================================
#  FONCTIONS
# ============================================================

def write_file(path, content, label=None):
    """Écrit un fichier avec backup automatique."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    label = label or os.path.relpath(path, BASE_DIR)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label} (déjà à jour)")
                return False
        shutil.copy2(path, path + ".bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")
    return True


def append_css():
    """Ajoute le CSS à index.css."""
    if not os.path.exists(CSS_PATH):
        print(f"  [ERREUR] {CSS_PATH} introuvable")
        return False

    with open(CSS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "mega-menu-header" in content:
        print("  [SKIP] CSS déjà présent")
        return False

    shutil.copy2(CSS_PATH, CSS_PATH + ".bak")
    with open(CSS_PATH, "a", encoding="utf-8") as f:
        f.write(CSS_BLOCK)
    print("  [OK] CSS ajouté à index.css")
    return True


def patch_header():
    """Modifie Header.jsx pour utiliser MegaMenuHeader."""
    if not os.path.exists(HEADER_PATH):
        print(f"  [ERREUR] {HEADER_PATH} introuvable")
        return False

    with open(HEADER_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "MegaMenuHeader" in content:
        print("  [SKIP] Header.jsx déjà patché")
        return False

    shutil.copy2(HEADER_PATH, HEADER_PATH + ".bak")

    # 1. Ajouter l'import après DynamicMenu
    if 'import DynamicMenu from "./DynamicMenu";' in content:
        content = content.replace(
            'import DynamicMenu from "./DynamicMenu";',
            'import DynamicMenu from "./DynamicMenu";\nimport MegaMenuHeader from "./MegaMenuHeader";',
        )
    else:
        # Fallback : après le premier import
        first_import = re.search(r'^(import\s+.*\n)', content, re.MULTILINE)
        if first_import:
            content = (
                content[:first_import.end()]
                + 'import MegaMenuHeader from "./MegaMenuHeader";\n'
                + content[first_import.end():]
            )

    # 2. Remplacer <DynamicMenu location="header" ... /> par <MegaMenuHeader />
    if '<DynamicMenu location="header"' in content:
        # Remplacer la ligne complète
        content = re.sub(
            r'<DynamicMenu\s+location="header"[^/]*/>',
            '<MegaMenuHeader />',
            content,
        )
        print("  [OK] <DynamicMenu> remplacé par <MegaMenuHeader />")
    else:
        print("  [ATTENTION] Aucun <DynamicMenu location='header'> trouvé")
        print("  → Vérifiez manuellement que Header.jsx utilise bien DynamicMenu")

    with open(HEADER_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] Header.jsx patché")
    return True


# ============================================================
#  MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  SETUP MÉGA MENU HEADER")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"\n  ❌ Dossier src/ introuvable dans {BASE_DIR}")
        print("  → Êtes-vous bien à la racine de nawa-shop-frontend ?")
        return

    print("\n[1/3] Création du composant MegaMenuHeader.jsx...")
    write_file(MEGA_PATH, MEGA_MENU_JSX)

    print("\n[2/3] Ajout du CSS...")
    append_css()

    print("\n[3/3] Modification du Header...")
    patch_header()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print("\nFichiers modifiés :")
    print("  src/components/MegaMenuHeader.jsx  (créé)")
    print("  src/components/Header.jsx           (patché)")
    print("  src/index.css                       (CSS ajouté)")
    print("\n📋 PROCHAINES ÉTAPES :")
    print("  1. Vérifiez dans VS Code que tout est correct")
    print("  2. Ouvrez GitHub Desktop")
    print("  3. Summary : feat: mega menu header from CMS")
    print("  4. Commit to main → Push origin")
    print("  5. Attendez Railway (~3 min)")
    print("  6. Testez : https://sweet-communication-production-1afa.up.railway.app")
    print("\n💡 Créez vos menus dans :")
    print("  https://theo-production-c85a.up.railway.app/admin/navigation/menu/")


if __name__ == "__main__":
    main()