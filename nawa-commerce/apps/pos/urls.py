from django.urls import path

from .views import POSSaleView

app_name = "pos"

urlpatterns = [path("sales/", POSSaleView.as_view(), name="pos-sale")]
