import streamlit as st
import requests

API_URL = "http://backend:8000"

st.title("📝 Task Manager")

task = st.text_input("Enter a task:")
if st.button("Add Task"):
    r = requests.post(f"{API_URL}/tasks/", json={"title": task})
    if r.status_code == 200:
        st.success("Task added!")

st.write("## All Tasks")
resp = requests.get(f"{API_URL}/tasks/")
if resp.status_code == 200:
    for task in resp.json():
        st.write(f"- {task['title']}")