"""Vues API pour les traductions."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import TranslationKey
from .serializers import TranslationKeySerializer


class TranslationKeyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API Traductions.

    GET /api/v1/translations/                    → liste complète
    GET /api/v1/translations/?lang=fr            → objet { "key": "value", ... } prêt à consommer
    GET /api/v1/translations/?context=Panier     → filtré par contexte
    GET /api/v1/translations/languages/          → liste des langues disponibles
    """
    queryset = TranslationKey.objects.filter(is_active=True)
    serializer_class = TranslationKeySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        context = self.request.query_params.get("context")
        if context:
            qs = qs.filter(context=context)
        return qs

    def list(self, request, *args, **kwargs):
        """Si ?lang= est fourni, on renvoie un objet plat { key: value }."""
        lang = request.query_params.get("lang")
        if lang:
            qs = self.get_queryset()
            data = {t.key: t.get_value(lang) for t in qs}
            return Response(data)
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def languages(self, request):
        """Liste toutes les langues disponibles."""
        langs = set()
        for t in self.get_queryset():
            langs.update((t.values or {}).keys())
        return Response(sorted(langs))
