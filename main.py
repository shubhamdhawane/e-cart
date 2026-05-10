"""
main.py - Entry point for the Flask e-commerce API
Connects to PostgreSQL, MongoDB, and Cassandra
"""

from flask import Flask
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from routes.products import products_bp
from routes.orders import orders_bp
from routes.tracking import tracking_bp
from routes.metrics import metrics_bp

app = Flask(__name__)

# Register all route blueprints
app.register_blueprint(products_bp)   # MongoDB - product catalog
app.register_blueprint(orders_bp)     # PostgreSQL - orders
app.register_blueprint(tracking_bp)   # Cassandra - user activity
app.register_blueprint(metrics_bp)    # Prometheus - metrics

# Mount Prometheus metrics endpoint at /metrics
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
