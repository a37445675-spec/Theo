"""
Inventaire des widgets Puck — Version corrigée (détecte les widgets locaux).

Usage : python test_widgets_inventory_v2.py
"""
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WIDGETS_DIR = os.path.join(BASE_DIR, "src", "puck", "widgets")
CONFIG_PATH = os.path.join(BASE_DIR, "src", "puck", "config.jsx")


EXPECTED = {
    "P7 — Base": [
        "Section", "Columns", "Divider", "Spacer",
        "Heading", "Text", "Image", "Button", "IconBox",
        "CTA", "Testimonial", "PricingTable", "Countdown", "ProgressBar",
        "Gallery", "Carousel", "Video", "SocialShare",
        "Accordion", "Tabs", "FlipBox",
        "ProductGrid", "BlogList",
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


def extract_all_widget_names():
    """
    Extrait tous les noms de widgets depuis :
    - Les exports des fichiers widgets/ (export const X = {...})
    - Les déclarations locales dans config.jsx (const X = {...})
    - Les imports dans config.jsx
    """
    names = set()

    # 1. Exports dans les fichiers de widgets
    if os.path.exists(WIDGETS_DIR):
        export_pattern = re.compile(r'export\s+const\s+(\w+)\s*=\s*\{')
        for f in os.listdir(WIDGETS_DIR):
            if f.endswith(".jsx") and not f.endswith(".bak"):
                with open(os.path.join(WIDGETS_DIR, f), "r", encoding="utf-8") as fh:
                    for match in export_pattern.finditer(fh.read()):
                        names.add(match.group(1))

    # 2. Déclarations locales + imports dans config.jsx
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            content = f.read()

        # const X = {...}
        const_pattern = re.compile(r'^const\s+(\w+)\s*=\s*\{', re.MULTILINE)
        for match in const_pattern.finditer(content):
            names.add(match.group(1))

        # imports
        import_pattern = re.compile(r'import\s*\{([^}]+)\}\s*from\s*["\']\./widgets/')
        for match in import_pattern.finditer(content):
            for name in match.group(1).split(","):
                name = name.strip()
                if name and re.match(r'^\w+$', name):
                    names.add(name)

    return names


def extract_config_components():
    """Extrait les composants réellement déclarés dans puckConfig.components."""
    if not os.path.exists(CONFIG_PATH):
        return set()

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Localiser components: {
    match = re.search(r'components:\s*\{', content)
    if not match:
        return set()

    # Compter les accolades
    start = match.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
        i += 1

    block = content[start:i - 1]

    # Extraire les identifiants (en ignorant commentaires)
    names = set()
    for line in block.split("\n"):
        # Retirer les commentaires
        line = re.sub(r'//.*$', '', line)
        line = re.sub(r'/\*.*?\*/', '', line, flags=re.DOTALL)
        # Chercher les identifiants
        for part in line.split(","):
            part = part.strip()
            if re.match(r'^\w+$', part):
                names.add(part)

    return names


def main():
    print("=" * 70)
    print("  INVENTAIRE DES WIDGETS PUCK — v2")
    print("=" * 70)
    print()

    all_names = extract_all_widget_names()
    config_components = extract_config_components()

    print(f"  Widgets trouvés (exports + imports + locaux) : {len(all_names)}")
    print(f"  Widgets déclarés dans puckConfig.components  : {len(config_components)}")
    print()

    all_ok = True
    total = 0
    found = 0

    for phase, widgets in EXPECTED.items():
        print("-" * 70)
        print(f"  {phase}")
        print("-" * 70)

        for widget in widgets:
            total += 1
            in_names = widget in all_names
            in_config = widget in config_components

            if in_names and in_config:
                print(f"    ✅ {widget}")
                found += 1
            elif in_names and not in_config:
                print(f"    ❌ {widget} (défini mais ABSENT du config)")
                all_ok = False
            elif not in_names and in_config:
                print(f"    ⚠️  {widget} (dans config mais introuvable)")
                all_ok = False
            else:
                print(f"    ❌ {widget} (MANQUANT)")
                all_ok = False
        print()

    print("=" * 70)
    print(f"  TOTAL : {found}/{total} widgets opérationnels")
    print("=" * 70)

    if all_ok:
        print("\n  🎉 Tous les widgets sont opérationnels !")
    else:
        print("\n  ⚠️  Certains widgets manquent.")
        print("  → Lancez fix_p10_config.py si des widgets P10 sont absents.")


if __name__ == "__main__":
    main()