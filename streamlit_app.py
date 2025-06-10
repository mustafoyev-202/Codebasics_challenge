import os
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="FinSolve RAG Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Session state initialization
if 'access_token' not in st.session_state:
    st.session_state.access_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def make_api_request(endpoint, method="GET", data=None, headers=None):
    """Make API request with error handling."""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if headers is None:
            headers = {}
        
        if st.session_state.access_token:
            headers["Authorization"] = f"Bearer {st.session_state.access_token}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

def login_user(username, password):
    """Login user and store token."""
    data = {"username": username, "password": password}
    response = make_api_request("/login", method="POST", data=data)
    
    if response:
        st.session_state.access_token = response["access_token"]
        st.session_state.user_info = {
            "username": username,
            "role": response["user_role"],
            "name": response["user_name"]
        }
        return True
    return False

def logout_user():
    """Logout user and clear session."""
    st.session_state.access_token = None
    st.session_state.user_info = None
    st.session_state.chat_history = []

def get_user_permissions():
    """Get user permissions."""
    return make_api_request("/permissions")

def get_sample_users():
    """Get sample users for demonstration."""
    return make_api_request("/sample-users")

def process_query(query):
    """Process user query."""
    data = {"message": query}
    return make_api_request("/chat", method="POST", data=data)

def get_department_summary(department):
    """Get department summary."""
    return make_api_request(f"/department/{department}/summary")

def get_system_stats():
    """Get system statistics."""
    return make_api_request("/system/stats")

def display_login_page():
    """Display login page."""
    st.title("🏢 FinSolve RAG Assistant")
    st.markdown("### Role-Based Access Control System")
    
    # Get sample users
    sample_users = get_sample_users()
    
    if sample_users:
        st.info("**Demo Users Available:**")
        for username, user_data in sample_users.items():
            st.write(f"• **{user_data['name']}** ({username}) - {user_data['role'].title()}")
    
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit_button = st.form_submit_button("Login")
        with col2:
            if st.form_submit_button("Demo Login (C-Level)"):
                username = "Tony"
                password = "password123"
                submit_button = True
        
        if submit_button:
            if login_user(username, password):
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Login failed. Please check your credentials.")

def display_main_interface():
    """Display main chat interface."""
    # Sidebar
    with st.sidebar:
        st.title("👤 User Info")
        if st.session_state.user_info:
            st.write(f"**Name:** {st.session_state.user_info['name']}")
            st.write(f"**Role:** {st.session_state.user_info['role'].title()}")
            st.write(f"**Username:** {st.session_state.user_info['username']}")
        
        st.markdown("---")
        
        # Get user permissions
        permissions = get_user_permissions()
        if permissions:
            st.subheader("🔐 Permissions")
            st.write(f"**Role:** {permissions['role_name']}")
            st.write(f"**Description:** {permissions['role_description']}")
            
            st.subheader("📁 Accessible Departments")
            for dept in permissions['accessible_departments']:
                st.write(f"• {dept.title()}")
        
        st.markdown("---")
        
        # Department summary buttons
        if permissions:
            st.subheader("📊 Department Summaries")
            for dept in permissions['accessible_departments']:
                if st.button(f"📋 {dept.title()} Summary", key=f"summary_{dept}"):
                    with st.spinner(f"Generating {dept.title()} summary..."):
                        summary = get_department_summary(dept)
                        if summary:
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": f"**{dept.title()} Department Summary:**\n\n{summary['response']}",
                                "timestamp": datetime.now(),
                                "sources": summary['sources']
                            })
                            st.rerun()
        
        st.markdown("---")
        
        # System stats (only for C-level)
        if st.session_state.user_info and st.session_state.user_info['role'] == 'c_level':
            if st.button("📈 System Statistics"):
                with st.spinner("Loading system statistics..."):
                    stats = get_system_stats()
                    if stats:
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": f"**System Statistics:**\n\n"
                                      f"• Total Documents: {stats['vector_store_stats']['total_documents']}\n"
                                      f"• Departments: {', '.join(stats['vector_store_stats']['departments'])}\n"
                                      f"• File Types: {', '.join(stats['vector_store_stats']['file_types'])}\n"
                                      f"• Total Departments: {stats['total_departments']}",
                            "timestamp": datetime.now(),
                            "sources": []
                        })
                        st.rerun()
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout"):
            logout_user()
            st.rerun()
    
    # Main chat area
    st.title("💬 FinSolve RAG Assistant")
    
    # Chat history
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    
                    # Show sources if available
                    if message.get("sources"):
                        with st.expander("📚 Sources"):
                            for i, source in enumerate(message["sources"], 1):
                                st.write(f"**Source {i}:**")
                                st.write(f"• Department: {source['department']}")
                                st.write(f"• File: {source['file_name']}")
                                st.write(f"• Relevance: {source['relevance_score']:.3f}")
                                st.write("---")
    
    # Query input
    with st.container():
        query = st.chat_input("Ask me anything about FinSolve Technologies...")
        
        if query:
            # Add user message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now()
            })
            
            # Process query
            with st.spinner("Processing your query..."):
                response = process_query(query)
                
                if response:
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response["response"],
                        "timestamp": datetime.now(),
                        "sources": response["sources"]
                    })
                    
                    st.rerun()
                else:
                    st.error("Failed to process query. Please try again.")

def display_analytics():
    """Display analytics dashboard."""
    st.title("📊 Analytics Dashboard")
    
    # Only show for C-level executives
    if not st.session_state.user_info or st.session_state.user_info['role'] != 'c_level':
        st.warning("This dashboard is only available for C-level executives.")
        return
    
    # Get system stats
    stats = get_system_stats()
    if not stats:
        st.error("Failed to load system statistics.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Documents",
            value=stats['vector_store_stats']['total_documents']
        )
    
    with col2:
        st.metric(
            label="Departments",
            value=stats['total_departments']
        )
    
    with col3:
        st.metric(
            label="File Types",
            value=len(stats['vector_store_stats']['file_types'])
        )
    
    with col4:
        st.metric(
            label="Supported Roles",
            value=len(stats['supported_roles'])
        )
    
    # Department distribution
    st.subheader("📁 Department Distribution")
    
    # Create sample data for visualization (in real app, this would come from actual data)
    dept_data = {
        'Department': ['Finance', 'Marketing', 'HR', 'Engineering', 'General'],
        'Documents': [50, 45, 30, 80, 25],
        'File Types': ['md, csv', 'md', 'csv', 'md', 'md']
    }
    
    df = pd.DataFrame(dept_data)
    
    fig = px.bar(
        df, 
        x='Department', 
        y='Documents',
        title="Documents per Department",
        color='Department'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Role permissions matrix
    st.subheader("🔐 Role Permissions Matrix")
    
    # Get roles
    roles_response = make_api_request("/roles")
    if roles_response:
        roles_data = []
        for role, info in roles_response.items():
            for dept, permission in info['permissions'].items():
                roles_data.append({
                    'Role': info['name'],
                    'Department': dept.title(),
                    'Permission': permission
                })
        
        roles_df = pd.DataFrame(roles_data)
        
        # Create heatmap
        pivot_df = roles_df.pivot(index='Role', columns='Department', values='Permission')
        
        # Convert permissions to numeric for visualization
        permission_map = {'none': 0, 'read': 1, 'full': 2}
        pivot_numeric = pivot_df.replace(permission_map)
        
        fig = px.imshow(
            pivot_numeric,
            title="Role Permissions Heatmap",
            color_continuous_scale="RdYlGn",
            aspect="auto"
        )
        fig.update_layout(
            xaxis_title="Department",
            yaxis_title="Role"
        )
        st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function."""
    # Check if user is logged in
    if st.session_state.access_token is None:
        display_login_page()
    else:
        # Navigation
        page = st.sidebar.selectbox(
            "Navigation",
            ["Chat", "Analytics"],
            index=0
        )
        
        if page == "Chat":
            display_main_interface()
        elif page == "Analytics":
            display_analytics()

if __name__ == "__main__":
    main() 