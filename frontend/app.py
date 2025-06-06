import streamlit as st
import requests

API_URL = "http://backend:8000"

st.title("💰 Smart Budget")

email = st.text_input("Email")
password = st.text_input("Password", type="password")
token = ""

if st.button("Login"):
    r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
    if r.status_code == 200:
        token = r.json()["access_token"]
        st.success("Logged in!")
    else:
        st.error("Login failed")

st.header("Add Transaction")
tx_type = st.selectbox("Type", ["income", "expense"])
category = st.text_input("Category")
amount = st.number_input("Amount", min_value=0.0)

if st.button("Add Transaction"):
    tx = {"type": tx_type, "category": category, "amount": amount}
    r = requests.post(f"{API_URL}/transactions/", json=tx)
    if r.status_code == 200:
        st.success("Transaction added!")

st.header("All Transactions")
r = requests.get(f"{API_URL}/transactions/")
if r.status_code == 200:
    for tx in r.json():
        st.write(f"{tx['timestamp']} - {tx['type']} - {tx['category']} - {tx['amount']} €")