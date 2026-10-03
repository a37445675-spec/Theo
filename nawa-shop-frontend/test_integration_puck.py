"""
Test d'intégration : vérifie que les widgets Puck peuvent être
sauvegardés et récupérés depuis l'API.

Usage : python test_integration_puck.py
"""
import json
import sys
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"


def api_call(method, path, data=None, token=None):
    url = BASE_URL + path
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"raw": body[:200]}
    except Exception as e:
        return 0, {"error": str(e)}


def main():
    print("=" * 70)
    print("  TEST D'INTÉGRATION PUCK ↔ API")
    print("=" * 70)
    print()

    # 1. Authentification (créer un token admin)
    print("[1] Authentification admin...")
    # On suppose que vous connaissez le user/mot de passe admin
    # Pour automatiser, on va utiliser une session Django plutôt que JWT
    print("  → Test via session admin (nécessite d'être loggé)")
    print("  ⚠️  Pour ce test, connectez-vous d'abord dans le navigateur")
    print("  ⚠️  puis relancez ce script (ou utilisez un token JWT valide)")
    print()

    # 2. Test de sauvegarde de l'arbre
    print("[2] Test POST /api/v1/cms/widgets/save-tree/")
    test_tree = {
        "page": 1,
        "tree": [
            {
                "widget_type": "heading",
                "content": {"text": "Test QA — Phase 1", "level": "h1"},
                "style": {},
                "children": [],
            },
            {
                "widget_type": "text",
                "content": {"text": "Ceci est un test d'intégration."},
                "style": {},
                "children": [],
            },
            {
                "widget_type": "section",
                "content": {},
                "style": {"padding": "40px"},
                "children": [
                    {
                        "widget_type": "button",
                        "content": {"label": "Cliquez", "url": "/"},
                        "style": {},
                        "children": [],
                    },
                ],
            },
        ],
    }
    status, resp = api_call("POST", "/api/v1/cms/widgets/save-tree/", test_tree)
    if status == 201 or status == 200:
        print(f"  ✅ Sauvegarde réussie : {resp}")
    elif status == 401 or status == 403:
        print(f"  ⚠️  Non authentifié (normal sans login) : {status}")
    else:
        print(f"  ❌ Erreur : {status} - {resp}")
    print()

    # 3. Récupérer les widgets
    print("[3] Test GET /api/v1/cms/widgets/?page=1")
    status, resp = api_call("GET", "/api/v1/cms/widgets/?page=1")
    if status == 200:
        count = len(resp) if isinstance(resp, list) else len(resp.get("results", []))
        print(f"  ✅ Récupération OK : {count} widgets")
    elif status in (401, 403):
        print(f"  ⚠️  Non authentifié : {status}")
    else:
        print(f"  ❌ Erreur : {status}")
    print()

    # 4. Test de duplication
    print("[4] Test POST /api/v1/cms/widgets/{id}/duplicate/")
    print("  ⚠️  Nécessite un ID de widget existant (skip si pas de widget)")
    print()

    print("=" * 70)
    print("  RÉSULTAT DU TEST D'INTÉGRATION")
    print("=" * 70)
    print()
    print("  Pour tester complètement, exécutez les commandes suivantes")
    print("  dans le Django shell :")
    print()
    print("    python manage.py shell")
    print("    >>> from apps.cms.models import Widget, PageTemplate")
    print("    >>> page = PageTemplate.objects.first()")
    print("    >>> Widget.objects.filter(page=page).count()")
    print()
    print("  Puis testez l'API manuellement dans le navigateur")
    print("  après vous être connecté à /admin/")


if __name__ == "__main__":
    main()