import psycopg2
import numpy as np
import time
import os
from datetime import datetime, timedelta
import random

# Configuration de la base de données
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'iot_anomaly_db')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin123')

class IoTDataGenerator:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.sensors = [
            {'id': 'TEMP_001', 'type': 'Temperature', 'base_temp': 45.0, 'variation': 5.0},
            {'id': 'TEMP_002', 'type': 'Temperature', 'base_temp': 38.0, 'variation': 4.0},
            {'id': 'VIB_001', 'type': 'Vibration', 'base_vib': 2.5, 'variation': 0.8},
            {'id': 'VIB_002', 'type': 'Vibration', 'base_vib': 3.2, 'variation': 1.0},
            {'id': 'POWER_001', 'type': 'Power', 'base_power': 1200.0, 'variation': 200.0},
            {'id': 'POWER_002', 'type': 'Power', 'base_power': 800.0, 'variation': 150.0}
        ]
    
    def connect_db(self):
        """Connexion à la base de données PostgreSQL"""
        try:
            self.conn = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD
            )
            self.cursor = self.conn.cursor()
            print("✅ Connexion à PostgreSQL établie")
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")
            return False
    
    def generate_sensor_data(self, sensor):
        """Génère des données réalistes pour un capteur"""
        
        # Génération de données de base
        timestamp = datetime.now()
        
        # Simulation de variations normales et d'anomalies occasionnelles
        anomaly_probability = 0.05  # 5% de chance d'anomalie
        is_anomaly = random.random() < anomaly_probability
        
        if sensor['type'] == 'Temperature':
            if is_anomaly:
                temperature = sensor['base_temp'] + random.uniform(-15, 20)  # Anomalie de température
            else:
                temperature = sensor['base_temp'] + random.gauss(0, sensor['variation'])
            
            humidity = max(20, min(80, 50 + random.gauss(0, 10)))
            pressure = 1013.25 + random.gauss(0, 5)
            
            return {
                'sensor_id': sensor['id'],
                'timestamp': timestamp,
                'temperature': round(temperature, 2),
                'humidity': round(humidity, 2),
                'pressure': round(pressure, 2),
                'vibration_x': None,
                'vibration_y': None,
                'vibration_z': None,
                'current': None,
                'voltage': None,
                'power': None
            }
            
        elif sensor['type'] == 'Vibration':
            if is_anomaly:
                vib_multiplier = random.uniform(3, 8)  # Vibration anormale
            else:
                vib_multiplier = 1
                
            vib_x = sensor['base_vib'] * vib_multiplier + random.gauss(0, 0.3)
            vib_y = sensor['base_vib'] * vib_multiplier + random.gauss(0, 0.3)
            vib_z = sensor['base_vib'] * vib_multiplier + random.gauss(0, 0.2)
            
            return {
                'sensor_id': sensor['id'],
                'timestamp': timestamp,
                'temperature': None,
                'humidity': None,
                'pressure': None,
                'vibration_x': round(vib_x, 3),
                'vibration_y': round(vib_y, 3),
                'vibration_z': round(vib_z, 3),
                'current': None,
                'voltage': None,
                'power': None
            }
            
        elif sensor['type'] == 'Power':
            if is_anomaly:
                power = sensor['base_power'] + random.uniform(-400, 500)  # Pic de consommation
            else:
                power = sensor['base_power'] + random.gauss(0, sensor['variation'])
            
            voltage = 230 + random.gauss(0, 5)
            current = power / voltage if voltage > 0 else 0
            
            return {
                'sensor_id': sensor['id'],
                'timestamp': timestamp,
                'temperature': None,
                'humidity': None,
                'pressure': None,
                'vibration_x': None,
                'vibration_y': None,
                'vibration_z': None,
                'current': round(current, 2),
                'voltage': round(voltage, 2),
                'power': round(power, 2)
            }
    
    def insert_data(self, data):
        """Insert les données dans la base"""
        try:
            insert_query = """
            INSERT INTO sensor_data (
                sensor_id, timestamp, temperature, humidity, pressure,
                vibration_x, vibration_y, vibration_z, current, voltage, power
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(insert_query, (
                data['sensor_id'],
                data['timestamp'],
                data['temperature'],
                data['humidity'],
                data['pressure'],
                data['vibration_x'],
                data['vibration_y'],
                data['vibration_z'],
                data['current'],
                data['voltage'],
                data['power']
            ))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"❌ Erreur d'insertion: {e}")
            self.conn.rollback()
            return False
    
    def generate_historical_data(self, hours_back=24):
        """Génère des données historiques"""
        print(f"📊 Génération de données historiques ({hours_back}h)...")
        
        start_time = datetime.now() - timedelta(hours=hours_back)
        current_time = start_time
        
        total_records = 0
        
        while current_time < datetime.now():
            for sensor in self.sensors:
                # Génère des données toutes les 5 minutes
                data = self.generate_sensor_data(sensor)
                data['timestamp'] = current_time
                
                if self.insert_data(data):
                    total_records += 1
                
            current_time += timedelta(minutes=5)
        
        print(f"✅ {total_records} enregistrements historiques générés")
    
    def run_continuous(self):
        """Lance la génération continue de données"""
        print("🚀 Démarrage du générateur de données IoT...")
        
        if not self.connect_db():
            return
        
        # Génération de données historiques au démarrage
        self.generate_historical_data(24)
        
        print("📡 Mode temps réel activé...")
        
        try:
            while True:
                # Génération de données pour tous les capteurs
                for sensor in self.sensors:
                    data = self.generate_sensor_data(sensor)
                    
                    if self.insert_data(data):
                        print(f"📊 {sensor['id']}: {data}")
                    else:
                        print(f"❌ Erreur pour {sensor['id']}")
                
                # Attente avant la prochaine génération (30 secondes)
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du générateur...")
        except Exception as e:
            print(f"❌ Erreur: {e}")
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
            print("✅ Connexion fermée")

def main():
    """Fonction principale"""
    print("🔧 Initialisation du générateur de données IoT...")
    
    # Attente que la base soit prête
    time.sleep(10)
    
    generator = IoTDataGenerator()
    generator.run_continuous()

if __name__ == "__main__":
    main()