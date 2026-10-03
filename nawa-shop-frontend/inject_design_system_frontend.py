"""
Injection automatique du module Design System - Frontend React.
Crée le ThemeContext et injecte les variables CSS.

Usage : python inject_design_system_frontend.py
"""
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")


THEME_CONTEXT_JSX = '''import { createContext, useContext, useEffect, useState } from "react";

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/v1/design-system/active/")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setTheme(data);
        applyTheme(data);
        loadGoogleFonts(data);
      })
      .catch((err) => console.warn("Erreur chargement design system:", err))
      .finally(() => setLoading(false));
  }, []);

  const applyTheme = (config) => {
    if (!config) return;
    const root = document.documentElement;
    const vars = {
      "--color-primary": config.color_primary,
      "--color-secondary": config.color_secondary,
      "--color-bg": config.color_background,
      "--color-surface": config.color_surface,
      "--color-text": config.color_text,
      "--color-text-muted": config.color_text_muted,
      "--color-accent": config.color_accent,
      "--color-error": config.color_error,
      "--color-success": config.color_success,
      "--font-heading": `"${config.font_heading}", serif`,
      "--font-body": `"${config.font_body}", sans-serif`,
      "--font-size-base": config.font_size_base,
      "--font-size-h1": config.font_size_h1,
      "--font-size-h2": config.font_size_h2,
      "--font-size-h3": config.font_size_h3,
      "--line-height": config.line_height,
      "--radius": config.border_radius,
      "--button-radius": config.button_radius,
      "--card-radius": config.card_radius,
      "--shadow-sm": config.shadow_sm,
      "--shadow-md": config.shadow_md,
      "--shadow-lg": config.shadow_lg,
    };
    Object.entries(vars).forEach(([key, value]) => {
      if (value) root.style.setProperty(key, value);
    });

    if (config.custom_css) {
      let styleEl = document.getElementById("cms-custom-css");
      if (!styleEl) {
        styleEl = document.createElement("style");
        styleEl.id = "cms-custom-css";
        document.head.appendChild(styleEl);
      }
      styleEl.textContent = config.custom_css;
    }
  };

  const loadGoogleFonts = (config) => {
    const fonts = [config.font_heading, config.font_body]
      .filter(Boolean)
      .map((f) => f.replace(/ /g, "+"))
      .join("&family=");
    if (!fonts) return;

    const linkId = "cms-google-fonts";
    let link = document.getElementById(linkId);
    if (!link) {
      link = document.createElement("link");
      link.id = linkId;
      link.rel = "stylesheet";
      document.head.appendChild(link);
    }
    link.href = `https://fonts.googleapis.com/css2?family=${fonts}&display=swap`;
  };

  return (
    <ThemeContext.Provider value={{ theme, loading }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme doit être utilisé dans un ThemeProvider");
  return ctx;
}
'''


CSS_VARIABLES = '''
/* ===== Variables CSS globales (remplies dynamiquement par le CMS) ===== */
:root {
  --color-primary: #C1652F;
  --color-secondary: #2F4A3C;
  --color-bg: #F7F0E4;
  --color-surface: #FFFFFF;
  --color-text: #221B15;
  --color-text-muted: #6B6259;
  --color-accent: #D4A843;
  --color-error: #DC2626;
  --color-success: #16A34A;
  --font-heading: "Fraunces", serif;
  --font-body: "Sora", sans-serif;
  --font-size-base: 16px;
  --font-size-h1: 3.5rem;
  --font-size-h2: 2.5rem;
  --font-size-h3: 1.75rem;
  --line-height: 1.6;
  --radius: 16px;
  --button-radius: 999px;
  --card-radius: 16px;
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.10);
  --shadow-lg: 0 10px 30px rgba(0,0,0,0.15);
}

body {
  background-color: var(--color-bg);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: var(--font-size-base);
  line-height: var(--line-height);
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  color: var(--color-text);
}

h1 { font-size: var(--font-size-h1); }
h2 { font-size: var(--font-size-h2); }
h3 { font-size: var(--font-size-h3); }

a { color: var(--color-primary); }

.btn-primary {
  background-color: var(--color-primary);
  color: white;
  border-radius: var(--button-radius);
  padding: 0.75rem 1.5rem;
  border: none;
  cursor: pointer;
  font-family: var(--font-body);
}

.card {
  background-color: var(--color-surface);
  border-radius: var(--card-radius);
  box-shadow: var(--shadow-md);
  padding: 1.5rem;
}
/* ===== Fin variables CMS ===== */
'''


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            existing = f.read()
        if existing.strip() == content.strip():
            print(f"  [SKIP] {os.path.relpath(path, BASE_DIR)}")
            return False
        shutil.copy2(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {os.path.relpath(path, BASE_DIR)}")
    return True


def append_css():
    """Ajoute les variables CSS dans le fichier de style principal."""
    candidates = [
        os.path.join(SRC_DIR, "index.css"),
        os.path.join(SRC_DIR, "App.css"),
        os.path.join(SRC_DIR, "styles", "global.css"),
        os.path.join(SRC_DIR, "styles.css"),
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                existing = f.read()
            if "--color-primary" in existing:
                print(f"  [SKIP] {os.path.relpath(path, BASE_DIR)} (variables déjà présentes)")
                return
            shutil.copy2(path, path + ".bak")
            with open(path, "a", encoding="utf-8") as f:
                f.write(CSS_VARIABLES)
            print(f"  [OK] variables CSS ajoutées à {os.path.relpath(path, BASE_DIR)}")
            return
    print("  [ATTENTION] Aucun fichier CSS trouvé. Créez src/index.css manuellement.")


def inject_theme_provider():
    """Enveloppe l'application avec ThemeProvider dans App.jsx."""
    app_path = os.path.join(SRC_DIR, "App.jsx")
    if not os.path.exists(app_path):
        app_path = os.path.join(SRC_DIR, "App.js")
    if not os.path.exists(app_path):
        print("  [ATTENTION] App.jsx introuvable. Enveloppez manuellement l'app :")
        print("              <ThemeProvider><App /></ThemeProvider>")
        return

    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "ThemeProvider" in content:
        print(f"  [SKIP] ThemeProvider déjà dans {os.path.basename(app_path)}")
        return

    shutil.copy2(app_path, app_path + ".bak")

    # Ajouter l'import
    import_line = 'import { ThemeProvider } from "./context/ThemeContext";\n'
    if "import " in content and content.strip().startswith("import"):
        content = import_line + content

    # Envelopper le return
    # Chercher le return principal
    match = re.search(r"(return\s*\()\s*(<[A-Za-z]+[^>]*>)", content)
    if match:
        content = content.replace(
            match.group(2),
            f"<ThemeProvider>\n      {match.group(2)}",
            1,
        )
        # Trouver la fermeture correspondante (approximatif)
        # Chercher la dernière balise JSX avant )
        # On va plutôt ajouter </ThemeProvider> avant la dernière parenthèse
        last_paren = content.rfind(")")
        if last_paren != -1:
            content = content[:last_paren] + "    </ThemeProvider>\n  " + content[last_paren:]
    else:
        print("  [ATTENTION] Impossible d'auto-envelopper. Enveloppez manuellement.")

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] ThemeProvider ajouté à {os.path.basename(app_path)}")


def main():
    print("=" * 60)
    print("  INJECTION DESIGN SYSTEM - FRONTEND")
    print("=" * 60)

    if not os.path.exists(SRC_DIR):
        print(f"\n  [ERREUR] Dossier src/ introuvable dans {BASE_DIR}")
        return

    print("\n1. Création du ThemeContext...")
    write_file(os.path.join(SRC_DIR, "context", "ThemeContext.jsx"), THEME_CONTEXT_JSX)

    print("\n2. Injection des variables CSS...")
    append_css()

    print("\n3. Enveloppement de l'App avec ThemeProvider...")
    inject_theme_provider()

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nVérifiez le résultat dans le navigateur :")
    print("  1. Le fond doit être crème (#F7F0E4)")
    print("  2. Les titres doivent être en Fraunces")
    print("  3. Ouvrez l'admin Django et changez color_primary")
    print("  4. Le site doit se mettre à jour au prochain rafraîchissement")


if __name__ == "__main__":
    main()