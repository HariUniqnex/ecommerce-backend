from django.apps import AppConfig
from mongoengine import connect
from decouple import config
import logging

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        try:
           
            connect(
    db=config("MONGO_DB_NAME"),
    host=config("MONGO_DB_URI"),
    connectTimeoutMS=30000,  
    socketTimeoutMS=30000,  
    ssl=True,
    tlsAllowInvalidCertificates=False,
)
            print("MongoDB connection successful")
        except Exception as e:
            
            logger = logging.getLogger(__name__)
            logger.error(f"MongoDB connection failed: {e}")
