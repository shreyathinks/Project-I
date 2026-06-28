-- PostgreSQL initialization script
-- Runs once when the container is first created

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Ensure the database exists (already created by POSTGRES_DB env var)
-- This script is for extensions and initial setup only

GRANT ALL PRIVILEGES ON DATABASE kitchen_db TO kitchen_user;
