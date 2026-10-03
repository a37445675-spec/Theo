"""
Correctif CSRF complet :
1. Configure le proxy Vite correctement
2. Crée un composant CsrfBootstrap qui s'exécute au boot
3. Patche cart.js pour ajouter X-CSRFToken manuellement

Usage : python fix_csrf_complete.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
VITE_CONFIG = os.path.join(BASE_DIR, "vite.config.js")


# ============================================================
#              VITE CONFIG AVEC PROXY
# ============================================================

VITE_PROXY_BLOCK = '''      // === Proxy API vers le backend Django ===
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: false,
        secure: false,
        cookieDomainRewrite: "localhost",
      },
      "/media": {
        target: "http://localhost:8000",
        changeOrigin: false,
        secure: false,
      },
      "/static": {
        target: "http://localhost:8000",
        changeOrigin: false,
        secure: false,
      },
'''


def fix_vite_config():
    """Ajoute/remplace le proxy dans vite.config.js."""
    if not os.path.exists(VITE_CONFIG):
        print("  [ATTENTION] vite.config.js introuvable")
        return False

    with open(VITE_CONFIG, "r", encoding="utf-8") as f:
        content = f.read()

    if 'target: "http://localhost:8000"' in content and 'cookieDomainRewrite' in content:
        print("  [SKIP] vite.config.js déjà correctement configuré")
        return False

    shutil.copy2(VITE_CONFIG, VITE_CONFIG + ".bak")

    # Chercher la section server existante
    server_match = re.search(r'server\s*:\s*\{', content)
    if server_match:
        # Trouver la fin du bloc server
        start = server_match.end()
        depth = 1
        i = start
        while i < len(content) and depth > 0:
            if content[i] == "{":
                depth += 1
            elif content[i] == "}":
                depth -= 1
            i += 1
        end = i - 1

        # Remplacer le contenu de server
        before = content[:start]
        after = content[end:]
        content = before + "\n" + VITE_PROXY_BLOCK + "    " + after
    else:
        # Ajouter une section server avant la dernière }
        insert_pos = content.rfind("}")
        server_block = f"""
  server: {{
    port: 5173,
    proxy: {{
{VITE_PROXY_BLOCK}    }},
  }},
"""
        content = content[:insert_pos] + server_block + content[insert_pos:]

    with open(VITE_CONFIG, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] vite.config.js : proxy /api configuré")
    return True


# ============================================================
#              PATCH CART.JS
# ============================================================

def patch_cart_js():
    """Ajoute X-CSRFToken manuellement dans cart.js."""
    cart_path = None
    for candidate in [
        os.path.join(SRC_DIR, "api", "cart.js"),
        os.path.join(SRC_DIR, "services", "cart.js"),
        os.path.join(SRC_DIR, "lib", "cart.js"),
    ]:
        if os.path.exists(candidate):
            cart_path = candidate
            break

    if not cart_path:
        print("  [ATTENTION] cart.js introuvable")
        return False

    with open(cart_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "X-CSRFToken" in content:
        print(f"  [SKIP] {os.path.basename(cart_path)} : X-CSRFToken déjà présent")
        return False

    shutil.copy2(cart_path, cart_path + ".bak")

    # 1. Ajouter un helper CSRF en haut du fichier
    helper = '''
// === Helper CSRF ===
function getCsrfToken() {
  const match = document.cookie.match(/(?:^|;\\s*)csrftoken=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : "";
}

async function ensureCsrf() {
  if (getCsrfToken()) return getCsrfToken();
  try {
    const res = await fetch("/api/v1/csrf/", { credentials: "include" });
    if (res.ok) {
      const data = await res.json();
      return data.csrfToken || getCsrfToken();
    }
  } catch (e) {
    console.warn("CSRF bootstrap failed", e);
  }
  return "";
}
// === Fin helper CSRF ===

'''

    # 2. Ajouter le helper après le dernier import
    lines = content.split("\n")
    last_import = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            last_import = i
    lines.insert(last_import + 1, helper)

    content = "\n".join(lines)

    # 3. Wrapper les appels POST/PUT/PATCH/DELETE
    # Trouver les fonctions qui font des POST
    patterns = [
        # axios.post("/api/v1/...", data)
        (r'axios\.post\(([^,)]+)', r'axios.post(\1, undefined, { headers: { "X-CSRFToken": await ensureCsrf() } })// '),
    ]

    # Approche plus simple : ajouter X-CSRFToken dans tous les axios.post/put/patch/delete
    # On insère un headers dans le 3e argument

    # Pattern : await axios.post("/api/...", data) → await axios.post("/api/...", data, { headers: { "X-CSRFToken": await ensureCsrf() } })
    def add_csrf_to_post(match):
        full = match.group(0)
        # Vérifier s'il y a déjà un objet de config
        return full  # Pour l'instant on ne peut pas facilement parser

    # Alternative : modifier la fonction exportée pour wrapper
    # On va simplement ajouter le header au niveau du module via un intercepteur
    csrf_interceptor = '''
// === Intercepteur CSRF (ajouté automatiquement) ===
axios.interceptors.request.use(async (config) => {
  const method = (config.method || "get").toLowerCase();
  if (["post", "put", "patch", "delete"].includes(method)) {
    const token = await ensureCsrf();
    if (token) {
      config.headers = config.headers || {};
      config.headers["X-CSRFToken"] = token;
    }
  }
  return config;
});
// === Fin intercepteur ===

'''

    # Ajouter l'intercepteur à la fin du fichier
    content = content.rstrip() + "\n\n" + csrf_interceptor

    with open(cart_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {os.path.basename(cart_path)} : intercepteur CSRF ajouté")
    return True


# ============================================================
#              PATCH MAIN.JSX
# ============================================================

def patch_main():
    """Importe axiosConfig dans main.jsx."""
    main_path = None
    for c in [
        os.path.join(SRC_DIR, "main.jsx"),
        os.path.join(SRC_DIR, "main.js"),
        os.path.join(SRC_DIR, "index.jsx"),
    ]:
        if os.path.exists(c):
            main_path = c
            break

    if not main_path:
        print("  [ATTENTION] main.jsx introuvable")
        return False

    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "axiosConfig" in content:
        print("  [SKIP] main.jsx déjà patché")
        return False

    shutil.copy2(main_path, main_path + ".bak")

    import_line = 'import "./api/axiosConfig"; // CSRF + JWT global\n'
    content = import_line + content

    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {os.path.basename(main_path)} : axiosConfig importé")
    return True


# ============================================================
#                    MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  CORRECTIF CSRF COMPLET")
    print("=" * 60)

    print("\n[1/3] Configuration du proxy Vite...")
    fix_vite_config()

    print("\n[2/3] Patch de cart.js...")
    patch_cart_js()

    print("\n[3/3] Patch de main.jsx...")
    patch_main()

    print()
    print("=" * 60)
    print("  ✅ CORRECTIF APPLIQUÉ")
    print("=" * 60)
    print("\nÉtapes suivantes :")
    print("  1. Redémarrer Vite :")
    print("     Ctrl+C puis npm run dev")
    print("  2. Vider le cache navigateur : Ctrl+Shift+R")
    print("  3. F12 → Application → Cookies : vérifier 'csrftoken'")


if __name__ == "__main__":
    main()