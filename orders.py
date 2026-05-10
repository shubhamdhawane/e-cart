"""
orders.py - POST /order endpoint
Saves orders to PostgreSQL (transactional, ACID-compliant)
"""

from flask import Blueprint, jsonify, request
from app.db import get_postgres_conn
from prometheus_client import Counter, Histogram
import time

orders_bp = Blueprint('orders', __name__)

# Prometheus metrics
ORDERS_REQUESTS = Counter('orders_requests_total', 'Total POST /order requests')
ORDERS_LATENCY = Histogram('orders_request_duration_seconds', 'Latency of /order endpoint')


@orders_bp.route('/order', methods=['POST'])
def place_order():
    """
    Place a new order. Saves to PostgreSQL because orders need
    ACID transactions - we can't afford to lose or duplicate order data.

    Expected JSON body:
    {
        "user_id": 1,
        "product_id": "PROD001",
        "quantity": 2,
        "total_price": 49.99
    }
    """
    ORDERS_REQUESTS.inc()
    start = time.time()

    try:
        data = request.get_json()

        # Basic validation
        required = ["user_id", "product_id", "quantity", "total_price"]
        for field in required:
            if field not in data:
                return jsonify({"status": "error", "message": f"Missing field: {field}"}), 400

        conn = get_postgres_conn()
        cur = conn.cursor()

        # Insert the order into the orders table
        cur.execute("""
            INSERT INTO orders (user_id, product_id, quantity, total_price, status)
            VALUES (%s, %s, %s, %s, 'pending')
            RETURNING id, created_at
        """, (data["user_id"], data["product_id"], data["quantity"], data["total_price"]))

        order_id, created_at = cur.fetchone()
        conn.commit()           # Commit the transaction
        cur.close()
        conn.close()

        ORDERS_LATENCY.observe(time.time() - start)
        return jsonify({
            "status": "success",
            "order_id": order_id,
            "created_at": str(created_at)
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
