from django.urls import path

from .views import MyLoyaltyView

app_name = "loyalty"

urlpatterns = [path("mine/", MyLoyaltyView.as_view(), name="mine")]
