FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev tesseract-ocr tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    fastapi "uvicorn[standard]" sqlalchemy aiosqlite \
    "python-jose[cryptography]" "passlib[bcrypt]" "bcrypt==4.0.1" \
    pydantic pydantic-settings python-multipart \
    httpx aiohttp structlog cuid python-dateutil pytz \
    email-validator "crewai>=0.86.0" langchain langchain-anthropic \
    langchain-google-genai langchain-openai langchain-community \
    anthropic openai google-generativeai \
    duckdb pandas numpy jinja2 nbformat \
    pypdf2 pillow beautifulsoup4 lxml reportlab \
    websockets python-dotenv

# Copy backend app and ai crew module
COPY backend/ ./backend/
COPY ai/ ./ai/

WORKDIR /app/backend

RUN mkdir -p /app/backend/db /app/backend/data /app/backend/exports

ENV PYTHONPATH=/app/backend:/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
