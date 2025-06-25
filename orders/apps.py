import certifi
from mongoengine import connect
from decouple import config
import logging
import os
from django.apps import AppConfig  

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        try:
            logger = logging.getLogger(__name__)

            connect(
                'ecommerce',  
                host=config('MONGO_DB_URI'),
                tls=True,  
                tlsCAFile=certifi.where(), 
                connectTimeoutMS=300000,  
                socketTimeoutMS=300000,  
            )
            logger.info("MongoDB connection successful")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
