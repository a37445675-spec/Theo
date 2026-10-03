from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from apps.core.mixins import TimeStampedModel
from apps.seo.models import SEOFieldsMixin

from .validators import validate_attributes_against_set


class AttributeType(models.TextChoices):
    TEXT = "text", "Texte"
    NUMBER = "number", "Nombre"
    BOOLEAN = "boolean", "Booléen"
    SINGLE_CHOICE = "single_choice", "Choix unique"
    MULTI_CHOICE = "multi_choice", "Choix multiple"
    RANGE = "range", "Plage (min/max)"


class AttributeDefinition(TimeStampedModel):
    code = models.SlugField(max_length=64, unique=True)
    label = models.CharField(max_length=120)
    attribute_type = models.CharField(max_length=20, choices=AttributeType.choices)
    unit = models.CharField(max_length=20, blank=True)
    choices = models.JSONField(default=list, blank=True)
    help_text = models.CharField(max_length=255, blank=True)
    is_filterable = models.BooleanField(default=True)

    class Meta:
        ordering = ["label"]

    def __str__(self):
        return f"{self.label} ({self.code})"

    def clean(self):
        if self.attribute_type in {AttributeType.SINGLE_CHOICE, AttributeType.MULTI_CHOICE} and not self.choices:
            raise ValidationError({"choices": "Requis pour un attribut à choix unique ou multiple."})

    def validate_value(self, value):
        if self.attribute_type == AttributeType.TEXT and not isinstance(value, str):
            raise ValidationError(f"'{self.code}' doit être une chaîne de caractères.")
        if self.attribute_type == AttributeType.NUMBER and not isinstance(value, (int, float)):
            raise ValidationError(f"'{self.code}' doit être un nombre.")
        if self.attribute_type == AttributeType.BOOLEAN and not isinstance(value, bool):
            raise ValidationError(f"'{self.code}' doit être un booléen.")
        if self.attribute_type == AttributeType.SINGLE_CHOICE and value not in self.choices:
            raise ValidationError(f"'{self.code}' doit être l'une des valeurs : {self.choices}.")
        if self.attribute_type == AttributeType.MULTI_CHOICE:
            if not isinstance(value, list) or not all(v in self.choices for v in value):
                raise ValidationError(f"'{self.code}' doit être une liste parmi : {self.choices}.")
        if self.attribute_type == AttributeType.RANGE:
            if not (isinstance(value, dict) and "min" in value and "max" in value):
                raise ValidationError(f"'{self.code}' doit être un objet {{'min': ..., 'max': ...}}.")


class AttributeSet(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    attributes = models.ManyToManyField(AttributeDefinition, through="AttributeSetItem", related_name="attribute_sets")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def required_codes(self):
        return set(self.items.filter(is_required=True).values_list("attribute__code", flat=True))

    def allowed_codes(self):
        return set(self.items.values_list("attribute__code", flat=True))


class AttributeSetItem(models.Model):
    attribute_set = models.ForeignKey(AttributeSet, on_delete=models.CASCADE, related_name="items")
    attribute = models.ForeignKey(AttributeDefinition, on_delete=models.CASCADE, related_name="set_items")
    is_required = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]
        unique_together = ["attribute_set", "attribute"]

    def __str__(self):
        return f"{self.attribute_set.name} · {self.attribute.code}"


class Category(TimeStampedModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    attribute_set = models.ForeignKey(AttributeSet, null=True, blank=True, on_delete=models.SET_NULL, related_name="categories")
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=8, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_ancestors(self):
        ancestors = []
        node = self.parent
        while node is not None:
            ancestors.append(node)
            node = node.parent
        return list(reversed(ancestors))

    def get_effective_attribute_set(self):
        node = self
        while node is not None:
            if node.attribute_set_id:
                return node.attribute_set
            node = node.parent
        return None


class Brand(TimeStampedModel):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    logo = models.ImageField(upload_to="brands/%Y/%m/", blank=True, null=True)
    country = models.CharField(max_length=100, blank=True)
    story = models.TextField(blank=True)
    website = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProductType(models.TextChoices):
    SIMPLE = "simple", "Simple"
    VARIANT = "variant", "À variantes"
    BOOKING = "booking", "Réservation / service"
    DEPOSIT = "deposit", "Avec acompte"
    WHOLESALE = "wholesale", "Wholesale / B2B"


class ProductStatus(models.TextChoices):
    DRAFT = "draft", "Brouillon"
    ACTIVE = "active", "Actif"
    ARCHIVED = "archived", "Archivé"


class Product(SEOFieldsMixin, TimeStampedModel):
    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL, related_name="products")

    product_type = models.CharField(max_length=12, choices=ProductType.choices, default=ProductType.SIMPLE)
    status = models.CharField(max_length=10, choices=ProductStatus.choices, default=ProductStatus.DRAFT, db_index=True)

    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="EUR")
    stock = models.PositiveIntegerField(default=0)
    track_stock = models.BooleanField(default=True)

    attributes = models.JSONField(default=dict, blank=True)

    weight_kg = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    length_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    width_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    is_featured = models.BooleanField(default=False)
    vendor = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="vendor_products")

    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "category"]),
            GinIndex(fields=["attributes"], name="product_attributes_gin"),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        attribute_set = self.category.get_effective_attribute_set() if self.category_id else None
        validate_attributes_against_set(self.attributes or {}, attribute_set)

    @property
    def in_stock(self) -> bool:
        if self.product_type == ProductType.VARIANT:
            return self.variants.filter(stock__gt=0).exists()
        return (not self.track_stock) or self.stock > 0


class ProductVariant(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=64, unique=True)
    attributes = models.JSONField(default=dict, blank=True)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [GinIndex(fields=["attributes"], name="variant_attributes_gin")]
        ordering = ["id"]

    def __str__(self):
        return f"{self.product.name} — {self.attributes}"

    def clean(self):
        attribute_set = self.product.category.get_effective_attribute_set() if self.product_id else None
        validate_attributes_against_set(self.attributes or {}, attribute_set, enforce_required=False)

    @property
    def effective_price(self):
        return self.price_override if self.price_override is not None else self.product.price


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/%Y/%m/")
    alt_text = models.CharField(max_length=255, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image #{self.order} — {self.product.name}"

    def save(self, *args, **kwargs):
        if self.image and (not self.width or not self.height):
            try:
                self.width, self.height = self.image.width, self.image.height
            except Exception:
                pass
        super().save(*args, **kwargs)
