"""
tracking.py - POST /track endpoint
Records user activity/events to Cassandra
Cassandra is ideal for high-volume write-heavy workloads like event tracking
"""

from flask import Blueprint, jsonify, request
from app.db import get_cassandra_session
from prometheus_client import Counter, Histogram
import uuid
import time

tracking_bp = Blueprint('tracking', __name__)

# Prometheus metrics
TRACK_REQUESTS = Counter('track_requests_total', 'Total POST /track requests')
TRACK_LATENCY = Histogram('track_request_duration_seconds', 'Latency of /track endpoint')


@tracking_bp.route('/track', methods=['POST'])
def track_activity():
    """
    Track a user activity event (page view, click, purchase, etc.)
    Cassandra handles millions of writes per second - perfect for event logs.

    Expected JSON body:
    {
        "user_id": "user_123",
        "event_type": "page_view",
        "product_id": "PROD001",
        "metadata": "homepage"
    }
    """
    TRACK_REQUESTS.inc()
    start = time.time()

    try:
        data = request.get_json()

        # Validate required fields
        if "user_id" not in data or "event_type" not in data:
            return jsonify({"status": "error", "message": "user_id and event_type are required"}), 400

        session = get_cassandra_session()

        # Generate a unique event ID using UUID
        event_id = uuid.uuid4()

        # Insert event into Cassandra user_activity table
        session.execute("""
            INSERT INTO user_activity (event_id, user_id, event_type, product_id, metadata, created_at)
            VALUES (%s, %s, %s, %s, %s, toTimestamp(now()))
        """, (
            event_id,
            data["user_id"],
            data["event_type"],
            data.get("product_id", ""),     # Optional field
            data.get("metadata", "")        # Optional field
        ))

        TRACK_LATENCY.observe(time.time() - start)
        return jsonify({
            "status": "success",
            "event_id": str(event_id)
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
