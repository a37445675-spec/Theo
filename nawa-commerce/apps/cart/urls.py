from django.urls import path

from .views import CartAddLineView, CartLineDetailView, CartView

app_name = "cart"

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("lines/", CartAddLineView.as_view(), name="add-line"),
    path("lines/<int:line_id>/", CartLineDetailView.as_view(), name="line-detail"),
]
