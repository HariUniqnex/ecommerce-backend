# orders/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        # Don't connect here - just initialize signals if needed
        if config('INIT_DB_ON_STARTUP', default=False, cast=bool):
            self._connect_to_mongo()

    @classmethod
    def _connect_to_mongo(cls):
        """Lazy connection method to be called when needed"""
        from mongoengine import connect
        from decouple import config
        
        try:
            connect(
                db=config("MONGO_DB_NAME"),
                host=config("MONGO_DB_URI"),
                connect=False if config('RENDER', default=False) else True
            )
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise