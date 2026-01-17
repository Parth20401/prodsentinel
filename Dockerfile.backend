# Base image
FROM python:3.12-slim

# Install system dependencies
# gcc/libpq-dev for building psycopg2/asyncpg if needed (though usually binary wheels are available)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy all requirements first to cache installation
COPY prodsentinel-backend/requirements.txt ./backend-requirements.txt
COPY prodsentinel-pipeline/requirements.txt ./pipeline-requirements.txt
COPY prodsentinel-fake-services/requirements.txt ./fake-requirements.txt

# Install all dependencies into system python (no venv needed for Docker)
RUN uv pip install --system -r backend-requirements.txt && \
    uv pip install --system -r pipeline-requirements.txt && \
    uv pip install --system -r fake-requirements.txt

# Copy source code
COPY prodsentinel-backend/ ./prodsentinel-backend/
COPY prodsentinel-pipeline/ ./prodsentinel-pipeline/
COPY prodsentinel-fake-services/ ./prodsentinel-fake-services/

# Fix Python path so all modules are discoverable
ENV PYTHONPATH="/app/prodsentinel-backend:/app/prodsentinel-pipeline:/app/prodsentinel-fake-services"

# Make the start script executable
RUN chmod +x /app/prodsentinel-backend/start_combined.sh

# Expose the Backend port (only one allowed by Render free tier for public traffic)
EXPOSE 8000

# Start command
CMD ["/app/prodsentinel-backend/start_combined.sh"]
