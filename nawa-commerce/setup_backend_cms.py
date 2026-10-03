"""
Script d'installation automatique du CMS Headless - Partie Backend.
Usage : python setup_backend_cms.py
"""
import os
import re
import shutil
import subprocess
import sys

# Chemins des fichiers à modifier
MODELS_PATH = os.path.join("apps", "cms", "models.py")
SERIALIZERS_PATH = os.path.join("apps", "cms", "serializers.py")
ADMIN_PATH = os.path.join("apps", "cms", "admin.py")


def backup_file(path):
    """Crée une copie de sauvegarde avant modification."""
    if os.path.exists(path):
        backup = path + ".bak"
        shutil.copy2(path, backup)
        print(f"  [BACKUP] {backup}")


def update_models():
    """Ajoute les champs ImageField et les champs title/subtitle."""
    if not os.path.exists(MODELS_PATH):
        print(f"  [ERREUR] {MODELS_PATH} introuvable.")
        return False

    with open(MODELS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Vérification d'idempotence
    if "icon_cart = models.ImageField" in content:
        print("  [INFO] Les champs existent déjà dans models.py. Étape ignorée.")
        return True

    backup_file(MODELS_PATH)
    modified = False

    # 1. Ajouter les champs d'icônes au GlobalDesignSystem
    # On cherche la ligne "name = ..." pour insérer juste après
    if "class GlobalDesignSystem" in content:
        # Insérer les nouveaux champs après le premier champ du modèle
        # Pattern : on ajoute après le champ 'name' ou le début de la classe
        pattern = r'(class GlobalDesignSystem\(models\.Model\):\s*\n(?:.*?\n)*?)'
        match = re.search(pattern, content)
        if match:
            # Insérer après la première ligne de champ
            insert_after = re.search(
                r'(class GlobalDesignSystem\(models\.Model\):\s*\n\s*\w+\s*=\s*models\.\w+Field\([^\n]*\n)',
                content
            )
            if insert_after:
                new_fields = """
    # Icônes et Favicons (CMS Headless)
    favicon = models.ImageField(upload_to='cms/favicons/', blank=True, null=True, verbose_name="Favicon du site")
    logo_principal = models.ImageField(upload_to='cms/logos/', blank=True, null=True, verbose_name="Logo principal")
    icon_search = models.ImageField(upload_to='cms/icons/', blank=True, null=True, verbose_name="Icône de recherche")
    icon_user = models.ImageField(upload_to='cms/icons/', blank=True, null=True, verbose_name="Icône utilisateur")
    icon_cart = models.ImageField(upload_to='cms/icons/', blank=True, null=True, verbose_name="Icône du panier")
"""
                content = content.replace(insert_after.group(1), insert_after.group(1) + new_fields)
                modified = True

    # 2. Ajouter title et subtitle au PageBlock
    if "class PageBlock" in content and "title = models.CharField" not in content:
        # Insérer après le champ "order"
        order_match = re.search(r'(\s+order\s*=\s*models\.\w+Field\([^\n]*\n)', content)
        if order_match:
            new_fields_pb = """    title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nom de la section")
    subtitle = models.CharField(max_length=255, blank=True, null=True, verbose_name="Sous-titre")
"""
            content = content.replace(order_match.group(1), order_match.group(1) + new_fields_pb)
            modified = True

    if modified:
        with open(MODELS_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [OK] models.py mis à jour avec les nouveaux champs.")
    else:
        print("  [ATTENTION] Aucune modification n'a pu être appliquée automatiquement.")
        print("           Vérifiez manuellement le fichier models.py.")

    return modified


def update_serializers():
    """S'assure que le serializer inclut tous les champs."""
    if not os.path.exists(SERIALIZERS_PATH):
        print(f"  [INFO] {SERIALIZERS_PATH} introuvable, étape ignorée.")
        return

    with open(SERIALIZERS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "cart_icon" in content and "favicon" in content:
        print("  [INFO] Le serializer semble déjà à jour.")
        return

    backup_file(SERIALIZERS_PATH)

    # Remplacer fields = [...] par fields = '__all__' pour simplifier
    if "fields = '__all__'" not in content:
        content = re.sub(
            r'(class GlobalDesignSystemSerializer\(serializers\.ModelSerializer\):\s*\n(?:.*?\n)*?)\s*fields\s*=\s*\[[^\]]*\]',
            r"\1        fields = '__all__'",
            content
        )
        with open(SERIALIZERS_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print("  [OK] serializers.py mis à jour (fields = '__all__').")
    else:
        print("  [INFO] fields = '__all__' déjà présent.")


def update_admin():
    """Ajoute le PageBlockInline dans l'admin."""
    if not os.path.exists(ADMIN_PATH):
        print(f"  [INFO] {ADMIN_PATH} introuvable, étape ignorée.")
        return

    with open(ADMIN_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if "PageBlockInline" in content:
        print("  [INFO] PageBlockInline existe déjà dans admin.py.")
        return

    backup_file(ADMIN_PATH)

    # Ajouter la classe Inline et l'enregistrer dans PageTemplateAdmin
    inline_code = '''
class PageBlockInline(admin.TabularInline):
    """Permet d'ajouter/réorganiser les sections directement depuis un template."""
    model = PageBlock
    extra = 1
    fields = ('order', 'block_type', 'title', 'subtitle', 'config', 'is_visible')
    ordering = ('order',)
    classes = ('collapse',)


@admin.register(PageTemplate)
class PageTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type')
    inlines = [PageBlockInline]
'''
    # Éviter un doublon de @admin.register(PageTemplate)
    content = re.sub(r'@admin\.register\(PageTemplate\)\s*\nclass PageTemplateAdmin.*?(?=\n@admin|\nclass|\Z)', '', content, flags=re.DOTALL)
    content += "\n" + inline_code

    with open(ADMIN_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("  [OK] admin.py mis à jour (PageBlockInline ajouté).")


def run_django_commands():
    """Lance makemigrations et migrate."""
    print("\n--- Exécution des migrations Django ---")
    try:
        subprocess.run([sys.executable, "manage.py", "makemigrations", "cms"], check=True)
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("  [OK] Migrations appliquées avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"  [ERREUR] Échec lors des migrations : {e}")


def main():
    print("===============================================")
    print("  Installation du CMS Headless - Backend Django")
    print("===============================================\n")

    print("1. Modification de models.py...")
    update_models()

    print("\n2. Mise à jour des serializers...")
    update_serializers()

    print("\n3. Mise à jour de l'admin...")
    update_admin()

    print("\n4. Migrations de base de données...")
    run_django_commands()

    print("\n===============================================")
    print("  Terminé ! Vérifiez les fichiers .bak en cas de souci.")
    print("  N'oubliez pas de faire un 'git diff' pour voir les changements.")
    print("===============================================")


if __name__ == "__main__":
    main()
