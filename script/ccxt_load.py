import ccxt
import psycopg2
import pandas as pd
import time
from datetime import datetime, timezone
import json
import os
import logging

# Configuration
DATABASE = {
    'host': os.getenv('DATABASE_HOST'),
    'dbname': os.getenv('DATABASE_NAME'),
    'user': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD')
}
CONFIG_FILE = 'config.json'

# Logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

def connect_db():
    try:
        conn = psycopg2.connect(**DATABASE)
        logging.info("Database connection established.")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to the database: {e}")
        raise

def create_table(conn, exchange, symbol, timeframe):
    table_name = f'{exchange}_{symbol}_{timeframe}'
    create_table_query = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        timestamp TIMESTAMPTZ PRIMARY KEY,
        open DOUBLE PRECISION,
        high DOUBLE PRECISION,
        low DOUBLE PRECISION,
        close DOUBLE PRECISION,
        volume DOUBLE PRECISION
    );
    SELECT create_hypertable('{table_name}', 'timestamp', if_not_exists => TRUE);
    '''
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
        conn.commit()
        logging.info(f"Table {table_name} created or already exists.")
    except Exception as e:
        logging.error(f"Failed to create table {table_name}: {e}")
        raise

def get_latest_timestamp(conn, exchange, symbol, timeframe):
    table_name = f'{exchange}_{symbol}_{timeframe}'
    query = f'SELECT MAX(timestamp) FROM {table_name};'
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
        if result[0]:
            return int(result[0].timestamp() * 1000)  # Convert to milliseconds
        return None
    except Exception as e:
        logging.error(f"Failed to get latest timestamp from {table_name}: {e}")
        raise

def fetch_historical_data(exchange, symbol, timeframe, since):
    all_data = []
    while True:
        try:
            data = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=500)
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            break
        if not data:
            break
        since = data[-1][0] + 1
        all_data.extend(data)
        time.sleep(3)
    return all_data

def insert_ohlcv_data(conn, data, exchange, symbol, timeframe):
    table_name = f'{exchange}_{symbol}_{timeframe}'
    try:
        with conn.cursor() as cursor:
            for entry in data:
                timestamp = datetime.fromtimestamp(entry[0] / 1000, tz=timezone.utc).isoformat()
                cursor.execute(
                    f'INSERT INTO {table_name} (timestamp, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s) '
                    'ON CONFLICT (timestamp) DO NOTHING',
                    (timestamp, entry[1], entry[2], entry[3], entry[4], entry[5])
                )
        conn.commit()
        logging.info(f"Inserted {len(data)} rows into {table_name}.")
    except Exception as e:
        logging.error(f"Failed to insert data into {table_name}: {e}")
        raise

def main():
    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        logging.info("Config file loaded successfully.")
        
        conn = connect_db()
        for conf in config:
            exchange = getattr(ccxt, conf['exchange'])()
            symbol = conf['symbol']
            timeframe = conf['timeframe']
            create_table(conn, exchange, symbol, timeframe)
            since = get_latest_timestamp(conn, exchange, symbol, timeframe)
            if since is None:
                since = 473385600000 # Unix timestamp for 1984-01-01  
            data = fetch_historical_data(exchange, symbol, timeframe, since)
            insert_ohlcv_data(conn, data, exchange, symbol, timeframe)
        conn.close()
        logging.info("Script completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")
        raise

if __name__ == '__main__':
    main()
