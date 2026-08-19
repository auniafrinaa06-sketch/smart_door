import streamlit as st
import mysql.connector
import pandas as pd
import base64
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration
st.set_page_config(
    page_title="Smart Door System",
    page_icon="🔑",
    layout="wide"
)

# Function to encode background image
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

img_base64 = get_base64_image("bg_rumah.jpg")
if img_base64:
    bg_style = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(35, 10, 25, 0.92), rgba(35, 10, 25, 0.92)), 
                          url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
else:
    bg_style = "<style>.stApp { background-color: #2d0f1e; }</style>"

# =========================================================
# 🎨 CUSTOM CSS: PROTOTYPING ANIMATIONS
# =========================================================
st.markdown(bg_style + """
    <style>
    @keyframes prototypeEntry {
        0% { opacity: 0; transform: translateY(30px) scale(0.98); }
        100% { opacity: 1; transform: translateY(0) scale(1); }
    }

    div[data-testid="stMetric"] {
        background: rgba(60, 20, 45, 0.65);
        border: 1px solid rgba(244, 114, 182, 0.3);
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
        transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), border-color 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        animation: prototypeEntry 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-8px) scale(1.03);
        border-color: rgba(244, 114, 182, 0.9);
        box-shadow: 0 15px 35px rgba(244, 114, 182, 0.35);
    }
    div[data-testid="stMetricLabel"] > div { color: #fce7f3 !important; font-size: 15px; }
    div[data-testid="stMetricValue"] > div { color: #ffffff !important; font-weight: 700; }

    div[data-testid="stPlotlyChart"] {
        background: rgba(45, 15, 35, 0.5);
        border-radius: 20px;
        padding: 10px;
        border: 1px solid rgba(244, 114, 182, 0.2);
        backdrop-filter: blur(10px);
        transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), border-color 0.3s ease;
        animation: prototypeEntry 0.9s cubic-bezier(0.16, 1, 0.3, 1) 0.3s both;
    }
    div[data-testid="stPlotlyChart"]:hover {
        transform: translateY(-5px);
        border-color: rgba(244, 114, 182, 0.6);
    }

    div[data-testid="stDataFrame"] {
        background-color: rgba(25, 8, 18, 0.75);
        padding: 15px;
        border-radius: 18px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(244, 114, 182, 0.25);
        transition: transform 0.3s ease, border-color 0.3s ease;
        animation: prototypeEntry 1s cubic-bezier(0.16, 1, 0.3, 1) 0.5s both;
    }

    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #f472b6;
        text-shadow: 0px 4px 12px rgba(244,114,182,0.4);
        margin-bottom: 2px;
        animation: prototypeEntry 0.7s ease both;
    }
    .sub-title {
        font-size: 16px;
        color: #fbcfe8;
        margin-bottom: 20px;
        animation: prototypeEntry 0.7s ease 0.1s both;
    }
    h2, h3 { color: #f9a8d4 !important; font-weight: 600; animation: prototypeEntry 0.8s ease both; }

    div.stButton > button {
        background: linear-gradient(135deg, #f472b6 0%, #db2777 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(219, 39, 119, 0.3);
        transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
        width: 100%;
        cursor: pointer;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #f472b6 0%, #be185d 100%);
        box-shadow: 0 8px 25px rgba(219, 39, 119, 0.6);
        transform: translateY(-3px) scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# 🔒 LOGIN PAGE
def login_page():
    st.markdown('<div class="main-title" style="text-align: center;">🔑 Smart Door Access System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title" style="text-align: center;">Owner Portal Authentication</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("🌸 Admin Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Sign In")
            
            if submit_button:
                if username == "admin" and password == "admin123":
                    st.session_state["logged_in"] = True
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

# Database Connection Function
def get_db_data():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="smart_door_db",
            port=3307
        )
        query = "SELECT id, uid_card, username, status, timestamp FROM access_log ORDER BY timestamp DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return pd.DataFrame()

# 🧹 FUNGSI UNTUK RESET / PADAM SEMUA DATABASE LOGS
def clear_db_logs():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="smart_door_db",
            port=3307
        )
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE access_log;")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Failed to reset logs: {e}")
        return False

# 🛠️ FUNGSI PENGELOMPOKAN KATEGORI
def map_access_category(row):
    status = str(row['status']).upper()
    username = str(row['username']).lower()
    
    if status == 'FAILED' or 'unknown' in username:
        return 'Unknown'
    elif 'rfid' in username or 'card' in username:
        return 'RFID'
    elif 'pin' in username or 'keypad' in username:
        return 'Keypad'
    elif 'finger' in username or 'jari' in username or 'auni' in username:
        return 'Fingerprint'
    else:
        return 'Unknown'

# 📊 MAIN DASHBOARD
def main_dashboard():
    st_autorefresh(interval=3000, key="datarefresh")

    # SIDEBAR
    with st.sidebar:
        st.title("🌸 System Portal")
        st.caption("Owner & Admin Control Panel")
        st.markdown("---")
        
        st.subheader("⚙️ System Actions")
        
        # 🚨 POP-UP PENGESAHAN PADAM LOG
        with st.expander("🗑️ Reset Database Logs"):
            st.warning("⚠️ Adakah anda pasti? Semua log rekod akan dipadam kekal!")
            if st.button("🔴 Confirm Reset All"):
                if clear_db_logs():
                    st.success("Semua log telah berjaya dipadam!")
                    st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state["logged_in"] = False
            st.rerun()

    # HEADER
    st.markdown('<div class="main-title">🔑 Smart Door Access System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Real-Time Access Control & Monitoring Dashboard</div>', unsafe_allow_html=True)

    df = get_db_data()

    if not df.empty:
        # METRICS OVERVIEW
        total_logs = len(df)
        success_logs = len(df[df['status'] == 'SUCCESS'])
        failed_logs = len(df[df['status'] == 'FAILED'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="📊 Total Scans", value=total_logs)
        with col2:
            st.metric(label="✅ Access Granted", value=success_logs)
        with col3:
            st.metric(label="❌ Access Denied", value=failed_logs)

        st.markdown("---")

        # CHARTS SECTION
        st.subheader("📈 Access Analytics")
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            status_counts = df['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Total']
            
            fig_pie = px.pie(
                status_counts, 
                names='Status', 
                values='Total', 
                title="Access Ratio",
                color='Status',
                color_discrete_map={'SUCCESS': '#f472b6', 'FAILED': '#be185d'},
                hole=0.45
            )
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f1f5f9", margin=dict(t=40, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

        with chart_col2:
            df['Access_Method'] = df.apply(map_access_category, axis=1)
            category_counts = df['Access_Method'].value_counts().reset_index()
            category_counts.columns = ['Access Method', 'Access Count']
            
            fig_bar = px.bar(
                category_counts, 
                x='Access Method', 
                y='Access Count', 
                title="Access Method Frequency",
                color='Access Count',
                color_continuous_scale=['#fce7f3', '#f472b6', '#db2777']
            )
            fig_bar.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", 
                plot_bgcolor="rgba(0,0,0,0)", 
                font_color="#f1f5f9", 
                margin=dict(t=40, b=0, l=0, r=0),
                xaxis=dict(title="Method")
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")

        # LOGS TABLE
        st.subheader("📋 Recent Access Logs")
        
        display_df = df[['id', 'uid_card', 'username', 'status', 'timestamp']].copy()
        display_df.columns = ['ID', 'UID / Input', 'Username', 'Access Status', 'Date & Time']

        def color_status(val):
            color = '#f472b6' if val == 'SUCCESS' else '#ef4444' if val == 'FAILED' else ''
            return f'color: {color}; font-weight: bold;'

        styled_df = display_df.style.map(color_status, subset=['Access Status'])
        st.dataframe(styled_df, use_container_width=True, height=400)

    else:
        st.info("No access log records found in the database. (System is clean)")

# PAGE ROUTING
if st.session_state["logged_in"]:
    main_dashboard()
else:
    login_page()