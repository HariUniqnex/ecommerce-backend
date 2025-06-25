# orders/middleware.py
from django.utils.deprecation import MiddlewareMixin
from .apps import OrdersConfig

class MongoDBConnectionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, '_mongo_connected'):
            OrdersConfig._connect_to_mongo()
            request._mongo_connected = True