FROM python:3.11-slim

WORKDIR /app

# Install required system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    libffi-dev \
    libssl-dev \
    curl \
    netcat-traditional \
    supervisor \
    ca-certificates \
    git \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Upgrade pip/setuptools/wheel
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies (including Jazzmin)
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy project files
COPY . .

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000 8001

CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
