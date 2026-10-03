"""
Finalise la Phase 7 frontend :
1. Installe @measured/puck
2. Crée AdminPagesList.jsx
3. Ajoute les routes dans App.jsx

Usage : python fix_phase7_frontend.py
"""
import os
import re
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")


ADMIN_PAGES_LIST = '''import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

/**
 * Liste des pages éditables (templates CMS).
 * Route : /admin/pages
 */
export default function AdminPagesList() {
  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/v1/cms/page-templates/", { credentials: "include" })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        const list = Array.isArray(data) ? data : data.results || [];
        setPages(list);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div style={{ padding: "3rem", textAlign: "center", color: "#6B6259" }}>
        Chargement des pages...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "3rem", textAlign: "center", color: "#DC2626" }}>
        Erreur : {error}
      </div>
    );
  }

  return (
    <div style={{ padding: "2rem", maxWidth: "1000px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "0.5rem" }}>Éditeur de pages</h1>
      <p style={{ color: "#6B6259", marginBottom: "2rem" }}>
        Sélectionnez une page pour l'éditer dans le constructeur visuel.
      </p>

      {pages.length === 0 ? (
        <div style={{
          padding: "3rem",
          textAlign: "center",
          background: "#F7F0E4",
          borderRadius: "12px",
          color: "#6B6259",
        }}>
          <p>Aucune page disponible.</p>
          <p style={{ fontSize: "0.9rem" }}>
            Créez-en une dans{" "}
            <a
              href="http://localhost:8000/admin/cms/pagetemplate/"
              target="_blank"
              rel="noreferrer"
              style={{ color: "#C1652F", textDecoration: "underline" }}
            >
              l'admin Django
            </a>.
          </p>
        </div>
      ) : (
        <ul style={{ listStyle: "none", padding: 0 }}>
          {pages.map((page) => (
            <li
              key={page.id}
              style={{
                padding: "1.25rem",
                borderBottom: "1px solid #eee",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: "1rem",
              }}
            >
              <div>
                <strong style={{ fontSize: "1.05rem" }}>{page.name}</strong>
                <div style={{ fontSize: "0.85rem", color: "#888", marginTop: "4px" }}>
                  Type : {page.template_type || "—"} · ID : {page.id}
                </div>
              </div>
              <Link
                to={`/admin/pages/${page.id}/builder`}
                style={{
                  background: "#C1652F",
                  color: "#fff",
                  padding: "10px 20px",
                  borderRadius: "8px",
                  textDecoration: "none",
                  fontWeight: 600,
                  fontSize: "0.9rem",
                  whiteSpace: "nowrap",
                }}
              >
                Éditer
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
'''


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    label = os.path.relpath(path, BASE_DIR)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label} (déjà à jour)")
                return False
        shutil.copy2(path, path + ".bak")
        print(f"  [BACKUP] {label}.bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")
    return True


def install_puck():
    pkg = os.path.join(BASE_DIR, "package.json")
    if not os.path.exists(pkg):
        print("  [ATTENTION] package.json introuvable.")
        return

    with open(pkg, "r", encoding="utf-8") as f:
        content = f.read()

    if "@measured/puck" in content:
        print("  [SKIP] @measured/puck déjà dans package.json")
        return

    print("  → npm install @measured/puck")
    try:
        subprocess.run(
            ["npm", "install", "@measured/puck"],
            cwd=BASE_DIR, check=True, shell=True,
        )
        print("  [OK] @measured/puck installé")
    except subprocess.CalledProcessError as e:
        print(f"  [ATTENTION] Échec npm install : {e}")
        print("  → Lancez manuellement : npm install @measured/puck")


def add_routes_to_app():
    app_path = None
    for name in ["App.jsx", "App.js"]:
        p = os.path.join(SRC_DIR, name)
        if os.path.exists(p):
            app_path = p
            break

    if not app_path:
        print("  [ERREUR] App.jsx introuvable dans src/")
        return

    label = os.path.relpath(app_path, BASE_DIR)

    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    needs_import = "AdminPagesList" not in content or "PageBuilder" not in content
    needs_route = "admin/pages/:pageId/builder" not in content

    if not needs_import and not needs_route:
        print(f"  [SKIP] {label} (routes déjà présentes)")
        return

    shutil.copy2(app_path, app_path + ".bak")
    print(f"  [BACKUP] {label}.bak")

    # 1. Ajouter les imports (juste après le premier import React)
    if "AdminPagesList" not in content:
        imports = (
            'import AdminPagesList from "./pages/admin/AdminPagesList";\n'
            'import PageBuilder from "./pages/admin/PageBuilder";\n'
        )
        # Insérer avant le premier import de page existant
        marker = 'import Home from "./pages/Home'
        if marker in content:
            content = content.replace(marker, imports + marker, 1)
        else:
            # Sinon, juste en haut du fichier
            content = imports + content
        print("  [OK] imports ajoutés")

    # 2. Ajouter les routes avant la route NotFound
    if "admin/pages/:pageId/builder" not in content:
        routes = (
            '            {/* === Admin : Page Builder === */}\n'
            '            <Route path="/admin/pages" element={<AdminPagesList />} />\n'
            '            <Route path="/admin/pages/:pageId/builder" element={<PageBuilder />} />\n\n'
        )

        # Pattern 1 : chercher la route NotFound
        patterns = [
            r'(\s*<Route path="\*" element=\{<NotFound />\} />)',
            r'(\s*<Route path="\*" element=\{<NotFound\s*/>\} />)',
        ]
        replaced = False
        for pattern in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, routes + r'\1', content, count=1)
                replaced = True
                break

        if replaced:
            print("  [OK] routes ajoutées")
        else:
            print("  [ATTENTION] Route NotFound introuvable.")
            print("  → Ajoutez manuellement dans App.jsx :")
            print('     import AdminPagesList from "./pages/admin/AdminPagesList";')
            print('     import PageBuilder from "./pages/admin/PageBuilder";')
            print('     <Route path="/admin/pages" element={<AdminPagesList />} />')
            print('     <Route path="/admin/pages/:pageId/builder" element={<PageBuilder />} />')

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    print("=" * 60)
    print("  FINALISATION PHASE 7 — FRONTEND")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable dans {BASE_DIR}")
        print("  Êtes-vous bien à la racine de nawa-shop-frontend ?")
        return

    print("\n1. Installation de Puck...")
    install_puck()

    print("\n2. Création de AdminPagesList.jsx...")
    write_file(
        os.path.join(SRC_DIR, "pages", "admin", "AdminPagesList.jsx"),
        ADMIN_PAGES_LIST,
    )

    print("\n3. Ajout des routes dans App.jsx...")
    add_routes_to_app()

    print("\n" + "=" * 60)
    print("  ✅ PHASE 7 — FRONTEND FINALISÉ")
    print("=" * 60)
    print("\nVérification :")
    print("  cd ..")
    print("  python verify_phase7.py")


if __name__ == "__main__":
    main()