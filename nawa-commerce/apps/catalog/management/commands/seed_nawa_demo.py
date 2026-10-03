"""
Commande de seed multi-verticales pour NAWA Commerce.

python manage.py seed_nawa_demo

Crée : les AttributeDefinition/AttributeSet des 4 verticales (cosmétiques,
vêtements, chaussures, électroménager), les catégories, marques/productrices,
12+ produits cosmétiques, 4+ vêtements, 4+ chaussures, 4+ électroménagers,
8+ articles de blog, des coupons, un abonnement démo, les rôles/utilisateurs
de démonstration, et les données du Theme Builder headless (PageTemplate,
PageBlock, GlobalDesignSystem, DynamicTag, SiteKit).
"""
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Seed de démonstration multi-verticales pour NAWA Commerce."

    def handle(self, *args, **options):
        self.stdout.write("Seed NAWA Commerce — démarrage...")
        self.seed_users_and_roles()
        attribute_sets = self.seed_attributes()
        categories = self.seed_categories(attribute_sets)
        brands = self.seed_brands()
        self.seed_cosmetics(categories, brands)
        self.seed_clothing(categories, brands)
        self.seed_shoes(categories, brands)
        self.seed_appliances(categories, brands)
        self.seed_blog()
        self.seed_promotions(categories)
        self.seed_cms()
        self.stdout.write(self.style.SUCCESS("Seed NAWA Commerce terminé."))

    # ------------------------------------------------------------------
    def seed_users_and_roles(self):
        from apps.accounts.models import ROLE_ADMINISTRATOR, ROLE_CUSTOMER, ROLE_SHOP_MANAGER, ROLE_VENDOR, User

        for role in [ROLE_CUSTOMER, ROLE_SHOP_MANAGER, ROLE_ADMINISTRATOR, ROLE_VENDOR]:
            Group.objects.get_or_create(name=role)

        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser("admin", "admin@nawa.com", "ChangeMoi123!")
            admin.groups.add(Group.objects.get(name=ROLE_ADMINISTRATOR))

        manager, created = User.objects.get_or_create(username="manager_aicha", defaults={"email": "aicha@nawa.com", "first_name": "Aïcha", "last_name": "Koné"})
        if created:
            manager.set_password("Demo1234!")
            manager.save()
        manager.groups.add(Group.objects.get(name=ROLE_SHOP_MANAGER))

        customer, created = User.objects.get_or_create(username="client_fatou", defaults={"email": "fatou@example.com", "first_name": "Fatou", "last_name": "Diallo"})
        if created:
            customer.set_password("Demo1234!")
            customer.save()
        customer.groups.add(Group.objects.get(name=ROLE_CUSTOMER))
        self.demo_customer = customer

        self.stdout.write("  ✓ Utilisateurs & rôles")

    # ------------------------------------------------------------------
    def seed_attributes(self):
        from apps.catalog.models import AttributeDefinition, AttributeSet, AttributeSetItem, AttributeType

        def make_attr(code, label, atype, unit="", choices=None):
            attr, _ = AttributeDefinition.objects.get_or_create(
                code=code, defaults={"label": label, "attribute_type": atype, "unit": unit, "choices": choices or []}
            )
            return attr

        def make_set(name, items):
            attr_set, _ = AttributeSet.objects.get_or_create(name=name)
            for attr, required in items:
                AttributeSetItem.objects.get_or_create(attribute_set=attr_set, attribute=attr, defaults={"is_required": required})
            return attr_set

        # Cosmétiques
        type_peau = make_attr("type_peau", "Type de peau", AttributeType.SINGLE_CHOICE, choices=["sèche", "grasse", "mixte", "normale", "sensible"])
        texture_cheveux = make_attr("texture_cheveux", "Texture cheveux", AttributeType.SINGLE_CHOICE, choices=["crépus", "bouclés", "ondulés", "lisses"])
        objectifs = make_attr("objectifs", "Objectifs", AttributeType.MULTI_CHOICE, choices=["hydratation", "brillance", "croissance", "anti-chute", "réparation", "définition des boucles"])
        sensibilites = make_attr("sensibilites", "Sensibilités", AttributeType.MULTI_CHOICE, choices=["sans sulfates", "sans silicones", "sans parfum", "vegan"])
        contenance = make_attr("contenance_ml", "Contenance", AttributeType.NUMBER, unit="ml")
        cosmetics_set = make_set("Cosmétiques", [(type_peau, False), (texture_cheveux, False), (objectifs, False), (sensibilites, False), (contenance, False)])

        # Vêtements
        taille = make_attr("taille", "Taille", AttributeType.SINGLE_CHOICE, choices=["XS", "S", "M", "L", "XL", "XXL"])
        couleur = make_attr("couleur", "Couleur", AttributeType.TEXT)
        matiere_vetement = make_attr("matiere", "Matière", AttributeType.SINGLE_CHOICE, choices=["coton", "lin", "soie", "polyester", "laine", "bazin"])
        genre = make_attr("genre", "Genre", AttributeType.SINGLE_CHOICE, choices=["femme", "homme", "unisexe", "enfant"])
        clothing_set = make_set("Vêtements", [(taille, True), (couleur, True), (matiere_vetement, False), (genre, True)])

        # Chaussures
        pointure = make_attr("pointure", "Pointure", AttributeType.NUMBER, unit="EU")
        largeur_chaussure = make_attr("largeur_chaussure", "Largeur", AttributeType.SINGLE_CHOICE, choices=["étroite", "standard", "large"])
        matiere_chaussure = make_attr("matiere_chaussure", "Matière", AttributeType.SINGLE_CHOICE, choices=["cuir", "toile", "synthétique", "daim"])
        shoes_set = make_set("Chaussures", [(pointure, False), (largeur_chaussure, False), (matiere_chaussure, False), (couleur, False)])

        # Électroménager
        puissance = make_attr("puissance_w", "Puissance", AttributeType.NUMBER, unit="W")
        voltage = make_attr("voltage", "Voltage", AttributeType.SINGLE_CHOICE, choices=["110V", "220V", "110V/220V"])
        garantie = make_attr("garantie", "Garantie", AttributeType.NUMBER, unit="ans")
        classe_energetique = make_attr("classe_energetique", "Classe énergétique", AttributeType.SINGLE_CHOICE, choices=["A+++", "A++", "A+", "A", "B", "C"])
        dimensions = make_attr("dimensions", "Dimensions", AttributeType.TEXT)
        appliance_set = make_set("Électroménager", [(puissance, True), (voltage, True), (garantie, False), (classe_energetique, False), (dimensions, False)])

        self.stdout.write("  ✓ Attributs dynamiques (4 verticales)")
        return {"cosmetics": cosmetics_set, "clothing": clothing_set, "shoes": shoes_set, "appliances": appliance_set}

    # ------------------------------------------------------------------
    def seed_categories(self, attribute_sets):
        from apps.catalog.models import Category

        def make_cat(name, attr_set=None, parent=None, icon=""):
            cat, _ = Category.objects.get_or_create(name=name, defaults={"attribute_set": attr_set, "parent": parent, "icon": icon})
            return cat

        cosmetics_root = make_cat("Cosmétiques", attribute_sets["cosmetics"], icon="🧴")
        cheveux = make_cat("Cheveux crépus & bouclés", parent=cosmetics_root)
        peau = make_cat("Soins visage", parent=cosmetics_root)
        corps = make_cat("Soins du corps", parent=cosmetics_root)
        bebe = make_cat("Soins bébé", parent=cosmetics_root)
        maquillage = make_cat("Maquillage naturel", parent=cosmetics_root)

        clothing = make_cat("Vêtements", attribute_sets["clothing"], icon="👗")
        shoes = make_cat("Chaussures", attribute_sets["shoes"], icon="👟")
        appliances = make_cat("Électroménager", attribute_sets["appliances"], icon="🔌")

        self.stdout.write("  ✓ Catégories multi-verticales")
        return {
            "cosmetics_root": cosmetics_root, "cheveux": cheveux, "peau": peau, "corps": corps,
            "bebe": bebe, "maquillage": maquillage, "clothing": clothing, "shoes": shoes, "appliances": appliances,
        }

    # ------------------------------------------------------------------
    def seed_brands(self):
        from apps.catalog.models import Brand

        data = [
            ("NAWA Rituel", "Côte d'Ivoire", "La marque maison NAWA, karité et huiles pressées à froid."),
            ("Coopérative Kaya", "Burkina Faso", "Coopérative de productrices de karité biologique équitable."),
            ("Atelier Téranga", "Sénégal", "Confection textile artisanale, bazin et wax."),
            ("Sotra Électro", "Côte d'Ivoire", "Distributeur d'électroménager pour le marché ouest-africain."),
            ("Pas Global", "France", "Chaussures urbaines et sportives."),
            ("Douceur d'Ébène", "Côte d'Ivoire", "Cosmétiques bébé et soins doux naturels."),
        ]
        brands = {}
        for name, country, story in data:
            brand, _ = Brand.objects.get_or_create(name=name, defaults={"country": country, "story": story})
            brands[name] = brand
        self.stdout.write("  ✓ Marques & productrices")
        return brands

    # ------------------------------------------------------------------
    def seed_cosmetics(self, categories, brands):
        from apps.catalog.models import Product, ProductStatus

        products = [
            ("Beurre de Karité Pur", categories["corps"], brands["NAWA Rituel"], Decimal("14.90"), {"type_peau": "sèche", "objectifs": ["hydratation", "réparation"], "sensibilites": ["vegan"], "contenance_ml": 200}),
            ("Huile de Baobab Précieuse", categories["peau"], brands["NAWA Rituel"], Decimal("19.90"), {"type_peau": "sensible", "objectifs": ["hydratation"], "sensibilites": ["sans parfum"], "contenance_ml": 100}),
            ("Crème Hydratante Karité-Miel", categories["peau"], brands["Coopérative Kaya"], Decimal("16.50"), {"type_peau": "normale", "objectifs": ["hydratation"], "contenance_ml": 150}),
            ("Masque Capillaire Croissance", categories["cheveux"], brands["NAWA Rituel"], Decimal("22.00"), {"texture_cheveux": "crépus", "objectifs": ["croissance", "anti-chute"], "sensibilites": ["sans sulfates"], "contenance_ml": 250}),
            ("Gelée Définition Boucles", categories["cheveux"], brands["NAWA Rituel"], Decimal("13.90"), {"texture_cheveux": "bouclés", "objectifs": ["définition des boucles"], "contenance_ml": 200}),
            ("Shampoing Doux Sans Sulfates", categories["cheveux"], brands["Coopérative Kaya"], Decimal("11.90"), {"texture_cheveux": "ondulés", "objectifs": ["hydratation"], "sensibilites": ["sans sulfates", "vegan"], "contenance_ml": 300}),
            ("Huile de Ricin Fortifiante", categories["cheveux"], brands["NAWA Rituel"], Decimal("9.90"), {"texture_cheveux": "crépus", "objectifs": ["croissance"], "contenance_ml": 100}),
            ("Savon Noir Africain Gommant", categories["corps"], brands["Coopérative Kaya"], Decimal("8.50"), {"type_peau": "grasse", "objectifs": ["hydratation"], "contenance_ml": 200}),
            ("Lait Corporel Beurre de Cacao", categories["corps"], brands["NAWA Rituel"], Decimal("15.90"), {"type_peau": "sèche", "objectifs": ["hydratation"], "contenance_ml": 250}),
            ("Baume Change Bébé Calendula", categories["bebe"], brands["Douceur d'Ébène"], Decimal("10.90"), {"type_peau": "sensible", "sensibilites": ["sans parfum", "vegan"], "contenance_ml": 100}),
            ("Huile de Massage Bébé", categories["bebe"], brands["Douceur d'Ébène"], Decimal("12.90"), {"type_peau": "sensible", "objectifs": ["hydratation"], "contenance_ml": 150}),
            ("Rouge à Lèvres Karité Teinté", categories["maquillage"], brands["NAWA Rituel"], Decimal("17.90"), {"objectifs": ["hydratation"], "sensibilites": ["vegan"]}),
            ("Poudre Matifiante Minérale", categories["maquillage"], brands["Coopérative Kaya"], Decimal("21.90"), {"type_peau": "grasse", "sensibilites": ["vegan"]}),
        ]
        for i, (name, category, brand, price, attrs) in enumerate(products):
            Product.objects.get_or_create(
                sku=f"COS-{i + 1:03d}", defaults={
                    "name": name, "category": category, "brand": brand, "price": price, "status": ProductStatus.ACTIVE,
                    "stock": 40 + i * 3, "attributes": attrs, "short_description": f"{name} — cosmétique naturel NAWA.",
                    "description": f"{name}, formulé à partir d'ingrédients naturels tracés jusqu'aux productrices partenaires.",
                    "is_featured": i < 4,
                },
            )
        self.stdout.write(f"  ✓ {len(products)} produits cosmétiques")

    # ------------------------------------------------------------------
    def seed_clothing(self, categories, brands):
        from apps.catalog.models import Product, ProductStatus, ProductType, ProductVariant

        products = [
            ("Robe Wax Imprimée", Decimal("39.90"), {"taille": "M", "couleur": "orange", "matiere": "coton", "genre": "femme"}),
            ("Chemise Bazin Brodée", Decimal("54.90"), {"taille": "L", "couleur": "blanc", "matiere": "bazin", "genre": "homme"}),
            ("Ensemble Enfant Wax", Decimal("29.90"), {"taille": "S", "couleur": "vert", "matiere": "coton", "genre": "enfant"}),
            ("Boubou Léger Unisexe", Decimal("44.90"), {"taille": "L", "couleur": "bleu", "matiere": "lin", "genre": "unisexe"}),
        ]
        for i, (name, price, attrs) in enumerate(products):
            product, created = Product.objects.get_or_create(
                sku=f"CLO-{i + 1:03d}", defaults={
                    "name": name, "category": categories["clothing"], "brand": brands["Atelier Téranga"],
                    "price": price, "status": ProductStatus.ACTIVE, "product_type": ProductType.VARIANT,
                    "stock": 0, "attributes": attrs, "short_description": f"{name} — confection artisanale.",
                },
            )
            if created:
                for size in ["S", "M", "L"]:
                    ProductVariant.objects.get_or_create(product=product, sku=f"{product.sku}-{size}", defaults={"attributes": {"taille": size}, "stock": 15})
        self.stdout.write(f"  ✓ {len(products)} vêtements (+ variantes tailles)")

    # ------------------------------------------------------------------
    def seed_shoes(self, categories, brands):
        from apps.catalog.models import Product, ProductStatus, ProductType, ProductVariant

        products = [
    ("Sneakers Urbaines Toile", Decimal("59.90"), {"pointure": 40, "largeur_chaussure": "standard", "matiere_chaussure": "toile", "couleur": "noir"}),
    ("Sandales Cuir Tressé", Decimal("49.90"), {"pointure": 40, "largeur_chaussure": "large", "matiere_chaussure": "cuir", "couleur": "marron"}),
    ("Boots Daim Élégantes", Decimal("74.90"), {"pointure": 40, "largeur_chaussure": "standard", "matiere_chaussure": "daim", "couleur": "camel"}),
    ("Sneakers Running Légères", Decimal("64.90"), {"pointure": 40, "largeur_chaussure": "étroite", "matiere_chaussure": "synthétique", "couleur": "blanc"}),
]
        for i, (name, price, attrs) in enumerate(products):
            product, created = Product.objects.get_or_create(
                sku=f"SHO-{i + 1:03d}", defaults={
                    "name": name, "category": categories["shoes"], "brand": brands["Pas Global"],
                    "price": price, "status": ProductStatus.ACTIVE, "product_type": ProductType.VARIANT,
                    "stock": 0, "attributes": attrs, "short_description": f"{name}.",
                },
            )
            if created:
                for pointure in [38, 40, 42, 44]:
                    ProductVariant.objects.get_or_create(product=product, sku=f"{product.sku}-{pointure}", defaults={"attributes": {"pointure": pointure}, "stock": 8})
        self.stdout.write(f"  ✓ {len(products)} chaussures (+ variantes pointures)")

    # ------------------------------------------------------------------
    def seed_appliances(self, categories, brands):
        from apps.catalog.models import Product, ProductStatus

        products = [
            ("Réfrigérateur 250L No Frost", Decimal("389.00"), {"puissance_w": 150, "voltage": "220V", "garantie": 2, "classe_energetique": "A+", "dimensions": "60x65x170cm"}),
            ("Climatiseur Split 12000 BTU", Decimal("459.00"), {"puissance_w": 1200, "voltage": "220V", "garantie": 3, "classe_energetique": "A++", "dimensions": "80x28x20cm"}),
            ("Mixeur Blender Pro 1000W", Decimal("59.90"), {"puissance_w": 1000, "voltage": "110V/220V", "garantie": 1, "classe_energetique": "A", "dimensions": "20x20x40cm"}),
            ("Machine à Laver 7kg", Decimal("329.00"), {"puissance_w": 2000, "voltage": "220V", "garantie": 2, "classe_energetique": "A+++", "dimensions": "60x60x85cm"}),
        ]
        for i, (name, price, attrs) in enumerate(products):
            Product.objects.get_or_create(
                sku=f"APP-{i + 1:03d}", defaults={
                    "name": name, "category": categories["appliances"], "brand": brands["Sotra Électro"],
                    "price": price, "status": ProductStatus.ACTIVE, "stock": 12 + i * 2, "attributes": attrs,
                    "short_description": f"{name} — garantie {attrs['garantie']} ans.",
                    "weight_kg": Decimal("15.5"),
                },
            )
        self.stdout.write(f"  ✓ {len(products)} produits électroménager")

    # ------------------------------------------------------------------
    def seed_blog(self):
        from apps.blog.models import BlogCategory, Post

        categories_data = ["Rituels cheveux", "Soins de la peau", "Mode & style", "Astuces maison"]
        blog_categories = {}
        for name in categories_data:
            cat, _ = BlogCategory.objects.get_or_create(name=name)
            blog_categories[name] = cat

        posts = [
            ("5 gestes pour hydrater des cheveux crépus", "Rituels cheveux"),
            ("Le beurre de karité, allié beauté millénaire", "Soins de la peau"),
            ("Comment associer le wax à une garde-robe moderne", "Mode & style"),
            ("Bien choisir la puissance de son réfrigérateur", "Astuces maison"),
            ("Routine du soir pour peaux sensibles", "Soins de la peau"),
            ("Définir ses boucles sans agresser la fibre", "Rituels cheveux"),
            ("Entretenir ses chaussures en cuir naturellement", "Mode & style"),
            ("Économiser l'énergie avec la classe A+++", "Astuces maison"),
        ]
        for title, cat_name in posts:
            Post.objects.get_or_create(
                title=title, defaults={
                    "category": blog_categories[cat_name], "status": Post.STATUS_PUBLISHED, "published_at": timezone.now(),
                    "excerpt": f"{title} — conseils et bonnes pratiques NAWA.",
                    "content": f"{title}\n\nContenu détaillé à venir sur ce sujet, rédigé par l'équipe éditoriale NAWA.",
                },
            )
        self.stdout.write(f"  ✓ {len(posts)} articles de blog")

    # ------------------------------------------------------------------
    def seed_promotions(self, categories):
        from apps.promotions.models import Coupon, DiscountType

        Coupon.objects.get_or_create(code="BIENVENUE10", defaults={"discount_type": DiscountType.PERCENT, "discount_value": Decimal("10")})
        Coupon.objects.get_or_create(code="LIVRAISONOFFERTE", defaults={"discount_type": DiscountType.FREE_SHIPPING, "min_spend": Decimal("40")})
        self.stdout.write("  ✓ Coupons de démonstration")

    # ------------------------------------------------------------------
    def seed_cms(self):
        from apps.cms.models import DynamicTag, DynamicTagContext, GlobalDesignSystem, PageBlock, PageTemplate, PageTemplateType, SiteKit

        design_system, _ = GlobalDesignSystem.objects.get_or_create(
            name="NAWA Design System", defaults={
                "global_colors": {"cream": "#F7F0E4", "terracotta": "#C1652F", "clay": "#8A4B26", "forest": "#2F4A3C", "gold": "#D4A843", "charcoal": "#221B15"},
                "global_typography": {"heading": "Fraunces", "body": "Sora"},
                "global_components": {"button_radius": "999px", "card_radius": "16px", "halo": "organic-blur"},
            },
        )

        home_template, _ = PageTemplate.objects.get_or_create(name="Accueil NAWA", defaults={"template_type": PageTemplateType.HOME})
        PageBlock.objects.get_or_create(template=home_template, block_type="hero", order=0, defaults={"config": {"title": "La beauté d'Afrique, sublimée."}})
        PageBlock.objects.get_or_create(template=home_template, block_type="product_grid", order=1, defaults={"config": {"source": "featured", "columns": 4}})
        PageBlock.objects.get_or_create(template=home_template, block_type="blog_list", order=2, defaults={"config": {"limit": 3}})

        product_template, _ = PageTemplate.objects.get_or_create(name="Fiche produit standard", defaults={"template_type": PageTemplateType.SINGLE_PRODUCT})
        PageBlock.objects.get_or_create(template=product_template, block_type="product_single", order=0, defaults={"dynamic_content": {"title": "{{ product.title }}", "price": "{{ product.price }}"}})

        tags = [
            ("product.title", "Titre du produit", DynamicTagContext.PRODUCT),
            ("product.price", "Prix du produit", DynamicTagContext.PRODUCT),
            ("product.image", "Image principale", DynamicTagContext.PRODUCT),
            ("user.display_name", "Nom du client", DynamicTagContext.USER),
            ("order.total", "Total de la commande", DynamicTagContext.ORDER),
        ]
        for source, label, context in tags:
            DynamicTag.objects.get_or_create(source=source, defaults={"label": label, "context": context})

        kit, _ = SiteKit.objects.get_or_create(name="Kit Lancement NAWA", defaults={"description": "Preset de site pour le lancement de la boutique."})
        kit.templates.add(home_template, product_template)

        self.stdout.write("  ✓ Theme Builder headless (design system, templates, dynamic tags, site kit)")
