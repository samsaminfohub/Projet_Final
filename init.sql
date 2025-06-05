-- Création de la base de données et des tables

-- Table des capteurs IoT
CREATE TABLE IF NOT EXISTS sensors (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) UNIQUE NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    location VARCHAR(100) NOT NULL,
    installation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des données de capteurs
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    temperature FLOAT,
    humidity FLOAT,
    pressure FLOAT,
    vibration_x FLOAT,
    vibration_y FLOAT,
    vibration_z FLOAT,
    current FLOAT,
    voltage FLOAT,
    power FLOAT,
    FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id)
);

-- Table des anomalies détectées
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    anomaly_type VARCHAR(100),
    anomaly_score FLOAT,
    severity VARCHAR(20),
    description TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (sensor_id) REFERENCES sensors(sensor_id)
);

-- Table des modèles ML
CREATE TABLE IF NOT EXISTS ml_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    algorithm VARCHAR(50),
    accuracy FLOAT,
    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE,
    mlflow_run_id VARCHAR(100)
);

-- Insertion de capteurs d'exemple
INSERT INTO sensors (sensor_id, sensor_type, location) VALUES
('TEMP_001', 'Temperature', 'Production Line A'),
('TEMP_002', 'Temperature', 'Production Line B'),
('VIB_001', 'Vibration', 'Motor Assembly 1'),
('VIB_002', 'Vibration', 'Motor Assembly 2'),
('POWER_001', 'Power', 'Main Electrical Panel'),
('POWER_002', 'Power', 'Secondary Panel')
ON CONFLICT (sensor_id) DO NOTHING;

-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_data_sensor_id ON sensor_data(sensor_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomalies_sensor_id ON anomalies(sensor_id);