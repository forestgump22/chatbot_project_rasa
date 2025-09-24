FROM python:3.10.5

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# ⚡ CRÍTICO: Usar el puerto de Render, no uno fijo
CMD ["sh", "-c", "rasa run --enable-api --cors \"*\" --port $PORT"]