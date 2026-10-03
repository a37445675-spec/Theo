"""
Corrige le CSRF côté frontend :
- Crée un client API universel (src/utils/apiClient.js)
- Patche AddToCart et autres widgets pour utiliser apiFetch()
- Appelle /api/v1/csrf/ au démarrage de l'app

Usage : python fix_csrf_frontend.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
UTILS_DIR = os.path.join(SRC_DIR, "utils")


# ============================================================
#                    UTILITAIRE API
# ============================================================

API_CLIENT = '''/**
 * Client API universel — NAWA Commerce.
 *
 * Gère automatiquement :
 *  - Le token CSRF (cookie + header X-CSRFToken)
 *  - Le token JWT si présent dans localStorage
 *  - Les credentials (cookies de session)
 *  - Le parsing JSON + gestion d'erreurs
 *
 * Usage :
 *   import { apiFetch } from "../utils/apiClient";
 *   const data = await apiFetch("/api/v1/cart/lines/", {
 *     method: "POST",
 *     body: { product: 1, quantity: 2 },
 *   });
 */

const API_BASE = ""; // Les URLs incluent déjà /api/v1/


// ============================================================
//  LECTURE DES TOKENS
// ============================================================

export function getCsrfToken() {
  if (typeof document === "undefined") return "";
  const match = document.cookie.match(/(?:^|;\\s*)csrftoken=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : "";
}

export function getJwtToken() {
  if (typeof localStorage === "undefined") return "";
  return localStorage.getItem("access_token") || "";
}


// ============================================================
//  BOOTSTRAP CSRF
// ============================================================

let csrfBootstrapped = false;

/**
 * Appelé au boot de l'app pour obtenir le cookie CSRF.
 * Idempotent : ne fait qu'un seul appel par session.
 */
export async function bootstrapCsrf() {
  if (csrfBootstrapped) return getCsrfToken();
  try {
    const res = await fetch("/api/v1/csrf/", {
      credentials: "include",
      headers: { Accept: "application/json" },
    });
    if (res.ok) {
      const data = await res.json();
      csrfBootstrapped = true;
      return data.csrfToken || getCsrfToken();
    }
  } catch (err) {
    console.warn("Bootstrap CSRF échoué :", err);
  }
  return "";
}


// ============================================================
//  API FETCH
// ============================================================

export async function apiFetch(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();
  const isUnsafe = ["POST", "PUT", "PATCH", "DELETE"].includes(method);

  const headers = {
    Accept: "application/json",
    ...(options.headers || {}),
  };

  // Content-Type si body JSON (et pas déjà défini)
  if (options.body && !headers["Content-Type"] && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  // JWT
  const jwt = getJwtToken();
  if (jwt) {
    headers["Authorization"] = `Bearer ${jwt}`;
  }

  // CSRF pour les méthodes d'écriture
  if (isUnsafe) {
    let token = getCsrfToken();
    if (!token) {
      token = await bootstrapCsrf();
    }
    if (token) {
      headers["X-CSRFToken"] = token;
    }
  }

  // Body
  let body = options.body;
  if (body && typeof body === "object" && !(body instanceof FormData)) {
    body = JSON.stringify(body);
  }

  const url = path.startsWith("http") ? path : (API_BASE + path);

  const res = await fetch(url, {
    ...options,
    method,
    headers,
    body,
    credentials: "include",
  });

  // Parsing
  let data = null;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    try { data = await res.json(); } catch { data = null; }
  } else {
    try { data = await res.text(); } catch { data = null; }
  }

  if (!res.ok) {
    const err = new Error(
      (data && (data.detail || data.message)) || `HTTP ${res.status}`
    );
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}


// ============================================================
//  RACCOURCIS
// ============================================================

export const api = {
  get: (path, opts) => apiFetch(path, { ...opts, method: "GET" }),
  post: (path, body, opts) => apiFetch(path, { ...opts, method: "POST", body }),
  put: (path, body, opts) => apiFetch(path, { ...opts, method: "PUT", body }),
  patch: (path, body, opts) => apiFetch(path, { ...opts, method: "PATCH", body }),
  delete: (path, opts) => apiFetch(path, { ...opts, method: "DELETE" }),
};
'''


# ============================================================
#              PATCH DES WIDGETS
# ============================================================

# Pattern pour trouver les fetch() dans les widgets
FETCH_PATTERN = re.compile(
    r'await\s+fetch\(\s*["\'](/api/v1/[^"\']+)["\']\s*,\s*\{([^}]*)\}\s*\)',
    re.DOTALL,
)


def patch_widget_file(path):
    """Remplace les fetch() par apiFetch() dans un widget."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 1. Ajouter l'import apiFetch si pas présent
    if "apiFetch" not in content and "from \"../utils/apiClient\"" not in content:
        # Détecter le niveau d'import
        depth = path.count(os.sep) - path.split(os.sep).index("src") - 1
        rel = "../" * depth + "utils/apiClient"
        import_line = f'import {{ apiFetch }} from "{rel}";\n'
        # Ajouter après le premier import
        first_import = re.search(r'^import\s+', content, re.MULTILINE)
        if first_import:
            content = (
                content[:first_import.start()]
                + import_line
                + content[first_import.start():]
            )

    # 2. Remplacer les fetch POST/PUT/PATCH/DELETE par apiFetch
    def replacer(match):
        url = match.group(1)
        options = match.group(2)

        # Extraire la méthode
        method_match = re.search(r'method:\s*["\'](\w+)["\']', options)
        method = method_match.group(1) if method_match else "GET"

        # N'appliquer que pour les méthodes non-safe
        if method not in ("POST", "PUT", "PATCH", "DELETE"):
            return match.group(0)

        # Extraire le body
        body_match = re.search(r'body:\s*(JSON\.stringify\([^)]+\))', options, re.DOTALL)
        body = body_match.group(1) if body_match else None

        # Construire le nouvel appel
        if body:
            # Retirer le JSON.stringify
            inner = re.sub(r'^JSON\.stringify\((.*)\)$', r'\1', body, flags=re.DOTALL).strip()
            return f'await apiFetch("{url}", {{\n          method: "{method}",\n          body: {inner},\n        }})'
        else:
            return f'await apiFetch("{url}", {{ method: "{method}" }})'

    content = FETCH_PATTERN.sub(replacer, content)

    if content == original:
        return False

    shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True


def patch_app_bootstrap():
    """Ajoute bootstrapCsrf() au démarrage dans App.jsx."""
    app_path = os.path.join(SRC_DIR, "App.jsx")
    if not os.path.exists(app_path):
        print(f"  [SKIP] App.jsx introuvable")
        return False

    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "bootstrapCsrf" in content:
        print("  [SKIP] bootstrapCsrf déjà présent dans App.jsx")
        return False

    shutil.copy2(app_path, app_path + ".bak")

    # 1. Ajouter l'import
    import_line = 'import { bootstrapCsrf } from "./utils/apiClient";\n'
    first_import = re.search(r'^import\s+', content, re.MULTILINE)
    if first_import:
        content = (
            content[:first_import.start()]
            + import_line
            + content[first_import.start():]
        )

    # 2. Ajouter le useEffect dans App()
    # Chercher "export default function App() {" ou "function App() {"
    app_pattern = re.search(
        r'(export\s+default\s+function\s+App\(\)\s*\{|function\s+App\(\)\s*\{)',
        content,
    )
    if app_pattern:
        insert_pos = app_pattern.end()
        hook = """
  // Bootstrap CSRF au démarrage (pour le panier anonyme)
  useEffect(() => {
    bootstrapCsrf();
  }, []);
"""
        content = content[:insert_pos] + hook + content[insert_pos:]

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] App.jsx : bootstrapCsrf() ajouté")
    return True


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  CORRECTION CSRF — FRONTEND")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"  [ERREUR] src/ introuvable")
        return

    print("\n[1/3] Création de src/utils/apiClient.js...")
    ensure_dir = os.makedirs
    ensure_dir(UTILS_DIR, exist_ok=True)
    api_path = os.path.join(UTILS_DIR, "apiClient.js")
    if os.path.exists(api_path):
        with open(api_path, "r", encoding="utf-8") as f:
            if "export async function apiFetch" in f.read():
                print(f"  [SKIP] apiClient.js existe déjà")
            else:
                shutil.copy2(api_path, api_path + ".bak")
                with open(api_path, "w", encoding="utf-8") as f:
                    f.write(API_CLIENT)
                print(f"  [OK] apiClient.js mis à jour")
    else:
        with open(api_path, "w", encoding="utf-8") as f:
            f.write(API_CLIENT)
        print(f"  [OK] src/utils/apiClient.js créé")

    print("\n[2/3] Patch des widgets...")
    widgets_dir = os.path.join(SRC_DIR, "puck", "widgets")
    patched = 0
    for f_name in os.listdir(widgets_dir):
        if not f_name.endswith(".jsx") or f_name.endswith(".bak"):
            continue
        path = os.path.join(widgets_dir, f_name)
        if patch_widget_file(path):
            print(f"  [OK] {f_name}")
            patched += 1
    if patched == 0:
        print("  [SKIP] Aucun widget à patcher")

    print("\n[3/3] Bootstrap CSRF dans App.jsx...")
    patch_app_bootstrap()

    print()
    print("=" * 60)
    print("  ✅ TERMINÉ")
    print("=" * 60)
    print("\nÉtapes suivantes :")
    print("  1. Redémarrer le backend (pour prendre en compte la vue CSRF)")
    print("  2. Redémarrer le frontend : npm run dev")
    print("  3. Tester : ajouter un produit au panier")


if __name__ == "__main__":
    main()
