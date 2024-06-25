from flask import Flask, request, jsonify
import json
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

DATABASE = {
    'host': 'timescaledb',
    'dbname': 'ohlcv',
    'user': 'postgres',
    'password': os.getenv('password')
}
CONFIG_FILE = 'config.json'

def connect_db():
    conn = psycopg2.connect(**DATABASE)
    return conn

@app.route('/api/configs', methods=['GET'])
def get_configs():
    with open(CONFIG_FILE) as f:
        configs = json.load(f)

    conn = connect_db()
    for config in configs:
        table_name = f'ohlcv_{config["symbol"].replace("/", "_").lower()}_{config["timeframe"]}'
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT MIN(timestamp), MAX(timestamp) FROM {table_name};')
            result = cursor.fetchone()
            config['first_timestamp'] = result[0]
            config['last_timestamp'] = result[1]
    conn.close()
    return jsonify(configs)

@app.route('/api/configs', methods=['POST'])
def add_config():
    new_config = request.json
    with open(CONFIG_FILE, 'r+') as f:
        configs = json.load(f)
        configs.append(new_config)
        f.seek(0)
        json.dump(configs, f, indent=4)
    return jsonify(new_config), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
