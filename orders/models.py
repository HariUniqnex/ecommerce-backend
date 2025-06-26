from mongoengine import Document, EmbeddedDocument, fields

class Product(EmbeddedDocument):
    asin = fields.StringField()
    title = fields.StringField(required=True)
    quantity = fields.IntField(required=True, min_value=1)
    price = fields.FloatField(required=True)
    brand = fields.StringField()

class Order(Document):
    order_id = fields.StringField(required=True, unique=True)
    purchase_date = fields.DateTimeField(required=True)
    order_status = fields.StringField(required=True)
    products = fields.ListField(fields.EmbeddedDocumentField(Product), required=True)
    paymentMethod=fields.StringField(required=True)
    marketplace_id = fields.StringField()
    shipping_address = fields.DictField()   