"""
Upgrade MegaMenuHeader pour supporter 3+ niveaux de sous-menus.

Usage : python upgrade_mega_menu.py
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
MEGA_PATH = os.path.join(SRC_DIR, "components", "MegaMenuHeader.jsx")
CSS_PATH = os.path.join(SRC_DIR, "index.css")


# ============================================================
#  COMPOSANT MEGA MENU MULTI-NIVEAUX
# ============================================================

MEGA_MULTILEVEL = '''import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

/**
 * MegaMenu multi-niveaux — supporte N niveaux de sous-menus.
 * Fetch directement /api/v1/navigation/menus/?location=header
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
      .catch((err) => console.warn("Mega menu indisponible:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading || !menu || !menu.items || menu.items.length === 0) return null;

  return (
    <nav className="mega-menu-header">
      <ul className="mega-menu-list">
        {menu.items.map((item) => (
          <MegaItem
            key={item.id}
            item={item}
            isOpen={openItem === item.id}
            onOpen={() => setOpenItem(item.id)}
            onClose={() => setOpenItem(null)}
            level={0}
          />
        ))}
      </ul>
    </nav>
  );
}

/**
 * Rendu récursif d'un item de menu (supporte N niveaux).
 */
function MegaItem({ item, isOpen, onOpen, onClose, level }) {
  const hasChildren = item.children && item.children.length > 0;
  const isTopLevel = level === 0;

  // Niveau 0 (racine) : dropdown au survol
  if (isTopLevel) {
    return (
      <li
        className="mega-menu-item"
        onMouseEnter={hasChildren ? onOpen : undefined}
        onMouseLeave={hasChildren ? onClose : undefined}
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

        {hasChildren && isOpen && (
          <div className="mega-dropdown">
            <div className="mega-column-title">{item.label}</div>
            <ul className="mega-sublist">
              {item.children.map((child) => (
                <MegaItem
                  key={child.id}
                  item={child}
                  isOpen={false}
                  onOpen={() => {}}
                  onClose={() => {}}
                  level={1}
                />
              ))}
            </ul>
          </div>
        )}
      </li>
    );
  }

  // Niveaux 1+ : item avec sous-menu en cascade (au survol)
  return (
    <li
      className="mega-subitem"
      onMouseEnter={hasChildren ? onOpen : undefined}
      onMouseLeave={hasChildren ? onClose : undefined}
    >
      <Link to={item.url} className="mega-sublink">
        <span>{item.label}</span>
        {hasChildren && <span className="mega-cascade-arrow">›</span>}
      </Link>

      {hasChildren && isOpen && (
        <ul className="mega-cascade">
          {item.children.map((subChild) => (
            <MegaItem
              key={subChild.id}
              item={subChild}
              isOpen={false}
              onOpen={() => {}}
              onClose={() => {}}
              level={level + 1}
            />
          ))}
        </ul>
      )}
    </li>
  );
}
'''


# ============================================================
#  CSS MULTI-NIVEAUX
# ============================================================

CSS_MULTILEVEL = """
/* ===== Mega Menu Multi-Niveaux ===== */
.mega-subitem {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.mega-subitem > .mega-sublink {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 0;
}

.mega-cascade-arrow {
  font-size: 0.9rem;
  opacity: 0.4;
  margin-left: 8px;
}

/* Sous-menu en cascade (niveau 2+) */
.mega-cascade {
  position: absolute;
  top: 0;
  left: 100%;
  margin-left: 8px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  padding: 16px 20px;
  min-width: 200px;
  list-style: none;
  z-index: 110;
  animation: mega-fade-in 0.2s ease;
}

.mega-cascade .mega-sublink {
  display: block;
  padding: 6px 0;
  color: #221B15;
  text-decoration: none;
  font-size: 0.88rem;
  transition: color 0.15s, padding-left 0.15s;
}

.mega-cascade .mega-sublink:hover {
  color: var(--color-primary, #C1652F);
  padding-left: 4px;
}

/* Responsive : les cascades deviennent inline */
@media (max-width: 900px) {
  .mega-cascade {
    position: static;
    margin-left: 0;
    margin-top: 4px;
    box-shadow: none;
    padding: 4px 0 4px 16px;
    background: transparent;
  }
}
/* ===== Fin Mega Menu Multi-Niveaux ===== */
"""


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


def append_css():
    if not os.path.exists(CSS_PATH):
        print("  [INFO] index.css introuvable")
        return
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    if ".mega-cascade" in content:
        print("  [SKIP] CSS cascade déjà présent")
        return
    shutil.copy2(CSS_PATH, CSS_PATH + ".bak")
    with open(CSS_PATH, "a", encoding="utf-8") as f:
        f.write(CSS_MULTILEVEL)
    print("  [OK] CSS cascade ajouté")


def main():
    print("=" * 60)
    print("  UPGRADE MEGA MENU — Support N niveaux")
    print("=" * 60)

    print("\n[1/2] Mise à jour de MegaMenuHeader.jsx...")
    write_file(MEGA_PATH, MEGA_MULTILEVEL)

    print("\n[2/2] Ajout du CSS cascade...")
    append_css()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print("\n📋 PROCHAINES ÉTAPES :")
    print("  1. Ouvrez GitHub Desktop")
    print("  2. Summary : feat: mega menu supports N levels")
    print("  3. Commit to main → Push origin")
    print("  4. Attendez Railway (~3 min)")
    print()
    print("🎯 POUR TESTER :")
    print("  Créez un sous-sous-menu dans l'admin :")
    print("  https://theo-production-c85a.up.railway.app/admin/navigation/menuitem/add/")
    print("  → Parent = un item existant (ex: Cheveux)")


if __name__ == "__main__":
    main()