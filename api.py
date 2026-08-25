import os
from flask import Flask, request
import mysql.connector

app = Flask(__name__)

# Tetapan Database Aiven Cloud Auni
DB_CONFIG = {
    'host': 'mysql-3727e8f3-auniafrinaa06-9aec.a.aivencloud.com',
    'port': 10110,
    'user': 'avnadmin',
    'password': 'AVNS_y1pg9gwZWmf1339ju2q',
    'database': 'defaultdb'
}

# 1. API Endpoint untuk terima data POST dari ESP32
@app.route('/api/log', methods=['POST'])
def insert_log():
    try:
        uid_card = request.form.get('uid_card')
        status = request.form.get('status')
        username = request.form.get('username')

        # Semak jika parameter lengkap
        if not uid_card or not status:
            return "MISSING_PARAMS", 400

        # Sambung ke database dan masukkan log
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = "INSERT INTO access_log (uid_card, username, status) VALUES (%s, %s, %s)"
        cursor.execute(query, (uid_card, username, status))
        conn.commit()
        cursor.close()
        conn.close()

        return "SUCCESS", 200
    except Exception as e:
        return f"ERROR: {str(e)}", 500

# 2. Main route untuk semak status API
@app.route('/')
def home():
    return "Smart Door Access API Online!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
