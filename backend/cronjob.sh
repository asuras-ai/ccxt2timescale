#!/bin/sh
docker exec -it $(docker ps -qf "name=backend") python /app/fetch_ohlcv.py
