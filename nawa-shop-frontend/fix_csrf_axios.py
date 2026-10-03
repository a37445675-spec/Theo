"""
Corrige le CSRF pour axios (utilisé par cart.js, CartContext, etc.).
- Crée src/api/axiosConfig.js avec les intercepteurs
- L'importe automatiquement dans src/api/*.js
- L'importe dans main.jsx (pour config globale)

Usage : python fix_csrf_axios.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
API_DIR = os.path.join(SRC_DIR, "api")


# ============================================================
#              CONFIG AXIOS GLOBALE
# ============================================================

AXIOS_CONFIG = '''/**
 * Configuration axios globale pour NAWA Commerce.
 *
 * Gère automatiquement :
 *  - Le token CSRF (cookie csrftoken → header X-CSRFToken)
 *  - Le token JWT (localStorage → header Authorization)
 *  - Les credentials (cookies de session)
 *
 * Importer ce fichier UNE SEULE FOIS au boot (dans main.jsx).
 */

import axios from "axios";


// ============================================================
//  LECTURE DES TOKENS
// ============================================================

function getCsrfToken() {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(/(?:^|;\\s*)csrftoken=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : "";
}

function getJwtToken() {
  if (typeof localStorage === "undefined") return "";
  return localStorage.getItem("access_token") || "";
}


// ============================================================
//  CONFIGURATION DE BASE
// ============================================================

axios.defaults.withCredentials = true;
axios.defaults.headers.common["Accept"] = "application/json";
axios.defaults.headers.common["Content-Type"] = "application/json";


// ============================================================
//  INTERCEPTEUR DE REQUÊTE
// ============================================================

axios.interceptors.request.use(
  (config) => {
    const method = (config.method || "get").toLowerCase();
    const isUnsafe = ["post", "put", "patch", "delete"].includes(method);

    // JWT
    const jwt = getJwtToken();
    if (jwt) {
      config.headers = config.headers || {};
      config.headers["Authorization"] = `Bearer ${jwt}`;
    }

    // CSRF pour les méthodes d'écriture
    if (isUnsafe) {
      const token = getCsrfToken();
      if (token) {
        config.headers = config.headers || {};
        config.headers["X-CSRFToken"] = token;
      }
    }

    return config;
  },
  (error) => Promise.reject(error)
);


// ============================================================
//  BOOTSTRAP CSRF
// ============================================================

let csrfBootstrapped = false;

/**
 * À appeler au boot pour garantir qu'un cookie CSRF est présent.
 */
export async function bootstrapCsrf() {
  if (csrfBootstrapped) return getCsrfToken();
  try {
    const res = await axios.get("/api/v1/csrf/");
    csrfBootstrapped = true;
    return res.data?.csrfToken || getCsrfToken();
  } catch (err) {
    console.warn("Bootstrap CSRF échoué :", err?.message);
    return "";
  }
}


export default axios;
'''


# ============================================================
#              PATCH DES FICHIERS
# ============================================================

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_axios_config():
    """Crée src/api/axiosConfig.js."""
    ensure_dir(API_DIR)
    path = os.path.join(API_DIR, "axiosConfig.js")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if "bootstrapCsrf" in f.read():
                print("  [SKIP] axiosConfig.js existe déjà")
                return False
        shutil.copy2(path, path + ".bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(AXIOS_CONFIG)
    print("  [OK] src/api/axiosConfig.js créé")
    return True


def patch_main_entry():
    """Importe axiosConfig dans le point d'entrée (main.jsx / index.jsx)."""
    candidates = [
        os.path.join(SRC_DIR, "main.jsx"),
        os.path.join(SRC_DIR, "main.js"),
        os.path.join(SRC_DIR, "index.jsx"),
        os.path.join(SRC_DIR, "index.js"),
    ]
    main_path = None
    for c in candidates:
        if os.path.exists(c):
            main_path = c
            break

    if not main_path:
        print("  [ATTENTION] main.jsx introuvable")
        return False

    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "axiosConfig" in content:
        print(f"  [SKIP] {os.path.basename(main_path)} déjà patché")
        return False

    shutil.copy2(main_path, main_path + ".bak")

    import_line = 'import "./api/axiosConfig"; // Config CSRF + JWT globale\n'
    # Insérer au tout début
    content = import_line + content

    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {os.path.basename(main_path)} : import axiosConfig ajouté")
    return True


def patch_app_bootstrap():
    """Appelle bootstrapCsrf() au démarrage dans App.jsx."""
    app_path = os.path.join(SRC_DIR, "App.jsx")
    if not os.path.exists(app_path):
        print("  [SKIP] App.jsx introuvable")
        return False

    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "bootstrapCsrf" in content:
        print("  [SKIP] bootstrapCsrf déjà dans App.jsx")
        return False

    # Vérifier que useEffect est importé
    has_effect = "useEffect" in content
    has_react_import = re.search(r'import\s*\{[^}]*\}\s*from\s*["\']react["\']', content)

    shutil.copy2(app_path, app_path + ".bak")

    # 1. Import bootstrapCsrf
    import_line = 'import { bootstrapCsrf } from "./api/axiosConfig";\n'
    first_import = re.search(r'^import\s+', content, re.MULTILINE)
    if first_import:
        content = (
            content[:first_import.start()]
            + import_line
            + content[first_import.start():]
        )

    # 2. S'assurer que useEffect est importé
    if not has_effect:
        # Ajouter useEffect à l'import React
        react_match = re.search(
            r'import\s*\{([^}]+)\}\s*from\s*["\']react["\']',
            content,
        )
        if react_match:
            names = react_match.group(1).strip()
            if "useEffect" not in names:
                new_names = names + ", useEffect"
                content = content.replace(react_match.group(0), f'import {{{new_names}}} from "react";')
        else:
            # Ajouter un nouvel import
            content = 'import { useEffect } from "react";\n' + content

    # 3. Ajouter le useEffect dans App()
    app_pattern = re.search(
        r'(export\s+default\s+function\s+App\s*\(\s*\)\s*\{|function\s+App\s*\(\s*\)\s*\{)',
        content,
    )
    if app_pattern:
        insert_pos = app_pattern.end()
        hook = """

  // Bootstrap CSRF au démarrage
  useEffect(() => {
    bootstrapCsrf();
  }, []);
"""
        content = content[:insert_pos] + hook + content[insert_pos:]
        print("  [OK] App.jsx : bootstrapCsrf() ajouté dans App()")
    else:
        print("  [ATTENTION] Impossible de trouver App() dans App.jsx")

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  CORRECTION CSRF POUR AXIOS")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable")
        return

    print("\n[1/3] Création de src/api/axiosConfig.js...")
    write_axios_config()

    print("\n[2/3] Import dans le point d'entrée...")
    patch_main_entry()

    print("\n[3/3] Bootstrap CSRF dans App.jsx...")
    patch_app_bootstrap()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print("\nÉtapes suivantes :")
    print("  1. Vider le cache Vite :")
    print("     Remove-Item -Recurse -Force node_modules\\.vite")
    print("  2. Relancer : npm run dev")
    print("  3. Vider le cache navigateur : Ctrl + Shift + R")
    print("  4. Tester : ajouter un produit au panier")


if __name__ == "__main__":
    main()
