import streamlit as st
import requests

API_URL = "http://backend:8000"

st.title("💰 Smart Budget")

# Tabs: Login | Register | Budget
tab = st.sidebar.radio("Navigation", ["Login", "Register", "Budget"])

token = st.session_state.get("token", "")

if tab == "Login":
    st.header("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
        if r.status_code == 200:
            token = r.json()["access_token"]
            st.session_state["token"] = token
            st.success("Logged in!")
        else:
            st.error("Login failed")

elif tab == "Register":
    st.header("Register")
    reg_email = st.text_input("Email", key="reg_email")
    reg_password = st.text_input("Password", type="password", key="reg_password")

    if st.button("Register"):
        r = requests.post(f"{API_URL}/auth/register", json={"email": reg_email, "password": reg_password})
        if r.status_code == 200:
            st.success("User registered!")
        else:
            st.error("Registration failed: " + r.json().get("detail", "Unknown error"))

elif tab == "Budget":
    st.header("Add Transaction")
    tx_type = st.selectbox("Type", ["income", "expense"])
    category = st.text_input("Category")
    amount = st.number_input("Amount", min_value=0.0)

    if st.button("Add Transaction"):
        tx = {"type": tx_type, "category": category, "amount": amount}
        r = requests.post(f"{API_URL}/transactions/", json=tx)
        if r.status_code == 200:
            st.success("Transaction added!")
        else:
            st.error("Failed to add transaction.")

    st.header("All Transactions")
    r = requests.get(f"{API_URL}/transactions/")
    if r.status_code == 200:
        for tx in r.json():
            st.write(f"{tx['timestamp']} - {tx['type']} - {tx['category']} - {tx['amount']} €")