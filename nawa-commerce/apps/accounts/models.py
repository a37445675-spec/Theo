from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.mixins import TimeStampedModel

ROLE_CUSTOMER = "customer"
ROLE_SHOP_MANAGER = "shop_manager"
ROLE_ADMINISTRATOR = "administrator"
ROLE_VENDOR = "vendor"

ALL_ROLES = [ROLE_CUSTOMER, ROLE_SHOP_MANAGER, ROLE_ADMINISTRATOR, ROLE_VENDOR]


class User(AbstractUser):
    phone = models.CharField(max_length=32, blank=True)
    avatar = models.ImageField(upload_to="avatars/%Y/%m/", blank=True, null=True)

    is_business_account = models.BooleanField(default=False)
    company_name = models.CharField(max_length=200, blank=True)
    vat_number = models.CharField(max_length=32, blank=True)

    loyalty_points = models.PositiveIntegerField(default=0)
    preferred_currency = models.CharField(max_length=3, default="EUR")
    preferred_language = models.CharField(max_length=5, default="fr")

    def __str__(self):
        return self.get_full_name() or self.username

    def has_role(self, role_name: str) -> bool:
        return self.is_superuser or self.groups.filter(name=role_name).exists()

    @property
    def is_shop_manager(self) -> bool:
        return self.has_role(ROLE_SHOP_MANAGER) or self.has_role(ROLE_ADMINISTRATOR)

    @property
    def is_vendor(self) -> bool:
        return self.has_role(ROLE_VENDOR)

    def loyalty_tier(self) -> str:
        if self.loyalty_points >= 300:
            return "gold"
        if self.loyalty_points >= 100:
            return "silver"
        return "bronze"


class Address(TimeStampedModel):
    ADDRESS_SHIPPING = "shipping"
    ADDRESS_BILLING = "billing"
    ADDRESS_TYPE_CHOICES = [(ADDRESS_SHIPPING, "Livraison"), (ADDRESS_BILLING, "Facturation")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default=ADDRESS_SHIPPING)
    full_name = models.CharField(max_length=150)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=2)
    phone = models.CharField(max_length=32, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.city} ({self.country})"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, address_type=self.address_type).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
