import requests
from datetime import datetime
from .models import Order, Product
from decouple import config
import time 

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
  
    title = item.get('Title', '')
    if title:
        words = title.split()
        if words:
            first_word = words[0]
            if len(first_word) > 1 and first_word.isalpha():
                return first_word
    
    return 'Unknown'



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
    try:
        access_token = get_access_token()
        if not access_token:
            print("Failed to fetch access token")
            return

        today = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        
        orders_url = f"{config('AMAZON_API_BASE_URL')}/orders/v0/orders?MarketplaceIds=ATVPDKIKX0DER&LastUpdatedAfter=2024-01-01T00:00:00Z&LastUpdatedBefore={today}"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-amz-access-token': access_token,
            'Content-Type': 'application/json'
        }

        print("Fetching orders from Amazon API...")
        
        while orders_url:
            response = requests.get(orders_url, headers=headers)
            response.raise_for_status()
            orders_data = response.json().get('payload', {}).get('Orders', [])
            
            if not orders_data:
                print("No new orders found.")
                break

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
                    if items:
                        print("Available fields in first item:", list(items[0].keys()))
                        print("Full first item:", items[0])
                    time.sleep(1)  # Rate limiting
                    
                    products = []
                    for item in items:
                        try:
                            brand = extract_brand_from_item(item)
                            
                            product = Product(
                                title=item.get('Title', 'Unknown Product'),
                                quantity=int(item.get('QuantityOrdered', 1)),
                                price=float(item.get('ItemPrice', {}).get('Amount', 0.0)),
                                brand=brand, 
                                asin=item.get('ASIN', '')
                            )
                            
                            products.append(product)
                            print(f"Product saved with brand: {brand}")
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
                        shipping_address=order.get('ShippingAddress', {}),
                        paymentMethod=order.get("PaymentMethod", "Other")
                    )
                    
                    order_obj.save()
                    saved_count += 1
                    print(f"Successfully saved order {order_id}")

                except Exception as e:
                    print(f"Failed to process order {order_id}: {str(e)}")
                    continue

            print(f"\nProcessing complete. Saved {saved_count} new orders")

            next_token = response.json().get('nextToken')
            if next_token:
                orders_url = f"{config('AMAZON_API_BASE_URL')}/orders/v0/orders?MarketplaceIds=ATVPDKIKX0DER&LastUpdatedAfter=2024-01-01T00:00:00Z&LastUpdatedBefore={today}&NextToken={next_token}"
            else:
                orders_url = None  

    except Exception as e:
        print(f"Fatal error in fetch_and_save_amazon_orders: {str(e)}")