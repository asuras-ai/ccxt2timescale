FROM python:3.11-slim

# Install the necessary system packages
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install nano editor
RUN apt update -y && apt install nano

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "ccxt_load.py"]
