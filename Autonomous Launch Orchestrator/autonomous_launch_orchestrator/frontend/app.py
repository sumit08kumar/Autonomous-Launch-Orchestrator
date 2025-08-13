import streamlit as st
import requests
import json
from datetime import datetime
import pandas as pd

# Configuration
API_BASE_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="Autonomous Launch Orchestrator",
    page_icon="🚀",
    layout="wide"
)

def main():
    st.title("🚀 Autonomous Launch Orchestrator")
    st.markdown("*AI-driven multi-agent system for autonomous product launch coordination*")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Create Plan", "Task Management", "Execution Logs"])
    
    if page == "Create Plan":
        create_plan_page()
    elif page == "Task Management":
        task_management_page()
    elif page == "Execution Logs":
        execution_logs_page()

def create_plan_page():
    st.header("📋 Create Launch Plan")
    
    with st.form("create_plan_form"):
        goal = st.text_area(
            "Launch Goal",
            placeholder="e.g., Launch our new AI chatbot in 3 weeks",
            help="Describe your high-level launch objective"
        )
        
        submitted = st.form_submit_button("Generate Plan")
        
        if submitted and goal:
            with st.spinner("Creating launch plan..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/create-plan", params={"goal": goal})
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['message']}")
                        
                        # Display created tasks
                        st.subheader("Generated Tasks")
                        for task in result['tasks']:
                            with st.expander(f"{task['role'].title()} - {task['priority'].title()} Priority"):
                                st.write(f"**Description:** {task['description']}")
                                st.write(f"**Deadline:** {task['deadline']}")
                                st.write(f"**Task ID:** {task['task_id']}")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend API. Make sure the backend is running on port 8000.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

def task_management_page():
    st.header("📊 Task Management")
    
    # Refresh button
    if st.button("🔄 Refresh Tasks"):
        st.rerun()
    
    try:
        response = requests.get(f"{API_BASE_URL}/tasks")
        if response.status_code == 200:
            tasks = response.json()
            
            if not tasks:
                st.info("No tasks found. Create a launch plan first.")
                return
            
            # Filter options
            col1, col2, col3 = st.columns(3)
            with col1:
                role_filter = st.selectbox("Filter by Role", ["All"] + list(set(task['role'] for task in tasks)))
            with col2:
                status_filter = st.selectbox("Filter by Status", ["All"] + list(set(task['status'] for task in tasks)))
            with col3:
                priority_filter = st.selectbox("Filter by Priority", ["All"] + list(set(task['priority'] for task in tasks)))
            
            # Apply filters
            filtered_tasks = tasks
            if role_filter != "All":
                filtered_tasks = [t for t in filtered_tasks if t['role'] == role_filter]
            if status_filter != "All":
                filtered_tasks = [t for t in filtered_tasks if t['status'] == status_filter]
            if priority_filter != "All":
                filtered_tasks = [t for t in filtered_tasks if t['priority'] == priority_filter]
            
            # Display tasks
            for task in filtered_tasks:
                status_color = {
                    "pending": "🟡",
                    "approved": "🟢",
                    "rejected": "🔴",
                    "completed": "✅",
                    "failed": "❌"
                }.get(task['status'], "⚪")
                
                priority_color = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(task['priority'], "⚪")
                
                with st.expander(f"{status_color} {task['role'].title()} - {task['description'][:50]}..."):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Description:** {task['description']}")
                        st.write(f"**Role:** {task['role'].title()}")
                        st.write(f"**Priority:** {priority_color} {task['priority'].title()}")
                        st.write(f"**Status:** {status_color} {task['status'].title()}")
                        if task['deadline']:
                            deadline = datetime.fromisoformat(task['deadline'].replace('Z', '+00:00'))
                            st.write(f"**Deadline:** {deadline.strftime('%Y-%m-%d %H:%M')}")
                    
                    with col2:
                        if task['status'] == 'pending':
                            if st.button(f"✅ Approve", key=f"approve_{task['task_id']}"):
                                approve_task(task['task_id'])
                                st.rerun()
                            
                            if st.button(f"❌ Reject", key=f"reject_{task['task_id']}"):
                                reject_task(task['task_id'])
                                st.rerun()
        else:
            st.error(f"Error fetching tasks: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend API. Make sure the backend is running on port 8000.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def execution_logs_page():
    st.header("📜 Execution Logs")
    
    # Refresh button
    if st.button("🔄 Refresh Logs"):
        st.rerun()
    
    try:
        response = requests.get(f"{API_BASE_URL}/logs")
        if response.status_code == 200:
            logs = response.json()
            
            if not logs:
                st.info("No execution logs found.")
                return
            
            # Display logs in a table
            df = pd.DataFrame(logs)
            df['executed_at'] = pd.to_datetime(df['executed_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.dataframe(
                df[['task_id', 'workflow_name', 'execution_status', 'executed_at']],
                use_container_width=True
            )
            
            # Detailed view
            st.subheader("Detailed Logs")
            for log in logs:
                status_icon = "✅" if log['execution_status'] == 'success' else "❌"
                with st.expander(f"{status_icon} {log['workflow_name']} - {log['task_id']}"):
                    st.write(f"**Task ID:** {log['task_id']}")
                    st.write(f"**Workflow:** {log['workflow_name']}")
                    st.write(f"**Status:** {log['execution_status']}")
                    st.write(f"**Executed At:** {log['executed_at']}")
                    st.write(f"**Details:**")
                    st.code(log['execution_details'], language='json')
        else:
            st.error(f"Error fetching logs: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend API. Make sure the backend is running on port 8000.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def approve_task(task_id: str):
    """Approve a task"""
    try:
        response = requests.post(f"{API_BASE_URL}/tasks/{task_id}/approve")
        if response.status_code == 200:
            st.success("✅ Task approved and executed!")
        else:
            st.error(f"Error approving task: {response.status_code}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def reject_task(task_id: str):
    """Reject a task"""
    try:
        response = requests.post(f"{API_BASE_URL}/tasks/{task_id}/reject")
        if response.status_code == 200:
            st.success("❌ Task rejected!")
        else:
            st.error(f"Error rejecting task: {response.status_code}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

