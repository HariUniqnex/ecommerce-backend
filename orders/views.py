from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order
from bson import ObjectId
from .serializers import OrderSerializer
import calendar
from .amazon_integration import fetch_and_save_amazon_orders 
from collections import defaultdict

class AmazonOrderSyncView(APIView):
    def get(self, request):
        try:
            fetch_and_save_amazon_orders()
            return Response({"message": "✅ Orders fetched and saved from Amazon."})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
class OrderList(APIView):
    def get(self,request):
        orders=Order.objects.all()
        serializer=OrderSerializer(orders,many=True)
        return Response(serializer.data)
    

from rest_framework.views import APIView
from rest_framework.response import Response
from collections import defaultdict
import calendar
from .models import Order

class DashboardStatsView(APIView):
    def get(self, request):
        orders = Order.objects()
        total_orders = orders.count()

        total_revenue = sum(
            sum(p.price * p.quantity for p in order.products)
            for order in orders
        )

        average_order_value = total_revenue / total_orders if total_orders else 0

        status_counts = defaultdict(int)
        for order in orders:
            status_counts[order.order_status] += 1

        status_counts_data = [
            {"id": status, "count": count}
            for status, count in status_counts.items()
        ]

        monthly_data = defaultdict(int)
        for order in orders:
            try:
                month = order.purchase_date.strftime("%b") 
                monthly_data[month] += sum(p.price * p.quantity for p in order.products)
            except AttributeError:
                continue  

        monthly_totals = [
            {"month": m, "total": monthly_data[m]}
            for m in calendar.month_abbr[1:] if m in monthly_data
        ]

        return Response({
            'totalOrders': total_orders,
            'totalRevenue': total_revenue,
            'avgOrderValue': average_order_value,
            'statusCounts': status_counts_data,
            "monthlyTotals": monthly_totals
        })
   
class OrderDetailView(APIView):
    def get(self,request,order_id):
        try:
            object_id=ObjectId(order_id)
            order=Order.objects.get(id=object_id)
            serializer=OrderSerializer(order)
        except Order.DoesNotExist:
                return Response({'error':"Order not found"},status=404)
        
        serializer=OrderSerializer(order)
        return Response(serializer.data)

