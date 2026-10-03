"""
Génère une médiathèque de démonstration réaliste pour le seed multi-verticales
(photos produits par catégorie, logos de marques, images de blog, avatars,
bannières de catégories) — utilisée par seed_nawa_demo pour peupler les
ImageField sans dépendre d'assets externes.

Usage : python generate_seed_media.py
"""
import hashlib
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PALETTE = {
    "cream": (247, 240, 228), "terracotta": (193, 101, 47), "clay": (138, 75, 38),
    "forest": (47, 74, 60), "gold": (212, 168, 67), "charcoal": (34, 27, 21),
    "denim": (58, 80, 107), "rust": (169, 82, 45), "sage": (120, 138, 110),
}

# Correction 1 : Utilisation des polices Windows (ou Poppins si vous créez le dossier fonts)
FONT_BOLD = "C:/Windows/Fonts/arialbd.ttf"   # Arial Bold
FONT_REGULAR = "C:/Windows/Fonts/arial.ttf"  # Arial Regular

# Correction 2 : file -> __file__
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEED_DIR = os.path.join(BASE_DIR, "seed_assets")

def _seeded_random(key):
    return random.Random(int(hashlib.sha256(key.encode()).hexdigest(), 16))

def _gradient_array(size, color_a, color_b, rng, jitter=40):
    w, h = size
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))
    t = np.clip((xx + yy + rng.randint(-jitter, jitter)) / float(w + h), 0, 1)[..., None]
    a, b = np.array(color_a, dtype=np.float32), np.array(color_b, dtype=np.float32)
    return (a * (1 - t) + b * t).astype(np.uint8)

def _add_grain(arr, rng, strength=22, alpha=0.28):
    h, w, _ = arr.shape
    noise = np.random.default_rng(rng.randint(0, 2**32 - 1)).integers(128 - strength, 128 + strength, size=(h, w, 1)).astype(np.float32)
    noise_rgb = np.repeat(noise, 3, axis=2)
    return np.clip(arr.astype(np.float32) * (1 - alpha) + noise_rgb * alpha, 0, 255).astype(np.uint8)

def _halo(img, rng, color):
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = rng.randint(int(w * 0.15), int(w * 0.85)), rng.randint(int(h * 0.1), int(h * 0.5))
    radius = int(min(w, h) * rng.uniform(0.35, 0.65))
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(*color, 75))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=radius // 3))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def _label(img, title, subtitle=None):
    w, h = img.size
    title_size = max(20, w // 18)
    font_title = ImageFont.truetype(FONT_BOLD, title_size)
    pad = int(w * 0.06)
    y = h - pad - title_size - (title_size // 2 if subtitle else 0)
    band = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(band).rectangle([0, y - int(pad * 0.6), w, h], fill=(34, 27, 21, 155))
    img = Image.alpha_composite(img.convert("RGBA"), band).convert("RGB")
    draw = ImageDraw.Draw(img)
    draw.text((pad, y), title, font=font_title, fill=(247, 240, 228))
    if subtitle:
        font_sub = ImageFont.truetype(FONT_REGULAR, max(13, title_size // 2))
        draw.text((pad, y + title_size + 6), subtitle, font=font_sub, fill=(212, 168, 67))
    return img

def generate(path, title=None, subtitle=None, size=(2400, 1800), key=None, grain_alpha=0.45, quality=99, label=True):
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

# Correction 3 : Ajout du saut de ligne ci-dessus
def main():
    cosmetics = [
        "Beurre de Karité Pur", "Huile de Baobab Précieuse", "Crème Hydratante Karité-Miel",
        "Masque Capillaire Croissance", "Gelée Définition Boucles", "Shampoing Doux Sans Sulfates",
        "Huile de Ricin Fortifiante", "Savon Noir Africain Gommant", "Lait Corporel Beurre de Cacao",
        "Baume Change Bébé Calendula", "Huile de Massage Bébé", "Rouge à Lèvres Karité Teinté",
        "Poudre Matifiante Minérale",
    ]
    for name in cosmetics:
        slug = name.lower().replace(" ", "-").replace("'", "")
        for shot in ["packshot", "texture", "usage"]:
            generate(os.path.join(SEED_DIR, "cosmetics", f"{slug}-{shot}.jpg"), name, shot.capitalize(), key=f"{slug}-{shot}")

    clothing = ["Robe Wax Imprimée", "Chemise Bazin Brodée", "Ensemble Enfant Wax", "Boubou Léger Unisexe"]
    for name in clothing:
        slug = name.lower().replace(" ", "-")
        for i, variant in enumerate(["S", "M", "L"]):
            for shot in [1, 2]:
                generate(os.path.join(SEED_DIR, "clothing", f"{slug}-{variant}-{shot}.jpg"), name, f"Taille {variant}", key=f"{slug}-{variant}-{shot}")

    shoes = ["Sneakers Urbaines Toile", "Sandales Cuir Tressé", "Boots Daim Élégantes", "Sneakers Running Légères"]
    for name in shoes:
        slug = name.lower().replace(" ", "-")
        for pointure in [38, 40, 42, 44]:
            for shot in [1, 2]:
                generate(os.path.join(SEED_DIR, "shoes", f"{slug}-{pointure}-{shot}.jpg"), name, f"Pointure {pointure}", key=f"{slug}-{pointure}-{shot}")

    appliances = ["Réfrigérateur 250L No Frost", "Climatiseur Split 12000 BTU", "Mixeur Blender Pro 1000W", "Machine à Laver 7kg"]
    for name in appliances:
        slug = name.lower().replace(" ", "-")
        for shot in ["face", "profil", "detail"]:
            generate(os.path.join(SEED_DIR, "appliances", f"{slug}-{shot}.jpg"), name, shot.capitalize(), key=f"{slug}-{shot}")

    brands = ["NAWA Rituel", "Coopérative Kaya", "Atelier Téranga", "Sotra Électro", "Pas Global", "Douceur d'Ébène"]
    for name in brands:
        slug = name.lower().replace(" ", "-").replace("'", "")
        generate(os.path.join(SEED_DIR, "brands", f"{slug}-logo.jpg"), name, "NAWA Marketplace", size=(1200, 900), key=f"brand-{slug}")

    blog_posts = [
        "5-gestes-hydratation-cheveux", "beurre-karite-allie-beaute", "wax-garde-robe-moderne",
        "puissance-refrigerateur", "routine-soir-peaux-sensibles", "definir-boucles-sans-agresser",
        "entretenir-chaussures-cuir", "economiser-energie-classe-a",
    ]
    for slug in blog_posts:
        generate(os.path.join(SEED_DIR, "blog", f"{slug}.jpg"), slug.replace("-", " ").title(), "Journal NAWA", size=(1920, 1080), key=slug)

    for name in ["aicha-kone", "fatou-diallo", "admin-nawa"]:
        generate(os.path.join(SEED_DIR, "avatars", f"avatar-{name}.jpg"), None, size=(600, 600), key=f"avatar-{name}", label=False)

    categories = ["cosmetiques", "cheveux-crepus-boucles", "soins-visage", "soins-corps", "soins-bebe", "maquillage-naturel", "vetements", "chaussures", "electromenager"]
    for slug in categories:
        generate(os.path.join(SEED_DIR, "categories", f"{slug}-banner.jpg"), slug.replace("-", " ").title(), "NAWA", size=(2000, 800), key=f"cat-{slug}")

    print("Médiathèque de seed générée.")

def extra_margin():
    for i in range(10):
        generate(os.path.join(SEED_DIR, "categories", f"lifestyle-reference-{i}.jpg"), "NAWA Lifestyle", "Référence design", size=(2400, 1800), key=f"lifestyle-{i}")

# Correction 4 : Fusion des deux blocs if __name__ == "__main__"
if __name__ == "__main__":
    main()
    extra_margin()
