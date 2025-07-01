import requests
from datetime import datetime, timedelta
from .models import Order, Product
from decouple import config
import time  
from urllib.parse import urlencode
import pytz

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

def fetch_orders_page(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching orders page: {str(e)}")
        print(f"Response status: {response.status_code if 'response' in locals() else 'No response'}")
        if 'response' in locals():
            try:
                print(f"Response body: {response.text}")
            except:
                pass
        return None

def process_order_items(items, order_id):
    products = []
    for item in items:
        brand = extract_brand_from_item(item)
        asin = item.get('ASIN', 'N/A')
        title = item.get('Title', 'Unknown')
        quantity = item.get('QuantityOrdered', 1)
        price = float(item.get('ItemPrice', {}).get('Amount', 0.0))
        
        product = Product(
            asin=asin,
            title=title,
            quantity=quantity,
            price=price,
            brand=brand
        )
        products.append(product)
    return products

def fetch_and_save_amazon_orders(start_date=None, end_date=None):
    try:
        access_token = get_access_token()
        if not access_token:
            print("Failed to fetch access token")
            return
        
        pacific=pytz.timezone("America/Los_Angeles")
        now_pacific=datetime.now(pacific)

    
        
        if start_date is None:
            start_date = now_pacific.replace(hour=0,minute=0,second=0,microsecond=0)
        else:
            start_date = pacific.localize(start_date.replace(hour=0,minute=0,second=0,microsecond=0))

        if end_date is None:
            end_date=now_pacific-timedelta(minutes=10)
            end_date=end_date.replace(second=0,microsecond=0)
        else:
            end_date=pacific.localize(end_date)

        start_date_utc = start_date.astimezone(pytz.utc)
        end_date_utc= end_date.astimezone(pytz.utc)

        start_date_str = start_date_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_date_str = end_date_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

        base_url = f"{config('AMAZON_API_BASE_URL')}/orders/v0/orders"
        
        params = {
            'MarketplaceIds': 'ATVPDKIKX0DER',
            'CreatedAfter': start_date_str,
            'CreatedBefore': end_date_str,
            'OrderStatuses': ['Shipped', 'PartiallyShipped', 'Unshipped']  
        }

        headers = {
            'Authorization': f'Bearer {access_token}',
            'x-amz-access-token': access_token,
            'Content-Type': 'application/json'
        }

        print(f"Fetching orders from Amazon API from {start_date_str} to {end_date_str}...")
        next_token = None
        total_saved = 0

        while True:
            current_params = params.copy()
            if next_token:
                current_params['NextToken'] = next_token

            query_string = urlencode(current_params, doseq=True)
            full_url = f"{base_url}?{query_string}"
            
            print(f"Request URL: {full_url}")  
            
            response = fetch_orders_page(full_url, headers)
            if not response:
                break

            orders_data = response.get('payload', {}).get('Orders', [])
            if not orders_data:
                print("No orders found in this batch")
                break

            print(f"Processing {len(orders_data)} orders...")

            for order in orders_data:
                order_id = order.get('AmazonOrderId')
                if not order_id:
                    continue

                existing_order = Order.objects.filter(order_id=order_id).first()
                if existing_order:
                    print(f"Order {order_id} already exists, skipping")
                    continue

                print(f"Processing order {order_id}...")
                items = fetch_order_items(order_id, access_token)
                time.sleep(1) 

                products = process_order_items(items, order_id)

                if not products:
                    products.append(Product(
                        title=f"Amazon Order {order_id}",
                        quantity=1,
                        price=float(order.get('OrderTotal', {}).get('Amount', 0.0)),
                        brand="Unknown",
                        asin="N/A"
                    ))

                try:
                    purchase_date_str = order.get('PurchaseDate', '')
                    purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%dT%H:%M:%SZ') if purchase_date_str else None

                    order_obj = Order(
                        order_id=order_id,
                        purchase_date=purchase_date,
                        order_status=order.get('OrderStatus'),
                        products=products,
                        marketplace_id=order.get('MarketplaceId'),
                        shipping_address=order.get('ShippingAddress', {}),
                        paymentMethod=order.get("PaymentMethod", "Other"),
                    )

                    order_obj.save()
                    total_saved += 1
                    print(f"Saved order {order_id}")
                except Exception as e:
                    print(f"Failed to save order {order_id}: {str(e)}")

            next_token = response.get('payload', {}).get('NextToken')
            if not next_token:
                break

            print("Fetching next page of orders...")
            time.sleep(2) 

        print(f"\nProcessing complete. Saved {total_saved} new orders")

    except Exception as e:
        print(f"Fatal error in fetch_and_save_amazon_orders: {str(e)}")
        raise

