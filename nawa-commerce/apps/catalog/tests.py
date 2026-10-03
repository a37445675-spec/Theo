from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.catalog.models import AttributeDefinition, AttributeSet, AttributeSetItem, AttributeType, Category, Product


class CatalogEAVTestCase(TestCase):
    def setUp(self):
        self.attr_taille = AttributeDefinition.objects.create(
            code="taille", label="Taille", attribute_type=AttributeType.SINGLE_CHOICE, choices=["S", "M", "L", "XL"]
        )
        self.attr_couleur = AttributeDefinition.objects.create(code="couleur", label="Couleur", attribute_type=AttributeType.TEXT)
        self.clothing_set = AttributeSet.objects.create(name="Vêtements")
        AttributeSetItem.objects.create(attribute_set=self.clothing_set, attribute=self.attr_taille, is_required=True)
        AttributeSetItem.objects.create(attribute_set=self.clothing_set, attribute=self.attr_couleur, is_required=False)

        self.attr_voltage = AttributeDefinition.objects.create(
            code="voltage", label="Voltage", attribute_type=AttributeType.SINGLE_CHOICE, choices=["110V", "220V"]
        )
        self.attr_garantie = AttributeDefinition.objects.create(code="garantie", label="Garantie", attribute_type=AttributeType.NUMBER, unit="mois")
        self.appliance_set = AttributeSet.objects.create(name="Électroménager")
        AttributeSetItem.objects.create(attribute_set=self.appliance_set, attribute=self.attr_voltage, is_required=True)
        AttributeSetItem.objects.create(attribute_set=self.appliance_set, attribute=self.attr_garantie, is_required=False)

        self.clothing_category = Category.objects.create(name="Vêtements", attribute_set=self.clothing_set)
        self.appliance_category = Category.objects.create(name="Électroménager", attribute_set=self.appliance_set)

    def test_clothing_product_rejects_voltage_attribute(self):
        product = Product(
            sku="TSHIRT-001", name="T-shirt en coton", category=self.clothing_category, price=Decimal("19.90"),
            attributes={"taille": "M", "couleur": "rouge", "voltage": "220V"},
        )
        with self.assertRaises(ValidationError):
            product.save()

    def test_clothing_product_accepts_valid_attributes(self):
        product = Product.objects.create(
            sku="TSHIRT-002", name="T-shirt en lin", category=self.clothing_category, price=Decimal("24.90"),
            attributes={"taille": "L", "couleur": "bleu"},
        )
        self.assertEqual(product.attributes["taille"], "L")

    def test_clothing_product_requires_mandatory_attribute(self):
        product = Product(
            sku="TSHIRT-003", name="T-shirt sans taille", category=self.clothing_category, price=Decimal("19.90"),
            attributes={"couleur": "vert"},
        )
        with self.assertRaises(ValidationError):
            product.save()

    def test_dynamic_attribute_filtering_by_size(self):
        Product.objects.create(sku="TSHIRT-M", name="T-shirt M", category=self.clothing_category, price=Decimal("19.90"), status="active", attributes={"taille": "M", "couleur": "rouge"})
        Product.objects.create(sku="TSHIRT-L", name="T-shirt L", category=self.clothing_category, price=Decimal("19.90"), status="active", attributes={"taille": "L", "couleur": "rouge"})

        from apps.catalog.filters import DynamicAttributeFilterBackend

        class FakeRequest:
            query_params = {"category": "vetements", "taille": "M"}

        backend = DynamicAttributeFilterBackend()
        results = backend.filter_queryset(FakeRequest(), Product.objects.all(), None)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().sku, "TSHIRT-M")

    def test_dynamic_attribute_filtering_appliance_voltage_and_warranty(self):
        Product.objects.create(sku="FRIDGE-1", name="Réfrigérateur A", category=self.appliance_category, price=Decimal("450.00"), status="active", attributes={"voltage": "220V", "garantie": 2})
        Product.objects.create(sku="FRIDGE-2", name="Réfrigérateur B", category=self.appliance_category, price=Decimal("380.00"), status="active", attributes={"voltage": "220V", "garantie": 1})
        Product.objects.create(sku="FRIDGE-3", name="Réfrigérateur C (110V)", category=self.appliance_category, price=Decimal("410.00"), status="active", attributes={"voltage": "110V", "garantie": 3})

        from apps.catalog.filters import DynamicAttributeFilterBackend

        class FakeRequest:
            query_params = {"category": "electromenager", "voltage": "220V", "garantie_min": "2"}

        backend = DynamicAttributeFilterBackend()
        results = backend.filter_queryset(FakeRequest(), Product.objects.all(), None)
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().sku, "FRIDGE-1")

    def test_new_category_with_own_attribute_set_requires_no_migration(self):
        pointure = AttributeDefinition.objects.create(code="pointure", label="Pointure", attribute_type=AttributeType.NUMBER, unit="EU")
        largeur = AttributeDefinition.objects.create(code="largeur_chaussure", label="Largeur", attribute_type=AttributeType.SINGLE_CHOICE, choices=["étroite", "standard", "large"])
        shoe_set = AttributeSet.objects.create(name="Chaussures")
        AttributeSetItem.objects.create(attribute_set=shoe_set, attribute=pointure, is_required=True)
        AttributeSetItem.objects.create(attribute_set=shoe_set, attribute=largeur, is_required=False)

        shoe_category = Category.objects.create(name="Chaussures", attribute_set=shoe_set)

        product = Product.objects.create(sku="SHOE-001", name="Sneakers urbaines", category=shoe_category, price=Decimal("59.90"), attributes={"pointure": 42, "largeur_chaussure": "standard"})
        self.assertEqual(product.attributes["pointure"], 42)

        invalid_product = Product(sku="SHOE-002", name="Sneakers invalides", category=shoe_category, price=Decimal("59.90"), attributes={"pointure": 42, "voltage": "220V"})
        with self.assertRaises(ValidationError):
            invalid_product.save()

    def test_category_inherits_attribute_set_from_parent(self):
        sub_category = Category.objects.create(name="T-shirts", parent=self.clothing_category)
        self.assertEqual(sub_category.get_effective_attribute_set(), self.clothing_set)
