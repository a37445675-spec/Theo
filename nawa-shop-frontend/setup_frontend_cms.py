"""
Script d'installation automatique du CMS Headless - Partie Frontend.
Usage : python setup_frontend_cms.py
"""
import os
import re
import shutil

SRC_DIR = os.path.join("src")
HEADER_PATH = os.path.join(SRC_DIR, "components", "Header.jsx")
APP_PATH = os.path.join(SRC_DIR, "App.jsx")
CMS_CONTEXT_PATH = os.path.join(SRC_DIR, "context", "CmsContext.jsx")


def backup_file(path):
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak")
        print(f"  [BACKUP] {path}.bak")


def create_cms_context():
    """Crée un CmsContext s'il n'existe pas."""
    if os.path.exists(CMS_CONTEXT_PATH):
        print("  [INFO] CmsContext.jsx existe déjà.")
        return

    os.makedirs(os.path.dirname(CMS_CONTEXT_PATH), exist_ok=True)

    context_code = '''import { createContext, useContext, useEffect, useState } from "react";
import axios from "axios";

const CmsContext = createContext(null);

export function CmsProvider({ children }) {
  const [cmsConfig, setCmsConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Récupère la config globale depuis l'API Django
    axios.get("/api/v1/cms/design-system/")
      .then((res) => {
        // L'API peut renvoyer une liste ou un objet unique
        const data = Array.isArray(res.data) ? res.data[0] : res.data;
        setCmsConfig(data);
      })
      .catch((err) => {
        console.warn("Impossible de charger la config CMS :", err.message);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <CmsContext.Provider value={{ cmsConfig, loading }}>
      {children}
    </CmsContext.Provider>
  );
}

export function useCmsConfig() {
  const context = useContext(CmsContext);
  if (!context) {
    throw new Error("useCmsConfig doit être utilisé dans un CmsProvider");
  }
  return context;
}
'''
    with open(CMS_CONTEXT_PATH, "w", encoding="utf-8") as f:
        f.write(context_code)
    print(f"  [OK] {CMS_CONTEXT_PATH} créé.")


def update_app_jsx():
    """Ajoute le CmsProvider dans App.jsx."""
    if not os.path.exists(APP_PATH):
        print(f"  [INFO] {APP_PATH} introuvable. Ajoutez CmsProvider manuellement.")
        return

    with open(APP_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "CmsProvider" in content:
        print("  [INFO] CmsProvider déjà présent dans App.jsx.")
        return

    backup_file(APP_PATH)

    # Ajouter l'import
    if "useCmsConfig" not in content:
        content = content.replace(
            'import { AuthProvider }',
            'import { CmsProvider } from "./context/CmsContext";\nimport { AuthProvider }'
        )
        # Fallback si le pattern n'existe pas
        if "CmsProvider" not in content:
            content = 'import { CmsProvider } from "./context/CmsContext";\n' + content

    # Envelopper l'application dans le CmsProvider
    # On cherche la première balise JSX de retour
    if "<AuthProvider>" in content:
        content = content.replace("<AuthProvider>", "<CmsProvider>\n      <AuthProvider>")
        content = content.replace("</AuthProvider>", "</AuthProvider>\n    </CmsProvider>")

    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] App.jsx mis à jour (CmsProvider ajouté).")


def update_header():
    """Remplace les emojis par des images dynamiques dans Header.jsx."""
    if not os.path.exists(HEADER_PATH):
        print(f"  [INFO] {HEADER_PATH} introuvable. Vérifiez le chemin.")
        return

    with open(HEADER_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "useCmsConfig" in content:
        print("  [INFO] Header.jsx utilise déjà le CMS.")
        return

    backup_file(HEADER_PATH)

    # 1. Ajouter l'import
    content = content.replace(
        'import { useCart } from "../context/CartContext.jsx";',
        'import { useCart } from "../context/CartContext.jsx";\nimport { useCmsConfig } from "../context/CmsContext.jsx";'
    )

    # 2. Ajouter le hook dans le composant
    content = content.replace(
        'const { itemCount } = useCart();',
        'const { itemCount } = useCart();\n  const { cmsConfig } = useCmsConfig();'
    )

    # 3. Remplacer l'emoji utilisateur par une image dynamique
    content = content.replace(
        '<span className="icon">👤</span>',
        '{cmsConfig?.icon_user ? <img src={cmsConfig.icon_user} alt="Compte" className="nav-icon-img" /> : <span className="icon">👤</span>}'
    )

    # 4. Remplacer l'emoji panier par une image dynamique
    content = content.replace(
        '<span className="icon">🛍</span>',
        '{cmsConfig?.icon_cart ? <img src={cmsConfig.icon_cart} alt="Panier" className="nav-icon-img" /> : <span className="icon">🛍</span>}'
    )

    with open(HEADER_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] Header.jsx mis à jour (icônes dynamiques).")


def update_favicon_in_index():
    """Ajoute la mise à jour dynamique du favicon via un hook dans App.jsx."""
    if not os.path.exists(APP_PATH):
        return

    with open(APP_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "updateFavicon" in content or "link[rel*='icon']" in content:
        print("  [INFO] Favicon dynamique déjà configuré.")
        return

    # Injecter un useEffect dans App() pour le favicon
    if "function App()" in content:
        favicon_hook = '''
  // Mise à jour dynamique du favicon depuis le CMS
  useEffect(() => {
    if (cmsConfig?.favicon) {
      const link = document.querySelector("link[rel*='icon']") || document.createElement("link");
      link.type = "image/x-icon";
      link.rel = "shortcut icon";
      link.href = cmsConfig.favicon;
      document.getElementsByTagName("head")[0].appendChild(link);
    }
  }, [cmsConfig]);
'''
        # Chercher le début de la fonction App et y insérer le hook
        content = re.sub(
            r'(function App\(\)\s*\{)',
            r'\1' + favicon_hook,
            content
        )
        with open(APP_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [OK] App.jsx : mise à jour dynamique du favicon ajoutée.")


def add_css_classes():
    """Ajoute les styles CSS pour les icônes dynamiques."""
    css_files = [
        os.path.join(SRC_DIR, "index.css"),
        os.path.join(SRC_DIR, "App.css"),
        os.path.join(SRC_DIR, "styles", "global.css"),
    ]
    css_content = """
/* Icônes dynamiques du CMS */
.nav-icon-img {
  width: 22px;
  height: 22px;
  object-fit: contain;
  display: block;
}
"""
    for css_path in css_files:
        if os.path.exists(css_path):
            with open(css_path, "r", encoding="utf-8") as f:
                content = f.read()
            if ".nav-icon-img" not in content:
                with open(css_path, "a", encoding="utf-8") as f:
                    f.write(css_content)
                print(f"  [OK] Styles ajoutés à {css_path}")
            return
    print("  [INFO] Aucun fichier CSS trouvé. Ajoutez .nav-icon-img manuellement.")


def main():
    print("===============================================")
    print("  Installation du CMS Headless - Frontend React")
    print("===============================================\n")

    print("1. Création du CmsContext...")
    create_cms_context()

    print("\n2. Mise à jour de App.jsx...")
    update_app_jsx()
    update_favicon_in_index()

    print("\n3. Mise à jour de Header.jsx...")
    update_header()

    print("\n4. Ajout des styles CSS...")
    add_css_classes()

    print("\n===============================================")
    print("  Terminé ! Vérifiez les fichiers .bak si besoin.")
    print("  Relancez 'npm run dev' pour voir les changements.")
    print("===============================================")


if __name__ == "__main__":
    main()
