from django.contrib import admin

from .models import Currency, Language, PlatformSite, SiteSettings


@admin.register(PlatformSite)
class PlatformSiteAdmin(admin.ModelAdmin):
    list_display = ("name", "domain", "default_currency", "default_language", "is_active")


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "symbol", "exchange_rate_to_eur")


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("code", "name")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site", "contact_email", "maintenance_mode")
