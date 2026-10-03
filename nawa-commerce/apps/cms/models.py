from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.core.mixins import TimeStampedModel


class MediaAsset(TimeStampedModel):
    file = models.FileField(upload_to="cms/%Y/%m/")
    title = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="+")

    def __str__(self):
        return self.title or self.file.name


class PageTemplateType(models.TextChoices):
    HOME = "home", "Accueil"
    HEADER = "header", "Header (global)"
    FOOTER = "footer", "Footer (global)"
    SINGLE_PRODUCT = "single_product", "Fiche produit"
    PRODUCT_ARCHIVE = "product_archive", "Liste/grille produits"
    CART = "cart", "Panier"
    CHECKOUT = "checkout", "Tunnel de commande"
    MY_ACCOUNT = "my_account", "Mon compte"
    BLOG_LIST = "blog_list", "Liste d'articles"
    BLOG_SINGLE = "blog_single", "Article de blog"
    PAGE_GENERIC = "page_generic", "Page générique"
    NOT_FOUND = "404", "Page 404"


class PageTemplate(TimeStampedModel):
    """Gabarit de page réutilisable (Theme Builder). `display_conditions` cible un gabarit précis selon le contexte."""

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    template_type = models.CharField(max_length=20, choices=PageTemplateType.choices)
    display_conditions = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-priority", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def matches_context(self, context: dict) -> bool:
        for key, value in self.display_conditions.items():
            if context.get(key) != value:
                return False
        return True


class PageBlockType(models.TextChoices):
    HERO = "hero", "Hero"
    HEADING = "heading", "Titre"
    TEXT = "text", "Texte"
    IMAGE = "image", "Image"
    VIDEO = "video", "Vidéo"
    BUTTON = "button", "Bouton"
    SECTION = "section", "Section"
    COLUMNS = "columns", "Colonnes"
    PRODUCT_SINGLE = "product_single", "Widget produit (fiche)"
    PRODUCT_GRID = "product_grid", "Grille de produits"
    BLOG_LIST = "blog_list", "Liste d'articles"
    FAQ = "faq", "FAQ"
    FORM = "form", "Formulaire"
    MENU_CART = "menu_cart", "Mini-panier"
    CART_WIDGET = "cart_widget", "Widget panier complet"
    CHECKOUT_WIDGET = "checkout_widget", "Widget tunnel de commande"
    MY_ACCOUNT_WIDGET = "my_account_widget", "Widget mon compte"


class PageBlock(TimeStampedModel):
    """Bloc ordonné dans un PageTemplate — équivalent d'un widget Elementor."""

    template = models.ForeignKey(PageTemplate, on_delete=models.CASCADE, related_name="blocks")
    block_type = models.CharField(max_length=20, choices=PageBlockType.choices)
    order = models.PositiveIntegerField(default=0)
    config = models.JSONField(default=dict, blank=True)
    dynamic_content = models.JSONField(default=dict, blank=True)
    is_visible = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.get_block_type_display()} — {self.template.name} (#{self.order})"


class GlobalDesignSystem(TimeStampedModel):
    """Design system global — un seul enregistrement actif. Couleurs/typographies/styles de composants de base."""

    name = models.CharField(max_length=100, default="NAWA Design System")
    is_active = models.BooleanField(default=True)
    global_colors = models.JSONField(default=dict)
    global_typography = models.JSONField(default=dict)
    global_components = models.JSONField(default=dict)

    favicon = models.ImageField(upload_to='cms/favicons/', blank=True, null=True, verbose_name="Favicon du site")
    logo_principal = models.ImageField(upload_to='cms/logos/', blank=True, null=True, verbose_name="Logo principal")
    icon_search = models.ImageField(upload_to='cms/icons/', blank=True, null=True, verbose_name="Icône de recherche")
    icon_user = models.ImageField(upload_to='cms/icons/', blank=True, null=True, verbose_name="Icône utilisateur")
    icon_cart = models.ImageField(upload_to='cms/icons/', blank=True, null=True, verbose_name="Icône du panier")
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_active:
            GlobalDesignSystem.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class DynamicTagContext(models.TextChoices):
    PRODUCT = "product", "Produit"
    POST = "post", "Article de blog"
    USER = "user", "Utilisateur"
    ORDER = "order", "Commande"
    SITE = "site", "Site"


class DynamicTag(TimeStampedModel):
    """Registre des dynamic tags exploitables dans PageBlock.config (ex. {{ product.title }})."""

    source = models.CharField(max_length=100, unique=True)
    label = models.CharField(max_length=150)
    context = models.CharField(max_length=10, choices=DynamicTagContext.choices)

    class Meta:
        ordering = ["context", "source"]

    def __str__(self):
        return f"{{{{ {self.source} }}}}"


class SiteKit(TimeStampedModel):
    """Preset de site (campagne, pays, saison) regroupant plusieurs PageTemplate."""

    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField(blank=True)
    templates = models.ManyToManyField(PageTemplate, related_name="site_kits", blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def apply(self):
        for template in self.templates.all():
            PageTemplate.objects.filter(template_type=template.template_type).exclude(pk=template.pk).update(is_active=False)
            template.is_active = True
            template.save(update_fields=["is_active"])


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
