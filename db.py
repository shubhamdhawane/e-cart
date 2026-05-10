"""
db.py - Database connection handlers
Each function returns a connection/client for the respective database
"""

import os
import psycopg2                         # PostgreSQL driver
from pymongo import MongoClient         # MongoDB driver
from cassandra.cluster import Cluster   # Cassandra driver


# ─────────────────────────────────────────────
# PostgreSQL - Used for orders and users
# ─────────────────────────────────────────────
def get_postgres_conn():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres-primary"),
        port=os.getenv("POSTGRES_PORT", 5432),
        dbname=os.getenv("POSTGRES_DB", "ecommerce"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "admin123")
    )


# ─────────────────────────────────────────────
# MongoDB - Used for product catalog
# ─────────────────────────────────────────────
def get_mongo_db():
    uri = os.getenv("MONGO_URI", "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0")
    client = MongoClient(uri)
    return client["ecommerce"]   # Return the ecommerce database


# ─────────────────────────────────────────────
# Cassandra - Used for high-volume activity logs
# ─────────────────────────────────────────────
def get_cassandra_session():
    hosts = os.getenv("CASSANDRA_HOSTS", "cassandra1,cassandra2,cassandra3").split(",")
    cluster = Cluster(hosts)
    session = cluster.connect("ecommerce")  # Connect to the ecommerce keyspace
    return session
