"""
Setup de la route /pages/:id pour afficher un template Puck.

Usage : python setup_puck_page.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
PAGES_DIR = os.path.join(SRC_DIR, "pages")
APP_PATH = os.path.join(SRC_DIR, "App.jsx")
PUCK_PAGE_PATH = os.path.join(PAGES_DIR, "PuckPage.jsx")


# ============================================================
#  COMPOSANT PuckPage
# ============================================================

PUCK_PAGE_JSX = '''import { useEffect, useState } from "react";
import { Render } from "@puckeditor/core";
import { useParams } from "react-router-dom";
import { puckConfig } from "../puck/config";
import SeoHead from "../components/SeoHead";

/**
 * Affiche une page construite avec Puck.
 * Route : /pages/:pageId
 *
 * Charge les widgets depuis /api/v1/cms/widgets/?page=:pageId
 * et les rend avec le composant <Render /> de Puck.
 */
export default function PuckPage() {
  const { pageId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/v1/cms/widgets/?page=${pageId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((widgets) => {
        const list = Array.isArray(widgets) ? widgets : widgets.results || [];
        setData({
          content: list.map(widgetToPuck),
          root: { props: {} },
        });
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [pageId]);

  if (loading) {
    return (
      <div style={{ padding: "5rem 2rem", textAlign: "center", color: "#6B6259" }}>
        Chargement de la page...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: "5rem 2rem", textAlign: "center", color: "#DC2626" }}>
        <h2>Erreur</h2>
        <p>{error}</p>
        <p style={{ fontSize: "0.85rem", opacity: 0.7 }}>
          Vérifiez que la page ID "{pageId}" existe dans l'admin.
        </p>
      </div>
    );
  }

  if (!data || data.content.length === 0) {
    return (
      <div style={{ padding: "5rem 2rem", textAlign: "center", color: "#6B6259" }}>
        <h2>Page vide</h2>
        <p>Cette page ne contient aucun widget.</p>
        <p style={{ fontSize: "0.85rem", opacity: 0.7 }}>
          Ajoutez des widgets via l'éditeur : /admin/pages/{pageId}/builder
        </p>
      </div>
    );
  }

  return (
    <>
      <SeoHead
        title={`Page CMS #${pageId}`}
        description="Page éditée via l'éditeur Puck"
      />
      <Render config={puckConfig} data={data} />
    </>
  );
}

/**
 * Convertit un widget API en format Puck.
 */
function widgetToPuck(w) {
  return {
    type: w.widget_type || w.type,
    props: {
      id: `widget-${w.id}`,
      ...(w.content || {}),
      ...(w.style || {}),
      _children: (w.children || []).map(widgetToPuck),
    },
  };
}
'''


# ============================================================
#  FONCTIONS
# ============================================================

def write_file(path, content, label=None):
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


def patch_app_jsx():
    """Ajoute la route /pages/:pageId dans App.jsx."""
    if not os.path.exists(APP_PATH):
        print(f"  [ERREUR] {APP_PATH} introuvable")
        return False

    with open(APP_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "PuckPage" in content:
        print("  [SKIP] Route déjà présente dans App.jsx")
        return False

    shutil.copy2(APP_PATH, APP_PATH + ".bak")

    # 1. Ajouter l'import
    import_line = 'import PuckPage from "./pages/PuckPage.jsx";\n'
    first_import = re.search(r'^(import\s+.*\n)', content, re.MULTILINE)
    if first_import:
        content = (
            content[:first_import.end()]
            + import_line
            + content[first_import.end():]
        )

    # 2. Ajouter la route avant la route 404
    route_line = '                            <Route path="/pages/:pageId" element={<PuckPage />} />\n\n'
    marker = '<Route path="*" element={<NotFound />} />'
    if marker in content:
        content = content.replace(marker, route_line + "                            " + marker)
        print("  [OK] Route /pages/:pageId ajoutée avant NotFound")
    else:
        print("  [ATTENTION] Marker NotFound introuvable")
        return False

    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ============================================================
#  MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  SETUP ROUTE /pages/:pageId")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"\n  ❌ Dossier src/ introuvable")
        print("  → Êtes-vous à la racine de nawa-shop-frontend ?")
        return

    print("\n[1/2] Création du composant PuckPage.jsx...")
    write_file(PUCK_PAGE_PATH, PUCK_PAGE_JSX)

    print("\n[2/2] Ajout de la route dans App.jsx...")
    patch_app_jsx()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print("\n📋 PROCHAINES ÉTAPES :")
    print("  1. Vérifiez dans VS Code que tout est correct")
    print("  2. Ouvrez GitHub Desktop")
    print("  3. Summary : feat: add /pages/:id route for Puck")
    print("  4. Commit to main → Push origin")
    print("  5. Attendez Railway (~3 min)")
    print()
    print("🧪 TEST :")
    print("  1. Trouvez l'ID de votre template sur :")
    print("     https://theo-production-c85a.up.railway.app/admin/cms/pagetemplate/")
    print("  2. Ouvrez : https://sweet-communication-production-1afa.up.railway.app/pages/1")
    print("     (remplacez 1 par le vrai ID)")


if __name__ == "__main__":
    main()