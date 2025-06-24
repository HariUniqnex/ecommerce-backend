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
    products = ProductSerializer(many=True)

    def get_order_id(self, obj):
        return str(obj.id if hasattr(obj, 'id') else obj.get('_id', ''))
