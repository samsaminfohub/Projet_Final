-- Create database and user
CREATE DATABASE minilab;
CREATE USER minilabuser WITH PASSWORD 'minilabpass';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE minilab TO minilabuser;

-- Connect to the database
\c minilab

-- Create tables (example - customize as needed)
CREATE TABLE IF NOT EXISTS lab_data (
    id SERIAL PRIMARY KEY,
    experiment_name VARCHAR(255) NOT NULL,
    parameter1 FLOAT,
    parameter2 FLOAT,
    result FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant privileges on tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO minilabuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO minilabuser;
                        