from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer
from .amazon_integration import fetch_and_save_amazon_orders 

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
    

class OrderDetailView(APIView):
    def get(self,request,order_id):
        try:
            order=Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
                return Response({'error':"Order not found"},status=404)
        
        serializer=OrderSerializer(order)
        return Response(serializer.data)

