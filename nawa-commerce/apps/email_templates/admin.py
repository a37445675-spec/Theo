"""Admin Django pour les emails."""
from django.contrib import admin
from django.utils.html import format_html
from .models import EmailTemplate


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "subject_preview", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "subject")
    list_editable = ("is_active",)
    readonly_fields = ("created_at", "updated_at", "preview")

    fieldsets = (
        ("Identification", {"fields": ("code", "name", "description")}),
        ("Contenu", {"fields": ("subject", "body_text", "body_html")}),
        ("Configuration", {"fields": ("from_email", "variables", "is_active")}),
        ("Aperçu", {"fields": ("preview",)}),
        ("Métadonnées", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def subject_preview(self, obj):
        return obj.subject[:60]
    subject_preview.short_description = "Sujet"

    def preview(self, obj):
        if not obj.pk:
            return "Enregistrez d'abord le template."
        return format_html(
            '<div style="border:1px solid #ddd;border-radius:8px;padding:16px;'
            'background:#f9f9f9;max-width:700px;">'
            '<div style="font-weight:600;margin-bottom:8px;">Sujet : {}</div>'
            '<hr style="border:none;border-top:1px solid #eee;margin:8px 0;">'
            '<div>{}</div>'
            '</div>',
            obj.subject,
            format_html("{}", obj.body_html or obj.body_text or "(vide)")
        )
    preview.short_description = "Aperçu"
