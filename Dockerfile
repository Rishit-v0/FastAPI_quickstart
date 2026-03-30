# FROM sets the base image — the starting point for your container
# python:3.13-slim = official Python 3.13 image, slim variant
# slim strips out dev tools, docs, and test files — ~150MB instead of ~900MB
# Always use a specific version tag (3.13) not 'latest'
# 'latest' breaks builds when Python releases a new version
# Same base image as Django for consistency
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# WORKDIR sets the working directory inside the container
# All subsequent commands (COPY, RUN, CMD) happen relative to this path
# If this directory doesn't exist, Docker creates it automatically
# /app is the convention — not a hard rule, just widely used
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


# COPY copies files FROM your local machine INTO the container image
# First argument = source (on your machine)
# Second argument = destination (inside the container)
# We copy requirements.txt first, BEFORE copying the rest of the code
# Why? Docker caches each layer (each instruction = one layer)
# If you copy code first then requirements, every code change busts the cache
# and forces a full pip install — which takes minutes
# Copying requirements first means pip only re-runs when requirements.txt changes
COPY requirements.txt .

# RUN executes a shell command during the IMAGE BUILD phase
# This runs once when you build the image, not every time the container starts
# --no-cache-dir tells pip not to store downloaded packages inside the image
# This saves ~50MB from the final image size — no point caching inside a container
# --upgrade pip is good practice — older pip versions have known bugs
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt


# Now copy the rest of your application code into the container
# The . . means: copy everything in current local directory → /app in container
# We do this AFTER pip install to use Docker's layer caching correctly
COPY . .

# FastAPI runs on 8000 by default too
# EXPOSE documents which port the container listens on
# This is documentation only — it does NOT actually publish the port
# You actually publish ports in docker-compose.yml or docker run -p
# FastAPI + uvicorn defaults to port 8000
# We'll map it to 8001 on the host in docker-compose.yml
EXPOSE 8000

# CMD defines the command that runs when the container starts
# This is different from RUN — RUN is build time, CMD is runtime
# Use JSON array format (["cmd", "arg1"]) not string format ("cmd arg1")
# String format invokes a shell which adds overhead and causes signal handling issues
# uvicorn = ASGI server for FastAPI (like gunicorn for Django)
# app.main:app = find the 'app' object in app/main.py
# --host 0.0.0.0 = listen on all network interfaces inside container
#   Without this it only listens on localhost INSIDE the container
#   which means traffic from outside can't reach it
# --port 8000 = port inside the container
# No --reload here — that's for development only, not Docker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]