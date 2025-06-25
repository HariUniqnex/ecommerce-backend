from rest_framework import serializers
from bson import ObjectId

class ProductSerializer(serializers.Serializer):
    asin = serializers.CharField()      
    title = serializers.CharField()     
    brand = serializers.CharField()
    quantity = serializers.IntegerField()
    price = serializers.FloatField() 

class OrderSerializer(serializers.Serializer):
    order_id = serializers.SerializerMethodField()
    purchase_date=serializers.DateTimeField()
    products = ProductSerializer(many=True)
    shipping_address=serializers.DictField()
    paymentMethod=serializers.CharField()

    def get_order_id(self, obj):
        return str(obj.id if hasattr(obj, 'id') else obj.get('_id', ''))
