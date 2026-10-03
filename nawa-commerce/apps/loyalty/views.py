from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoyaltyTransactionSerializer


class MyLoyaltyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        transactions = request.user.loyalty_transactions.all()
        return Response({"points": request.user.loyalty_points, "tier": request.user.loyalty_tier(), "transactions": LoyaltyTransactionSerializer(transactions, many=True).data})
