FROM python:3.9-slim

RUN pip install ccxt psycopg2-binary pandas

COPY fetch_ohlcv.py /usr/src/app/fetch_ohlcv.py
COPY config.json /usr/src/app/config.json

CMD ["python", "/usr/src/app/fetch_ohlcv.py"]
