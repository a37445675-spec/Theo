"""
Répare cart.js :
1. Importe axios s'il manque
2. Vérifie que l'intercepteur est bien présent
3. Nettoie les éventuels doublons

Usage : python fix_axios_cart.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")


def find_cart_file():
    """Trouve le fichier cart.js (peut être à plusieurs endroits)."""
    candidates = [
        os.path.join(SRC_DIR, "api", "cart.js"),
        os.path.join(SRC_DIR, "services", "cart.js"),
        os.path.join(SRC_DIR, "lib", "cart.js"),
        os.path.join(SRC_DIR, "utils", "cart.js"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    # Recherche récursive
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        if "cart.js" in files:
            return os.path.join(root, "cart.js")
    return None


def fix_cart_file(path):
    print(f"  Fichier trouvé : {os.path.relpath(path, BASE_DIR)}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 1. Vérifier l'import axios
    has_axios_import = bool(re.search(
        r'^\s*import\s+axios\s+from\s+["\']axios["\']',
        content, re.MULTILINE
    ))

    if not has_axios_import:
        # Ajouter en haut du fichier
        content = 'import axios from "axios";\n' + content
        print("  [OK] Import axios ajouté")
    else:
        print("  [SKIP] axios déjà importé")

    # 2. Vérifier que getCsrfToken/ensureCsrf sont définis AVANT utilisation
    # Trouver la ligne de l'intercepteur (à la fin)
    interceptor_pattern = re.compile(
        r'axios\.interceptors\.request\.use\(',
        re.MULTILINE,
    )

    if interceptor_pattern.search(content):
        # Vérifier que ensureCsrf est défini
        if "function ensureCsrf" not in content and "const ensureCsrf" not in content:
            # Ajouter le helper avant l'intercepteur
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
// === Fin helper ===

'''
            # Insérer avant l'intercepteur
            idx = interceptor_pattern.search(content).start()
            content = content[:idx] + helper + content[idx:]
            print("  [OK] Helper CSRF ajouté")

    # 3. Supprimer les doublons d'intercepteurs
    interceptor_blocks = list(re.finditer(
        r'// === Intercepteur CSRF.*?// === Fin intercepteur ===',
        content, re.DOTALL
    ))
    if len(interceptor_blocks) > 1:
        print(f"  [ATTENTION] {len(interceptor_blocks)} intercepteurs détectés, on garde le dernier")
        # Supprimer tous sauf le dernier
        for block in reversed(interceptor_blocks[:-1]):
            content = content[:block.start()] + content[block.end():]
        print(f"  [OK] Doublons retirés")

    if content == original:
        print("  Aucune modification nécessaire")
        return False

    # Backup
    shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] Fichier mis à jour")
    return True


def main():
    print("=" * 60)
    print("  CORRECTION DE cart.js (axios undefined)")
    print("=" * 60)
    print()

    path = find_cart_file()
    if not path:
        print("  [ERREUR] Aucun fichier cart.js trouvé")
        return

    fixed = fix_cart_file(path)

    print()
    print("=" * 60)
    if fixed:
        print("  ✅ CORRECTION APPLIQUÉE")
    else:
        print("  Rien à corriger")
    print("=" * 60)
    print()
    print("Étapes suivantes :")
    print("  1. Remove-Item -Recurse -Force node_modules\\.vite")
    print("  2. npm run dev")
    print("  3. Ctrl+Shift+R dans le navigateur")


if __name__ == "__main__":
    main()