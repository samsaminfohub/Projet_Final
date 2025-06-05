# 🔍 Système de Détection d'Anomalies IoT

## 📋 Description du Projet

Ce projet est un **système complet de détection d'anomalies en temps réel** pour des données IoT avec prédiction de maintenance prédictive. Il combine plusieurs technologies modernes pour créer une solution industrielle complète.

### 🚀 Fonctionnalités Principales

- **Collecte de données IoT** en temps réel (température, vibrations, puissance)
- **Détection d'anomalies** avec Machine Learning (Isolation Forest)
- **Interface web interactive** avec Streamlit
- **Tracking des modèles ML** avec MLflow
- **Base de données PostgreSQL** pour le stockage
- **Administration** avec PgAdmin
- **Gestion des conteneurs** avec Portainer
- **Maintenance prédictive** et analytics avancées

### 🏗️ Architecture Technique

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   PostgreSQL    │    │    MLflow       │
│   (Frontend)    │◄──►│   (Database)    │◄──►│  (ML Tracking)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Data Generator │
                    │  (IoT Simulator)│
                    └─────────────────┘
```

## 🛠️ Technologies Utilisées

- **Frontend**: Streamlit, Plotly, Pandas
- **Backend**: Python, SQLAlchemy, Psycopg2
- **Machine Learning**: Scikit-learn, MLflow
- **Base de données**: PostgreSQL
- **Administration**: PgAdmin, Portainer
- **Conteneurisation**: Docker, Docker Compose

## 📦 Installation

### Prérequis

- Docker et Docker Compose installés
- Au moins 4GB de RAM disponible
- Ports 5000, 5050, 5432, 8501, 9000 libres

### 🚀 Démarrage Rapide

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd iot-anomaly-detection
```

2. **Lancer tous les services**
```bash
docker-compose up -d
```

3. **Vérifier le statut**
```bash
docker-compose ps
```

### 📊 Accès aux Services

| Service | URL | Identifiants |
|---------|-----|-------------|
| **Streamlit App** | http://localhost:8501 | - |
| **MLflow UI** | http://localhost:5000 | - |
| **PgAdmin** | http://localhost:5050 | admin@example.com / admin123 |
| **Portainer** | http://localhost:9000 | Créer compte admin |
| **PostgreSQL** | localhost:5432 | admin / admin123 |

### 🔧 Configuration PostgreSQL dans PgAdmin

1. Connectez-vous à PgAdmin (http://localhost:5050)
2. Ajoutez un serveur avec ces paramètres :
   - **Host**: `postgres`
   - **Port**: `5432`
   - **Database**: `iot_anomaly_db`
   - **Username**: `admin`
   - **Password**: `admin123`

## 🎯 Utilisation

### 📊 Dashboard Principal

1. Accédez à l'application Streamlit
2. Naviguez dans les différents onglets :
   - **Dashboard** : Vue d'ensemble temps réel
   - **Détection d'Anomalies** : Analyse ML
   - **Modèles ML** : Gestion des modèles
   - **Analytics** : Analyses avancées (PCA)
   - **Maintenance** : Prédiction de maintenance

### 🔍 Détection d'Anomalies

1. Ajustez le **taux de contamination** dans la sidebar
2. Cliquez sur **"Détecter les Anomalies"**
3. Analysez les résultats et visualisations
4. Les anomalies sont automatiquement sauvées en base

### 🤖 Entraînement de Modèles

1. Allez dans l'onglet **"Modèles ML"**
2. Cliquez sur **"Entraîner Modèle"**
3. Le modèle est automatiquement sauvé dans MLflow
4. Consultez les métriques dans l'interface MLflow

## 📈 Données Générées

Le système simule automatiquement des données IoT réalistes :

### 🌡️ Capteurs de Température
- Température ambiante (°C)
- Humidité relative (%)
- Pression atmosphérique (hPa)

### 📳 Capteurs de Vibration
- Vibrations X, Y, Z (m/s²)
- Détection d'anomalies mécaniques

### ⚡ Capteurs de Puissance
- Courant électrique (A)
- Tension (V)
- Puissance consommée (W)

## 🔧 Structure des Fichiers

```
iot-anomaly-detection/
│
├── docker-compose.yml      # Configuration Docker Compose
├── Dockerfile             # Image principale Streamlit
├── Dockerfile.generator   # Image générateur de données
├── requirements.txt       # Dépendances Python
├── init.sql              # Initialisation base de données
│
├── app.py                # Application Streamlit principale
├── data_generator.py     # Générateur de données IoT
│
└── data/                 # Dossier pour fichiers temporaires
```

## 🐛 Dépannage

### Problèmes Courants

#### 🔌 Erreur de connexion PostgreSQL
```bash
# Vérifier que PostgreSQL est démarré
docker-compose logs postgres

# Redémarrer le service
docker-compose restart postgres
```

#### 📊 Streamlit ne se charge pas
```bash
# Vérifier les logs
docker-compose logs streamlit_app

# Rebuilder l'image
docker-compose build streamlit_app
docker-compose up -d streamlit_app
```

#### 🤖 MLflow ne démarre pas
```bash
# Vérifier la connexion à PostgreSQL
docker-compose logs mlflow

# Redémarrer MLflow
docker-compose restart mlflow
```

### 🧹 Nettoyage Complet

```bash
# Arrêter tous les services
docker-compose down

# Supprimer les volumes (⚠️ Perte de données)
docker-compose down -v

# Supprimer les images
docker-compose down --rmi all
```

## 📊 Monitoring et Logs

### Surveillance des Services

```bash
# Logs de tous les services
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f streamlit_app

# Statut des conteneurs
docker-compose ps
```

### 📈 Métriques Système

Utilisez Portainer (http://localhost:9000) pour :
- Surveiller l'utilisation des ressources
- Gérer les conteneurs
- Consulter les logs en temps réel
- Redémarrer les services

## 🚀 Extensions Possibles

### 🔮 Améliorations Futures

1. **Notifications temps réel** (Slack, Email)
2. **API REST** pour intégration externe
3. **Tableaux de bord Grafana**
4. **Modèles Deep Learning** (LSTM, Autoencoders)
5. **Déploiement cloud** (AWS, Azure, GCP)
6. **Authentification utilisateur**
7. **Tests automatisés**

### 🎯 Cas d'Usage Industriels

- **Maintenance prédictive** d'équipements
- **Surveillance qualité** en production
- **Optimisation énergétique**
- **Détection de pannes** précoce
- **Conformité réglementaire**

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👥 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche feature
3. Commiter vos changements
4. Ouvrir une Pull Request

## 📞 Support

Pour toute question ou problème :

- Ouvrir une issue sur GitHub
- Consulter la documentation
- Vérifier les logs avec `docker-compose logs`

---

**🎉 Félicitations ! Vous avez maintenant un système complet de détection d'anomalies IoT avec Machine Learning !**