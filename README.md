# 🚀 Projet Full Stack - FastAPI + Streamlit + PostgreSQL

## Description

Ce projet est une application web complète utilisant une architecture moderne avec :
- **Backend** : FastAPI (API REST)
- **Frontend** : Streamlit (Interface utilisateur)
- **Base de données** : PostgreSQL
- **Administration** : PgAdmin
- **Gestion des conteneurs** : Portainer
- **Conteneurisation** : Docker & Docker Compose

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │    FastAPI      │    │   PostgreSQL    │
│   (Port 8501)   │◄──►│   (Port 8000)   │◄──►│   (Port 5432)   │
│    Frontend     │    │    Backend      │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   PgAdmin       │              │
         └──────────────│   (Port 5050)   │──────────────┘
                        │   Admin DB      │
                        └─────────────────┘
                                │
                        ┌─────────────────┐
                        │   Portainer     │
                        │   (Port 9000)   │
                        │ Container Mgmt  │
                        └─────────────────┘
```

## 🚀 Démarrage rapide

### Prérequis
- Docker
- Docker Compose

### Installation

1. **Cloner le projet**
```bash
git clone <url-du-repo>
cd projet-fullstack
```

2. **Créer la structure des dossiers**
```bash
mkdir -p backend frontend
```

3. **Créer les fichiers de configuration**
   - Copier le contenu des artifacts dans les fichiers appropriés
   - `docker-compose.yml` à la racine
   - `backend/Dockerfile`, `backend/main.py`, `backend/requirements.txt`
   - `frontend/Dockerfile`, `frontend/main.py`, `frontend/requirements.txt`
   - `init.sql` à la racine

4. **Démarrer l'application**
```bash
docker-compose up -d
```

5. **Vérifier le déploiement**
```bash
docker-compose ps
```

## 🌐 Accès aux services

| Service | URL | Identifiants |
|---------|-----|--------------|
| **Streamlit** | [http://localhost:8501](http://localhost:8501) | - |
| **FastAPI** | [http://localhost:8000](http://localhost:8000) | - |
| **API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | - |
| **PgAdmin** | [http://localhost:5050](http://localhost:5050) | admin@admin.com / admin123 |
| **Portainer** | [http://localhost:9000](http://localhost:9000) | À configurer au premier lancement |

## 📊 Fonctionnalités

### API FastAPI
- ✅ CRUD complet pour les utilisateurs
- ✅ CRUD complet pour les produits
- ✅ Endpoint de statistiques
- ✅ Documentation automatique avec Swagger
- ✅ Validation des données avec Pydantic
- ✅ Connexion PostgreSQL avec SQLAlchemy

### Interface Streamlit
- ✅ Dashboard avec métriques
- ✅ Gestion des utilisateurs
- ✅ Gestion des produits
- ✅ Statistiques avancées avec graphiques
- ✅ Interface responsive
- ✅ Filtres et recherches

### Base de données
- ✅ Modèles User et Product
- ✅ Données d'exemple préchargées
- ✅ Index pour optimisation
- ✅ Vues et fonctions SQL

## 🔧 Configuration

### Variables d'environnement

**Backend (FastAPI)**
```env
DATABASE_URL=postgresql://postgres:postgres123@postgres:5432/myapp_db
SECRET_KEY=your-secret-key-here
```

**Frontend (Streamlit)**
```env
FASTAPI_URL=http://fastapi:8000
```

**Base de données**
```env
POSTGRES_DB=myapp_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
```

## 🛠️ Développement

### Démarrage en mode développement
```bash
# Démarrer tous les services
docker-compose up

# Démarrer uniquement la base de données
docker-compose up postgres pgadmin

# Redémarrer un service spécifique
docker-compose restart fastapi
```

### Logs
```bash
# Voir tous les logs
docker-compose logs

# Logs d'un service spécifique
docker-compose logs fastapi
docker-compose logs streamlit
```

### Accès aux conteneurs
```bash
# Accéder au conteneur FastAPI
docker-compose exec fastapi bash

# Accéder au conteneur PostgreSQL
docker-compose exec postgres psql -U postgres -d myapp_db
```

## 📝 API Endpoints

### Utilisateurs
- `GET /users/` - Liste tous les utilisateurs
- `GET /users/{id}` - Récupère un utilisateur
- `POST /users/` - Crée un utilisateur
- `DELETE /users/{id}` - Supprime un utilisateur

### Produits
- `GET /products/` - Liste tous les produits
- `GET /products/{id}` - Récupère un produit
- `POST /products/` - Crée un produit
- `DELETE /products/{id}` - Supprime un produit

### Statistiques
- `GET /stats/` - Récupère les statistiques générales

## 🗄️ Schéma de base de données

### Table `users`
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    age INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Table `products`
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔒 Sécurité

- Validation des données avec Pydantic
- Gestion des erreurs HTTP appropriées
- Isolation des services via Docker
- Variables d'environnement pour les secrets

## 📈 Monitoring

- **Portainer** : Gestion et monitoring des conteneurs
- **PgAdmin** : Administration de la base de données
- **FastAPI** : Métriques et logs automatiques
- **Docker Health Checks** : Vérification de l'état des services

## 🚨 Dépannage

### Problèmes fréquents

1. **Erreur de connexion à la base de données**
   ```bash
   docker-compose logs postgres
   # Vérifier que PostgreSQL est démarré
   ```

2. **Port déjà utilisé**
   ```bash
   # Modifier les ports dans docker-compose.yml
   ports:
     - "8502:8501"  # Au lieu de 8501:8501
   ```

3. **Permissions de fichiers**
   ```bash
   sudo chown -R $USER:$USER .
   ```

### Commandes utiles

```bash
# Reconstruire les images
docker-compose build --no-cache

# Supprimer tous les conteneurs et volumes
docker-compose down -v

# Nettoyer le système Docker
docker system prune -a
```

## 🔄 Mise à jour

```bash
# Arrêter les services
docker-compose down

# Mettre à jour le code
git pull

# Reconstruire et redémarrer
docker-compose up --build -d
```

## 📋 Checklist de déploiement

- [ ] Cloner le repository
- [ ] Créer la structure des dossiers
- [ ] Copier tous les fichiers de configuration
- [ ] Modifier les variables d'environnement si nécessaire
- [ ] Exécuter `docker-compose up -d`
- [ ] Vérifier l'accès à tous les services
- [ ] Tester les fonctionnalités principales

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
- Créer une issue sur GitHub
- Consulter la documentation des outils utilisés
- Vérifier les logs des conteneurs

---

**Développé avec ❤️ par votre équipe de développement**