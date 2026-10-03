from datetime import date, timedelta

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsShopManagerOrAdmin

from . import services


class SalesReportView(APIView):
    permission_classes = [IsShopManagerOrAdmin]

    def get(self, request):
        date_to = request.query_params.get("date_to") or date.today().isoformat()
        date_from = request.query_params.get("date_from") or (date.today() - timedelta(days=30)).isoformat()
        report = services.generate_sales_report(date_from, date_to, request.query_params.get("sales_channel"))
        return Response(report)


class StockReportView(APIView):
    permission_classes = [IsShopManagerOrAdmin]

    def get(self, request):
        threshold = int(request.query_params.get("threshold", 5))
        return Response(services.generate_stock_report(threshold))


class CouponReportView(APIView):
    permission_classes = [IsShopManagerOrAdmin]

    def get(self, request):
        return Response(services.generate_coupon_report())
