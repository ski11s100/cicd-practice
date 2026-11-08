FROM python:3.12-slim

# Привязывает образ в реестре GHCR к репозиторию (права доступа берутся из репозитория).
LABEL org.opencontainers.image.source=https://github.com/ski11s100/cicd-practice

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY migrations ./migrations

# Версию передаёт пайплайн: docker build --build-arg APP_VERSION=sha-1a2b3c4
ARG APP_VERSION=local
ENV APP_VERSION=${APP_VERSION}

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
