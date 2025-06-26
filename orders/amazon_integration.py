import requests
from datetime import datetime
from .models import Order, Product
from decouple import config
import time  # For rate limiting

def get_access_token():
    token_url = config('AMAZON_TOKEN_URL')
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': config("AMAZON_REFRESH_TOKEN"),
        'client_id': config('AMAZON_CLIENT_ID'),
        'client_secret': config('AMAZON_CLIENT_SECRET')
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json().get('access_token')

def fetch_order_items(order_id, access_token):
    items_url = f"{config('AMAZON_API_BASE_URL')}/orders/v0/orders/{order_id}/orderItems"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(items_url, headers=headers)
        print('response', response)
        response.raise_for_status()
        items_data = response.json()
        return items_data.get('payload', {}).get('OrderItems', [])
    except Exception as e:
        print(f"Failed to fetch items for order {order_id}: {str(e)}")
        return []

def extract_brand_from_item(item):
    """
    Extract brand from order item - simple first word approach
    """
    title = item.get('Title', '')
    if title:
        words = title.split()
        if words:
            first_word = words[0]
            # Optional: Add some validation
            if len(first_word) > 1 and first_word.isalpha():
                return first_word
    
    return 'Unknown'

import requests
from datetime import datetime
from .models import Order, Product
from decouple import config
import time  # For rate limiting

def get_access_token():
    token_url = config('AMAZON_TOKEN_URL')
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': config("AMAZON_REFRESH_TOKEN"),
        'client_id': config('AMAZON_CLIENT_ID'),
        'client_secret': config('AMAZON_CLIENT_SECRET')
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    return response.json().get('access_token')

def fetch_order_items(order_id, access_token):
    items_url = f"{config('AMAZON_API_BASE_URL')}/orders/v0/orders/{order_id}/orderItems"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'x-amz-access-token': access_token,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(items_url, headers=headers)
        response.raise_for_status()
        items_data = response.json()
        return items_data.get('payload', {}).get('OrderItems', [])
    except Exception as e:
        print(f"Failed to fetch items for order {order_id}: {str(e)}")
        return []

def extract_brand_from_item(item):
    
    title = item.get('Title', '')
    if title:
        words = title.split()
        if words:
            first_word = words[0]
            if len(first_word) > 1 and first_word.isalpha():
                return first_word
    
    return 'Unknown'

def fetch_and_save_amazon_orders():
    """Main function to fetch and save Amazon orders with complete product details"""
    try:
        access_token = get_access_token()
        if not access_token:
            print("Failed to fetch access token")
            return

        orders_url = config('AMAZON_ORDERS_API_URL')
        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-amz-access-token': access_token,
            'Content-Type': 'application/json'
        }

        print("Fetching orders from Amazon API...")
        response = requests.get(orders_url, headers=headers)
        response.raise_for_status()
        orders_data = response.json().get('payload', {}).get('Orders', [])

        if not orders_data:
            print("No orders found in the response")
            return

        print(f"Found {len(orders_data)} orders to process")

        saved_count = 0
        for order in orders_data:
            try:
                order_id = order.get('AmazonOrderId')
                if not order_id:
                    continue

                if Order.objects(order_id=order_id).first():
                    print(f"Order {order_id} already exists, skipping")
                    continue

                print(f"Fetching items for order {order_id}...")
                items = fetch_order_items(order_id, access_token)
                time.sleep(1) 

                products = []
                for item in items:
                    try:
                        product = Product(
                            title=item.get('Title', 'Unknown Product'),
                            quantity=int(item.get('QuantityOrdered', 1)),
                            price=float(item.get('ItemPrice', {}).get('Amount', 0.0)),
                            brand=item.get('Brand', 'Unknown'),
                            asin=item.get('ASIN', '')
                        )
                        products.append(product)
                    except Exception as e:
                        print(f"Error processing item {item.get('OrderItemId')}: {str(e)}")

                if not products:
                    products.append(Product(
                        title=f"Amazon Order {order_id}",
                        quantity=1,
                        price=float(order.get('OrderTotal', {}).get('Amount', 0.0)),
                        brand="Unknown",
                        asin="N/A"
                    ))

                order_obj = Order(
                    order_id=order_id,
                    purchase_date=datetime.strptime(
                        order.get('PurchaseDate'), 
                        '%Y-%m-%dT%H:%M:%SZ'
                    ),
                    order_status=order.get('OrderStatus'),
                    products=products,
                    marketplace_id=order.get('MarketplaceId'),
                    shipping_address=order.get('ShippingAddress', {})
                )
                
                order_obj.save()
                saved_count += 1
                print(f"Successfully saved order {order_id}")

            except Exception as e:
                print(f"Failed to process order {order_id}: {str(e)}")
                continue

        print(f"\nProcessing complete. Saved {saved_count} new orders")

    except Exception as e:
        print(f"Fatal error in fetch_and_save_amazon_orders: {str(e)}")
        