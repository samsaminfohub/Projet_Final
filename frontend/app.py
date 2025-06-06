import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="MiniLab2 Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8fafc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
    }
    .success-message {
        background-color: #dcfce7;
        color: #166534;
        padding: 0.75rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #fef2f2;
        color: #dc2626;
        padding: 0.75rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def make_request(method, endpoint, data=None):
    """Make HTTP request to backend API"""
    url = f"{BACKEND_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        if response.status_code >= 400:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
        
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def get_users():
    """Fetch all users"""
    return make_request("GET", "/users/")

def get_tasks(user_id=None):
    """Fetch tasks, optionally filtered by user"""
    endpoint = "/tasks/"
    if user_id:
        endpoint += f"?user_id={user_id}"
    return make_request("GET", endpoint)

def create_user(username, email):
    """Create a new user"""
    return make_request("POST", "/users/", {"username": username, "email": email})

def create_task(title, description, user_id):
    """Create a new task"""
    return make_request("POST", "/tasks/", {
        "title": title,
        "description": description,
        "user_id": user_id
    })

def update_task(task_id, **kwargs):
    """Update a task"""
    return make_request("PUT", f"/tasks/{task_id}", kwargs)

def delete_task(task_id):
    """Delete a task"""
    return make_request("DELETE", f"/tasks/{task_id}")

# Main app
def main():
    st.markdown('<h1 class="main-header">🚀 MiniLab2 Dashboard</h1>', unsafe_allow_html=True)
    
    # Check backend health
    health = make_request("GET", "/health")
    if health:
        st.success(f"✅ Backend is healthy! Last checked: {datetime.now().strftime('%H:%M:%S')}")
    else:
        st.error("❌ Backend is not responding")
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", 
                               ["Dashboard", "Manage Users", "Manage Tasks", "Analytics"])
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Manage Users":
        show_user_management()
    elif page == "Manage Tasks":
        show_task_management()
    elif page == "Analytics":
        show_analytics()

def show_dashboard():
    """Dashboard overview page"""
    st.header("📊 Dashboard Overview")
    
    # Metrics
    users = get_users()
    tasks = get_tasks()
    
    if users and tasks:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Users", len(users))
        
        with col2:
            st.metric("Total Tasks", len(tasks))
        
        with col3:
            completed_tasks = sum(1 for task in tasks if task.get('completed', False))
            st.metric("Completed Tasks", completed_tasks)
        
        with col4:
            completion_rate = (completed_tasks / len(tasks) * 100) if tasks else 0
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        # Recent tasks
        st.subheader("Recent Tasks")
        if tasks:
            recent_tasks = sorted(tasks, key=lambda x: x['created_at'], reverse=True)[:5]
            for task in recent_tasks:
                status = "✅" if task['completed'] else "⏳"
                st.write(f"{status} **{task['title']}** - {task['description'][:50]}...")

def show_user_management():
    """User management page"""
    st.header("👥 User Management")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Create New User")
        with st.form("create_user_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            
            if st.form_submit_button("Create User"):
                if username and email:
                    result = create_user(username, email)
                    if result:
                        st.success("User created successfully!")
                        st.rerun()
                else:
                    st.error("Please fill in all fields")
    
    with col2:
        st.subheader("Existing Users")
        users = get_users()
        if users:
            df = pd.DataFrame(users)
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No users found")

def show_task_management():
    """Task management page"""
    st.header("📝 Task Management")
    
    # Create new task
    st.subheader("Create New Task")
    users = get_users()
    
    if users:
        with st.form("create_task_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Task Title")
                user_options = {f"{user['username']} ({user['email']})": user['id'] for user in users}
                selected_user = st.selectbox("Assign to User", list(user_options.keys()))
            
            with col2:
                description = st.text_area("Description")
            
            if st.form_submit_button("Create Task"):
                if title and selected_user:
                    user_id = user_options[selected_user]
                    result = create_task(title, description, user_id)
                    if result:
                        st.success("Task created successfully!")
                        st.rerun()
                else:
                    st.error("Please fill in required fields")
    else:
        st.warning("Please create users first before creating tasks")
    
    # Display tasks
    st.subheader("Existing Tasks")
    tasks = get_tasks()
    
    if tasks:
        for task in tasks:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    status = "✅ Completed" if task['completed'] else "⏳ Pending"
                    st.write(f"**{task['title']}** - {status}")
                    st.write(f"*{task['description']}*")
                
                with col2:
                    if st.button(f"Toggle", key=f"toggle_{task['id']}"):
                        result = update_task(task['id'], completed=not task['completed'])
                        if result:
                            st.rerun()
                
                with col3:
                    if st.button(f"Delete", key=f"delete_{task['id']}", type="secondary"):
                        result = delete_task(task['id'])
                        if result:
                            st.rerun()
                
                st.divider()
    else:
        st.info("No tasks found")

def show_analytics():
    """Analytics page"""
    st.header("📈 Analytics")
    
    tasks = get_tasks()
    users = get_users()
    
    if not tasks or not users:
        st.info("Not enough data for analytics")
        return
    
    # Task completion stats
    st.subheader("Task Completion Statistics")
    
    completed = sum(1 for task in tasks if task['completed'])
    total = len(tasks)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Completion pie chart
        completion_data = {
            'Status': ['Completed', 'Pending'],
            'Count': [completed, total - completed]
        }
        df_completion = pd.DataFrame(completion_data)
        st.subheader("Task Status Distribution")
        st.bar_chart(df_completion.set_index('Status'))
    
    with col2:
        # Tasks per user
        user_task_counts = {}
        for task in tasks:
            user_id = task['user_id']
            user = next((u for u in users if u['id'] == user_id), None)
            if user:
                username = user['username']
                user_task_counts[username] = user_task_counts.get(username, 0) + 1
        
        if user_task_counts:
            st.subheader("Tasks per User")
            df_user_tasks = pd.DataFrame(list(user_task_counts.items()), 
                                       columns=['User', 'Task Count'])
            st.bar_chart(df_user_tasks.set_index('User'))
    
    # Recent activity
    st.subheader("Recent Activity Timeline")
    if tasks:
        df_tasks = pd.DataFrame(tasks)
        df_tasks['date'] = pd.to_datetime(df_tasks['created_at']).dt.date
        activity = df_tasks.groupby('date').size().reset_index(name='tasks_created')
        st.line_chart(activity.set_index('date'))

if __name__ == "__main__":
    main()