import django_filters
from django.db.models import Q
from rest_framework.filters import BaseFilterBackend

from .models import AttributeType, Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name="category__slug", lookup_expr="exact")
    brand = django_filters.CharFilter(field_name="brand__slug", lookup_expr="exact")
    product_type = django_filters.CharFilter(field_name="product_type", lookup_expr="exact")
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    is_featured = django_filters.BooleanFilter(field_name="is_featured")

    class Meta:
        model = Product
        fields = []


class DynamicAttributeFilterBackend(BaseFilterBackend):
    """
    Filtre DRF sur mesure : tout paramètre correspondant au code d'un
    AttributeDefinition de la catégorie demandée filtre le JSONField
    attributes — un seul endpoint /api/catalog/products/ filtre
    dynamiquement N verticales différentes.
    """

    RESERVED_PARAMS = {
        "category", "brand", "product_type",
        "price_min", "price_max", "is_featured",
        "search", "ordering", "page", "page_size",
    }

    # ------------------------------------------------------------------
    #  DRF : filtrage
    # ------------------------------------------------------------------
    def filter_queryset(self, request, queryset, view):
        category_slug = request.query_params.get("category")
        if not category_slug:
            return queryset

        from .models import Category

        category = Category.objects.filter(slug=category_slug).select_related("attribute_set").first()
        if not category:
            return queryset

        attribute_set = category.get_effective_attribute_set()
        if not attribute_set:
            return queryset

        definitions_by_code = {
            item.attribute.code: item.attribute
            for item in attribute_set.items.select_related("attribute")
        }

        for param, value in request.query_params.items():
            if param in self.RESERVED_PARAMS:
                continue

            base_code, _, suffix = param.rpartition("_")
            is_range_bound = suffix in {"min", "max"} and base_code in definitions_by_code
            code = base_code if is_range_bound else param

            if code not in definitions_by_code:
                continue

            definition = definitions_by_code[code]
            lookup_key = f"attributes__{code}"

            if is_range_bound:
                lookup_key += "__gte" if suffix == "min" else "__lte"
                queryset = queryset.filter({lookup_key: _cast_numeric(value)})
            elif definition.attribute_type == AttributeType.MULTI_CHOICE:
                queryset = queryset.filter({f"{lookup_key}__contains": [value]})
            elif definition.attribute_type == AttributeType.NUMBER:
                queryset = queryset.filter({lookup_key: _cast_numeric(value)})
            elif definition.attribute_type == AttributeType.BOOLEAN:
                queryset = queryset.filter({lookup_key: value.lower() in {"1", "true", "yes"}})
            else:
                queryset = queryset.filter(Q(**{lookup_key: value}))

        return queryset

    # ------------------------------------------------------------------
    #  drf-spectacular : documentation OpenAPI
    # ------------------------------------------------------------------
    def get_schema_operation_parameters(self, view):
        """
        Décrit les paramètres du filtre dynamique pour drf-spectacular.
        Les vrais codes d'attributs dépendent de la catégorie demandée,
        donc on documente un paramètre générique + un exemple.
        """
        return [
            {
                "name": "attributes",
                "required": False,
                "in": "query",
                "description": (
                    "Filtre dynamique par attribut. Le nom du paramètre doit "
                    "correspondre au code d'un AttributeDefinition de la catégorie. "
                    "Exemples : `?type_peau=seche`, `?contenance_ml_min=100`, "
                    "`?objectifs=hydratation`."
                ),
                "schema": {"type": "string"},
            },
        ]


def _cast_numeric(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            return value