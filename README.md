# OHLCV Data Collector with TimescaleDB

This project sets up a TimescaleDB to store OHLCV data from various cryptocurrency exchanges using the CCXT library. It fetches historical data for initial load and updates the data when daily using a cron job, all deployed with Docker.

## Features

- Fetch historical OHLCV data from multiple exchanges and symbols.
- Store data in TimescaleDB with hypertable for efficient time-series data handling.
- Daily incremental data fetch using a cron job.
- Dockerized setup for easy deployment.

## Prerequisites

- Docker
- Docker Compose

## Setup

### Step 1: Clone the Repository

```sh
git clone https://github.com/asuras-ai/ccxt2timescale.git
cd ccxt2timescale
```

### Step 2: Configure Database and Symbols

1. **Edit** `config.json` to specify the exchanges, symbols, and timeframes you want to collect data for.
    ```json
    [
        {
            "exchange": "binance",
            "symbol": "BTC/USDT",
            "timeframe": "1d"
        },
        {
            "exchange": "binance",
            "symbol": "ETH/USDT",
            "timeframe": "1h"
        }
    ]
    ```
2. **Edit** Docker-Compose in `docker-compose.yml` to change database parameters.
    ```Docker-Compose
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: password
    POSTGRES_DB: ccxt
    ```
### Step 3: Build and Run Docker Containers

1. **Run Docker Compose:**
    ```sh
    docker-compose up -d
    ```

### Step 4: Initial Data Load
Run the following command to perform the initial data load:
```sh
docker run --rm --network host ohlcv-fetcher
```

### Step 5: Set Up Daily Data Fetch
1. **Create a shell script cronjob.sh:**
    ```sh
    #!/bin/sh
    docker exec -it $(docker ps -qf "ancestor=ohlcv-fetcher") python /usr/src/app/fetch_ohlcv.py
    ```
2. Make the script executable:
    ```sh
    chmod +x cronjob.sh
    ```
3. Add a cron job to run the script daily. Open the crontab editor:
    ```sh
    crontab -e
    ```
    Add the following line to schedule the job at midnight every day:
    ```sh
    0 0 * * * /path/to/your/cronjob.sh
    ```
### Step 6: Access the database for you analysis
Here is an example Python script to access the TimescaleDB database and load OHLCV data for backtesting purposes:
```python
import psycopg2
import pandas as pd

# Database configuration
DATABASE = {
    'host': 'localhost',
    'dbname': 'ohlcv',
    'user': 'postgres',
    'password': 'password'
}

def connect_db():
    """Establish a connection to the TimescaleDB."""
    conn = psycopg2.connect(**DATABASE)
    return conn

def fetch_ohlcv_data(conn, symbol, timeframe, start_date=None, end_date=None):
    """Fetch OHLCV data from the database."""
    table_name = f'ohlcv_{symbol.replace("/", "_").lower()}_{timeframe}'
    query = f'SELECT * FROM {table_name} WHERE true'
    
    if start_date:
        query += f" AND timestamp >= '{start_date}'"
    if end_date:
        query += f" AND timestamp <= '{end_date}'"
    
    query += ' ORDER BY timestamp ASC;'
    
    df = pd.read_sql(query, conn)
    return df

def main():
    # Example parameters
    symbol = 'BTC/USDT'
    timeframe = '1d'
    start_date = '2020-01-01'
    end_date = '2023-01-01'
    
    # Connect to the database
    conn = connect_db()
    
    # Fetch OHLCV data
    df = fetch_ohlcv_data(conn, symbol, timeframe, start_date, end_date)
    
    # Close the database connection
    conn.close()
    
    # Print the fetched data
    print(df)

if __name__ == '__main__':
    main()

```
## Files and Directories
- `/script/ccxt_load.py`: Python script to load the data from CCXT and store it in the database

- `/script/config.json`: Configuration file for specifying exchanges, symbols, and timeframes.
- `/script/Dockerfile`: Dockerfile for the OHLCV fetcher.
- `/script/requirements.txt`: Needed Python libraries to install with PIP
- `cronjob.sh`: Cron job template for automatic loads
- `docker-compose.yml`: Docker Compose configuration for TimescaleDB.



## Technologies
- Docker
- Docker Compose
- Python
- CCXT
- TimeScaleDB

## Contributing
Feel free to submit issues, fork the repository, and send pull requests!

## License
This project is licensed under the MIT License.
