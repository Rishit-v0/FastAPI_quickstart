# Same base image as Django for consistency
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# FastAPI needs gcc for some packages too
# curl is added because FastAPI healthchecks often use curl
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

# FastAPI runs on 8000 by default too
# We'll map it to 8001 on the host in docker-compose.yml
EXPOSE 8000

# uvicorn = ASGI server for FastAPI (like gunicorn for Django)
# app.main:app = find the 'app' object in app/main.py
# --host 0.0.0.0 = listen on all network interfaces inside container
#   Without this it only listens on localhost INSIDE the container
#   which means traffic from outside can't reach it
# --port 8000 = port inside the container
# No --reload here — that's for development only, not Docker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]