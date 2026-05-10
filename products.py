"""
products.py - GET /products endpoint
Fetches product catalog from MongoDB
"""

from flask import Blueprint, jsonify
from app.db import get_mongo_db
from prometheus_client import Counter, Histogram
import time

products_bp = Blueprint('products', __name__)

# Prometheus metrics for this endpoint
PRODUCTS_REQUESTS = Counter('products_requests_total', 'Total GET /products requests')
PRODUCTS_LATENCY = Histogram('products_request_duration_seconds', 'Latency of /products endpoint')


@products_bp.route('/products', methods=['GET'])
def get_products():
    """
    Fetch all products from MongoDB product catalog collection.
    MongoDB is ideal here because product data is flexible/schemaless.
    """
    PRODUCTS_REQUESTS.inc()         # Increment request counter
    start = time.time()             # Start timer for latency

    try:
        db = get_mongo_db()
        products_collection = db["products"]

        # Fetch all products, exclude internal MongoDB _id from response
        products = list(products_collection.find({}, {"_id": 0}))

        PRODUCTS_LATENCY.observe(time.time() - start)   # Record latency
        return jsonify({"status": "success", "count": len(products), "products": products}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
