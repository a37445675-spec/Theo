from rest_framework.decorators import api_view, permission_classes
"""Vues API pour le Widget Builder."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from django.shortcuts import get_object_or_404
from .models import Widget, ReusableSection, PageTemplate
from .widget_serializers import WidgetSerializer, ReusableSectionSerializer


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


# ============================================================
#  ENDPOINT PUBLIC — Widgets d'une page (sans auth)
# ============================================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(["GET"])
@permission_classes([AllowAny])
def public_page_widgets(request, page_id):
    """
    Endpoint public : retourne les widgets d'une page.
    Accessible sans authentification pour afficher les pages publiques.

    GET /api/v1/cms/pages/{page_id}/public/
    """
    from .models import PageTemplate, Widget
    from .widget_serializers import WidgetSerializer

    try:
        page = PageTemplate.objects.get(pk=page_id)
    except PageTemplate.DoesNotExist:
        return Response(
            {"detail": "Page introuvable."},
            status=404,
        )

    # Seuls les widgets racine (parent=None)
    widgets = Widget.objects.filter(page=page, parent=None).order_by("order")

    # Filtrer les widgets non visibles
    widgets = [w for w in widgets if w.is_visible]

    serializer = WidgetSerializer(widgets, many=True, context={"request": request})
    return Response({
        "page": {
            "id": page.pk,
            "name": page.name,
            "template_type": page.template_type,
        },
        "widgets": serializer.data,
    })
