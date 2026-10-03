"""
Audit complet du frontend NAWA Commerce.
Vérifie les widgets, la syntaxe, les imports, les routes et les contextes.

Usage : python frontend_audit.py
"""
import os
import re
import json
import sys
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
WIDGETS_DIR = os.path.join(SRC_DIR, "puck", "widgets")
HOOKS_DIR = os.path.join(SRC_DIR, "puck", "hooks")
CONTEXT_DIR = os.path.join(SRC_DIR, "context")
CONFIG_PATH = os.path.join(SRC_DIR, "puck", "config.jsx")
APP_PATH = os.path.join(SRC_DIR, "App.jsx")


# ============================================================
#              INVENTAIRE ATTENDU
# ============================================================

EXPECTED_WIDGETS = {
    "P7 — Base": [
        "Section", "Columns", "Divider", "Spacer",
        "Heading", "Text", "Image", "Button", "IconBox",
        "CTA", "Testimonial", "PricingTable", "Countdown", "ProgressBar",
        "Gallery", "Carousel", "Video", "SocialShare",
        "Accordion", "Tabs", "FlipBox",
    ],
    "P8 — Média & Interactifs": [
        "CarouselLoop", "CarouselMedia", "CarouselNested", "Slides", "VideoPlaylist",
        "TestimonialCarousel", "LottieWidget", "Hotspot", "TableOfContents",
        "Counter", "ProgressReview", "CodeHighlight", "Portfolio", "Review",
    ],
    "P9 — Marketing & Social": [
        "FacebookPage", "FacebookButton", "FacebookEmbed", "FacebookComments",
        "PayPalButton", "StripeButton",
        "MegaMenu", "OffCanvas", "MenuCart", "SocialShareExtended",
        "WhatsAppFloat", "NewsletterPopup", "CookieBanner",
    ],
    "P10 — Dynamiques": [
        "PostTitle", "PostContent", "PostExcerpt", "PostInfo",
        "PostNavigation", "PostComments", "AuthorBox",
        "ArchiveTitle", "ArchivePosts", "Breadcrumbs", "LoopGrid", "LoopCarousel",
        "Taxonomy", "SiteLogo", "SiteTitle", "SitelinkSearch", "PostPortfolio",
    ],
    "P11 — E-commerce": [
        "ProductTitle", "ProductImages", "ProductPrice", "AddToCart",
        "ProductRating", "ProductStock", "ProductMeta", "ShortDescription",
        "ProductContent", "ProductDataTabs", "ProductGrid", "Upsells",
        "RelatedProducts", "ProductCategories",
        "Cart", "Checkout", "PurchaseSummary", "MyAccount",
        "WcBreadcrumbs", "MenuCartExtended",
    ],
}

EXPECTED_HOOKS = [
    "useDynamicContext.jsx",
    "useProductContext.jsx",
]

EXPECTED_CONTEXTS = [
    "ThemeContext.jsx",
    "CmsContext.jsx",
    "AuthContext.jsx",
    "CartContext.jsx",
    "NavigationContext.jsx",
    "TranslationContext.jsx",
    "FeatureFlagsContext.jsx",
]

EXPECTED_ROUTES = [
    "/admin/pages",
    "/admin/pages/:pageId/builder",
    "/journal",
    "/produit/:slug",
    "/panier",
    "/commande",
    "/compte",
]


# ============================================================
#                    ANALYSEURS
# ============================================================

def extract_widget_names():
    """Extrait tous les noms de widgets depuis les exports et le config."""
    names = set()

    # 1. Exports depuis widgets/*.jsx
    if os.path.exists(WIDGETS_DIR):
        pat = re.compile(r'export\s+const\s+(\w+)\s*=\s*\{')
        for f in os.listdir(WIDGETS_DIR):
            if f.endswith(".jsx") and not f.endswith(".bak"):
                with open(os.path.join(WIDGETS_DIR, f), encoding="utf-8") as fh:
                    for m in pat.finditer(fh.read()):
                        names.add(m.group(1))

    # 2. Déclarations locales dans config.jsx
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            c = f.read()
        for m in re.finditer(r'^const\s+(\w+)\s*=\s*\{', c, re.MULTILINE):
            names.add(m.group(1))
        # Imports
        for m in re.finditer(r'import\s*\{([^}]+)\}\s*from\s*["\']\./widgets/', c):
            for x in m.group(1).split(","):
                x = x.strip()
                if x and re.match(r'^\w+$', x):
                    names.add(x)

    return names


def extract_config_components():
    """Extrait les composants déclarés dans puckConfig.components."""
    if not os.path.exists(CONFIG_PATH):
        return set()
    with open(CONFIG_PATH, encoding="utf-8") as f:
        c = f.read()
    m = re.search(r'components:\s*\{', c)
    if not m:
        return set()
    s = m.end()
    d = 1
    i = s
    while i < len(c) and d > 0:
        if c[i] == "{":
            d += 1
        elif c[i] == "}":
            d -= 1
        i += 1
    names = set()
    for line in c[s:i-1].split("\n"):
        line = re.sub(r'//.*$', '', line)
        line = re.sub(r'/\*.*?\*/', '', line, flags=re.DOTALL)
        for p in line.split(","):
            p = p.strip()
            if re.match(r'^\w+$', p):
                names.add(p)
    return names


def check_jsx_syntax(path):
    """Vérifie qu'un fichier JSX ne contient pas d'erreurs évidentes."""
    errors = []
    try:
        with open(path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"Lecture impossible : {e}"]

    # Vérifier l'équilibre des accolades
    opens = content.count("{") - content.count("}")
    if opens != 0:
        errors.append(f"Accolades déséquilibrées : {opens:+d}")

    # Vérifier l'équilibre des parenthèses
    parens = content.count("(") - content.count(")")
    if parens != 0:
        errors.append(f"Parenthèses déséquilibrées : {parens:+d}")

    # Vérifier les imports cassés (regex du bug précédent)
    if re.search(r'\.(get|post|put|patch|delete)\s*\(\s*/api/', content):
        errors.append("Import API sans guillemet (bug connu)")

    return errors


def check_routes():
    """Vérifie les routes déclarées dans App.jsx."""
    if not os.path.exists(APP_PATH):
        return set()
    with open(APP_PATH, encoding="utf-8") as f:
        content = f.read()
    routes = set()
    for m in re.finditer(r'path="([^"]+)"', content):
        routes.add(m.group(1))
    return routes


def check_hooks():
    """Vérifie que les hooks sont correctement exportés."""
    hooks = set()
    if not os.path.exists(HOOKS_DIR):
        return hooks
    for f in os.listdir(HOOKS_DIR):
        if f.endswith(".jsx") and not f.endswith(".bak"):
            hooks.add(f)
    return hooks


def check_contexts():
    """Vérifie que les contextes sont présents."""
    contexts = set()
    if not os.path.exists(CONTEXT_DIR):
        return contexts
    for f in os.listdir(CONTEXT_DIR):
        if f.endswith(".jsx") and not f.endswith(".bak"):
            contexts.add(f)
    return contexts


# ============================================================
#                    RAPPORT
# ============================================================

def print_header(title):
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subheader(title):
    print()
    print("-" * 70)
    print(f"  {title}")
    print("-" * 70)


def test_widgets():
    print_header("1. INVENTAIRE DES WIDGETS")
    all_n = extract_widget_names()
    cfg = extract_config_components()
    print(f"\n  Widgets trouvés : {len(all_n)}")
    print(f"  Dans config     : {len(cfg)}")

    total = 0
    found = 0
    missing = []
    for phase, widgets in EXPECTED_WIDGETS.items():
        phase_found = 0
        for w in widgets:
            total += 1
            if w in all_n and w in cfg:
                found += 1
                phase_found += 1
            else:
                missing.append(f"{phase} / {w}")
        status = "✅" if phase_found == len(widgets) else "⚠️ "
        print(f"  {status} {phase:<30} {phase_found}/{len(widgets)}")

    print()
    print(f"  TOTAL : {found}/{total} widgets opérationnels")
    if missing:
        print(f"\n  Manquants ({len(missing)}) :")
        for m in missing[:10]:
            print(f"    - {m}")
        if len(missing) > 10:
            print(f"    ... et {len(missing)-10} autres")
    return found == total


def test_syntax():
    print_header("2. SYNTAXE JSX")
    if not os.path.exists(SRC_DIR):
        print("  ❌ src/ introuvable")
        return False

    total = 0
    errors = []
    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        for f in files:
            if not f.endswith((".js", ".jsx")):
                continue
            total += 1
            path = os.path.join(root, f)
            errs = check_jsx_syntax(path)
            for e in errs:
                errors.append((os.path.relpath(path, BASE_DIR), e))

    print(f"  Fichiers analysés : {total}")
    if errors:
        print(f"  ⚠️  {len(errors)} problème(s) détecté(s) :")
        for path, err in errors[:20]:
            print(f"    - {path} : {err}")
        return False
    print("  ✅ Aucune erreur de syntaxe détectée")
    return True


def test_imports():
    print_header("3. IMPORTS / EXPORTS")
    total = 0
    errors = []

    for root, dirs, files in os.walk(SRC_DIR):
        dirs[:] = [d for d in dirs if d not in ("node_modules", "dist", ".vite", "build")]
        for f in files:
            if not f.endswith((".js", ".jsx")):
                continue
            total += 1
            path = os.path.join(root, f)
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            # Chercher les imports relatifs cassés (fichier manquant)
            for m in re.finditer(r'from\s+["\']\.{1,2}/[^"\']+["\']', content):
                imp = m.group(0)
                # Extraire le chemin
                rel = re.search(r'["\']([^"\']+)["\']', imp).group(1)
                base = os.path.dirname(path)
                candidates = [
                    os.path.normpath(os.path.join(base, rel)),
                    os.path.normpath(os.path.join(base, rel + ".js")),
                    os.path.normpath(os.path.join(base, rel + ".jsx")),
                    os.path.normpath(os.path.join(base, rel, "index.js")),
                    os.path.normpath(os.path.join(base, rel, "index.jsx")),
                ]
                if not any(os.path.exists(c) for c in candidates):
                    errors.append((os.path.relpath(path, BASE_DIR), rel))

    print(f"  Fichiers analysés : {total}")
    if errors:
        print(f"  ⚠️  {len(errors)} import(s) cassé(s) :")
        for path, imp in errors[:20]:
            print(f"    - {path} → {imp}")
        return False
    print("  ✅ Tous les imports relatifs sont valides")
    return True


def test_routes():
    print_header("4. ROUTES REACT")
    routes = check_routes()
    print(f"  Routes détectées : {len(routes)}")

    missing = []
    for r in EXPECTED_ROUTES:
        if r not in routes:
            missing.append(r)

    if missing:
        print(f"  ⚠️  {len(missing)} route(s) manquante(s) :")
        for m in missing:
            print(f"    - {m}")
        return False
    print("  ✅ Toutes les routes attendues sont présentes")
    return True


def test_hooks():
    print_header("5. HOOKS DYNAMIQUES")
    hooks = check_hooks()
    print(f"  Hooks détectés : {len(hooks)}")

    missing = [h for h in EXPECTED_HOOKS if h not in hooks]
    if missing:
        print(f"  ⚠️  Hooks manquants : {missing}")
        return False
    print("  ✅ Tous les hooks attendus sont présents")
    return True


def test_contexts():
    print_header("6. CONTEXTES REACT")
    contexts = check_contexts()
    print(f"  Contextes détectés : {len(contexts)}")

    missing = [c for c in EXPECTED_CONTEXTS if c not in contexts]
    if missing:
        print(f"  ⚠️  Contextes manquants : {missing}")
        return False
    print("  ✅ Tous les contextes attendus sont présents")
    return True


def print_checklist():
    print_header("7. CHECKLIST E2E MANUELLE")
    print("""
  Ouvrez le navigateur et testez dans cet ordre :

  ┌─────────────────────────────────────────────────────────────┐
  │  SCÉNARIO 1 — Page d'accueil                               │
  ├─────────────────────────────────────────────────────────────┤
  │  [ ] http://localhost:5173/ se charge sans erreur          │
  │  [ ] Console F12 : aucune erreur rouge                     │
  │  [ ] Le header affiche les menus                           │
  │  [ ] La bannière d'annonce s'affiche                       │
  │  [ ] Le footer s'affiche                                   │
  └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │  SCÉNARIO 2 — Éditeur Puck                                 │
  ├─────────────────────────────────────────────────────────────┤
  │  [ ] http://localhost:5173/admin/pages                     │
  │  [ ] La liste des pages s'affiche                          │
  │  [ ] Cliquer "Éditer" ouvre l'éditeur Puck                 │
  │  [ ] La palette de gauche affiche les catégories :         │
  │      Structure, Basiques, Média, Marketing,                │
  │      Interactif, Boutique, Article, Archive,               │
  │      Produit, Commerce                                     │
  │  [ ] Drag-and-drop d'un widget fonctionne                  │
  │  [ ] Le bouton "Publier" sauvegarde                        │
  └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │  SCÉNARIO 3 — Boutique                                     │
  ├─────────────────────────────────────────────────────────────┤
  │  [ ] http://localhost:5173/boutique/cosmetiques            │
  │  [ ] Les produits s'affichent avec images                  │
  │  [ ] Cliquer sur un produit ouvre la fiche                 │
  │  [ ] http://localhost:5173/produit/{slug}                  │
  │  [ ] Le titre, prix, description s'affichent               │
  └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │  SCÉNARIO 4 — Panier                                       │
  ├─────────────────────────────────────────────────────────────┤
  │  [ ] Cliquer "Ajouter au panier" sur un produit            │
  │  [ ] Le badge du panier s'incrémente                       │
  │  [ ] http://localhost:5173/panier                          │
  │  [ ] Les articles sont listés                              │
  │  [ ] Le total se calcule                                   │
  └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │  SCÉNARIO 5 — Journal / Blog                               │
  ├─────────────────────────────────────────────────────────────┤
  │  [ ] http://localhost:5173/journal                         │
  │  [ ] Les articles s'affichent                              │
  │  [ ] Cliquer sur un article                                │
  │  [ ] Le contenu et l'auteur s'affichent                    │
  └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │  SCÉNARIO 6 — Sélecteur de langue                          │
  ├─────────────────────────────────────────────────────────────┤
  │  [ ] Le sélecteur FR/EN est dans le header                 │
  │  [ ] Cliquer sur EN change les textes t()                  │
  │  [ ] Recharger : la langue est persistée                   │
  └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │  SCÉNARIO 7 — Annonces & Cookies                           │
  ├─────────────────────────────────────────────────────────────┤
  │  [ ] La bannière top_bar s'affiche                         │
  │  [ ] Le popup newsletter apparaît après 5s                 │
  │  [ ] Le cookie banner apparaît en bas                      │
  │  [ ] Cliquer "Accepter" masque le banner                   │
  │  [ ] Recharger : le banner ne réapparaît pas               │
  └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │  SCÉNARIO 8 — Authentification                             │
  ├─────────────────────────────────────────────────────────────┤
  │  [ ] http://localhost:5173/connexion                       │
  │  [ ] Se connecter avec manager_aicha / Demo1234!           │
  │  [ ] Le menu "Gestion" apparaît (Staff only)               │
  │  [ ] Se déconnecter → "Gestion" disparaît                  │
  └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │  SCÉNARIO 9 — Admin Django (backend)                       │
  ├─────────────────────────────────────────────────────────────┤
  │  [ ] http://localhost:8000/admin/                          │
  │  [ ] Menu, Widget, Design System accessibles               │
  │  [ ] Créer une annonce → apparaît sur le site              │
  │  [ ] Désactiver un flag → le widget disparaît              │
  └─────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────┐
  │  SCÉNARIO 10 — Performance & Erreurs                       │
  ├─────────────────────────────────────────────────────────────┤
  │  [ ] Ouvrir F12 → Console                                  │
  │  [ ] Naviguer sur 5 pages                                  │
  │  [ ] AUCUNE erreur rouge (warnings OK)                     │
  │  [ ] Onglet Network : pas de 404/500                       │
  │  [ ] Lighthouse (optionnel) : score > 70                   │
  └─────────────────────────────────────────────────────────────┘
""")


def main():
    print()
    print("=" * 70)
    print("  AUDIT FRONTEND — NAWA COMMERCE")
    print("=" * 70)

    if not os.path.exists(SRC_DIR):
        print(f"\n  ❌ Dossier src/ introuvable dans {BASE_DIR}")
        print("  → Êtes-vous à la racine de nawa-shop-frontend ?")
        sys.exit(1)

    results = {
        "Widgets": test_widgets(),
        "Syntaxe JSX": test_syntax(),
        "Imports": test_imports(),
        "Routes": test_routes(),
        "Hooks": test_hooks(),
        "Contextes": test_contexts(),
    }

    print_header("RÉSULTAT GLOBAL")
    for name, ok in results.items():
        icon = "✅" if ok else "⚠️ "
        print(f"  {icon} {name}")

    total_ok = sum(1 for v in results.values() if v)
    total = len(results)
    print()
    print(f"  SCORE : {total_ok}/{total}")
    print()
    if total_ok == total:
        print("  🎉 TOUS LES TESTS AUTOMATIQUES PASSENT !")
        print("  → Passez à la checklist E2E manuelle ci-dessous.")
    else:
        print("  ⚠️  Certains tests échouent. Corrigez avant E2E.")
    print()

    print_checklist()


if __name__ == "__main__":
    main()