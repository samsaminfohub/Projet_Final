import streamlit as st
import requests

API_URL = "http://backend:8000"

st.title("Catalogue de Livres")

menu = ["Afficher livres", "Ajouter un livre", "Ajouter un commentaire"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Afficher livres":
    response = requests.get(f"{API_URL}/books/")
    if response.status_code == 200:
        books = response.json()
        for book in books:
            st.subheader(book["title"])
            st.write(f"Auteur: {book['author']}")
            if book["description"]:
                st.write(book["description"])
            # Fetch comments
            com_resp = requests.get(f"{API_URL}/comments/{book['id']}")
            if com_resp.status_code == 200:
                comments = com_resp.json()
                for c in comments:
                    st.markdown(f"> {c['comment']} (Note: {c['rating']}/5)")
    else:
        st.error("Erreur lors de la récupération des livres")

elif choice == "Ajouter un livre":
    with st.form("form_add_book"):
        title = st.text_input("Titre")
        author = st.text_input("Auteur")
        description = st.text_area("Description")
        submitted = st.form_submit_button("Ajouter")
        if submitted:
            data = {"title": title, "author": author, "description": description}
            res = requests.post(f"{API_URL}/books/", json=data)
            if res.status_code == 200:
                st.success("Livre ajouté !")
            else:
                st.error("Erreur à l'ajout")

elif choice == "Ajouter un commentaire":
    response = requests.get(f"{API_URL}/books/")
    books = []
    if response.status_code == 200:
        books = response.json()
    book_options = {f"{b['title']} - {b['author']}": b['id'] for b in books}

    with st.form("form_add_comment"):
        book_sel = st.selectbox("Choisir un livre", options=list(book_options.keys()))
        comment = st.text_area("Commentaire")
        rating = st.slider("Note", 1, 5, 3)
        submitted = st.form_submit_button("Ajouter commentaire")
        if submitted:
            data = {
                "book_id": book_options[book_sel],
                "comment": comment,
                "rating": rating
            }
            res = requests.post(f"{API_URL}/comments/", json=data)
            if res.status_code == 200:
                st.success("Commentaire ajouté !")
            else:
                st.error("Erreur à l'ajout du commentaire")
