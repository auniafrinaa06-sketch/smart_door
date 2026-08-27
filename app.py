import streamlit as st
import mysql.connector
import pandas as pd
import base64
import plotly.express as px
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
# 🎨 CUSTOM CSS & ANTI-FADING OVERLAY
# =========================================================
st.markdown(bg_style + """
    <style>
    /* 🚫 MATIKAN OVERLAY PUDAR / KELABU SEMASA AUTO-REFRESH */
    .stApp *, 
    [data-testid="stVerticalBlock"] *,
    [data-testid="stAppViewContainer"] *,
    .element-container,
    .stPlotlyChart,
    .stDataFrame {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
    }

    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* ✨ STYLING DASHBOARD */
    div[data-testid="stMetric"] {
        background: rgba(60, 20, 45, 0.65);
        border: 1px solid rgba(244, 114, 182, 0.3);
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
        transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), border-color 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
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
    }

    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #f472b6;
        text-shadow: 0px 4px 12px rgba(244,114,182,0.4);
        margin-bottom: 2px;
    }
    .sub-title {
        font-size: 16px;
        color: #fbcfe8;
        margin-bottom: 20px;
    }
    h2, h3 { color: #f9a8d4 !important; font-weight: 600; }

    div.stButton > button {
        background: linear-gradient(135deg, #f472b6 0%, #db2777 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 10px 20px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(219, 39, 119, 0.3);
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

# Database Connection Helper Function
def create_connection():
    return mysql.connector.connect(
        host="mysql-3727e8f3-auniafrinaa06-9aec.a.aivencloud.com",
        user="avnadmin",
        password="AVNS_y1pg9gwZWmf1339ju2q",
        database="defaultdb",
        port=10110
    )

def get_db_data():
    conn = None
    try:
        conn = create_connection()
        query = "SELECT id, uid_card, username, status, timestamp FROM access_log ORDER BY timestamp DESC"
        df = pd.read_sql(query, conn)
        
        # 🔴 PENUKARAN ZON MASA: TAMBAH 8 JAM (UTC KE WAKTU MALAYSIA)
        if not df.empty and 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp']) + pd.Timedelta(hours=8)
            df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
        return df
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return pd.DataFrame()
    finally:
        if conn and conn.is_connected():
            conn.close()

# 🧹 FUNGSI UNTUK RESET / PADAM SEMUA DATABASE LOGS
def clear_db_logs():
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("TRUNCATE TABLE access_log;")
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        st.error(f"Failed to reset logs: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

# 📊 MAIN DASHBOARD
def main_dashboard():
    # Refresh data setiap 3 saat
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

        # CHARTS SECTION (PIE / DONUT CHART SAHAJA)
        st.subheader("📈 Access Analytics")
        
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
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font_color="#f1f5f9", 
            margin=dict(t=40, b=10, l=0, r=0)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")

        # LOGS TABLE
        st.subheader("📋 Recent Access Logs")
        
        display_df = df[['id', 'uid_card', 'username', 'status', 'timestamp']].copy()
        display_df.columns = ['ID', 'UID / Input', 'Username', 'Access Status', 'Date & Time']

        def color_status(val):
            color = '#f472b6' if val == 'SUCCESS' else '#ef4444' if val == 'FAILED' else ''
            return f'color: {color}; font-weight: bold;'

        # Compatible Styler for Pandas 1.x & 2.x
        try:
            styled_df = display_df.style.map(color_status, subset=['Access Status'])
        except AttributeError:
            styled_df = display_df.style.applymap(color_status, subset=['Access Status'])
            
        st.dataframe(styled_df, use_container_width=True, height=400)

    else:
        st.info("No access log records found in the database. (System is clean)")

# PAGE ROUTING
if st.session_state["logged_in"]:
    main_dashboard()
else:
    login_page()
