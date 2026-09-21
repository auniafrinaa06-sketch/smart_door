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

@app.route('/api/log', methods=['POST'])
def insert_log():
    try:
        # Terima data dari form submission mahupun JSON submission
        if request.is_json:
            data = request.get_json()
            uid_card = data.get('uid_card', 'UNKNOWN_UID')
            status = data.get('status', 'FAILED')
            username = data.get('username', 'Pelawat')
        else:
            uid_card = request.form.get('uid_card', 'UNKNOWN_UID')
            status = request.form.get('status', 'FAILED')
            username = request.form.get('username', 'Pelawat')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert terus log ke MySQL
        log_query = "INSERT INTO access_log (uid_card, username, status) VALUES (%s, %s, %s)"
        cursor.execute(log_query, (uid_card, username, status))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "SUCCESS",
            "message": "Log berjaya disimpan!"
        }), 200

    except Exception as e:
        print("Error:", str(e))
        return f"ERROR: {str(e)}", 500

@app.route('/')
def home():
    return "Smart Door Access API Online!"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
