# FastAPI API Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY scripts ./scripts

# Make startup script executable
RUN chmod +x scripts/startup.sh

# Use PORT environment variable from Render
ENV PORT=10000
EXPOSE ${PORT}

# Use unified startup script with environment-based configuration
CMD ["./scripts/startup.sh"]
