# 🛒 E-Commerce Backend - Microservices Architecture

A production-ready e-commerce backend using multiple databases for their individual strengths.

---

## 📐 Architecture Overview

```
Client
  │
  ▼
Flask API (Port 5000)
  ├── GET  /products  ──► MongoDB       (flexible product catalog)
  ├── POST /order     ──► PostgreSQL    (ACID transactions)
  ├── POST /track     ──► Cassandra     (high-volume event logs)
  └── GET  /metrics   ──► Prometheus    (observability)

Monitoring Stack
  ├── Prometheus (Port 9090) ──► scrapes /metrics
  └── Grafana    (Port 3000) ──► visualizes Prometheus data

Analytics
  └── Apache Spark (Master: 8080, Port: 7077)

Search
  └── Apache Solr (Port 8983)
```

---

## 📁 Project Structure

```
ecommerce-backend/
├── app/
│   ├── main.py               # Flask entry point
│   ├── db.py                 # DB connection helpers
│   ├── Dockerfile
│   ├── requirements.txt
│   └── routes/
│       ├── products.py       # GET /products (MongoDB)
│       ├── orders.py         # POST /order (PostgreSQL)
│       ├── tracking.py       # POST /track (Cassandra)
│       └── metrics.py        # GET /metrics (Prometheus)
├── db/
│   ├── postgres/
│   │   └── init.sql          # Table creation + sample users
│   ├── mongo/
│   │   ├── init-replica.js   # Replica set init
│   │   └── seed_mongo.py     # Sample product data
│   └── cassandra/
│       └── init.cql          # Keyspace + table creation
├── monitoring/
│   ├── prometheus.yml        # Scrape config
│   └── grafana-dashboard.json
├── scripts/
│   ├── postgres_backup.sh    # pg_dump backup
│   ├── mongo_backup.sh       # mongodump backup
│   ├── cassandra_backup.sh   # nodetool snapshot
│   └── init_cassandra.sh     # Wait + run CQL init
├── docker-compose.yml
└── README.md
```

---

## 🚀 Setup Instructions

### Step 1 — Clone and enter project
```bash
cd ecommerce-backend
```

### Step 2 — Start all services
```bash
docker-compose up -d
```
> First run takes 5-10 minutes to pull images and initialize clusters.

### Step 3 — Initialize MongoDB Replica Set
```bash
# Wait ~10 seconds for mongo containers to be ready, then:
docker exec mongo1 mongosh --eval "
  rs.initiate({
    _id: 'rs0',
    members: [
      { _id: 0, host: 'mongo1:27017' },
      { _id: 1, host: 'mongo2:27017' },
      { _id: 2, host: 'mongo3:27017' }
    ]
  })
"
```

### Step 4 — Seed product data into MongoDB
```bash
docker exec flask-api python db/mongo/seed_mongo.py
```

### Step 5 — Initialize Cassandra keyspace
```bash
# Wait ~30 seconds for all 3 Cassandra nodes to join cluster
bash scripts/init_cassandra.sh
# OR manually:
docker exec cassandra1 cqlsh -f /db/cassandra/init.cql
```

### Step 6 — Verify everything is running
```bash
docker-compose ps
```

---

## 🧪 Sample curl Commands

### GET /products — Fetch product catalog (MongoDB)
```bash
curl http://localhost:5000/products
```

### POST /order — Place an order (PostgreSQL)
```bash
curl -X POST http://localhost:5000/order \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "product_id": "PROD001",
    "quantity": 2,
    "total_price": 99.98
  }'
```

### POST /track — Track user activity (Cassandra)
```bash
curl -X POST http://localhost:5000/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "event_type": "page_view",
    "product_id": "PROD001",
    "metadata": "homepage"
  }'
```

### GET /metrics — Prometheus metrics
```bash
curl http://localhost:5000/metrics
```

---

## 📊 Monitoring

| Tool       | URL                        | Credentials       |
|------------|----------------------------|-------------------|
| Prometheus | http://localhost:9090       | —                 |
| Grafana    | http://localhost:3000       | admin / admin123  |
| Spark UI   | http://localhost:8080       | —                 |
| Solr UI    | http://localhost:8983/solr  | —                 |

### Grafana Setup:
1. Open http://localhost:3000
2. Go to **Connections → Data Sources → Add Prometheus**
3. URL: `http://prometheus:9090`
4. Import `monitoring/grafana-dashboard.json`

---

## 💾 Backup Commands

```bash
# PostgreSQL backup
bash scripts/postgres_backup.sh

# MongoDB backup
bash scripts/mongo_backup.sh

# Cassandra snapshot
bash scripts/cassandra_backup.sh
```

---

## 🔍 Why Each Database?

| Database    | Used For          | Reason                                      |
|-------------|-------------------|---------------------------------------------|
| PostgreSQL  | Orders, Users     | ACID transactions — can't lose order data   |
| MongoDB     | Product Catalog   | Flexible schema — products have varied attrs|
| Cassandra   | Activity Logs     | Handles millions of writes per second       |
| Spark       | Analytics         | Distributed processing of large datasets    |
| Solr        | Search            | Full-text search with faceting              |

---

## 🛑 Stop Everything

```bash
docker-compose down           # Stop containers
docker-compose down -v        # Stop + delete all data volumes
```
