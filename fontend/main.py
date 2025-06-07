import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Configuration de la page
st.set_page_config(
    page_title="Mon App Full Stack",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de l'API FastAPI
API_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

# Fonctions utilitaires pour l'API
def get_users():
    try:
        response = requests.get(f"{API_URL}/users/")
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        st.error("Impossible de se connecter à l'API")
        return []

def create_user(name, email, age):
    try:
        data = {"name": name, "email": email, "age": age}
        response = requests.post(f"{API_URL}/users/", json=data)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        st.error("Erreur lors de la création de l'utilisateur")
        return False

def delete_user(user_id):
    try:
        response = requests.delete(f"{API_URL}/users/{user_id}")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        st.error("Erreur lors de la suppression de l'utilisateur")
        return False

def get_products():
    try:
        response = requests.get(f"{API_URL}/products/")
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        st.error("Impossible de récupérer les produits")
        return []

def create_product(name, description, price, category):
    try:
        data = {
            "name": name,
            "description": description,
            "price": price,
            "category": category
        }
        response = requests.post(f"{API_URL}/products/", json=data)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        st.error("Erreur lors de la création du produit")
        return False

def get_stats():
    try:
        response = requests.get(f"{API_URL}/stats/")
        if response.status_code == 200:
            return response.json()
        return {}
    except requests.exceptions.RequestException:
        st.error("Impossible de récupérer les statistiques")
        return {}

# Interface principale
def main():
    st.title("🚀 Mon Application Full Stack")
    st.markdown("---")
    
    # Sidebar pour la navigation
    st.sidebar.title("Navigation")
    pages = ["Dashboard", "Utilisateurs", "Produits", "Statistiques"]
    selected_page = st.sidebar.selectbox("Choisir une page", pages)
    
    if selected_page == "Dashboard":
        dashboard_page()
    elif selected_page == "Utilisateurs":
        users_page()
    elif selected_page == "Produits":
        products_page()
    elif selected_page == "Statistiques":
        stats_page()

def dashboard_page():
    st.header("📊 Dashboard")
    
    # Récupération des statistiques
    stats = get_stats()
    
    if stats:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="👥 Nombre d'utilisateurs",
                value=stats.get("total_users", 0)
            )
        
        with col2:
            st.metric(
                label="📦 Nombre de produits",
                value=stats.get("total_products", 0)
            )
        
        with col3:
            st.metric(
                label="🏷️ Catégories",
                value=len(stats.get("categories", {}))
            )
        
        # Graphique des catégories
        if stats.get("categories"):
            st.subheader("Répartition des produits par catégorie")
            categories_df = pd.DataFrame(
                list(stats["categories"].items()),
                columns=["Catégorie", "Nombre"]
            )
            
            fig = px.pie(
                categories_df,
                values="Nombre",
                names="Catégorie",
                title="Distribution des produits"
            )
            st.plotly_chart(fig, use_container_width=True)

def users_page():
    st.header("👥 Gestion des Utilisateurs")
    
    # Formulaire d'ajout d'utilisateur
    with st.expander("➕ Ajouter un nouvel utilisateur"):
        with st.form("user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nom")
                email = st.text_input("Email")
            
            with col2:
                age = st.number_input("Âge", min_value=1, max_value=120, value=25)
            
            submitted = st.form_submit_button("Créer l'utilisateur")
            
            if submitted and name and email:
                if create_user(name, email, age):
                    st.success("Utilisateur créé avec succès!")
                    st.rerun()
                else:
                    st.error("Erreur lors de la création de l'utilisateur")
    
    # Liste des utilisateurs
    st.subheader("Liste des utilisateurs")
    users = get_users()
    
    if users:
        df = pd.DataFrame(users)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Affichage du tableau avec possibilité de suppression
        for i, user in enumerate(users):
            col1, col2, col3, col4, col5 = st.columns([2, 3, 1, 2, 1])
            
            with col1:
                st.text(user["name"])
            with col2:
                st.text(user["email"])
            with col3:
                st.text(str(user["age"]))
            with col4:
                st.text(user["created_at"][:10])
            with col5:
                if st.button("🗑️", key=f"delete_user_{user['id']}"):
                    if delete_user(user["id"]):
                        st.success("Utilisateur supprimé!")
                        st.rerun()
    else:
        st.info("Aucun utilisateur trouvé")

def products_page():
    st.header("📦 Gestion des Produits")
    
    # Formulaire d'ajout de produit
    with st.expander("➕ Ajouter un nouveau produit"):
        with st.form("product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nom du produit")
                price = st.number_input("Prix", min_value=0.0, step=0.01)
            
            with col2:
                category = st.selectbox(
                    "Catégorie",
                    ["Électronique", "Vêtements", "Alimentation", "Livres", "Sport"]
                )
                description = st.text_area("Description")
            
            submitted = st.form_submit_button("Créer le produit")
            
            if submitted and name and description:
                if create_product(name, description, price, category):
                    st.success("Produit créé avec succès!")
                    st.rerun()
                else:
                    st.error("Erreur lors de la création du produit")
    
    # Liste des produits
    st.subheader("Liste des produits")
    products = get_products()
    
    if products:
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            categories = list(set([p["category"] for p in products]))
            selected_category = st.selectbox("Filtrer par catégorie", ["Toutes"] + categories)
        
        with col2:
            price_range = st.slider(
                "Gamme de prix",
                min_value=0.0,
                max_value=max([p["price"] for p in products]) if products else 100.0,
                value=(0.0, max([p["price"] for p in products]) if products else 100.0)
            )
        
        # Filtrage des produits
        filtered_products = products
        if selected_category != "Toutes":
            filtered_products = [p for p in filtered_products if p["category"] == selected_category]
        
        filtered_products = [
            p for p in filtered_products 
            if price_range[0] <= p["price"] <= price_range[1]
        ]
        
        # Affichage des produits en grille
        cols = st.columns(3)
        for i, product in enumerate(filtered_products):
            with cols[i % 3]:
                with st.container():
                    st.subheader(product["name"])
                    st.write(f"**Prix:** {product['price']:.2f} €")
                    st.write(f"**Catégorie:** {product['category']}")
                    st.write(f"**Description:** {product['description']}")
                    st.markdown("---")
    else:
        st.info("Aucun produit trouvé")

def stats_page():
    st.header("📈 Statistiques Avancées")
    
    # Récupération des données
    users = get_users()
    products = get_products()
    
    if users and products:
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique de répartition des âges
            st.subheader("Répartition des âges des utilisateurs")
            ages = [user["age"] for user in users]
            fig_age = px.histogram(
                x=ages,
                nbins=10,
                title="Distribution des âges",
                labels={"x": "Âge", "y": "Nombre d'utilisateurs"}
            )
            st.plotly_chart(fig_age, use_container_width=True)
        
        with col2:
            # Graphique des prix des produits
            st.subheader("Distribution des prix")
            prices = [product["price"] for product in products]
            fig_price = px.box(
                y=prices,
                title="Répartition des prix des produits",
                labels={"y": "Prix (€)"}
            )
            st.plotly_chart(fig_price, use_container_width=True)
        
        # Tableau de bord temporel
        st.subheader("Évolution dans le temps")
        
        # Préparation des données temporelles
        user_dates = [user["created_at"][:10] for user in users]
        product_dates = [product["created_at"][:10] for product in products]
        
        date_counts = {}
        for date in user_dates + product_dates:
            if date in date_counts:
                date_counts[date] += 1
            else:
                date_counts[date] = 1
        
        if date_counts:
            dates_df = pd.DataFrame(
                list(date_counts.items()),
                columns=["Date", "Nombre d'ajouts"]
            )
            dates_df["Date"] = pd.to_datetime(dates_df["Date"])
            dates_df = dates_df.sort_values("Date")
            
            fig_timeline = px.line(
                dates_df,
                x="Date",
                y="Nombre d'ajouts",
                title="Activité dans le temps"
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
    
    else:
        st.info("Pas assez de données pour afficher les statistiques")

# Pied de page
def footer():
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>🚀 Application Full Stack - FastAPI + Streamlit + PostgreSQL</p>
            <p>Développé avec ❤️ par votre équipe de développement</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
    footer()