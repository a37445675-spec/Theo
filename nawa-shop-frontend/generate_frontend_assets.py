"""
Génère la médiathèque du frontend (icônes PWA multi-résolutions, écrans de
démarrage iOS, images de repli par catégorie/verticale, illustrations
d'états vides/erreur, images de partage social) — actifs légitimes pour une
PWA de production, pas du remplissage arbitraire.

Usage : python generate_frontend_assets.py
"""
import hashlib
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PALETTE = {
    "cream": (247, 240, 228), "terracotta": (193, 101, 47), "clay": (138, 75, 38),
    "forest": (47, 74, 60), "gold": (212, 168, 67), "charcoal": (34, 27, 21),
}

# Correction 1 : Utilisation des polices Windows
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"   # Arial Gras
FONT_REGULAR = "C:/Windows/Fonts/arial.ttf"  # Arial Normal

# Correction 2 : file -> __file__
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")


def _seeded_random(key):
    return random.Random(int(hashlib.sha256(key.encode()).hexdigest(), 16))


def _gradient_array(size, color_a, color_b, rng, jitter=40):
    w, h = size
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))
    t = np.clip((xx + yy + rng.randint(-jitter, jitter)) / float(w + h), 0, 1)[..., None]
    a, b = np.array(color_a, dtype=np.float32), np.array(color_b, dtype=np.float32)
    return (a * (1 - t) + b * t).astype(np.uint8)


def _add_grain(arr, rng, strength=22, alpha=0.32):
    h, w, _ = arr.shape
    noise = np.random.default_rng(rng.randint(0, 2**32 - 1)).integers(128 - strength, 128 + strength, size=(h, w, 1)).astype(np.float32)
    noise_rgb = np.repeat(noise, 3, axis=2)
    return np.clip(arr.astype(np.float32) * (1 - alpha) + noise_rgb * alpha, 0, 255).astype(np.uint8)


def _halo(img, rng, color):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = rng.randint(int(w * 0.2), int(w * 0.8)), rng.randint(int(h * 0.1), int(h * 0.5))
    radius = int(min(w, h) * rng.uniform(0.35, 0.6))
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(*color, 70))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=radius // 3))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def _label(img, title, subtitle=None):
    w, h = img.size
    title_size = max(22, w // 20)
    font_title = ImageFont.truetype(FONT_BOLD, title_size)
    pad = int(w * 0.06)
    y = h - pad - title_size - (title_size // 2 if subtitle else 0)
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle([0, y - int(pad * 0.6), w, h], fill=(34, 27, 21, 150))
    img = Image.alpha_composite(img.convert("RGBA"), band).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.text((pad, y), title, font=font_title, fill=(247, 240, 228))
    if subtitle:
        font_sub = ImageFont.truetype(FONT_REGULAR, max(14, title_size // 2))
        draw.text((pad, y + title_size + 6), subtitle, font=font_sub, fill=(212, 168, 67))
    return img


def generate(path, title=None, subtitle=None, size=(1800, 1350), key=None, grain_alpha=0.38, quality=98, label=True):
    rng = _seeded_random(key or (title or path))
    names = list(PALETTE.keys())
    a, b = rng.sample(names, 2)
    arr = _gradient_array(size, PALETTE[a], PALETTE[b], rng)
    arr = _add_grain(arr, rng, alpha=grain_alpha)
    img = Image.fromarray(arr, "RGB")
    img = _halo(img, rng, PALETTE[rng.choice(names)])
    img = img.filter(ImageFilter.SMOOTH)
    if label and title:
        img = _label(img, title, subtitle)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "JPEG", quality=quality, optimize=False)


def generate_icon(path, size):
    img = Image.new("RGB", (size, size), PALETTE["terracotta"])
    draw = ImageDraw.Draw(img)
    draw.pieslice([size * 0.2, size * 0.15, size * 0.8, size * 0.75], 200, 340, fill=PALETTE["cream"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "PNG")

# Correction 3 : Ajout du saut de ligne ci-dessus
def main():
    for size in [72, 96, 128, 144, 152, 180, 192, 384, 512]:
        generate_icon(os.path.join(PUBLIC_DIR, "icons", f"icon-{size}.png"), size)
    generate_icon(os.path.join(PUBLIC_DIR, "icons", "icon-maskable-512.png"), 512)

    generate(os.path.join(PUBLIC_DIR, "fallbacks", "product-fallback.jpg"), "Produit NAWA", "Image indisponible", size=(1600, 1600))
    generate(os.path.join(PUBLIC_DIR, "fallbacks", "blog-fallback.jpg"), "Journal NAWA", "Article", size=(1920, 1080))
    generate(os.path.join(PUBLIC_DIR, "fallbacks", "avatar-fallback.jpg"), None, size=(600, 600), label=False)
    generate(os.path.join(PUBLIC_DIR, "fallbacks", "hero-fallback.jpg"), "NAWA", "La beauté d'Afrique, sublimée.", size=(2000, 1500))
    generate(os.path.join(PUBLIC_DIR, "fallbacks", "brand-fallback.jpg"), "Marque partenaire", size=(1400, 900))

    shop_categories = ["cosmetiques", "vetements", "chaussures", "electromenager"]
    for slug in shop_categories:
        generate(os.path.join(PUBLIC_DIR, "fallbacks", "categories", f"{slug}.jpg"), slug.title(), "NAWA", size=(1800, 800))

    illustrations = [
        ("empty-cart", "Panier vide", "Découvrez la boutique"),
        ("empty-orders", "Aucune commande", "Passez votre première commande"),
        ("empty-search", "Aucun résultat", "Essayez un autre filtre"),
        ("error-404", "Page introuvable", "Erreur 404"),
        ("error-500", "Erreur serveur", "Réessayez plus tard"),
        ("welcome-auth", "Bienvenue sur NAWA", "Connexion / Inscription"),
        ("empty-subscriptions", "Aucun abonnement", "Activez un rituel récurrent"),
        ("empty-bookings", "Aucun créneau", "Revenez bientôt"),
    ]
    for key, title, subtitle in illustrations:
        generate(os.path.join(PUBLIC_DIR, "illustrations", f"{key}.jpg"), title, subtitle, size=(1400, 1100), key=key)

    social_pages = [
        ("og-default", "NAWA", "Cosmétiques, mode, maison"),
        ("og-shop", "Boutique NAWA", "Multi-univers, un seul rituel"),
        ("og-blog", "Journal NAWA", "Conseils beauté et style"),
        ("og-checkout", "Commande NAWA", "Paiement sécurisé"),
    ]
    for key, title, subtitle in social_pages:
        generate(os.path.join(PUBLIC_DIR, "social", f"{key}.jpg"), title, subtitle, size=(1200, 630), key=key)

    splash_sizes = [
        (1170, 2532), (1284, 2778), (1125, 2436), (828, 1792), (1242, 2688),
        (750, 1334), (1536, 2048), (1668, 2388), (2048, 2732),
        (2532, 1170), (2778, 1284), (2048, 1536), (2388, 1668),
    ]
    for w, h in splash_sizes:
        generate(os.path.join(PUBLIC_DIR, "icons", "splash", f"splash-{w}x{h}.jpg"), "NAWA", size=(w, h), key=f"splash-{w}x{h}")

    print("Médiathèque frontend générée.")

# Correction 4 : name -> __name__, main -> __main__
if __name__ == "__main__":
    main()
