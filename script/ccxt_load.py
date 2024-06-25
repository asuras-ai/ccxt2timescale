import ccxt
import psycopg2
import pandas as pd
import time
from datetime import datetime, timezone
import json
import os

# Configuration
database_url = os.getenv('DATABASE_URL')
CONFIG_FILE = 'config.json'

def connect_db():
    conn = psycopg2.connect(database_url)
    return conn

def create_table(conn, exchange, symbol, timeframe):
    #table_name = f'ohlcv_{symbol.replace("/", "_").lower()}_{timeframe}'
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
    with conn.cursor() as cursor:
        cursor.execute(create_table_query)
    conn.commit()

def get_latest_timestamp(conn, exchange, symbol, timeframe):
    table_name = f'{exchange}_{symbol}_{timeframe}'
    query = f'SELECT MAX(timestamp) FROM {table_name};'
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchone()
    if result[0]:
        return int(result[0].timestamp() * 1000)  # Convert to milliseconds
    return None

def fetch_historical_data(exchange, symbol, timeframe, since):
    #since =  473385600000 # Unix timestamp for 1984-01-01 00:00:00 alternative: exchange.parse8601('2017-01-01T00:00:00Z')
    all_data = []
    while True:
        try:
            data = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=500)
        except Exception as e:
            print(f"Error fetching data: {e}")
            break
        if not data:
            break
        since = data[-1][0] + 1
        all_data.extend(data)
        #print('increment loaded ' + str(since))
        time.sleep(3)
    print('load finished: ' + str(exchange) + ' ' + str(symbol) + ' ' + str(timeframe))
    return all_data

def insert_ohlcv_data(conn, data, exchange, symbol, timeframe):
    table_name = f'{exchange}_{symbol}_{timeframe}'
    with conn.cursor() as cursor:
        for entry in data:
            #timestamp = datetime.utcfromtimestamp(entry[0] / 1000).isoformat()
            timestamp = datetime.fromtimestamp(entry[0] / 1000, tz=timezone.utc).isoformat()
            cursor.execute(
                f'INSERT INTO {table_name} (timestamp, open, high, low, close, volume) VALUES (%s, %s, %s, %s, %s, %s) '
                'ON CONFLICT (timestamp) DO NOTHING',
                (timestamp, entry[1], entry[2], entry[3], entry[4], entry[5])
            )
    conn.commit()

def main():
    with open(CONFIG_FILE) as f:
        config = json.load(f)

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

if __name__ == '__main__':
    main()
