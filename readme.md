# Amazon Orders API Integration with Django, MongoDB, and React

This project is a full-stack application for fetching Amazon orders via the Selling Partner API (SP-API), storing them in MongoDB, and displaying them through a Django REST API and a React frontend.

---

## Features

- **Backend**: Django + Django REST Framework + MongoEngine (MongoDB)
  - Fetches Amazon orders and order items from SP-API
  - Stores orders and product details in MongoDB
  - Exposes a REST API for frontend consumption
  - CORS-enabled for local frontend development

- **Frontend**: React (Vite or Create React App)
  - Fetches and displays orders and product data from the backend
  - Presents order and product details in a user-friendly interface

---

## Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB (local or cloud)
- Amazon SP-API credentials (client ID, client secret, refresh token, etc.)

---

## Backend Setup

1. **Clone the repository**

    ```sh
    git clone https://github.com/your-username/your-repo.git
    cd your-repo/backend
    ```

2. **Create and activate virtual environment**

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install dependencies**

    ```sh
    pip install -r requirements.txt
    ```

4. **Configure environment variables**

    Create a `.env` file in `backend/`:

    ```
    SECRET_KEY=your-django-secret-key
    MONGO_DB_URI=mongodb://localhost:27017/your-db
    MONGO_DB_NAME=your-db
    AMAZON_CLIENT_ID=your-amazon-client-id
    AMAZON_CLIENT_SECRET=your-amazon-client-secret
    AMAZON_REFRESH_TOKEN=your-refresh-token
    AMAZON_TOKEN_URL=https://api.amazon.com/auth/o2/token
    AMAZON_ORDERS_API_URL=https://sellingpartnerapi-na.amazon.com/orders/v0/orders?MarketplaceIds=ATVPDKIKX0DER&CreatedAfter=2024-01-01T00:00:00Z
    ```

5. **Run migrations (if needed)**

    (MongoEngine does not require Django migrations.)

6. **Run the backend server**

    ```sh
    python manage.py runserver
    ```

    The API will be available at `http://127.0.0.1:8000/api/orders/`.

---

## Frontend Setup

1. **Navigate to the frontend directory**

    ```sh
    cd ../frontend
    ```

2. **Install dependencies**

    ```sh
    npm install
    ```

3. **Start the frontend server**

    ```sh
    npm run dev
    ```

    The frontend will be available at `http://localhost:5173`.

---

## API Example

- **Get all orders**:
    ```
    GET http://127.0.0.1:8000/api/orders/
    ```
    Response example:
    ```json
    [
      {
        "order_id": "111-5329356-4490607",
        "purchase_date": "2024-01-01T02:09:26Z",
        "order_status": "Shipped",
        "products": [
          {
            "product_id": "B002QYW8LW",
            "name": "Amazon Basics Mouse",
            "brand": "Amazon Basics",
            "quantity": 2,
            "sold_price": 15.99
          }
        ]
      }
    ]
    ```

---

## CORS Configuration

- In `settings.py`, ensure:

    ```python
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
    ]
    MIDDLEWARE = [
        "corsheaders.middleware.CorsMiddleware",
        # ...other middleware...
    ]
    ```

---

## Notes

- Make sure your Amazon SP-API credentials are correct and you have the necessary developer account permissions.
- For production, set `DEBUG = False`, set appropriate `ALLOWED_HOSTS`, and use secure credentials.
- If you want to fetch the brand for products, you must use the Amazon Catalog Items API as described in the backend logic.

---

## License

MIT License

---

## Author

- [Your Name](https://github.com/your-username)
