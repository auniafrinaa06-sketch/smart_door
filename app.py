import streamlit as st
import pandas as pd
import mysql.connector

# --- CONFIGURASI MUKA SURAT STREAMLIT ---
st.set_page_config(
    page_title="Smart Door Access System",
    page_icon="🔑",
    layout="wide"
)

# --- FUNGSI CONNECTION PANGKALAN DATA AIVEN ---
def init_connection():
    return mysql.connector.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        port=st.secrets["mysql"]["port"]
    )

# --- FUNGSI AMBIL DATA LOG ---
def load_data():
    conn = init_connection()
    # Pastikan nama table dan nama lajur mengikut skema database Auni
    query = "SELECT * FROM access_logs ORDER BY id DESC;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- TAJUK DASHBOARD ---
st.title("🔑 Smart Door Access System")
st.caption("Real-Time Access Control & Monitoring Dashboard")

try:
    df = load_data()

    # --- PENUKARAN MASA KE WAKTU MALAYSIA (UTC+8) ---
    # Ganti 'created_at' dengan nama lajur tarikh/masa sebenar dalam DB Auni (cth: 'timestamp' atau 'Date & Time')
    time_column = None
    for col in ['created_at', 'timestamp', 'date_time', 'Date & Time']:
        if col in df.columns:
            time_column = col
            break

    if time_column:
        df[time_column] = pd.to_datetime(df[time_column]) + pd.Timedelta(hours=8)
        df[time_column] = df[time_column].dt.strftime('%Y-%m-%d %H:%M:%S')

    # --- RINGKASAN METRICS (TOTAL, GRANTED, DENIED) ---
    col1, col2, col3 = st.columns(3)
    
    total_scans = len(df)
    # Sesuaikan status string mengikut nilai dalam DB Auni (cth: 'SUCCESS' / 'GRANTED')
    granted = len(df[df['status'].isin(['SUCCESS', 'GRANTED'])]) if 'status' in df.columns else 0
    denied = len(df[df['status'].isin(['FAILED', 'DENIED'])]) if 'status' in df.columns else 0

    col1.metric("📊 Total Scans", total_scans)
    col2.metric("✅ Access Granted", granted)
    col3.metric("❌ Access Denied", denied)

    st.markdown("---")

    # --- PAPARAN JADUAL RECENT ACCESS LOGS ---
    st.subheader("📋 Recent Access Logs")
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Gagal menyambung ke pangkalan data: {e}")
