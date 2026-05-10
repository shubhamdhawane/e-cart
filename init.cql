-- Cassandra initialization CQL
-- Creates keyspace and tables for user activity tracking

-- Create keyspace with replication across 3 nodes
-- SimpleStrategy is fine for single datacenter setups
CREATE KEYSPACE IF NOT EXISTS ecommerce
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 3      -- Data stored on all 3 Cassandra nodes
};

-- Switch to ecommerce keyspace
USE ecommerce;

-- User activity log table
-- Partitioned by user_id so all events for a user are on the same node
-- Clustered by created_at so events are stored in time order
CREATE TABLE IF NOT EXISTS user_activity (
    event_id    UUID,
    user_id     TEXT,
    event_type  TEXT,       -- e.g. page_view, add_to_cart, purchase
    product_id  TEXT,
    metadata    TEXT,
    created_at  TIMESTAMP,
    PRIMARY KEY ((user_id), created_at, event_id)
) WITH CLUSTERING ORDER BY (created_at DESC);   -- Latest events first
