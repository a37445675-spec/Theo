from django.urls import path

from .views import CouponValidateView

app_name = "promotions"

urlpatterns = [path("coupons/validate/", CouponValidateView.as_view(), name="coupon-validate")]
