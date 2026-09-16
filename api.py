import os
from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Tetapan Database Aiven Cloud
DB_CONFIG = {
    'host': 'mysql-3727e8f3-auniafrinaa06-9aec.a.aivencloud.com',
    'port': 10110,
    'user': 'avnadmin',
    'password': 'AVNS_y1pg9gwZWmf1339ju2q',
    'database': 'defaultdb'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# =========================================================
# 1. API UNTUK DAFTAR USER BAHARU (DARI ESP32 MOD ENROLL)
# =========================================================
@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        uid_card = request.form.get('uid_card')
        username = request.form.get('username')
        user_type = request.form.get('user_type', 'RFID')  # Contoh: RFID atau FINGERPRINT

        if not uid_card or not username:
            return "MISSING_PARAMS", 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Simpan atau kemas kini jika UID sudah sedia ada
        query = """
            INSERT INTO registered_users (uid_card, username, user_type) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE username = %s, user_type = %s
        """
        cursor.execute(query, (uid_card, username, user_type, username, user_type))
        conn.commit()
        
        cursor.close()
        conn.close()
        return "REGISTER_SUCCESS", 200

    except Exception as e:
        return f"ERROR: {str(e)}", 500

# =========================================================
# 2. API UNTUK SEMAK STATUS & LOG AKSES (LOGIK PENTING)
# =========================================================
@app.route('/api/log', methods=['POST'])
def insert_log():
    try:
        uid_card = request.form.get('uid_card')

        if not uid_card:
            return "MISSING_PARAMS", 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 🔍 SEMAK SAMA ADA UID MASIH WUJUD DALAM REGISTERED_USERS
        check_query = "SELECT username FROM registered_users WHERE uid_card = %s"
        cursor.execute(check_query, (uid_card,))
        user_record = cursor.fetchone()

        if user_record:
            # Jika user wujud (belum dipadam dari Streamlit)
            status = "SUCCESS"
            username = user_record['username']
        else:
            # Jika user TIADA / TELAH DIPADAM dari Streamlit
            status = "FAILED"
            username = "UNKNOWN / DELETED"

        # 📝 REKOD KAN HASIL SEMAKAN KE DALAM ACCESS_LOG
        log_query = "INSERT INTO access_log (uid_card, username, status) VALUES (%s, %s, %s)"
        cursor.execute(log_query, (uid_card, username, status))
        conn.commit()

        cursor.close()
        conn.close()

        # Pulangkan status kepada ESP32
        return jsonify({
            "status": status,
            "username": username
        }), 200

    except Exception as e:
        return f"ERROR: {str(e)}", 500

# 3. Main route untuk semak status API
@app.route('/')
def home():
    return "Smart Door Access API Online!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
