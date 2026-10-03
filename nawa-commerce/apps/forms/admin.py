"""Admin Django pour les formulaires."""
from django.contrib import admin
from django.utils.html import format_html
from .models import FormDefinition, FormField, FormSubmission


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 1
    fields = (
        "order", "label", "field_key", "field_type",
        "placeholder", "is_required", "options"
    )
    ordering = ("order",)


@admin.register(FormDefinition)
class FormDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "field_count", "submission_count", "is_active")
    list_filter = ("is_active", "captcha_enabled")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [FormFieldInline]

    fieldsets = (
        ("Identification", {"fields": ("name", "slug", "description")}),
        ("Après soumission", {"fields": ("success_message", "redirect_url", "email_notification")}),
        ("Sécurité & Statut", {"fields": ("captcha_enabled", "is_active")}),
    )

    def field_count(self, obj):
        return obj.fields.count()
    field_count.short_description = "Champs"

    def submission_count(self, obj):
        count = obj.submissions.count()
        if count == 0:
            return "—"
        return format_html(
            '<a href="/admin/forms/formsubmission/?form__id__exact={}">'
            '<span style="background:#2F4A3C;color:#fff;padding:2px 8px;'
            'border-radius:999px;font-size:11px;">{} soumission(s)</span></a>',
            obj.id, count
        )
    submission_count.short_description = "Soumissions"


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ("form", "preview", "status_badge", "created_at")
    list_filter = ("form", "status", "created_at")
    search_fields = ("data",)
    readonly_fields = (
        "form", "data", "ip_address", "user_agent",
        "referer", "user", "created_at",
    )
    list_per_page = 50
    date_hierarchy = "created_at"

    def preview(self, obj):
        if not obj.data:
            return "—"
        items = list(obj.data.items())[:2]
        return " | ".join([f"{k}: {str(v)[:30]}" for k, v in items])
    preview.short_description = "Aperçu"

    def status_badge(self, obj):
        colors = {
            "new": "#D4A843", "read": "#2F4A3C",
            "replied": "#16A34A", "archived": "#6B6259", "spam": "#DC2626",
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;">{}</span>',
            colors.get(obj.status, "#6B6259"),
            obj.get_status_display()
        )
    status_badge.short_description = "Statut"


# Actions en masse
@admin.action(description="Marquer comme lu")
def mark_as_read(modeladmin, request, queryset):
    queryset.update(status="read")


@admin.action(description="Marquer comme répondu")
def mark_as_replied(modeladmin, request, queryset):
    queryset.update(status="replied")


@admin.action(description="Marquer comme spam")
def mark_as_spam(modeladmin, request, queryset):
    queryset.update(status="spam")


FormSubmissionAdmin.actions = [mark_as_read, mark_as_replied, mark_as_spam]
