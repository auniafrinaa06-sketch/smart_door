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

# Custom CSS
st.markdown(bg_style + """
    <style>
    .stApp *, [data-testid="stVerticalBlock"] *, [data-testid="stAppViewContainer"] *,
    .element-container, .stPlotlyChart, .stDataFrame {
        opacity: 1 !important;
        filter: none !important;
        transition: none !important;
    }
    [data-testid="stStatusWidget"] { display: none !important; }
    div[data-testid="stMetric"] {
        background: rgba(60, 20, 45, 0.65);
        border: 1px solid rgba(244, 114, 182, 0.3);
        padding: 20px;
        border-radius: 18px;
        backdrop-filter: blur(12px);
    }
    .main-title {
        font-size: 38px;
        font-weight: 800;
        color: #f472b6;
        text-shadow: 0px 4px 12px rgba(244,114,182,0.4);
    }
    .sub-title { font-size: 16px; color: #fbcfe8; margin-bottom: 20px; }
    div.stButton > button {
        background: linear-gradient(135deg, #f472b6 0%, #db2777 100%);
        color: white; border-radius: 12px; border: none; padding: 8px 16px;
    }
    </style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

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

# ---------------------------------------------------------
# FUNGSI PENGURUSAN USER (GET & DELETE)
# ---------------------------------------------------------
def get_registered_users():
    conn = None
    try:
        conn = create_connection()
        query = "SELECT id, uid_card, username, user_type, created_at FROM registered_users ORDER BY id DESC"
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        return pd.DataFrame()
    finally:
        if conn and conn.is_connected():
            conn.close()

def delete_user_by_id(user_id):
    conn = None
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registered_users WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        st.error(f"Gagal memadam pengguna: {e}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()

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

# 🔒 LOGIN PAGE
def login_page():
    st.markdown('<div class="main-title" style="text-align: center;">🔑 Smart Door Access System</div>', unsafe_allow_html=True)
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
                    st.error("Invalid credentials.")

# 📊 MAIN DASHBOARD
def main_dashboard():
    st_autorefresh(interval=3000, key="datarefresh")

    # SIDEBAR CONTROL PANEL
    with st.sidebar:
        st.markdown("<h2 style='color: #f472b6;'>🌸 System Portal</h2>", unsafe_allow_html=True)
        st.caption("Owner & Admin Control Panel")
        st.markdown("---")
        
        st.markdown("<h3 style='color: #f9a8d4; font-size: 18px;'>⚙️ System Actions</h3>", unsafe_allow_html=True)
        with st.expander("🗑️ Reset Database Logs", expanded=False):
            st.warning("⚠️ Semua log akan dipadam!")
            if st.button("🔴 Confirm Reset All"):
                if clear_db_logs():
                    st.success("Log berjaya dipadam!")
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Logout"):
            st.session_state["logged_in"] = False
            st.rerun()

    # HEADER
    st.markdown('<div class="main-title">🔑 Smart Door Access System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Real-Time Access Control & Monitoring Dashboard</div>', unsafe_allow_html=True)

    # TAB SIKAP / FUNGSI
    tab1, tab2 = st.tabs(["📊 Access Logs", "👥 Registered Users (Delete/Manage)"])

    with tab1:
        df = get_db_data()
        if not df.empty:
            total_logs = len(df)
            success_logs = len(df[df['status'] == 'SUCCESS'])
            failed_logs = len(df[df['status'] == 'FAILED'])
            
            col1, col2, col3 = st.columns(3)
            col1.metric(label="📊 Total Scans", value=total_logs)
            col2.metric(label="✅ Access Granted", value=success_logs)
            col3.metric(label="❌ Access Denied", value=failed_logs)

            st.markdown("---")
            st.subheader("📋 Recent Access Logs")
            st.dataframe(df, use_container_width=True, height=350)
        else:
            st.info("No access log records found.")

    # 🔴 TAB PENGURUSAN USER (DELETE REGISTERED CARDS / FINGERPRINTS)
    with tab2:
        st.subheader("🗑️ Pengurusan Pengguna Berdaftar")
        st.caption("Padamkan kad RFID atau Fingerprint dari pangkalan data di sini.")

        users_df = get_registered_users()
        if not users_df.empty:
            for idx, row in users_df.iterrows():
                col_info, col_btn = st.columns([4, 1])
                with col_info:
                    st.markdown(f"**Nama:** {row['username']} | **ID/UID:** `{row['uid_card']}` | **Jenis:** {row['user_type']}")
                with col_btn:
                    if st.button(f"🗑️ Padam", key=f"del_{row['id']}"):
                        if delete_user_by_id(row['id']):
                            st.success(f"Pengguna {row['username']} berjaya dipadam!")
                            st.rerun()
                st.markdown("<hr style='margin: 5px 0; border-color: rgba(244, 114, 182, 0.2);'>", unsafe_allow_html=True)
        else:
            st.info("Tiada pengguna berdaftar dijumpai dalam pangkalan data.")

# ROUTING
if st.session_state["logged_in"]:
    main_dashboard()
else:
    login_page()
