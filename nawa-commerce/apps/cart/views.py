from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product, ProductVariant

from . import services
from .models import CartLine
from .serializers import AddLineSerializer, CartSerializer, UpdateLineSerializer


@extend_schema(exclude=True)


class CartView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        cart = services.get_or_create_cart(request)
        return Response(CartSerializer(cart).data)


@extend_schema(exclude=True)


class CartAddLineView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = AddLineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        product = get_object_or_404(Product, pk=data["product_id"], status="active")
        variant = None
        if data.get("variant_id"):
            variant = get_object_or_404(ProductVariant, pk=data["variant_id"], product=product)

        cart = services.get_or_create_cart(request)
        services.add_line(cart, product, variant, data["quantity"])
        return Response(CartSerializer(cart).data, status=201)


@extend_schema(exclude=True)


class CartLineDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def patch(self, request, line_id):
        cart = services.get_or_create_cart(request)
        line = get_object_or_404(CartLine, pk=line_id, cart=cart)
        serializer = UpdateLineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.update_line_quantity(line, serializer.validated_data["quantity"])
        return Response(CartSerializer(cart).data)

    def delete(self, request, line_id):
        cart = services.get_or_create_cart(request)
        line = get_object_or_404(CartLine, pk=line_id, cart=cart)
        line.delete()
        return Response(CartSerializer(cart).data)
