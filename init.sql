-- Création de la base de données et des tables

-- Drop existing tables (be careful - this will delete data!)
DROP TABLE IF EXISTS anomalies CASCADE;
DROP TABLE IF EXISTS sensors CASCADE;
DROP TABLE IF EXISTS sensor_data CASCADE;

-- Create sensors table
CREATE TABLE sensors (
    sensor_id SERIAL PRIMARY KEY,
    sensor_type VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create sensor_data table for IoT readings
CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER REFERENCES sensors(sensor_id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    temperature REAL,
    humidity REAL,
    pressure REAL,
    vibration_x REAL,
    vibration_y REAL,
    vibration_z REAL,
    current_amp REAL,
    voltage REAL,
    power_consumption REAL
);

-- Create anomalies table
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    sensor_id INTEGER REFERENCES sensors(sensor_id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    anomaly_score REAL NOT NULL,
    anomaly_type VARCHAR(50),
    description TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    temperature REAL,
    humidity REAL,
    pressure REAL,
    vibration_x REAL,
    vibration_y REAL,
    vibration_z REAL,
    current_amp REAL,
    voltage REAL,
    power_consumption REAL
);

-- Insert sample sensors
INSERT INTO sensors (sensor_type, location) VALUES
('temperature', 'Factory Floor A'),
('vibration', 'Motor Unit 1'),
('electrical', 'Power Panel B'),
('environmental', 'Warehouse Section C');

-- Create indexes for better performance
CREATE INDEX idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX idx_anomalies_sensor_id ON anomalies(sensor_id);
CREATE INDEX idx_sensor_data_timestamp ON sensor_data(timestamp);
CREATE INDEX idx_sensor_data_sensor_id ON sensor_data(sensor_id);



-- Add sensor_id column to anomalies table
ALTER TABLE anomalies 
ADD COLUMN sensor_id INTEGER;

-- If you want to reference the sensors table
ALTER TABLE anomalies
ADD CONSTRAINT fk_anomaly_sensor
FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id);


