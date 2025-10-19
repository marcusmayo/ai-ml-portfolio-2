"""
GoalPilot - Vanguard Brand Edition
Matching official Vanguard website and brand guidelines
"""
import streamlit as st
import requests
from datetime import datetime
import json
from typing import Dict, Any
import time

# ============================================================================
# Configuration
# ============================================================================

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="GoalPilot - AI Financial Planning",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Vanguard Brand Colors (Official)
# ============================================================================

VANGUARD_RED = "#9A0718"  # Official Vanguard Red
VANGUARD_BLACK = "#1F1F1F"  # Text on white
VANGUARD_WHITE = "#FFFFFF"  # Background
VANGUARD_LIGHT_GRAY = "#F5F5F5"  # Light backgrounds

# ============================================================================
# Vanguard Brand CSS - Matching Website
# ============================================================================

st.markdown("""
<style>
    /* Remove Streamlit branding */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Global - White background with dark text */
    .stApp {
        background-color: #FFFFFF;
        color: #1F1F1F;
    }
    
    .main .block-container {
        padding-top: 2rem;
        background-color: #FFFFFF;
    }
    
    
    
    /* Sidebar example buttons - white text on red */
    [data-testid="stSidebar"] .stButton>button {
        color: #FFFFFF !important;
        color: #FFFFFF !important;
    }
    /* Sidebar - White background */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E5E5;
    }
    
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    /* Headers - Vanguard style */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #9A0718;
        text-align: center;
        margin-bottom: 0.5rem;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #666666;
        text-align: center;
        margin-bottom: 1.5rem;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Input fields - White with dark text */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #FFFFFF !important;
        border: 2px solid #CCCCCC !important;
        font-size: 1rem !important;
        font-family: Georgia, serif !important;
    }
    
    /* Experience dropdown - white bg, black text */
    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        color: #FFFFFF !important;
    }
    
    .stSelectbox select {
        background-color: #FFFFFF !important;
        color: #FFFFFF !important;
    }
    
    .stSelectbox select, .stSelectbox > div {
        background-color: #FFFFFF !important;
        color: #FFFFFF !important;
        border: 2px solid #CCCCCC !important;
    }
    
    /* Labels - Dark text */
    .stTextArea label, .stSelectbox label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }
    
    /* Buttons - Vanguard Red */
    .stButton>button {
        background-color: #9A0718 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        font-size: 1.1rem !important;
        border-radius: 4px !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    }
    
    .stButton>button:hover {
        background-color: #7A0510 !important;
    }
    
    /* Success box - White with Vanguard red border */
    .success-box {
        background-color: #FFFFFF;
        border: 2px solid #9A0718;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 0.5rem 0 1rem 0;
    }
    
    .success-box h3 {
        color: #9A0718;
        margin-bottom: 1rem;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    .success-box strong {
        color: #1F1F1F;
        font-weight: 700;
    }
    
    .success-box p {
        color: #1F1F1F !important;
        font-family: Georgia, serif;
        line-height: 1.6;
    }
    
    /* Metric cards - White with red border */
    .metric-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        border: 2px solid #9A0718;
    }
    
    /* Data sources box */
    .data-sources-box {
        background-color: #F5F5F5;
        border-left: 4px solid #9A0718;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
    }
    
    .data-sources-box h4 {
        color: #9A0718;
        margin-top: 0;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    .data-sources-box ul {
        margin: 0;
        padding-left: 1.5rem;
    }
    
    .data-sources-box li {
        color: #1F1F1F;
        padding: 0.3rem 0;
        font-size: 0.95rem;
    }
    
    /* Action step cards - White with left red border */
    .step-card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border-left: 5px solid #9A0718;
        border: 1px solid #E5E5E5;
        border-left: 5px solid #9A0718;
    }
    
    .step-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1F1F1F;
        margin-bottom: 0.8rem;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    .step-description {
        color: #1F1F1F;
        font-size: 1rem;
        line-height: 1.6;
        margin-bottom: 0;
        font-family: Georgia, serif;
    }
    
    .step-meta-line {
        display: block;
        margin-top: 0.8rem;
        padding-top: 0.8rem;
        border-top: 1px solid #E5E5E5;
        color: #666666;
        font-size: 0.95rem;
    }
    
    
    /* Expander - White background with black text */
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: 2px solid #9A0718 !important;
        border-radius: 6px !important;
        padding: 1rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #F5F5F5 !important;
        color: #FFFFFF !important;
    }
    
    details[open] > summary {
        background-color: #FFFFFF !important;
        color: #FFFFFF !important;
    }
    
    /* Sidebar branding box */
    .vanguard-logo {
        background-color: #9A0718;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .vanguard-logo h2, .vanguard-logo p {
        color: #FFFFFF !important;
        margin: 0;
    }
    
    .vanguard-logo p {
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* All text should be dark on white */
    .stMarkdown {
        color: #FFFFFF;
    }
    
    
    /* All headers - black text on white */
    h1, h2, h3, h4, h5, h6 {
        color: #1F1F1F !important;
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1F1F1F !important;
    }

    
    /* Tooltip - Vanguard style */
    [data-testid="stTooltipIcon"] {
        color: #9A0718 !important;
    }
    
    .stTooltip {
        background-color: #FFFFFF !important;
        color: #1F1F1F !important;
        border: 2px solid #9A0718 !important;
    }

    
    /* ===== COMPLETE TEXT CONTRAST FIXES ===== */
    
    /* SIDEBAR - All text black on white background */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #1F1F1F !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #1F1F1F !important;
    }
    
    /* Red boxes in sidebar - WHITE text */
    [data-testid="stSidebar"] .vanguard-logo h2,
    [data-testid="stSidebar"] .vanguard-logo p {
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] .stButton>button {
        color: #FFFFFF !important;
    }
    
    /* MAIN CONTENT - All text black on white */
    .main * {
        color: #1F1F1F !important;
    }
    
    /* Labels - BLACK text */
    label, .stTextArea label, .stSelectbox label {
        color: #1F1F1F !important;
        font-weight: 600 !important;
    }
    
    /* Input fields - BLACK text on WHITE background */
    .stTextArea textarea,
    .stSelectbox select,
    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        color: #1F1F1F !important;
    }
    
    /* Headers - ALL BLACK */
    h1, h2, h3, h4, h5, h6 {
        color: #1F1F1F !important;
    }
    
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4 {
        color: #1F1F1F !important;
    }
    
    /* Success message - BLACK text */
    .success-box * {
        color: #1F1F1F !important;
    }
    
    /* All body text - BLACK */
    p, span, div:not(.stButton):not(.vanguard-logo) {
        color: #1F1F1F !important;
    }
    
    /* Buttons - WHITE text on RED */
    .stButton>button {
        background-color: #9A0718 !important;
        color: #FFFFFF !important;
    }
    
    /* Tooltip - BLACK text on WHITE background */
    [role="tooltip"] {
        background-color: #FFFFFF !important;
        color: #1F1F1F !important;
        border: 2px solid #9A0718 !important;
    }
    
    .stTooltipContent {
        background-color: #FFFFFF !important;
        color: #1F1F1F !important;
    }


    /* Download button - WHITE text on DARK */
    .stDownloadButton>button {
        background-color: #2C2C2C !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    .stDownloadButton>button:hover {
        background-color: #1F1F1F !important;
    }

    /* Tooltip - BLACK text on WHITE with border */
    [data-baseweb="tooltip"] {
        background-color: #FFFFFF !important;
        color: #1F1F1F !important;
        border: 2px solid #9A0718 !important;
        padding: 0.5rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
    }
    
    [data-baseweb="tooltip"] * {
        color: #1F1F1F !important;
    }
    
    .stTooltipContent {
        background-color: #FFFFFF !important;
        color: #1F1F1F !important;
    }

    
    /* ===== FORCE TEXT COLOR FIXES ===== */
    
    /* 1. Example buttons - WHITE text on RED */
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] .stButton > button,
    [data-testid="stSidebar"] button[kind="secondary"] {
        color: #FFFFFF !important;
        background-color: #9A0718 !important;
    }
    
    [data-testid="stSidebar"] button *,
    [data-testid="stSidebar"] .stButton > button * {
        color: #FFFFFF !important;
    }
    
    /* 2. Generate Plan button - WHITE text on RED */
    .main button[kind="primary"],
    .main .stButton > button[kind="primary"],
    button[data-testid="baseButton-primary"],
    .stButton > button {
        color: #FFFFFF !important;
        background-color: #9A0718 !important;
    }
    
    .main button[kind="primary"] *,
    .stButton > button * {
        color: #FFFFFF !important;
    }
    
    /* 3. Download button - WHITE text on BLACK */
    .stDownloadButton button,
    .stDownloadButton > button,
    button[kind="secondary"][data-testid*="download"],
    .main .stDownloadButton button {
        color: #FFFFFF !important;
        background-color: #2C2C2C !important;
    }
    
    .stDownloadButton button *,
    .stDownloadButton > button * {
        color: #FFFFFF !important;
    }
    
    /* 4. Tooltip - BLACK text on WHITE */
    div[data-baseweb="tooltip"],
    div[role="tooltip"],
    .stTooltipContent,
    [class*="tooltip"] {
        background-color: #FFFFFF !important;
        color: #1F1F1F !important;
        border: 2px solid #9A0718 !important;
    }
    
    div[data-baseweb="tooltip"] *,
    div[role="tooltip"] *,
    .stTooltipContent * {
        color: #1F1F1F !important;
        background-color: transparent !important;
    }


    
    /* Tooltip icon - Vanguard red for visibility */
    [data-testid="stTooltipIcon"],
    .stTooltipIcon,
    svg[data-testid="stTooltipIcon"] {
        color: #9A0718 !important;
        fill: #9A0718 !important;
    }
    
    [data-testid="stTooltipIcon"] svg {
        color: #9A0718 !important;
        fill: #9A0718 !important;
    }

    
    button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Alternative selectors in case Streamlit changes structure */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    section[data-testid="stSidebar"] > div > button {
        display: none !important;
    }


    /* NUCLEAR OPTION: HIDE COLLAPSE BUTTON WITH ALL SELECTORS */
    button[kind="header"],
    button[data-testid="baseButton-header"],
    button[data-testid="collapsedControl"],
    [data-testid="collapsedControl"],
    [data-testid="collapsedControl"] button,
    section[data-testid="stSidebar"] button[kind="header"],
    section[data-testid="stSidebar"] > div > button,
    section[data-testid="stSidebar"] > div > div > button,
    div[data-testid="stSidebar"] button,
    .css-1outpf7,
    .css-163ttbj {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        width: 0 !important;
        height: 0 !important;
        position: absolute !important;
        left: -9999px !important;
    }
    
    /* Force sidebar to always be visible */
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
    }

</style>
""", unsafe_allow_html=True)

# ============================================================================
# Helper Functions
# ============================================================================

def check_api_health() -> bool:
    """Check if API is available"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def call_api(endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
    """Call API with error handling"""
    url = f"{API_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=90)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=90)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("🔴 Cannot connect to API. Start: `python -m src.app.api`")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out.")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def display_plan(plan_data: Dict[str, Any]):
    """Display plan with Vanguard styling and formatted steps"""
    
    # Success box
    st.markdown("<div class='success-box'>", unsafe_allow_html=True)
    st.markdown("### ✅ Your Personalized Financial Plan is Ready!")
    
    goal_type = plan_data['goal_type'].replace('_', ' ').title()
    st.markdown(f"**Goal:** {goal_type}")
    
    summary = plan_data['summary']
    st.markdown(f"**Summary:** {summary}")
    
    confidence = int(plan_data['confidence_score'] * 100)
    st.markdown(f"**Confidence Score:** {confidence}%")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Plan Steps", len(plan_data['plan_steps']))
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Data Sources", len(plan_data['api_data']))
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        quality = "Excellent" if plan_data['confidence_score'] >= 0.8 else "Good"
        st.metric("Plan Quality", quality)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Data sources
    sources = []
    if 'retirement_projection' in plan_data['api_data']:
        sources.append("📊 Retirement Calculator - Compound interest projections")
    if 'mortgage' in plan_data['api_data']:
        sources.append("🏠 Mortgage Calculator - Standard amortization")
    if 'stock_quote' in plan_data['api_data']:
        sources.append("📈 Alpha Vantage API - Real-time S&P 500 market data")
    sources.append("🤖 Claude 3.5 Sonnet - AI financial analysis")
    
    sources_html = "<div class='data-sources-box'><h4>📚 Data Sources Used:</h4><ul>"
    for source in sources:
        sources_html += f"<li>{source}</li>"
    sources_html += "</ul></div>"
    st.markdown(sources_html, unsafe_allow_html=True)
    
    # Financial Analysis
    if plan_data['api_data']:
        st.markdown("## 📊 Financial Analysis")
        
        with st.expander("📈 View Detailed Financial Data", expanded=True):
            if 'retirement_projection' in plan_data['api_data']:
                proj = plan_data['api_data']['retirement_projection']
                st.subheader("💰 Retirement Projection")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Projected Balance", f"${proj['projected_balance']:,.2f}")
                    st.metric("Total Contributions", f"${proj['total_contributions']:,.2f}")
                with col2:
                    st.metric("Interest Earned", f"${proj['total_interest_earned']:,.2f}")
                    st.metric("Monthly Withdrawal (4% rule)", f"${proj['safe_withdrawal_rate_4pct']:,.2f}")
            
            if 'mortgage' in plan_data['api_data']:
                mort = plan_data['api_data']['mortgage']
                st.subheader("🏠 Mortgage Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Home Price", f"${mort['home_price']:,.2f}")
                    st.metric("Down Payment", f"${mort['down_payment']:,.2f}")
                    st.metric("Loan Amount", f"${mort['loan_amount']:,.2f}")
                with col2:
                    st.metric("Monthly Payment", f"${mort['total_monthly_payment']:,.2f}")
                    st.metric("Interest Rate", f"{mort['interest_rate']}%")
                    st.metric("Total Interest", f"${mort['total_interest_paid']:,.2f}")
            
            if 'stock_quote' in plan_data['api_data']:
                quote = plan_data['api_data']['stock_quote']
                st.subheader("📈 Market Overview (S&P 500)")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Price", f"${quote['price']:.2f}", delta=f"{quote['change_percent']:.2f}%")
                with col2:
                    st.metric("10-Year Return", f"{quote['historical_return_10yr']:.1f}%")
                with col3:
                    st.metric("Dividend Yield", f"{quote['dividend_yield']:.2f}%")
    
    # Action Plan - Formatted like screenshot
    st.markdown("## 📋 Your Action Plan")
    
    for step in plan_data['plan_steps']:
        title = step['title']
        description = step['description']
        duration = step.get('estimated_duration', 'Varies')
        
        # Parse timeline and resources from description
        desc_main = description
        timeline = ""
        resources = ""
        
        if 'Timeline:' in description:
            parts = description.split('Timeline:')
            desc_main = parts[0].strip()
            if len(parts) > 1:
                rest = parts[1]
                if 'Resources:' in rest:
                    t_parts = rest.split('Resources:')
                    timeline = t_parts[0].strip()
                    resources = t_parts[1].strip() if len(t_parts) > 1 else ""
                else:
                    timeline = rest.strip()
        
        # Build step card HTML
        step_html = f"""
        <div class='step-card'>
            <div class='step-title'>Step {step['step_number']}: {title}</div>
            <div class='step-description'>
                <strong>Description:</strong> {desc_main}
        """
        
        if timeline:
            step_html += f"<span class='step-meta-line'><strong>Timeline:</strong> {timeline}</span>"
        
        if resources:
            step_html += f"<span class='step-meta-line'><strong>Resources:</strong> {resources}</span>"
        
        step_html += f"""
                <span class='step-meta-line'>⏱️ <strong>Estimated Duration:</strong> {duration}</span>
            </div>
        </div>
        """
        st.markdown(step_html, unsafe_allow_html=True)

# ============================================================================
# Main App
# ============================================================================

def main():

    # Use components to inject CSS with maximum priority
    import streamlit.components.v1 as components
    
    components.html("""
        <style>
        /* Ultra-specific selectors to hide collapse button */
        button[kind="header"],
        button[data-testid="baseButton-header"],
        [data-testid="collapsedControl"],
        section[data-testid="stSidebar"] button[kind="header"] {
            display: none !important;
        }
        </style>
        <script>
        (function() {
            function hideButton() {
                const buttons = window.parent.document.querySelectorAll('button[kind="header"]');
                buttons.forEach(b => b.style.display = 'none');
            }
            hideButton();
            setInterval(hideButton, 100);
        })();
        </script>
    """, height=0)
    

    
    
    st.markdown("<h1 class='main-header'>🎯 GoalPilot</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>AI-Powered Financial Planning with Claude 3.5 Sonnet</p>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("""
        <div class='vanguard-logo'>
            <h2>🎯 GoalPilot</h2>
            <p>Intelligent Financial Planning</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🚀 Quick Start")
        st.markdown("1. Enter your financial goal\n2. Select experience level\n3. Click Generate Plan\n4. Review your roadmap")
        
        if check_api_health():
            st.success("✅ API Connected")
        else:
            st.error("❌ API Offline")
        
        st.markdown("---")
        st.markdown("### 💡 Example Goals")
        
        examples = [
            ("I want to retire comfortably in 20 years", "novice"),
            ("I need to save for a $500K house", "diy"),
            ("Save for child's college in 10 years", "novice")
        ]
        
        for goal, profile in examples:
            if st.button(f"📌 {goal[:30]}...", key=goal, use_container_width=True):
                st.session_state.goal_input = goal
                st.session_state.profile_input = profile
                st.rerun()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        goal_input = st.text_area(
            "💰 Describe Your Financial Goal",
            value=st.session_state.get('goal_input', ''),
            height=100,
            placeholder="Example: I want to retire comfortably in 20 years..."
        )
    
    with col2:
        profile_input = st.selectbox(
            "👤 Experience Level",
            options=["novice", "diy", "near-retiree"],
            index=["novice", "diy", "near-retiree"].index(st.session_state.get('profile_input', 'novice')),
            help="**Novice**: New to investing, need detailed guidance | **DIY**: Comfortable managing finances independently | **Near-retiree**: Approaching retirement age"
        )
    
    if st.button("✨ Generate My Plan", type="primary", use_container_width=True):
        if not goal_input or len(goal_input) < 10:
            st.error("❌ Please enter a goal (at least 10 characters)")
        elif not check_api_health():
            st.error("❌ API not running: `python -m src.app.api`")
        else:
            progress_text = st.empty()
            progress_bar = st.progress(0)
            
            progress_text.text("🔍 Analyzing your goal...")
            progress_bar.progress(20)
            time.sleep(0.3)
            
            progress_text.text("💰 Fetching financial data...")
            progress_bar.progress(40)
            
            with st.spinner("🤖 Generating plan..."):
                plan_data = call_api("/plan", "POST", {"goal": goal_input, "user_profile": profile_input})
                
                if plan_data:
                    progress_text.text("✅ Success!")
                    progress_bar.progress(100)
                    time.sleep(0.5)
                    progress_text.empty()
                    progress_bar.empty()
                    
                    st.session_state.last_plan = plan_data
                    st.balloons()
                    st.rerun()
                else:
                    progress_text.empty()
                    progress_bar.empty()
    
    if 'last_plan' in st.session_state:
        display_plan(st.session_state.last_plan)
        
        plan_json = json.dumps(st.session_state.last_plan, indent=2)
        st.download_button(
            "📥 Download Plan (JSON)",
            data=plan_json,
            file_name=f"goalpilot_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

if __name__ == "__main__":
    main()
