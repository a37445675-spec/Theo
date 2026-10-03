"""
Inventaire des widgets Puck - v2 (détecte les widgets locaux).

Usage : python test_widgets_inventory_v2.py
"""
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WIDGETS_DIR = os.path.join(BASE_DIR, "src", "puck", "widgets")
CONFIG_PATH = os.path.join(BASE_DIR, "src", "puck", "config.jsx")

EXPECTED = {
    "P7 - Base": [
        "Section", "Columns", "Divider", "Spacer",
        "Heading", "Text", "Image", "Button", "IconBox",
        "CTA", "Testimonial", "PricingTable", "Countdown", "ProgressBar",
        "Gallery", "Carousel", "Video", "SocialShare",
        "Accordion", "Tabs", "FlipBox",
    ],
    "P8 - Media": [
        "CarouselLoop", "CarouselMedia", "CarouselNested", "Slides", "VideoPlaylist",
        "TestimonialCarousel", "LottieWidget", "Hotspot", "TableOfContents",
        "Counter", "ProgressReview", "CodeHighlight", "Portfolio", "Review",
    ],
    "P9 - Marketing": [
        "FacebookPage", "FacebookButton", "FacebookEmbed", "FacebookComments",
        "PayPalButton", "StripeButton",
        "MegaMenu", "OffCanvas", "MenuCart", "SocialShareExtended",
        "WhatsAppFloat", "NewsletterPopup", "CookieBanner",
    ],
    "P10 - Dynamiques": [
        "PostTitle", "PostContent", "PostExcerpt", "PostInfo",
        "PostNavigation", "PostComments", "AuthorBox",
        "ArchiveTitle", "ArchivePosts", "Breadcrumbs", "LoopGrid", "LoopCarousel",
        "Taxonomy", "SiteLogo", "SiteTitle", "SitelinkSearch", "PostPortfolio",
    ],
    "P11 - E-commerce": [
        "ProductTitle", "ProductImages", "ProductPrice", "AddToCart",
        "ProductRating", "ProductStock", "ProductMeta", "ShortDescription",
        "ProductContent", "ProductDataTabs", "ProductGrid", "Upsells",
        "RelatedProducts", "ProductCategories",
        "Cart", "Checkout", "PurchaseSummary", "MyAccount",
        "WcBreadcrumbs", "MenuCartExtended",
    ],
}


def extract_names():
    names = set()
    if os.path.exists(WIDGETS_DIR):
        pat = re.compile(r'export\s+const\s+(\w+)\s*=\s*\{')
        for f in os.listdir(WIDGETS_DIR):
            if f.endswith(".jsx") and not f.endswith(".bak"):
                with open(os.path.join(WIDGETS_DIR, f), encoding="utf-8") as fh:
                    for m in pat.finditer(fh.read()):
                        names.add(m.group(1))
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            c = f.read()
        for m in re.finditer(r'^const\s+(\w+)\s*=\s*\{', c, re.MULTILINE):
            names.add(m.group(1))
        for m in re.finditer(r'import\s*\{([^}]+)\}\s*from\s*["\']\./widgets/', c):
            for x in m.group(1).split(","):
                x = x.strip()
                if x and re.match(r'^\w+$', x):
                    names.add(x)
    return names


def extract_config():
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


def main():
    print("=" * 70)
    print("  INVENTAIRE DES WIDGETS PUCK")
    print("=" * 70)
    all_n = extract_names()
    cfg = extract_config()
    print(f"\n  Widgets trouves : {len(all_n)}")
    print(f"  Dans config     : {len(cfg)}\n")
    total = 0
    found = 0
    errors = []
    for phase, widgets in EXPECTED.items():
        print("-" * 70)
        print(f"  {phase}")
        print("-" * 70)
        for w in widgets:
            total += 1
            if w in all_n and w in cfg:
                print(f"    OK  {w}")
                found += 1
            else:
                print(f"    KO  {w}")
                errors.append(w)
        print()
    print("=" * 70)
    print(f"  TOTAL : {found}/{total}")
    print("=" * 70)
    if not errors:
        print("\n  Tous les widgets sont operationnels !")
    else:
        print(f"\n  {len(errors)} widget(s) manquant(s) :")
        for e in errors:
            print(f"    - {e}")


if __name__ == "__main__":
    main()