# AURA Deployment & Operations Guide

## 1. Deployment Topology & Overview

AURA supports three primary deployment configurations:
1. **Local Development**: FastAPI Uvicorn server + Vite dev server + local SQLite/JSON vectors.
2. **Containerized Production (Docker Compose)**: Multi-container setup with Backend, Frontend Nginx reverse proxy, PostgreSQL 16 with `pgvector`, and Redis.
3. **Enterprise Cloud (Kubernetes / Azure / AWS)**: Decoupled microservices with managed Postgres/pgvector, object storage (S3/Azure Blob), and ingress controllers.

---

## 2. Docker Compose Deployment

The root `docker-compose.yml` provides a production-grade multi-service stack:

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    container_name: aura-postgres
    environment:
      POSTGRES_DB: aura_db
      POSTGRES_USER: aura_user
      POSTGRES_PASSWORD: aura_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aura_user -d aura_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: aura-backend
    environment:
      DATABASE_URL: postgresql+asyncpg://aura_user:aura_secure_password@postgres:5432/aura_db
      JWT_SECRET: ${JWT_SECRET:-super-secret-jwt-key-replace-in-production}
      ENVIRONMENT: production
      CORS_ORIGINS: http://localhost,http://localhost:80,http://localhost:3000
    depends_on:
      postgres:
        condition: service_healthy
    ports:
      - "8000:8000"
    volumes:
      - storage_data:/app/storage

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: aura-frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
  storage_data:
```

### Launching with Docker Compose:
```bash
# 1. Clone repository
git clone https://github.com/enterprise/aura-platform.git
cd aura-platform

# 2. Configure environment
cp .env.example .env
# Edit .env with your production secrets

# 3. Build and launch all services
docker compose up -d --build

# 4. Verify running services
docker compose ps
```

The application is immediately accessible at `http://localhost` (Frontend) and `http://localhost:8000/docs` (Backend OpenAPI).

---

## 3. Environment Variables Reference

| Variable Name | Required | Default Value | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | `sqlite+aiosqlite:///./aura.db` | Connection string for database (SQLite or PostgreSQL). |
| `JWT_SECRET` | Yes | `change-me-secret-key-32-chars-min` | Cryptographic secret for signing JWT access tokens. |
| `JWT_ALGORITHM` | No | `HS256` | Token signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Lifespan of access tokens in minutes. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `7` | Lifespan of refresh tokens in days. |
| `OPENAI_API_KEY` | Optional | `None` | Optional API key for OpenAI GPT-4o / embeddings. |
| `GEMINI_API_KEY` | Optional | `None` | Optional API key for Google Gemini models. |
| `VECTOR_STORE_TYPE` | No | `sqlite` | Vector storage backend: `sqlite` or `pgvector`. |
| `STORAGE_DIR` | No | `./storage` | Directory path for physical document files. |
| `ENVIRONMENT` | No | `development` | Deployment environment: `development`, `staging`, `production`. |
| `CORS_ORIGINS` | No | `*` | Comma-separated list of allowed origins. |

---

## 4. Multi-Stage Dockerfile Architecture

### Backend (`Dockerfile.backend`)
```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY backend/app /app/app
COPY storage /app/storage
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (`Dockerfile.frontend`)
```dockerfile
FROM node:20-alpine as builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY infrastructure/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 5. Cloud Deployment: Azure Container Apps / AWS ECS

### Deploying to Azure Container Apps:
```bash
# Login to Azure
az login

# Create resource group
az group create --name aura-rg --location eastus

# Deploy PostgreSQL flexible server with pgvector
az postgres flexible-server create --resource-group aura-rg --name aura-pg --version 16

# Build and push images to Azure Container Registry (ACR)
az acr build --registry auraacr --image aura-backend:latest -f Dockerfile.backend .
az acr build --registry auraacr --image aura-frontend:latest -f Dockerfile.frontend .

# Deploy Container App
az containerapp create \
  --name aura-backend \
  --resource-group aura-rg \
  --image auraacr.azurecr.io/aura-backend:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars DATABASE_URL=secretref:db-conn-string JWT_SECRET=secretref:jwt-secret
```

---

## 6. Backup, Recovery & Maintenance

1. **Database Backups**:
   - For PostgreSQL: `pg_dump -U aura_user -d aura_db -F c -b -v -f aura_backup.dump`
   - For SQLite: Safely copy `aura.db` while no writes are active or use SQLite `.backup` command.
2. **File Storage Backups**:
   - Periodic sync of the `storage/` directory to object storage (e.g. S3 / Azure Blob).
3. **Log Rotation**:
   - Docker container logs managed via `json-file` log driver with `max-size: "50m"` and `max-file: "5"`.
