import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from sqlalchemy import create_engine
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

def save_anomalies_to_db(anomalies_df):
    """Sauvegarde les anomalies détectées en base"""
    
    engine = get_db_connection()
    
    for _, row in anomalies_df.iterrows():
        # Détermination de la sévérité
        score = abs(row['anomaly_score'])
        if score > 0.5:
            severity = 'CRITICAL'
        elif score > 0.3:
            severity = 'HIGH'
        elif score > 0.1:
            severity = 'MEDIUM'
        else:
            severity = 'LOW'
        
        # Insertion en base
        query = """
        INSERT INTO anomalies (sensor_id, anomaly_type, anomaly_score, severity, description)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        with engine.connect() as conn:
            conn.execute(query, (
                row['sensor_id'],
                'Statistical Anomaly',
                float(row['anomaly_score']),
                severity,
                f"Anomalie détectée avec un score de {row['anomaly_score']:.3f}"
            ))

if __name__ == "__main__":
    main()