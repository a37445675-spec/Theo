"""
Injection du Widget Builder (Elementor-like) - Backend Django.
Ajoute les modèles Widget + ReusableSection, API, admin, seed.

Prérequis : l'app apps/cms/ existe.

Usage : python inject_widget_builder_backend.py
"""
import os
import re
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CMS_DIR = os.path.join(BASE_DIR, "apps", "cms")


WIDGET_MODELS_ADDITION = '''

# ============================================================
#           WIDGET BUILDER (Elementor-like)
# ============================================================

class Widget(models.Model):
    """
    Un widget dans l'arborescence d'une page.
    Peut contenir des enfants (colonnes, sections imbriquées).
    Stocke le contenu et le style en JSON pour être agnostique.
    """

    WIDGET_TYPE_CHOICES = [
        # Structure
        ("section", "Section"),
        ("column", "Colonne"),
        ("container", "Conteneur"),
        # Basiques
        ("heading", "Titre"),
        ("text", "Texte"),
        ("image", "Image"),
        ("button", "Bouton"),
        ("divider", "Séparateur"),
        ("spacer", "Espace"),
        ("icon", "Icône"),
        ("icon_box", "Bloc icône"),
        ("html", "Code HTML"),
        # Mise en page
        ("tabs", "Onglets"),
        ("accordion", "Accordéon"),
        ("toggle", "Boîte à bascule"),
        ("table_of_contents", "Table des matières"),
        ("progress", "Barre de progression"),
        ("counter", "Compteur animé"),
        ("countdown", "Compte à rebours"),
        # Média
        ("gallery", "Galerie"),
        ("carousel", "Carrousel"),
        ("carousel_loop", "Carrousel en boucle"),
        ("carousel_media", "Carrousel média"),
        ("carousel_nested", "Carrousel imbriqué"),
        ("slides", "Diapositives"),
        ("video", "Vidéo"),
        ("video_playlist", "Liste de lecture vidéo"),
        ("lottie", "Lottie"),
        ("hotspot", "Point d'accès (Hotspot)"),
        # Marketing / Social
        ("cta", "Appel à l'action"),
        ("testimonial", "Témoignage"),
        ("testimonial_carousel", "Témoignages en carrousel"),
        ("review", "Avis"),
        ("pricing_table", "Tableau des prix"),
        ("pricing_list", "Liste des prix"),
        ("progress_review", "Suivi des avis"),
        ("social_share", "Boutons de partage"),
        ("facebook_page", "Page Facebook"),
        ("facebook_button", "Bouton Facebook"),
        ("facebook_embed", "Intégration Facebook"),
        ("facebook_comments", "Commentaires Facebook"),
        ("paypal_button", "Bouton PayPal"),
        ("stripe_button", "Bouton Stripe"),
        ("portfolio", "Portfolio"),
        # Formulaires & Auth
        ("form", "Formulaire"),
        ("login", "Connexion"),
        ("menu", "Menu de navigation"),
        ("mega_menu", "Méga menu"),
        ("off_canvas", "Hors cadre"),
        # Dynamique
        ("archive_posts", "Archive Posts"),
        ("archive_title", "Archive Title"),
        ("breadcrumbs", "Breadcrumbs"),
        ("post_comments", "Post Comments"),
        ("post_content", "Post Content"),
        ("post_excerpt", "Post Excerpt"),
        ("post_info", "Post Info"),
        ("post_navigation", "Post Navigation"),
        ("post_title", "Post Title"),
        ("site_logo", "Site Logo"),
        ("site_title", "Site Title"),
        ("sitelink_search", "Sitelink Search Box"),
        ("loop_grid", "Loop Grid"),
        ("loop_carousel", "Loop Carousel"),
        ("taxonomy", "Taxonomy"),
        ("author_box", "Author Box"),
        ("post_portfolio", "Post/Portfolio"),
        # WooCommerce
        ("products", "Products"),
        ("wc_breadcrumbs", "WooCommerce Breadcrumbs"),
        ("product_title", "Product Title"),
        ("product_images", "Product Images"),
        ("product_price", "Product Price"),
        ("add_to_cart", "Add to Cart"),
        ("product_rating", "Product Rating"),
        ("product_stock", "Product Stock"),
        ("product_meta", "Product Meta"),
        ("short_description", "Short Description"),
        ("product_content", "Product Content"),
        ("product_data_tabs", "Product Data Tabs"),
        ("upsells", "Upsells"),
        ("related_products", "Related Products"),
        ("product_categories", "Product Categories"),
        ("menu_cart", "Menu Cart"),
        ("cart", "Cart"),
        ("checkout", "Checkout"),
        ("my_account", "My Account"),
        ("purchase_summary", "Purchase Summary"),
    ]

    # === Rattachement ===
    page = models.ForeignKey(
        "PageTemplate", on_delete=models.CASCADE,
        related_name="widgets", null=True, blank=True
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE,
        related_name="children", null=True, blank=True
    )

    # === Type ===
    widget_type = models.CharField(max_length=40, choices=WIDGET_TYPE_CHOICES)
    name = models.CharField(max_length=100, blank=True, help_text="Nom custom dans l'éditeur")

    # === Contenu ===
    content = models.JSONField(
        default=dict, blank=True,
        help_text='Contenu du widget. Ex: {"text": "Bonjour", "level": "h1"}'
    )

    # === Style (responsive : desktop / tablet / mobile) ===
    style = models.JSONField(
        default=dict, blank=True,
        help_text='Style responsive. Ex: {"padding": "80px 0", "background": "#fff"}'
    )

    # === Avancé ===
    custom_css = models.TextField(blank=True)
    custom_id = models.CharField(max_length=100, blank=True)
    custom_classes = models.CharField(max_length=255, blank=True)
    animation = models.CharField(max_length=50, blank=True, help_text="fade, slide, zoom...")

    # === Ordre & visibilité ===
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Widget"
        verbose_name_plural = "Widgets"

    def __str__(self):
        return f"{self.get_widget_type_display()} #{self.pk or 'new'}"

    def save(self, *args, **kwargs):
        # Validation : un widget ne peut pas être son propre parent
        if self.parent and self.parent.pk == self.pk:
            self.parent = None
        super().save(*args, **kwargs)


class ReusableSection(models.Model):
    """Une section sauvegardée, réutilisable sur plusieurs pages."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="cms/sections/", blank=True, null=True)
    structure = models.JSONField(
        default=dict,
        help_text="Arbre complet de widgets sérialisé en JSON."
    )
    category = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Section réutilisable"
        verbose_name_plural = "Sections réutilisables"

    def __str__(self):
        return self.name
'''


WIDGET_SERIALIZERS_PY = '''"""Serializers DRF pour le Widget Builder."""
from rest_framework import serializers
from .models import Widget, ReusableSection


class WidgetSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Widget
        fields = [
            "id", "page", "parent", "widget_type", "name",
            "content", "style",
            "custom_css", "custom_id", "custom_classes", "animation",
            "order", "is_visible", "is_locked",
            "children",
        ]

    def get_children(self, obj):
        children = obj.children.order_by("order")
        return WidgetSerializer(children, many=True).data


class ReusableSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReusableSection
        fields = "__all__"
'''


WIDGET_VIEWS_PY = '''"""Vues API pour le Widget Builder."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from .models import Widget, ReusableSection, PageTemplate
from .serializers import WidgetSerializer, ReusableSectionSerializer


class WidgetViewSet(viewsets.ModelViewSet):
    """
    API pour gérer l'arbre de widgets d'une page.

    GET    /api/v1/cms/widgets/?page={id}     → arbre complet d'une page
    POST   /api/v1/cms/widgets/               → créer un widget
    PATCH  /api/v1/cms/widgets/{id}/          → modifier
    DELETE /api/v1/cms/widgets/{id}/          → supprimer (cascade)
    POST   /api/v1/cms/widgets/save-tree/     → sauvegarde bulk de l'arbre
    POST   /api/v1/cms/widgets/{id}/duplicate/ → dupliquer un widget
    """
    queryset = Widget.objects.all()
    serializer_class = WidgetSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = super().get_queryset()
        page_id = self.request.query_params.get("page")
        if page_id:
            qs = qs.filter(page_id=page_id, parent__isnull=True)
        return qs

    @action(detail=False, methods=["post"], url_path="save-tree")
    def save_tree(self, request):
        """
        Sauvegarde l'arbre complet d'une page en une seule requête.
        Body : {"page": 1, "tree": [{...}, {...}]}
        """
        page_id = request.data.get("page")
        tree = request.data.get("tree", [])

        if not page_id:
            return Response({"detail": "Le champ 'page' est requis."},
                            status=status.HTTP_400_BAD_REQUEST)

        page = get_object_or_404(PageTemplate, id=page_id)

        # Supprimer tous les widgets existants de la page
        Widget.objects.filter(page=page).delete()

        # Recréer l'arbre
        created = self._create_widgets(tree, page=page, parent=None)

        return Response({
            "page": page_id,
            "created": created,
            "count": Widget.objects.filter(page=page).count(),
        })

    @staticmethod
    def _create_widgets(items, page, parent):
        count = 0
        for idx, item in enumerate(items):
            widget = Widget.objects.create(
                page=page,
                parent=parent,
                widget_type=item.get("widget_type", "text"),
                name=item.get("name", ""),
                content=item.get("content", {}),
                style=item.get("style", {}),
                custom_css=item.get("custom_css", ""),
                custom_id=item.get("custom_id", ""),
                custom_classes=item.get("custom_classes", ""),
                animation=item.get("animation", ""),
                order=idx,
                is_visible=item.get("is_visible", True),
                is_locked=item.get("is_locked", False),
            )
            count += 1
            if item.get("children"):
                count += WidgetViewSet._create_widgets(
                    item["children"], page=page, parent=widget
                )
        return count

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        """Duplique un widget et tous ses enfants."""
        original = self.get_object()

        def clone(widget, parent=None):
            new = Widget.objects.create(
                page=widget.page, parent=parent,
                widget_type=widget.widget_type,
                name=f"{widget.name} (copie)",
                content=widget.content, style=widget.style,
                custom_css=widget.custom_css, custom_id=widget.custom_id,
                custom_classes=widget.custom_classes, animation=widget.animation,
                order=widget.order + 1, is_visible=widget.is_visible,
            )
            for child in widget.children.all():
                clone(child, parent=new)
            return new

        new_widget = clone(original, parent=original.parent)
        return Response({"id": new_widget.id}, status=status.HTTP_201_CREATED)


class ReusableSectionViewSet(viewsets.ModelViewSet):
    queryset = ReusableSection.objects.filter(is_active=True)
    serializer_class = ReusableSectionSerializer
    permission_classes = [IsAdminUser]
'''


WIDGET_URLS_PY = '''"""URLs pour le Widget Builder."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .widget_views import WidgetViewSet, ReusableSectionViewSet

router = DefaultRouter()
router.register(r"widgets", WidgetViewSet, basename="widget")
router.register(r"reusable-sections", ReusableSectionViewSet, basename="reusable-section")

urlpatterns = [
    path("", include(router.urls)),
]
'''


WIDGET_ADMIN_PY = '''"""Admin Django pour le Widget Builder."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Widget, ReusableSection


class WidgetChildInline(admin.TabularInline):
    model = Widget
    fk_name = "parent"
    extra = 0
    fields = ("order", "widget_type", "name", "is_visible")
    ordering = ("order",)
    show_change_link = True


@admin.register(Widget)
class WidgetAdmin(admin.ModelAdmin):
    list_display = ("id", "type_badge", "name", "page", "parent", "order", "is_visible")
    list_filter = ("widget_type", "is_visible", "page")
    search_fields = ("name", "widget_type")
    list_editable = ("order", "is_visible")
    inlines = [WidgetChildInline]
    ordering = ("page", "order")

    fieldsets = (
        ("Identification", {"fields": ("page", "parent", "widget_type", "name")}),
        ("Contenu (JSON)", {"fields": ("content",), "classes": ("collapse",)}),
        ("Style (JSON)", {"fields": ("style",), "classes": ("collapse",)}),
        ("Avancé", {
            "fields": ("custom_css", "custom_id", "custom_classes", "animation"),
            "classes": ("collapse",)
        }),
        ("Ordre & Visibilité", {"fields": ("order", "is_visible", "is_locked")}),
    )

    def type_badge(self, obj):
        colors = {
            "section": "#C1652F", "column": "#8A4B26",
            "heading": "#2F4A3C", "text": "#6B6259",
            "image": "#D4A843", "button": "#16A34A",
            "product_grid": "#DC2626", "carousel": "#1E40AF",
        }
        color = colors.get(obj.widget_type, "#221B15")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;">{}</span>',
            color, obj.get_widget_type_display()
        )
    type_badge.short_description = "Type"


@admin.register(ReusableSection)
class ReusableSectionAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description")
'''

WIDGET_SEED_PY = '''"""Crée une page d'exemple avec des widgets de démo."""
from django.core.management.base import BaseCommand
from apps.cms.models import PageTemplate, Widget


class Command(BaseCommand):
    help = "Crée une page d'exemple avec des widgets variés."

    def handle(self, *args, **options):
        page, created = PageTemplate.objects.get_or_create(
            name="Page Builder Démo",
            defaults={"template_type": "home"}
        )
        if not created and page.widgets.exists():
            self.stdout.write(self.style.WARNING(
                "La page a déjà des widgets. Étape ignorée."
            ))
            return

        page.widgets.all().delete()

        # Section Hero
        hero = Widget.objects.create(
            page=page, widget_type="section",
            name="Section Hero", order=0,
            content={}, style={"padding": "80px 0", "background": "#F7F0E4"}
        )
        col_left = Widget.objects.create(
            page=page, parent=hero, widget_type="column",
            name="Colonne gauche", order=0,
            content={}, style={"width": "50%"}
        )
        Widget.objects.create(
            page=page, parent=col_left, widget_type="heading",
            order=0,
            content={"text": "La beauté d'Afrique, sublimée.", "level": "h1"},
            style={"color": "#221B15", "marginBottom": "16px"}
        )
        Widget.objects.create(
            page=page, parent=col_left, widget_type="text",
            order=1,
            content={"text": "Découvrez notre sélection de cosmétiques naturels, mode et maison."},
            style={"fontSize": "18px", "color": "#6B6259"}
        )
        Widget.objects.create(
            page=page, parent=col_left, widget_type="button",
            order=2,
            content={"label": "Découvrir", "url": "/boutique/cosmetiques"},
            style={"backgroundColor": "#C1652F", "color": "#fff"}
        )
        col_right = Widget.objects.create(
            page=page, parent=hero, widget_type="column",
            name="Colonne droite", order=1,
            content={}, style={"width": "50%"}
        )
        Widget.objects.create(
            page=page, parent=col_right, widget_type="image",
            order=0,
            content={"src": "/fallbacks/hero-fallback.jpg", "alt": "Hero"},
            style={"borderRadius": "24px"}
        )

        self.stdout.write(self.style.SUCCESS(
            "[OK] Page 'Page Builder Démo' créée avec 6 widgets."
        ))
'''


# ============================================================
#                   FONCTIONS UTILITAIRES
# ============================================================

def find_cms_models():
    return os.path.join(CMS_DIR, "models.py")


def append_to_models():
    """Ajoute les modèles Widget et ReusableSection à la fin de cms/models.py."""
    path = find_cms_models()
    if not os.path.exists(path):
        print(f"  [ERREUR] {path} introuvable.")
        return False

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if "class Widget(models.Model)" in content:
        print("  [SKIP] class Widget déjà présente")
        return True

    shutil.copy2(path, path + ".bak")
    print(f"  [BACKUP] {os.path.relpath(path, BASE_DIR)}.bak")

    with open(path, "a", encoding="utf-8") as f:
        f.write(WIDGET_MODELS_ADDITION)

    print(f"  [OK] Modèles Widget + ReusableSection ajoutés à cms/models.py")
    return True


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    label = os.path.relpath(path, BASE_DIR)

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            if f.read().strip() == content.strip():
                print(f"  [SKIP] {label}")
                return
        shutil.copy2(path, path + ".bak")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {label}")


def find_urls():
    for c in [
        os.path.join(BASE_DIR, "config", "urls.py"),
        os.path.join(BASE_DIR, "nawa_commerce", "urls.py"),
    ]:
        if os.path.exists(c):
            return c
    return None


def add_url_route():
    urls = find_urls()
    if not urls:
        print("  [ERREUR] urls.py introuvable.")
        return

    with open(urls, "r", encoding="utf-8") as f:
        content = f.read()

    if "apps.cms.widget_urls" in content:
        print("  [SKIP] route widget déjà présente")
        return

    shutil.copy2(urls, urls + ".bak")

    m = re.search(r"urlpatterns\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if not m:
        return

    insertion = '\n    # === Widget Builder ===\n    path("api/v1/cms/", include("apps.cms.widget_urls")),\n'
    new_block = m.group(1).rstrip() + insertion
    new_content = content[:m.start(1)] + new_block + content[m.end(1):]

    with open(urls, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("  [OK] routes Widget Builder ajoutées à urls.py")


def run_cmd(*args, allow_fail=False):
    try:
        subprocess.run([sys.executable, "manage.py", *args], check=True)
    except subprocess.CalledProcessError as e:
        print(f"  [ERREUR] {e}")
        if not allow_fail:
            sys.exit(1)


def main():
    print("=" * 60)
    print("  INJECTION WIDGET BUILDER - BACKEND")
    print("=" * 60)

    print("\n1. Ajout des modèles à apps/cms/models.py...")
    append_to_models()

    print("\n2. Création des serializers, vues, URLs, admin...")
    write_file(os.path.join(CMS_DIR, "widget_serializers.py"), WIDGET_SERIALIZERS_PY)
    write_file(os.path.join(CMS_DIR, "widget_views.py"), WIDGET_VIEWS_PY)
    write_file(os.path.join(CMS_DIR, "widget_urls.py"), WIDGET_URLS_PY)

    # On ne touche PAS à admin.py existant : on crée un widget_admin.py séparé
    write_file(os.path.join(CMS_DIR, "widget_admin.py"), WIDGET_ADMIN_PY)

    # Import auto du widget_admin dans l'admin.py principal
    admin_path = os.path.join(CMS_DIR, "admin.py")
    if os.path.exists(admin_path):
        with open(admin_path, "r", encoding="utf-8") as f:
            admin_content = f.read()
        if "widget_admin" not in admin_content:
            shutil.copy2(admin_path, admin_path + ".bak")
            with open(admin_path, "a", encoding="utf-8") as f:
                f.write("\n\n# === Widget Builder (import automatique) ===\nfrom . import widget_admin  # noqa: F401,E402\n")

    print("\n3. Création du seed...")
    seed_dir = os.path.join(CMS_DIR, "management", "commands")
    os.makedirs(seed_dir, exist_ok=True)
    for sub in ["management", "management/commands"]:
        init_path = os.path.join(CMS_DIR, sub, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, "w") as f:
                f.write("")
    write_file(os.path.join(seed_dir, "seed_page_builder.py"), WIDGET_SEED_PY)

    print("\n4. Mise à jour de urls.py...")
    add_url_route()

    print("\n5. Migrations...")
    run_cmd("makemigrations", "cms", allow_fail=True)
    run_cmd("migrate")

    print("\n6. Seed de la page démo...")
    run_cmd("seed_page_builder", allow_fail=True)

    print("\n" + "=" * 60)
    print("  TERMINÉ !")
    print("=" * 60)
    print("\nEndpoints :")
    print("  Widgets : http://127.0.0.1:8000/api/v1/cms/widgets/?page=1")
    print("  Sections réutilisables : http://127.0.0.1:8000/api/v1/cms/reusable-sections/")
    print("\nAdmin :")
    print("  Widgets : http://127.0.0.1:8000/admin/cms/widget/")


if __name__ == "__main__":
    main()