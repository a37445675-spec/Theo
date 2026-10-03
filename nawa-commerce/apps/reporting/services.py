from decimal import Decimal

from django.db.models import Count, F, Sum
from django.db.models.functions import TruncDay


def generate_sales_report(date_from, date_to, sales_channel=None):
    from apps.orders.models import Order, OrderStatus

    qs = Order.objects.filter(created_at__date__gte=date_from, created_at__date__lte=date_to, status=OrderStatus.PAID)
    if sales_channel:
        qs = qs.filter(sales_channel=sales_channel)

    aggregate = qs.aggregate(total_revenue=Sum("total"), order_count=Count("id"))
    total_revenue = aggregate["total_revenue"] or Decimal("0")
    order_count = aggregate["order_count"] or 0
    daily = qs.annotate(day=TruncDay("created_at")).values("day").annotate(revenue=Sum("total"), orders=Count("id")).order_by("day")

    return {
        "total_revenue": total_revenue, "order_count": order_count,
        "average_order_value": (total_revenue / order_count) if order_count else Decimal("0"),
        "daily_breakdown": list(daily),
    }


def generate_stock_report(low_stock_threshold: int = 5):
    from apps.catalog.models import Product

    return list(Product.objects.filter(track_stock=True, stock__lte=low_stock_threshold, status="active").values("id", "sku", "name", "stock", "category__name").order_by("stock"))


def generate_coupon_report():
    from apps.promotions.models import Coupon

    return list(Coupon.objects.annotate(usage=F("times_used")).values("code", "discount_type", "discount_value", "usage").order_by("-usage"))
