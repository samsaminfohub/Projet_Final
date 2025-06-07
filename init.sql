-- Script d'initialisation pour le projet de détection d'anomalies IoT
-- Base de données: iot_anomaly_db

-- Supprimer les tables si elles existent (pour réinitialisation)
DROP TABLE IF EXISTS anomalies CASCADE;
DROP TABLE IF EXISTS ml_models CASCADE;
DROP TABLE IF EXISTS maintenance_predictions CASCADE;
DROP TABLE IF EXISTS sensor_data CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS equipment CASCADE;

-- Extension pour UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table des utilisateurs
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Table des équipements
CREATE TABLE equipment (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(100),
    model VARCHAR(50),
    serial_number VARCHAR(100) UNIQUE,
    installation_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des données de capteurs IoT
CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES equipment(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    temperature REAL,
    humidity REAL,
    pressure REAL,
    vibration_x REAL,
    vibration_y REAL,
    vibration_z REAL,
    current_amperage REAL,
    voltage REAL,
    power_consumption REAL,
    is_anomaly BOOLEAN DEFAULT false,
    anomaly_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des anomalies détectées
CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    sensor_data_id INTEGER REFERENCES sensor_data(id),
    equipment_id INTEGER REFERENCES equipment(id),
    anomaly_type VARCHAR(50),
    severity VARCHAR(20) DEFAULT 'medium',
    anomaly_score REAL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'open',
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    resolved_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des modèles ML
CREATE TABLE ml_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    algorithm VARCHAR(50),
    version VARCHAR(20),
    accuracy REAL,
    precision_score REAL,
    recall_score REAL,
    f1_score REAL,
    training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_path VARCHAR(255),
    parameters JSONB,
    is_active BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des prédictions de maintenance
CREATE TABLE maintenance_predictions (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES equipment(id),
    model_id INTEGER REFERENCES ml_models(id),
    prediction_type VARCHAR(50),
    predicted_failure_date TIMESTAMP,
    confidence_score REAL,
    maintenance_priority VARCHAR(20) DEFAULT 'medium',
    recommendations TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des alertes
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    equipment_id INTEGER REFERENCES equipment(id),
    anomaly_id INTEGER REFERENCES anomalies(id),
    alert_type VARCHAR(50),
    priority VARCHAR(20) DEFAULT 'medium',
    message TEXT,
    is_read BOOLEAN DEFAULT false,
    is_acknowledged BOOLEAN DEFAULT false,
    acknowledged_by INTEGER REFERENCES users(id),
    acknowledged_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour optimiser les performances
CREATE INDEX idx_sensor_data_timestamp ON sensor_data(timestamp);
CREATE INDEX idx_sensor_data_equipment_id ON sensor_data(equipment_id);
CREATE INDEX idx_sensor_data_is_anomaly ON sensor_data(is_anomaly);
CREATE INDEX idx_anomalies_detected_at ON anomalies(detected_at);
CREATE INDEX idx_anomalies_status ON anomalies(status);
CREATE INDEX idx_anomalies_equipment_id ON anomalies(equipment_id);
CREATE INDEX idx_maintenance_predictions_equipment_id ON maintenance_predictions(equipment_id);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);
CREATE INDEX idx_alerts_is_read ON alerts(is_read);

-- Données initiales pour les tests

-- Utilisateur admin par défaut
INSERT INTO users (username, email, password_hash, role) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewQNEk0W8gSH1xGW', 'admin'),
('operator', 'operator@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewQNEk0W8gSH1xGW', 'operator'),
('viewer', 'viewer@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewQNEk0W8gSH1xGW', 'viewer');

-- Équipements de test
INSERT INTO equipment (name, type, location, model, serial_number, installation_date) VALUES
('Compresseur A1', 'Compressor', 'Atelier 1', 'COMP-500X', 'COMP001', '2023-01-15'),
('Moteur B2', 'Motor', 'Atelier 2', 'MOT-750', 'MOT002', '2023-02-20'),
('Pompe C3', 'Pump', 'Station de pompage', 'PUMP-300', 'PUMP003', '2023-03-10'),
('Ventilateur D4', 'Fan', 'Système de ventilation', 'FAN-1200', 'FAN004', '2023-04-05'),
('Générateur E5', 'Generator', 'Salle des machines', 'GEN-2000', 'GEN005', '2023-05-12');

-- Modèle ML par défaut
INSERT INTO ml_models (model_name, model_type, algorithm, version, accuracy, created_by) VALUES
('Isolation Forest v1.0', 'Anomaly Detection', 'Isolation Forest', '1.0', 0.95, 1),
('Random Forest Classifier', 'Classification', 'Random Forest', '1.0', 0.92, 1),
('LSTM Predictor', 'Time Series', 'LSTM', '1.0', 0.88, 1);

-- Trigger pour mettre à jour la colonne updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Appliquer le trigger aux tables qui ont une colonne updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_equipment_updated_at BEFORE UPDATE ON equipment
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maintenance_predictions_updated_at BEFORE UPDATE ON maintenance_predictions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Vue pour les statistiques en temps réel
CREATE VIEW v_equipment_stats AS
SELECT 
    e.id,
    e.name,
    e.type,
    e.location,
    e.status,
    COUNT(sd.id) as total_readings,
    COUNT(CASE WHEN sd.is_anomaly = true THEN 1 END) as anomaly_count,
    AVG(sd.temperature) as avg_temperature,
    AVG(sd.humidity) as avg_humidity,
    AVG(sd.pressure) as avg_pressure,
    AVG(sd.power_consumption) as avg_power,
    MAX(sd.timestamp) as last_reading
FROM equipment e
LEFT JOIN sensor_data sd ON e.id = sd.equipment_id
WHERE sd.timestamp >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY e.id, e.name, e.type, e.location, e.status;

-- Vue pour les anomalies récentes
CREATE VIEW v_recent_anomalies AS
SELECT 
    a.id,
    e.name as equipment_name,
    e.type as equipment_type,
    a.anomaly_type,
    a.severity,
    a.anomaly_score,
    a.description,
    a.status,
    a.detected_at,
    CASE 
        WHEN a.detected_at >= CURRENT_TIMESTAMP - INTERVAL '1 hour' THEN 'Très récente'
        WHEN a.detected_at >= CURRENT_TIMESTAMP - INTERVAL '6 hours' THEN 'Récente'
        WHEN a.detected_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours' THEN 'Aujourd''hui'
        ELSE 'Ancienne'
    END as time_category
FROM anomalies a
JOIN equipment e ON a.equipment_id = e.id
WHERE a.detected_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY a.detected_at DESC;

-- Permissions et sécurité
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO admin;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO admin;

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Base de données initialisée avec succès !';
    RAISE NOTICE 'Tables créées: users, equipment, sensor_data, anomalies, ml_models, maintenance_predictions, alerts';
    RAISE NOTICE 'Vues créées: v_equipment_stats, v_recent_anomalies';
    RAISE NOTICE 'Utilisateurs de test créés avec mot de passe par défaut';
END $$;