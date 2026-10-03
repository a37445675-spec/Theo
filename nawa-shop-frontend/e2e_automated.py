"""
E2E automatisé — NAWA Commerce.
Vérifie que les pages, APIs et widgets clés répondent correctement.

Usage : python e2e_automated.py
"""
import json
import sys
import urllib.request
import urllib.error

BACKEND = "http://localhost:8000"
FRONTEND = "http://localhost:5173"


# ============================================================
#         SCÉNARIOS AUTOMATISÉS (URL → Statut)
# ============================================================

BACKEND_CHECKS = [
    # (URL, statut, description)
    ("/api/v1/design-system/active/", 200, "Design System actif"),
    ("/api/v1/navigation/menus/", 200, "Menus de navigation"),
    ("/api/v1/feature-flags/", 200, "Feature flags"),
    ("/api/v1/announcements/?position=top_bar", 200, "Annonces top_bar"),
    ("/api/v1/announcements/?position=popup", 200, "Annonces popup"),
    ("/api/v1/translations/?lang=fr", 200, "Traductions FR"),
    ("/api/v1/translations/?lang=en", 200, "Traductions EN"),
    ("/api/v1/catalog/products/", 200, "Catalogue produits"),
    ("/api/v1/catalog/categories/", 200, "Catégories produits"),
    ("/api/v1/catalog/products/?is_featured=true", 200, "Produits vedettes"),
    ("/api/v1/blog/posts/", 200, "Articles blog"),
    ("/api/v1/blog/categories/", 200, "Catégories blog"),
    ("/api/v1/blog/tags/", 200, "Tags blog"),
    ("/api/v1/cart/", 200, "Panier"),
    ("/api/v1/forms/definitions/contact/", 200, "Formulaire contact"),
    ("/api/v1/media-library/assets/", 200, "Médiathèque assets"),
    ("/api/v1/cms/templates/", 200, "Templates CMS"),
    ("/api/v1/seo/metadata/sitemap/", 200, "Sitemap JSON"),
    ("/api/v1/redirects/", 200, "Redirections"),
    ("/api/v1/third-party-scripts/", 200, "Scripts tiers"),
    ("/api/schema/", 200, "Schéma OpenAPI"),
]

FRONTEND_CHECKS = [
    # (URL, description)  — vérifie que le HTML se charge
    ("/", "Page d'accueil"),
    ("/admin/pages", "Liste des pages admin"),
    ("/journal", "Journal / Blog"),
    ("/boutique/cosmetiques", "Boutique cosmétiques"),
    ("/panier", "Panier"),
    ("/connexion", "Connexion"),
]


def check_url(url, expected_status=None, timeout=5):
    """Vérifie une URL. Retourne (status, ok, detail)."""
    try:
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            body = resp.read().decode(errors="ignore")
    except urllib.error.HTTPError as e:
        status = e.code
        body = ""
    except Exception as e:
        return 0, False, str(e)

    if expected_status is not None:
        ok = (status == expected_status)
    else:
        ok = 200 <= status < 400  # Pour le frontend, tout sauf 5xx

    return status, ok, body


def check_json_endpoint(url, required_keys=None):
    """Vérifie qu'un endpoint JSON répond et contient les clés attendues."""
    status, ok, body = check_url(url, 200)
    if not ok:
        return False, f"Statut {status}"

    try:
        data = json.loads(body)
    except Exception as e:
        return False, f"JSON invalide : {e}"

    if required_keys:
        # Si c'est un dict avec pagination
        if isinstance(data, dict) and "results" in data:
            data = data["results"]
        if isinstance(data, list) and len(data) > 0:
            for key in required_keys:
                if key not in data[0]:
                    return False, f"Clé '{key}' manquante"
        elif isinstance(data, dict):
            for key in required_keys:
                if key not in data:
                    return False, f"Clé '{key}' manquante"

    return True, f"{len(data) if isinstance(data, list) else 'obj'} élément(s)"


# ============================================================
#                    VÉRIFICATIONS DÉTAILLÉES
# ============================================================

def test_widget_data_availability():
    """Vérifie que les widgets Puck peuvent obtenir leurs données."""
    print("\n[3] Données disponibles pour les widgets")

    checks = [
        ("Design System (ThemeContext)", "/api/v1/design-system/active/",
         ["colorPrimary", "fontHeading"]),
        ("Menus (NavigationContext)", "/api/v1/navigation/menus/",
         ["items", "location"]),
        ("Feature Flags", "/api/v1/feature-flags/",
         ["code", "isEnabled"]),
        ("Annonces top_bar", "/api/v1/announcements/?position=top_bar",
         ["message", "backgroundColor"]),
        ("Traductions FR", "/api/v1/translations/?lang=fr", None),
        ("Produits", "/api/v1/catalog/products/",
         ["id", "name", "slug", "price"]),
        ("Posts blog", "/api/v1/blog/posts/",
         ["id", "title", "slug"]),
    ]

    passed = 0
    for label, path, keys in checks:
        ok, detail = check_json_endpoint(BACKEND + path, keys)
        icon = "✅" if ok else "❌"
        print(f"  {icon} {label:<40} {detail}")
        if ok:
            passed += 1

    return passed == len(checks)


def test_critical_scenarios():
    """Vérifie les scénarios critiques (data-level)."""
    print("\n[4] Scénarios critiques (data)")

    # Test 1 : Un produit accessible par slug
    print("  → Test 1 : Produit par slug")
    status, ok, body = check_url(BACKEND + "/api/v1/catalog/products/", 200)
    if ok:
        try:
            products = json.loads(body)
            list_data = products if isinstance(products, list) else products.get("results", [])
            if list_data:
                slug = list_data[0].get("slug")
                status2, ok2, body2 = check_url(f"{BACKEND}/api/v1/catalog/products/{slug}/")
                icon = "✅" if ok2 else "❌"
                print(f"    {icon} /produit/{slug} → {status2}")
            else:
                print("    ⚠️  Aucun produit à tester")
        except Exception as e:
            print(f"    ❌ Parsing : {e}")
    else:
        print(f"    ❌ Catalogue inaccessible ({status})")

    # Test 2 : Un post accessible par slug
    print("  → Test 2 : Article par slug")
    status, ok, body = check_url(BACKEND + "/api/v1/blog/posts/", 200)
    if ok:
        try:
            posts = json.loads(body)
            list_data = posts if isinstance(posts, list) else posts.get("results", [])
            if list_data:
                slug = list_data[0].get("slug")
                status2, ok2, body2 = check_url(f"{BACKEND}/api/v1/blog/posts/{slug}/")
                icon = "✅" if ok2 else "❌"
                print(f"    {icon} /journal/{slug} → {status2}")
            else:
                print("    ⚠️  Aucun post à tester")
        except Exception as e:
            print(f"    ❌ Parsing : {e}")
    else:
        print(f"    ❌ Blog inaccessible ({status})")

    # Test 3 : Menu contient des items
    print("  → Test 3 : Menu header avec items")
    status, ok, body = check_url(BACKEND + "/api/v1/navigation/menus/?location=header", 200)
    if ok:
        try:
            data = json.loads(body)
            menus = data if isinstance(data, list) else data.get("results", [])
            if menus and menus[0].get("items"):
                print(f"    ✅ Menu header : {len(menus[0]['items'])} item(s)")
            else:
                print("    ⚠️  Menu header vide")
        except Exception as e:
            print(f"    ❌ {e}")
    else:
        print(f"    ❌ {status}")

    # Test 4 : Design System renvoie les couleurs
    print("  → Test 4 : Design System personnalisé")
    status, ok, body = check_url(BACKEND + "/api/v1/design-system/active/", 200)
    if ok:
        try:
            ds = json.loads(body)
            color = ds.get("colorPrimary") or ds.get("color_primary")
            if color:
                print(f"    ✅ Couleur primaire : {color}")
            else:
                print("    ⚠️  Aucune couleur détectée")
        except Exception as e:
            print(f"    ❌ {e}")


# ============================================================
#                          MAIN
# ============================================================

def main():
    print("=" * 70)
    print("  E2E AUTOMATISÉ — NAWA COMMERCE")
    print("=" * 70)
    print()

    # 1. Backend accessible
    print("[1] Backend — Endpoints API")
    print("-" * 70)
    backend_passed = 0
    for path, expected, label in BACKEND_CHECKS:
        status, ok, _ = check_url(BACKEND + path, expected)
        icon = "✅" if ok else "❌"
        status_str = str(status) if ok else f"{expected}→{status}"
        print(f"  {icon} {label:<40} {status_str}")
        if ok:
            backend_passed += 1
    print(f"\n  → {backend_passed}/{len(BACKEND_CHECKS)}")

    # 2. Frontend accessible
    print("\n[2] Frontend — Pages React")
    print("-" * 70)
    frontend_passed = 0
    for path, label in FRONTEND_CHECKS:
        status, ok, _ = check_url(FRONTEND + path, None, timeout=10)
        icon = "✅" if ok else "❌"
        print(f"  {icon} {label:<40} {status}")
        if ok:
            frontend_passed += 1
    print(f"\n  → {frontend_passed}/{len(FRONTEND_CHECKS)}")

    # 3. Données pour widgets
    widgets_ok = test_widget_data_availability()

    # 4. Scénarios critiques
    test_critical_scenarios()

    # Résumé final
    print()
    print("=" * 70)
    print("  RÉSUMÉ")
    print("=" * 70)
    print(f"  Backend  : {backend_passed}/{len(BACKEND_CHECKS)}")
    print(f"  Frontend : {frontend_passed}/{len(FRONTEND_CHECKS)}")
    print(f"  Widgets  : {'✅ OK' if widgets_ok else '❌ Problème'}")
    print()
    if backend_passed == len(BACKEND_CHECKS) and frontend_passed >= len(FRONTEND_CHECKS) - 1:
        print("  🎉 PARTIE A VALIDÉE")
        print("  → Passez à la Partie B (checklist manuelle)")
    else:
        print("  ⚠️  Certains tests échouent")


if __name__ == "__main__":
    main()