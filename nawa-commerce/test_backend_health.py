"""
Test intensif du backend : vérifie que toutes les routes API répondent.

Usage : python test_backend_health.py
"""
import json
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8000"

# Liste exhaustive des endpoints à tester
ENDPOINTS = [
    # (méthode, url, statut_attendu, catégorie, description)
    ("GET", "/api/schema/", 200, "Docs", "Schéma OpenAPI"),
    ("GET", "/api/docs/", 406, "Docs", "Swagger UI (HTML)"),

    # Design System
    ("GET", "/api/v1/design-system/", 200, "Design", "Liste design systems"),
    ("GET", "/api/v1/design-system/active/", 200, "Design", "Design system actif"),

    # Navigation
    ("GET", "/api/v1/navigation/menus/", 200, "Navigation", "Liste menus"),
    ("GET", "/api/v1/navigation/menus/?location=header", 200, "Navigation", "Menu header"),

    # SEO
    ("GET", "/api/v1/seo/metadata/", 200, "SEO", "Métadonnées SEO"),
    ("GET", "/api/v1/seo/metadata/sitemap/", 200, "SEO", "Sitemap JSON"),

    # Traductions
    ("GET", "/api/v1/translations/?lang=fr", 200, "i18n", "Traductions FR"),
    ("GET", "/api/v1/translations/?lang=en", 200, "i18n", "Traductions EN"),
    ("GET", "/api/v1/translations/languages/", 200, "i18n", "Langues dispo"),

    # Feature Flags
    ("GET", "/api/v1/feature-flags/", 200, "Flags", "Liste feature flags"),

    # Annonces
    ("GET", "/api/v1/announcements/", 200, "Annonces", "Liste annonces"),
    ("GET", "/api/v1/announcements/?position=top_bar", 200, "Annonces", "Top bar"),

    # Médiathèque
    ("GET", "/api/v1/media-library/assets/", 200, "Média", "Liste assets"),
    ("GET", "/api/v1/media-library/tags/", 200, "Média", "Liste tags"),
    ("GET", "/api/v1/media-library/assets/stats/", 200, "Média", "Stats"),

    # Formulaires
    ("GET", "/api/v1/forms/definitions/", 200, "Forms", "Liste formulaires"),
    ("GET", "/api/v1/forms/definitions/contact/", 200, "Forms", "Formulaire contact"),

    # Redirections
    ("GET", "/api/v1/redirects/", 200, "Redirects", "Liste redirections"),

    # Scripts tiers
    ("GET", "/api/v1/third-party-scripts/", 200, "Scripts", "Scripts tiers"),

    # Emails (auth requise)
    ("GET", "/api/v1/email-templates/", 401, "Emails", "Templates emails (auth)"),

    # Widget Builder
    ("GET", "/api/v1/cms/widgets/?page=1", 401, "Widget", "Widgets page 1 (auth)"),
    ("GET", "/api/v1/cms/reusable-sections/", 401, "Widget", "Sections réutil. (auth)"),

    # CMS général
    ("GET", "/api/v1/cms/templates/", 200, "CMS", "Templates CMS"),
    ("GET", "/api/v1/cms/dynamic-tags/", 200, "CMS", "Dynamic tags"),
    ("GET", "/api/v1/cms/site-kits/", 200, "CMS", "Site kits"),

    # Blog
    ("GET", "/api/v1/blog/posts/", 200, "Blog", "Liste posts"),
    ("GET", "/api/v1/blog/categories/", 200, "Blog", "Catégories blog"),
    ("GET", "/api/v1/blog/tags/", 200, "Blog", "Tags blog"),

    # Catalogue
    ("GET", "/api/v1/catalog/products/", 200, "Catalog", "Liste produits"),
    ("GET", "/api/v1/catalog/categories/", 200, "Catalog", "Catégories produits"),
    ("GET", "/api/v1/catalog/products/?is_featured=true", 200, "Catalog", "Produits vedettes"),

    # Panier
    ("GET", "/api/v1/cart/", 200, "Cart", "Panier courant"),

    # Auth
    ("GET", "/api/v1/auth/token/", 405, "Auth", "Endpoint token (POST only)"),
]


def test_endpoint(method, url, expected_status, category, description):
    """Test un endpoint et retourne le résultat."""
    full_url = BASE_URL + url
    try:
        req = urllib.request.Request(full_url, method=method)
        req.add_header("Accept", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                status = resp.status
        except urllib.error.HTTPError as e:
            status = e.code

        ok = (status == expected_status)
        return {
            "ok": ok,
            "method": method,
            "url": url,
            "expected": expected_status,
            "got": status,
            "category": category,
            "description": description,
        }
    except Exception as e:
        return {
            "ok": False,
            "method": method,
            "url": url,
            "expected": expected_status,
            "got": f"ERREUR: {e}",
            "category": category,
            "description": description,
        }


def main():
    print("=" * 70)
    print("  TEST BACKEND — NAWA Commerce")
    print("=" * 70)

    # Vérifier que le serveur tourne
    try:
        urllib.request.urlopen(BASE_URL + "/api/v1/design-system/active/", timeout=3)
    except Exception:
        print(f"\n  ❌ Serveur inaccessible : {BASE_URL}")
        print("  → Lancez 'python manage.py runserver' d'abord.\n")
        sys.exit(1)

    print(f"\n  Serveur accessible : {BASE_URL}\n")
    print("-" * 70)
    print(f"  {'CATÉGORIE':<12} {'STATUT':<10} {'DESCRIPTION':<40}")
    print("-" * 70)

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(test_endpoint, *ep): ep
            for ep in ENDPOINTS
        }
        for future in as_completed(futures):
            results.append(future.result())

    # Trier par catégorie pour lisibilité
    results.sort(key=lambda r: (r["category"], r["url"]))

    total = len(results)
    passed = 0
    failed = []
    for r in results:
        icon = "✅" if r["ok"] else "❌"
        status_str = str(r["got"]) if r["got"] == r["expected"] else f"{r['expected']}→{r['got']}"
        print(f"  {icon} {r['category']:<10} {status_str:<10} {r['description']:<40}")
        if r["ok"]:
            passed += 1
        else:
            failed.append(r)

    print("-" * 70)
    print(f"\n  RÉSULTAT : {passed}/{total} tests passés ({passed * 100 // total}%)\n")

    if failed:
        print("  ❌ Échecs :")
        for r in failed:
            print(f"    - {r['method']} {r['url']}")
            print(f"      Attendu {r['expected']}, reçu {r['got']}")
    else:
        print("  🎉 Tous les endpoints fonctionnent !")

    print()
    # Code de sortie : 0 si tout OK, 1 sinon
    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
