import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from datetime import datetime
import time
import os
from dotenv import load_dotenv
from ai_services import (
    chat_with_watson, 
    analyze_financial_sentiment,
    analyze_financial_document,
    call_granite_model
)

# Load environment variables
load_dotenv()

# Backend API configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Financial Assistant",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'token' not in st.session_state:
    st.session_state.token = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'financial_data' not in st.session_state:
    st.session_state.financial_data = {}
if 'document_analysis' not in st.session_state:
    st.session_state.document_analysis = {}
if 'ai_analysis' not in st.session_state:
    st.session_state.ai_analysis = ""

# Authentication functions
def login(username, password):
    """Authenticate user and get JWT token"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def get_user_profile():
    """Fetch user profile from backend"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(
            f"{BACKEND_URL}/user/profile",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def update_user_profile(profile_data):
    """Update user profile"""
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state.token}",
            "Content-Type": "application/json"
        }
        response = requests.put(
            f"{BACKEND_URL}/user/profile",
            headers=headers,
            json=profile_data
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Financial data functions
def upload_statement(file):
    """Upload bank statement PDF"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        files = {"file": (file.name, file.getvalue(), "application/pdf")}
        response = requests.post(
            f"{BACKEND_URL}/upload/statement",
            headers=headers,
            files=files
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def get_financial_data():
    """Fetch financial data from backend"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(
            f"{BACKEND_URL}/financial/data",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def send_chat_message(message):
    """Send chat message to AI services and stream response"""
    try:
        # Use Watson Assistant for financial conversations
        response, context = chat_with_watson(message)
        
        # Enhance with additional analysis if needed
        if any(keyword in message.lower() for keyword in ['analyze', 'sentiment', 'review']):
            analysis = analyze_financial_sentiment(message)
            if isinstance(analysis, dict):
                sentiment = analysis.get('sentiment', {}).get('document', {}).get('label', 'neutral')
                response += f"\n\nSentiment Analysis: {sentiment.capitalize()}"
        
        return response
    except Exception as e:
        return f"I encountered an error: {str(e)}. Please try again."

# Financial health calculations
def calculate_financial_health_score(income, expenses, savings):
    """Calculate simple financial health score"""
    if income == 0:
        return 0
    
    savings_rate = (savings / income) * 100 if income > 0 else 0
    expense_diversity = min(len(set(expenses.keys())) / 10, 1.0)  # Normalize to 0-1
    
    # Weighted score (0-100)
    score = (savings_rate * 0.6) + (expense_diversity * 40)
    return min(max(score, 0), 100)

# Login page
def login_page():
    st.title("💰 Financial Assistant Login")
    st.markdown("---")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username and password:
                auth_data = login(username, password)
                if auth_data:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.token = auth_data.get("access_token")
                    st.session_state.user_profile = get_user_profile() or {}
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            else:
                st.error("Please enter both username and password.")

# Main application
def main_app():
    # Sidebar
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.username}!")
        st.markdown("---")
        
        # Profile section
        if st.button("🔄 Refresh Profile"):
            st.session_state.user_profile = get_user_profile() or {}
            st.rerun()
        
        # File uploader for bank statements
        st.subheader("📄 Upload Bank Statement")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            key="statement_uploader"
        )
        
        if uploaded_file is not None:
            if st.button("Upload and Analyze Statement"):
                with st.spinner("Uploading and analyzing statement with AI..."):
                    # Read and extract text from PDF (simplified)
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    
                    # Use AI to analyze the document
                    analysis = analyze_financial_document(text)
                    
                    # Store analysis results
                    st.session_state.document_analysis = analysis
                    st.success("Statement analyzed with AI!")
                    
                    # Refresh financial data
                    st.session_state.financial_data = get_financial_data() or {}
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.token = None
            st.session_state.chat_history = []
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # User Profile Section
        st.header("👤 User Profile")
        with st.form("profile_form"):
            name = st.text_input(
                "Full Name",
                value=st.session_state.user_profile.get("name", "")
            )
            email = st.text_input(
                "Email",
                value=st.session_state.user_profile.get("email", "")
            )
            age = st.number_input(
                "Age",
                min_value=18,
                max_value=100,
                value=st.session_state.user_profile.get("age", 25)
            )
            income = st.number_input(
                "Annual Income ($)",
                min_value=0,
                value=st.session_state.user_profile.get("income", 50000)
            )
            
            if st.form_submit_button("Update Profile"):
                profile_data = {
                    "name": name,
                    "email": email,
                    "age": age,
                    "income": income
                }
                if update_user_profile(profile_data):
                    st.success("Profile updated successfully!")
                    st.session_state.user_profile = profile_data
                else:
                    st.error("Failed to update profile.")
    
    with col2:
        # Financial Health Section
        st.header("💪 Financial Health")
        
        # Calculate financial health score (mock data - replace with actual data)
        financial_data = st.session_state.financial_data or {}
        income = financial_data.get("monthly_income", 5000)
        expenses = financial_data.get("monthly_expenses", {})
        savings = financial_data.get("monthly_savings", 1000)
        
        health_score = calculate_financial_health_score(income, expenses, savings)
        
        col_health1, col_health2 = st.columns(2)
        with col_health1:
            st.metric("Financial Health Score", f"{health_score:.1f}/100")
            
            # Smart alerts
            if health_score < 50:
                st.error("⚠️ Financial health needs improvement")
            elif health_score < 75:
                st.warning("ℹ️ Good financial health - room for improvement")
            else:
                st.success("✅ Excellent financial health!")
                
            if sum(expenses.values()) > income * 0.6:
                st.error("🚨 High spending alert! Expenses exceed 60% of income")
        
        with col_health2:
            # Goal tracker
            st.subheader("🎯 Savings Goal")
            goal_amount = st.number_input(
                "Target Savings ($)",
                min_value=0,
                value=5000,
                key="savings_goal"
            )
            current_savings = financial_data.get("total_savings", 1500)
            progress = min((current_savings / goal_amount) * 100, 100) if goal_amount > 0 else 0
            
            st.progress(progress / 100)
            st.write(f"${current_savings} / ${goal_amount} ({progress:.1f}%)")
    
    # AI-Powered Insights Section
    st.markdown("---")
    st.subheader("🤖 AI-Powered Insights")

    if st.button("Generate Deep Financial Analysis"):
        with st.spinner("Analyzing your financial data with AI..."):
            # Prepare data for analysis
            financial_context = f"""
            User Profile: {st.session_state.user_profile}
            Financial Data: {st.session_state.financial_data}
            """
            
            # Use Granite for comprehensive analysis
            analysis = call_granite_model(
                f"Provide a comprehensive financial analysis and recommendations based on this data: {financial_context}"
            )
            
            st.session_state.ai_analysis = analysis

    if st.session_state.ai_analysis:
        st.text_area("AI Analysis", st.session_state.ai_analysis, height=300)
    
    # Financial Dashboard
    st.markdown("---")
    st.header("📊 Financial Dashboard")
    
    tab1, tab2 = st.tabs(["Budget Summary", "Spending Analysis"])
    
    with tab1:
        st.subheader("Budget Overview")
        
        # Mock data - replace with actual API call
        budget_data = financial_data.get("budget", {})
        
        if budget_data:
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                st.metric("Monthly Budget", f"${budget_data.get('total_budget', 4000)}")
            with col_b2:
                st.metric("Actual Spending", f"${budget_data.get('actual_spending', 3200)}")
            with col_b3:
                remaining = budget_data.get('total_budget', 4000) - budget_data.get('actual_spending', 3200)
                st.metric("Remaining", f"${remaining}")
            
            # Budget visualization
            categories = list(budget_data.get('category_budget', {}).keys())
            budgeted = list(budget_data.get('category_budget', {}).values())
            actual = list(budget_data.get('category_actual', {}).values())
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Budgeted',
                x=categories,
                y=budgeted,
                marker_color='lightblue'
            ))
            fig.add_trace(go.Bar(
                name='Actual',
                x=categories,
                y=actual,
                marker_color='coral'
            ))
            fig.update_layout(
                title="Budget vs Actual Spending by Category",
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # AI-generated summary
            st.subheader("📝 AI Insights")
            st.write(financial_data.get("budget_summary", "No summary available yet. Upload statements to get insights."))
        
        else:
            st.info("Upload bank statements to see your budget analysis.")
    
    with tab2:
        st.subheader("Spending Analysis")
        
        spending_data = financial_data.get("spending_analysis", {})
        
        if spending_data:
            # Categorized transactions
            st.write("### Categorized Transactions")
            transactions_df = pd.DataFrame(spending_data.get("transactions", []))
            if not transactions_df.empty:
                st.dataframe(transactions_df)
            
            # Spending by category pie chart
            category_totals = spending_data.get("category_totals", {})
            if category_totals:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=list(category_totals.keys()),
                    values=list(category_totals.values()),
                    hole=.3
                )])
                fig_pie.update_layout(title="Spending by Category")
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Cost-cutting insights
            st.subheader("💡 Cost-cutting Insights")
            insights = spending_data.get("insights", [])
            for insight in insights:
                st.info(insight)
        
        else:
            st.info("Upload bank statements to see spending analysis and insights.")
    
    # Chat Interface
    st.markdown("---")
    st.header("💬 Financial Assistant Chat")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your finances..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Get AI response using integrated services
            response = send_chat_message(prompt)
            
            # Stream the response (simulated)
            for chunk in response.split():
                full_response += chunk + " "
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.05)
            
            message_placeholder.markdown(full_response)
            
            # Add AI response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})

# Main application flow
def main():
    if not st.session_state.authenticated:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()