from django.urls import path

from .views import CouponReportView, SalesReportView, StockReportView

app_name = "reporting"

urlpatterns = [
    path("sales/", SalesReportView.as_view(), name="sales-report"),
    path("stock/", StockReportView.as_view(), name="stock-report"),
    path("coupons/", CouponReportView.as_view(), name="coupon-report"),
]
