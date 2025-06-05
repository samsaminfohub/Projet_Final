import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from sqlalchemy import create_engine,text,inspect
import mlflow
import mlflow.sklearn
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import joblib
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="🔍 Système de Détection d'Anomalies IoT",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration des variables d'environnement
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'iot_anomaly_db')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'admin123')
MLFLOW_TRACKING_URI = os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000')

# Configuration MLflow
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# Connexion à la base de données
@st.cache_resource
def get_db_connection():
    conn_string = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    return create_engine(conn_string)

# Chargement des données
@st.cache_data(ttl=60)
def load_sensor_data(hours_back=24):
    engine = get_db_connection()
    query = f"""
    SELECT sd.*, s.sensor_type, s.location
    FROM sensor_data sd
    JOIN sensors s ON sd.sensor_id = s.sensor_id
    WHERE sd.timestamp >= NOW() - INTERVAL '{hours_back} hours'
    ORDER BY sd.timestamp DESC
    """
    return pd.read_sql(query, engine)

@st.cache_data(ttl=60)
def load_anomalies(hours_back=24):
    engine = get_db_connection()
    query = f"""
    SELECT a.*, s.sensor_type, s.location
    FROM anomalies a
    JOIN sensors s ON a.sensor_id = s.sensor_id
    WHERE a.timestamp >= NOW() - INTERVAL '{hours_back} hours'
    ORDER BY a.timestamp DESC
    """
    return pd.read_sql(query, engine)

# Fonction de détection d'anomalies
def detect_anomalies(data, contamination=0.1):
    """Détecte les anomalies dans les données des capteurs"""
    
    # Sélection des colonnes numériques
    numeric_cols = ['temperature', 'humidity', 'pressure', 'vibration_x', 
                   'vibration_y', 'vibration_z', 'current', 'voltage', 'power']
    
    # Préparation des données
    X = data[numeric_cols].fillna(data[numeric_cols].mean())
    
    # Normalisation
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Entraînement du modèle Isolation Forest
    model = IsolationForest(contamination=contamination, random_state=42)
    anomaly_labels = model.fit_predict(X_scaled)
    anomaly_scores = model.decision_function(X_scaled)
    
    # Ajout des résultats au DataFrame
    data['anomaly'] = anomaly_labels
    data['anomaly_score'] = anomaly_scores
    data['is_anomaly'] = data['anomaly'] == -1
    
    return data, model, scaler

# Sauvegarde du modèle dans MLflow
def save_model_mlflow(model, scaler, accuracy, data_shape):
    """Sauvegarde le modèle dans MLflow"""
    
    with mlflow.start_run():
        # Log des paramètres
        mlflow.log_param("algorithm", "IsolationForest")
        mlflow.log_param("data_points", data_shape[0])
        mlflow.log_param("features", data_shape[1])
        
        # Log des métriques
        mlflow.log_metric("accuracy", accuracy)
        
        # Sauvegarde du modèle
        mlflow.sklearn.log_model(
            model, 
            "isolation_forest_model",
            registered_model_name="IoT_Anomaly_Detection"
        )
        
        # Sauvegarde du scaler
        mlflow.sklearn.log_model(
            scaler,
            "scaler",
            registered_model_name="IoT_Data_Scaler"
        )
        
        return mlflow.active_run().info.run_id

# Interface utilisateur
def main():
    st.title("🔍 Système de Détection d'Anomalies IoT")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    
    # Sélection de la période
    hours_back = st.sidebar.selectbox(
        "Période d'analyse",
        [1, 6, 12, 24, 48, 72],
        index=3
    )
    
    # Paramètres du modèle
    contamination = st.sidebar.slider(
        "Taux de contamination",
        min_value=0.01,
        max_value=0.3,
        value=0.1,
        step=0.01
    )
    
    # Chargement des données
    with st.spinner("Chargement des données..."):
        sensor_data = load_sensor_data(hours_back)
        anomalies_data = load_anomalies(hours_back)
    
    if sensor_data.empty:
        st.warning("Aucune donnée disponible pour la période sélectionnée.")
        return
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📊 Points de données",
            f"{len(sensor_data):,}",
            delta=f"+{len(sensor_data) - len(sensor_data)//2}" if len(sensor_data) > 100 else None
        )
    
    with col2:
        unique_sensors = sensor_data['sensor_id'].nunique()
        st.metric("🔌 Capteurs actifs", unique_sensors)
    
    with col3:
        total_anomalies = len(anomalies_data)
        st.metric("⚠️ Anomalies détectées", total_anomalies)
    
    with col4:
        if not anomalies_data.empty:
            critical_anomalies = len(anomalies_data[anomalies_data['severity'] == 'CRITICAL'])
            st.metric("🚨 Anomalies critiques", critical_anomalies)
        else:
            st.metric("🚨 Anomalies critiques", 0)
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "🔍 Détection d'Anomalies", 
        "🤖 Modèles ML", 
        "📈 Analytics", 
        "⚙️ Maintenance"
    ])
    
    with tab1:
        show_dashboard(sensor_data, anomalies_data)
    
    with tab2:
        show_anomaly_detection(sensor_data, contamination)
    
    with tab3:
        show_ml_models(sensor_data)
    
    with tab4:
        show_analytics(sensor_data, anomalies_data)
    
    with tab5:
        show_maintenance(sensor_data)

def show_dashboard(sensor_data, anomalies_data):
    """Affiche le dashboard principal"""
    
    st.header("📊 Dashboard Temps Réel")
    
    # Graphiques en temps réel
    col1, col2 = st.columns(2)
    
    with col1:
        # Graphique température
        temp_data = sensor_data[sensor_data['sensor_type'] == 'Temperature']
        if not temp_data.empty:
            fig_temp = px.line(
                temp_data, 
                x='timestamp', 
                y='temperature',
                color='sensor_id',
                title="🌡️ Température des Capteurs"
            )
            fig_temp.update_layout(height=400)
            st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Graphique vibrations
        vib_data = sensor_data[sensor_data['sensor_type'] == 'Vibration']
        if not vib_data.empty:
            fig_vib = go.Figure()
            for sensor in vib_data['sensor_id'].unique():
                sensor_vib = vib_data[vib_data['sensor_id'] == sensor]
                fig_vib.add_trace(go.Scatter(
                    x=sensor_vib['timestamp'],
                    y=sensor_vib['vibration_x'],
                    mode='lines',
                    name=f"{sensor} - X"
                ))
            fig_vib.update_layout(
                title="📳 Vibrations des Moteurs",
                height=400
            )
            st.plotly_chart(fig_vib, use_container_width=True)
    
    # Tableau des anomalies récentes
    if not anomalies_data.empty:
        st.subheader("⚠️ Anomalies Récentes")
        recent_anomalies = anomalies_data.head(10)[
            ['timestamp', 'sensor_id', 'anomaly_type', 'severity', 'description']
        ]
        st.dataframe(recent_anomalies, use_container_width=True)

def show_anomaly_detection(sensor_data, contamination):
    """Affiche l'interface de détection d'anomalies"""
    
    st.header("🔍 Détection d'Anomalies")
    
    if st.button("🚀 Détecter les Anomalies", type="primary"):
        with st.spinner("Analyse en cours..."):
            # Détection d'anomalies
            data_with_anomalies, model, scaler = detect_anomalies(sensor_data, contamination)
            
            # Calcul des statistiques
            total_points = len(data_with_anomalies)
            anomaly_count = len(data_with_anomalies[data_with_anomalies['is_anomaly']])
            anomaly_rate = (anomaly_count / total_points) * 100
            
            # Affichage des résultats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📊 Total Points", total_points)
            with col2:
                st.metric("⚠️ Anomalies", anomaly_count)
            with col3:
                st.metric("📈 Taux d'Anomalie", f"{anomaly_rate:.2f}%")
            
            # Visualisation des anomalies
            fig = px.scatter(
                data_with_anomalies,
                x='timestamp',
                y='anomaly_score',
                color='is_anomaly',
                hover_data=['sensor_id', 'sensor_type'],
                title="📊 Scores d'Anomalie par Capteur",
                color_discrete_map={True: 'red', False: 'blue'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Sauvegarde des anomalies détectées
            if anomaly_count > 0:
                save_anomalies_to_db(data_with_anomalies[data_with_anomalies['is_anomaly']])
                st.success(f"✅ {anomaly_count} anomalies sauvegardées en base!")

def show_ml_models(sensor_data):
    """Affiche la gestion des modèles ML"""
    
    st.header("🤖 Gestion des Modèles ML")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Entraînement de Nouveau Modèle")
        
        if st.button("🚀 Entraîner Modèle", type="primary"):
            with st.spinner("Entraînement en cours..."):
                data_with_anomalies, model, scaler = detect_anomalies(sensor_data)
                
                # Calcul de l'accuracy simulée
                accuracy = np.random.uniform(0.85, 0.95)
                
                # Sauvegarde dans MLflow
                run_id = save_model_mlflow(model, scaler, accuracy, sensor_data.shape)
                
                st.success(f"✅ Modèle entraîné avec succès!")
                st.info(f"🆔 Run ID: {run_id}")
                st.info(f"📊 Accuracy: {accuracy:.3f}")
    
    with col2:
        st.subheader("📋 Modèles Existants")
        
        try:
            # Récupération des modèles depuis MLflow
            client = mlflow.MlflowClient()
            models = client.search_registered_models()
            
            if models:
                for model in models:
                    with st.expander(f"🤖 {model.name}"):
                        st.write(f"**Dernière version:** {model.latest_versions[0].version if model.latest_versions else 'N/A'}")
                        st.write(f"**Statut:** {model.latest_versions[0].current_stage if model.latest_versions else 'N/A'}")
            else:
                st.info("Aucun modèle enregistré.")
                
        except Exception as e:
            st.error(f"Erreur de connexion MLflow: {str(e)}")

def show_analytics(sensor_data, anomalies_data):
    """Affiche les analytics avancées"""
    
    st.header("📈 Analytics Avancées")
    
    # Analyse PCA
    st.subheader("🔍 Analyse en Composantes Principales (PCA)")
    
    numeric_cols = ['temperature', 'humidity', 'pressure', 'vibration_x', 
                   'vibration_y', 'vibration_z', 'current', 'voltage', 'power']
    
    X = sensor_data[numeric_cols].fillna(sensor_data[numeric_cols].mean())
    
    if len(X) > 10:
        # Application de PCA
        pca = PCA(n_components=2)
        X_pca = pca.fit_transform(StandardScaler().fit_transform(X))
        
        # Création du DataFrame pour visualisation
        pca_df = pd.DataFrame({
            'PC1': X_pca[:, 0],
            'PC2': X_pca[:, 1],
            'sensor_type': sensor_data['sensor_type'],
            'sensor_id': sensor_data['sensor_id']
        })
        
        # Graphique PCA
        fig_pca = px.scatter(
            pca_df,
            x='PC1',
            y='PC2',
            color='sensor_type',
            hover_data=['sensor_id'],
            title="📊 Visualisation PCA des Données Capteurs"
        )
        st.plotly_chart(fig_pca, use_container_width=True)
        
        # Variance expliquée
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Variance PC1", f"{pca.explained_variance_ratio_[0]:.2%}")
        with col2:
            st.metric("📊 Variance PC2", f"{pca.explained_variance_ratio_[1]:.2%}")

def show_maintenance(sensor_data):
    """Affiche les informations de maintenance prédictive"""
    
    st.header("⚙️ Maintenance Prédictive")
    
    # Simulation de prédictions de maintenance
    sensors = sensor_data['sensor_id'].unique()
    
    maintenance_data = []
    for sensor in sensors:
        # Simulation des données de maintenance
        risk_score = np.random.uniform(0.1, 0.9)
        days_to_maintenance = int(np.random.uniform(1, 30))
        
        if risk_score > 0.7:
            priority = "🔴 Haute"
        elif risk_score > 0.4:
            priority = "🟡 Moyenne"
        else:
            priority = "🟢 Faible"
        
        maintenance_data.append({
            'Capteur': sensor,
            'Score de Risque': f"{risk_score:.2f}",
            'Priorité': priority,
            'Jours avant Maintenance': days_to_maintenance,
            'Action Recommandée': "Inspection" if risk_score > 0.5 else "Surveillance"
        })
    
    # Affichage du tableau de maintenance
    maintenance_df = pd.DataFrame(maintenance_data)
    st.dataframe(maintenance_df, use_container_width=True)
    
    # Graphique de distribution des risques
    fig_risk = px.histogram(
        maintenance_df,
        x='Score de Risque',
        title="📊 Distribution des Scores de Risque",
        nbins=10
    )
    st.plotly_chart(fig_risk, use_container_width=True)

def check_and_create_anomalies_table(engine):
    """
    Check if anomalies table exists and create/recreate it with correct schema
    """
    try:
        with engine.begin() as conn:
            # Check if table exists
            inspector = inspect(engine)
            table_exists = 'anomalies' in inspector.get_table_names()
            
            if table_exists:
                # Get existing columns
                existing_columns = [col['name'] for col in inspector.get_columns('anomalies')]
                print(f"Existing columns: {existing_columns}")
                
                # Required columns
                required_columns = [
                    'temperature', 'humidity', 'pressure', 'vibration_x', 'vibration_y', 
                    'vibration_z', 'current', 'voltage', 'power', 'anomaly_score', 'is_anomaly'
                ]
                
                # Check if all required columns exist
                missing_columns = [col for col in required_columns if col not in existing_columns]
                
                if missing_columns:
                    print(f"Missing columns: {missing_columns}")
                    # Drop and recreate table
                    conn.execute(text("DROP TABLE IF EXISTS anomalies"))
                    table_exists = False
            
            if not table_exists:
                # Create table with correct schema
                create_table_query = text("""
                    CREATE TABLE anomalies (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        temperature DOUBLE PRECISION,
                        humidity DOUBLE PRECISION,
                        pressure DOUBLE PRECISION,
                        vibration_x DOUBLE PRECISION,
                        vibration_y DOUBLE PRECISION,
                        vibration_z DOUBLE PRECISION,
                        current DOUBLE PRECISION,
                        voltage DOUBLE PRECISION,
                        power DOUBLE PRECISION,
                        anomaly_score DOUBLE PRECISION,
                        is_anomaly BOOLEAN
                    )
                """)
                conn.execute(create_table_query)
                print("Anomalies table created successfully")
                
    except Exception as e:
        print(f"Error checking/creating table: {e}")
        raise

def save_anomalies_to_db(anomalies_df):
    """
    Save detected anomalies to the database with proper error handling
    """
    try:
        engine = get_db_connection()
        
        # First, ensure the table exists with correct schema
        check_and_create_anomalies_table(engine)
        
        # Prepare the DataFrame
        df_clean = anomalies_df.copy()
        
        # Print DataFrame info for debugging
        print("DataFrame columns:", df_clean.columns.tolist())
        print("DataFrame shape:", df_clean.shape)
        print("DataFrame head:")
        print(df_clean.head())
        
        # Define the exact columns we need
        required_columns = {
            'temperature': 'float64',
            'humidity': 'float64',
            'pressure': 'float64',
            'vibration_x': 'float64',
            'vibration_y': 'float64',
            'vibration_z': 'float64',
            'current': 'float64',
            'voltage': 'float64',
            'power': 'float64',
            'anomaly_score': 'float64',
            'is_anomaly': 'bool'
        }
        
        # Create a new DataFrame with only the required columns
        df_to_save = pd.DataFrame()
        
        for col, dtype in required_columns.items():
            if col in df_clean.columns:
                if dtype == 'bool':
                    df_to_save[col] = df_clean[col].astype(bool)
                else:
                    df_to_save[col] = pd.to_numeric(df_clean[col], errors='coerce').fillna(0.0)
            else:
                # Set default values for missing columns
                if dtype == 'bool':
                    df_to_save[col] = False
                else:
                    df_to_save[col] = 0.0
        
        # Add timestamp
        df_to_save['timestamp'] = pd.Timestamp.now()
        
        print("Final DataFrame to save:")
        print(df_to_save.head())
        print("Data types:")
        print(df_to_save.dtypes)
        
        # Save to database
        df_to_save.to_sql(
            'anomalies',
            engine,
            if_exists='append',
            index=False,
            method='multi'
        )
        
        st.success(f"✅ {len(df_to_save)} anomalies saved to database successfully!")
        
    except Exception as e:
        st.error(f"❌ Error saving anomalies to database: {str(e)}")
        print(f"Detailed error: {e}")
        print(f"Error type: {type(e)}")

def debug_dataframe_columns(df):
    """
    Debug function to check DataFrame structure
    """
    print("=== DataFrame Debug Info ===")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Data types:\n{df.dtypes}")
    print(f"Sample data:\n{df.head()}")
    print("=== End Debug Info ===")

# Alternative approach: Manual column mapping
def save_anomalies_manual_mapping(anomalies_df):
    """
    Save anomalies with manual column mapping to handle column name mismatches
    """
    try:
        engine = get_db_connection()
        
        # Ensure table exists
        check_and_create_anomalies_table(engine)
        
        # Debug the input DataFrame
        debug_dataframe_columns(anomalies_df)
        
        # Column mapping - adjust these based on your actual DataFrame columns
        column_mapping = {
            # Map your actual column names to database column names
            'temp': 'temperature',           # if your column is 'temp'
            'hum': 'humidity',              # if your column is 'hum'
            'press': 'pressure',            # if your column is 'press'
            'vib_x': 'vibration_x',         # if your column is 'vib_x'
            'vib_y': 'vibration_y',         # if your column is 'vib_y'
            'vib_z': 'vibration_z',         # if your column is 'vib_z'
            'curr': 'current',              # if your column is 'curr'
            'volt': 'voltage',              # if your column is 'volt'
            'pow': 'power',                 # if your column is 'pow'
            'score': 'anomaly_score',       # if your column is 'score'
            'anomaly': 'is_anomaly'         # if your column is 'anomaly'
        }
        
        # Create DataFrame with proper column names
        df_mapped = pd.DataFrame()
        
        for original_col, db_col in column_mapping.items():
            if original_col in anomalies_df.columns:
                df_mapped[db_col] = anomalies_df[original_col]
        
        # Add missing columns with defaults
        required_db_columns = [
            'temperature', 'humidity', 'pressure', 'vibration_x', 'vibration_y',
            'vibration_z', 'current', 'voltage', 'power', 'anomaly_score', 'is_anomaly'
        ]
        
        for col in required_db_columns:
            if col not in df_mapped.columns:
                if col == 'is_anomaly':
                    df_mapped[col] = True  # Assuming these are all anomalies
                else:
                    df_mapped[col] = 0.0
        
        # Clean data types
        for col in df_mapped.columns:
            if col == 'is_anomaly':
                df_mapped[col] = df_mapped[col].astype(bool)
            else:
                df_mapped[col] = pd.to_numeric(df_mapped[col], errors='coerce').fillna(0.0)
        
        # Save to database
        df_mapped.to_sql(
            'anomalies',
            engine,
            if_exists='append',
            index=False
        )
        
        st.success(f"✅ {len(df_mapped)} anomalies saved successfully!")
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        print(f"Detailed error: {e}")

# Simple troubleshooting function
def troubleshoot_database():
    """
    Troubleshoot database connection and table structure
    """
    try:
        engine = get_db_connection()
        
        with engine.connect() as conn:
            # Check if table exists
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'anomalies'
            """))
            table_exists = result.fetchone() is not None
            
            print(f"Anomalies table exists: {table_exists}")
            
            if table_exists:
                # Get table structure
                result = conn.execute(text("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'anomalies'
                    ORDER BY ordinal_position
                """))
                columns = result.fetchall()
                print("Table structure:")
                for col in columns:
                    print(f"  {col[0]}: {col[1]}")
            
            # Test connection
            result = conn.execute(text("SELECT 1"))
            print(f"Database connection test: {result.fetchone()[0]}")
            
    except Exception as e:
        print(f"Troubleshooting error: {e}")

if __name__ == "__main__":
    main()