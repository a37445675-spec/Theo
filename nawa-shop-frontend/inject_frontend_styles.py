"""
Injection des styles CSS pour le layout global.
Ajoute à la fin de src/index.css (avec backup).

Usage : python inject_frontend_styles.py
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")


CSS_CONTENT = """

/* ============================================================
   NAWA Commerce — Styles layout global
   ============================================================ */

.site-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: var(--color-surface, #fff);
  transition: box-shadow 0.2s;
}
.site-header.is-scrolled {
  box-shadow: var(--shadow-sm, 0 1px 2px rgba(0, 0, 0, 0.05));
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  padding: 1rem 0;
}

.logo-text {
  font-family: var(--font-heading, serif);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--color-text, #221B15);
  text-decoration: none;
}
.logo-img { height: 36px; width: auto; display: block; }

.main-nav { display: flex; align-items: center; }
.main-nav-list { display: flex; gap: 1.5rem; list-style: none; margin: 0; padding: 0; }

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.icon-link {
  position: relative;
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  color: inherit;
  display: inline-flex;
  align-items: center;
}
.cart-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: var(--color-primary, #C1652F);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  min-width: 18px;
  height: 18px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}
.user-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 8px;
  height: 8px;
  background: var(--color-success, #16A34A);
  border-radius: 50%;
}

/* === Dropdown compte === */
.account-menu { position: relative; }
.account-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 240px;
  background: var(--color-surface, #fff);
  border-radius: var(--radius, 16px);
  box-shadow: var(--shadow-lg, 0 10px 30px rgba(0, 0, 0, 0.15));
  overflow: hidden;
  z-index: 1001;
}
.account-dropdown-header { padding: 1rem 1.25rem; border-bottom: 1px solid #eee; }
.account-dropdown-name { font-weight: 600; }
.account-dropdown-email { font-size: 0.8rem; color: #888; }
.account-dropdown-body { padding: 0.5rem 0; }
.account-dropdown-body a {
  display: block;
  padding: 0.6rem 1.25rem;
  color: var(--color-text, #221B15);
  text-decoration: none;
  font-size: 0.9rem;
}
.account-dropdown-body a:hover { background: #f7f7f7; }
.account-dropdown-staff { border-top: 1px solid #eee; }
.account-dropdown-staff a {
  display: block;
  padding: 0.6rem 1.25rem;
  color: var(--color-primary, #C1652F);
  font-weight: 600;
  text-decoration: none;
}
.account-dropdown-footer { border-top: 1px solid #eee; padding: 0.5rem 0; }
.account-dropdown-footer button {
  width: 100%;
  text-align: left;
  padding: 0.6rem 1.25rem;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-error, #DC2626);
  font-size: 0.9rem;
}

/* === Recherche === */
.search-wrapper { position: relative; }
.search-form {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  display: flex;
  background: #fff;
  border-radius: var(--radius, 16px);
  box-shadow: var(--shadow-lg, 0 10px 30px rgba(0, 0, 0, 0.15));
  overflow: hidden;
}
.search-form input {
  border: none;
  padding: 0.75rem 1rem;
  min-width: 240px;
  outline: none;
}
.search-form button {
  background: var(--color-primary, #C1652F);
  color: #fff;
  border: none;
  padding: 0 1rem;
  cursor: pointer;
}

/* === Annonces === */
.announcement-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 0.65rem 1rem;
  font-size: 0.9rem;
  position: relative;
}
.announcement-link { text-decoration: underline; font-weight: 600; color: inherit; }
.announcement-close {
  position: absolute;
  right: 1rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  color: inherit;
  opacity: 0.7;
}
.announcement-popup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.announcement-popup {
  max-width: 500px;
  padding: 2rem;
  border-radius: var(--radius, 16px);
  position: relative;
}

/* === Mobile === */
.menu-toggle { display: none; background: none; border: none; cursor: pointer; padding: 8px; }
.menu-toggle span {
  display: block;
  width: 24px;
  height: 2px;
  background: var(--color-text, #221B15);
  margin: 5px 0;
  transition: all 0.2s;
}

@media (max-width: 900px) {
  .menu-toggle { display: block; }
  .main-nav {
    position: fixed;
    top: 0;
    right: -100%;
    width: 280px;
    height: 100vh;
    background: #fff;
    flex-direction: column;
    padding: 4rem 2rem;
    transition: right 0.3s;
    box-shadow: var(--shadow-lg);
    z-index: 999;
  }
  .main-nav.is-open { right: 0; }
  .main-nav-list { flex-direction: column; }
  .mobile-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 998;
  }
  .header-lang { display: none; }
}

.media-image { max-width: 100%; height: auto; display: block; }
/* ============================================================
   Fin des styles layout NAWA
   ============================================================ */
"""


def find_css_file():
    """Cherche le fichier CSS principal à enrichir."""
    candidates = [
        os.path.join(SRC_DIR, "index.css"),
        os.path.join(SRC_DIR, "App.css"),
        os.path.join(SRC_DIR, "styles", "global.css"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return None


def main():
    print("=" * 60)
    print("  INJECTION STYLES CSS (Week 4, 5, 6)")
    print("=" * 60)

    css_path = find_css_file()
    if not css_path:
        print("  [ERREUR] Aucun fichier CSS trouvé.")
        print("  Créez src/index.css puis relancez.")
        return

    label = os.path.relpath(css_path, BASE_DIR)
    print(f"\n  Fichier cible : {label}")

    with open(css_path, "r", encoding="utf-8") as f:
        existing = f.read()

    # Anti-doublon
    if "NAWA Commerce — Styles layout global" in existing:
        print("  [SKIP] Les styles sont déjà présents.")
        return

    shutil.copy2(css_path, css_path + ".bak")
    print(f"  [BACKUP] {label}.bak")

    with open(css_path, "a", encoding="utf-8") as f:
        f.write(CSS_CONTENT)

    print(f"  [OK] Styles ajoutés à {label}")
    print()
    print("=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nRestaurer en cas de problème :")
    print(f'  Copy-Item "{label}.bak" "{label}" -Force')


if __name__ == "__main__":
    main()