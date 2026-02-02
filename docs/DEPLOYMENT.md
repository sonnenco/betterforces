# Deployment Guide

This guide covers deploying BetterForces to production.

## Prerequisites

- Docker and Docker Compose installed
- Domain name (optional, for HTTPS)
- SSL certificates (if using HTTPS)

## Environment Variables

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

### Required Variables

```bash
# Redis
REDIS_URL=redis://redis:6379/0

# Codeforces API
CODEFORCES_API_BASE=https://codeforces.com/api

# Cache settings
CACHE_FRESH_TTL=14400    # 4 hours
CACHE_STALE_TTL=86400    # 24 hours

# Worker settings
WORKER_RATE_LIMIT=5      # Max 5 req/sec to Codeforces API
WORKER_QUEUE_KEY=fetch_queue

# Task settings
TASK_STATUS_TTL=300      # 5 minutes
PENDING_TASK_TTL=60      # 60 seconds

# Rate limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=hour

# CORS (adjust for your domain)
CORS_ALLOWED_ORIGINS=["https://yourdomain.com"]

# Development (set to false in production)
DEV_MODE=false
```

## Docker Deployment

### Build and Start Services

```bash
# Build all images
docker-compose build

# Start in detached mode
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Service Ports

- Frontend: 3000
- Backend API: 8000
- Redis: 6379 (internal only)

### Health Checks

```bash
# Backend health
curl http://localhost:8000/schema/openapi.json

# Frontend
curl http://localhost:3000

# Redis
docker-compose exec redis redis-cli PING
```

## Production Recommendations

### 1. Use Reverse Proxy

Use Nginx or Caddy as a reverse proxy:

```nginx
server {
    listen 80;
    server_name betterforces.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name betterforces.example.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeouts for long-running requests
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

### 2. Enable Redis Persistence

Modify `docker-compose.yml` to enable Redis persistence:

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes
  volumes:
    - redis_data:/data
  restart: unless-stopped
```

### 3. Set Resource Limits

Add resource limits to prevent OOM issues:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M

  worker:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M
```

### 4. Configure Logging

Use logging driver for better log management:

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  worker:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 5. Enable Auto-Restart

Ensure services restart on failure:

```yaml
services:
  backend:
    restart: unless-stopped

  worker:
    restart: unless-stopped

  frontend:
    restart: unless-stopped

  redis:
    restart: unless-stopped
```

## Monitoring

### Docker Stats

```bash
# View resource usage
docker stats

# View logs
docker-compose logs -f backend
docker-compose logs -f worker
```

### Redis Monitoring

```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Check memory usage
INFO memory

# Check connected clients
CLIENT LIST

# Monitor commands
MONITOR
```

### Application Metrics

Monitor these key metrics:

1. **API Response Times**: Check backend logs for slow requests
2. **Queue Length**: Monitor `fetch_queue` length in Redis
3. **Worker Throughput**: Count processed tasks per minute
4. **Cache Hit Rate**: Track cache hits vs misses
5. **Error Rate**: Monitor 4xx/5xx responses

### Health Check Endpoints

```bash
# Backend health
curl https://yourdomain.com/api/schema/openapi.json

# Check specific endpoint
curl https://yourdomain.com/api/difficulty-distribution/tourist
```

## Backup & Recovery

### Backup Redis Data

```bash
# Create backup
docker-compose exec redis redis-cli SAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb ./backup-$(date +%Y%m%d).rdb

# Or use automated backup script
docker-compose exec redis redis-cli BGSAVE
```

### Restore Redis Data

```bash
# Stop Redis
docker-compose stop redis

# Copy backup file
docker cp ./backup.rdb $(docker-compose ps -q redis):/data/dump.rdb

# Start Redis
docker-compose start redis
```

## Scaling

### Horizontal Scaling

Run multiple worker instances:

```yaml
services:
  worker:
    deploy:
      replicas: 3
```

Or manually:

```bash
docker-compose up -d --scale worker=3
```

### Vertical Scaling

Increase resource limits in `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
```

## Security

### 1. Environment Variables

Never commit `.env` file to version control. Use secret management:

```bash
# Add to .gitignore
echo ".env" >> .gitignore
```

### 2. CORS Configuration

Restrict CORS to your domain only:

```bash
CORS_ALLOWED_ORIGINS=["https://yourdomain.com"]
```

### 3. Rate Limiting

Adjust rate limits based on your needs:

```bash
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=hour
```

### 4. Redis Security

Add Redis password:

```yaml
redis:
  command: redis-server --requirepass yourpassword
```

Update `.env`:

```bash
REDIS_URL=redis://:yourpassword@redis:6379/0
```

### 5. Network Isolation

Use Docker networks to isolate services:

```yaml
networks:
  frontend-network:
  backend-network:

services:
  frontend:
    networks:
      - frontend-network

  backend:
    networks:
      - frontend-network
      - backend-network

  redis:
    networks:
      - backend-network
```

## Troubleshooting

### High Memory Usage

```bash
# Check Redis memory
docker-compose exec redis redis-cli INFO memory

# Reduce cache TTL
CACHE_STALE_TTL=43200  # 12 hours instead of 24
```

### Slow Response Times

```bash
# Check queue length
docker-compose exec redis redis-cli LLEN fetch_queue

# Scale workers
docker-compose up -d --scale worker=3

# Check backend logs
docker-compose logs backend | grep "ERROR"
```

### Worker Not Processing Tasks

```bash
# Check worker status
docker-compose ps worker

# View worker logs
docker-compose logs -f worker

# Restart worker
docker-compose restart worker
```

### Redis Connection Issues

```bash
# Check Redis status
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli PING

# Check logs
docker-compose logs redis
```

## Updates & Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build

# Restart services (no downtime for stateless services)
docker-compose up -d

# Check status
docker-compose ps
```

### Database Migrations

Currently, the application uses Redis (in-memory cache), so no migrations are needed. If adding a database in the future:

1. Stop services
2. Run migration scripts
3. Restart services

### Clean Up

```bash
# Remove old images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove all stopped containers
docker container prune
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/betterforces
            git pull origin main
            docker-compose build
            docker-compose up -d
```

## Performance Tuning

### Redis Configuration

Optimize Redis for your workload:

```bash
# Max memory policy
redis-cli CONFIG SET maxmemory 256mb
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Persistence settings
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

### Worker Configuration

Adjust rate limits based on your needs:

```bash
# Increase rate limit (be careful with Codeforces API limits)
WORKER_RATE_LIMIT=10

# Increase cache TTL to reduce API calls
CACHE_FRESH_TTL=28800  # 8 hours
CACHE_STALE_TTL=172800 # 48 hours
```

## Support

For deployment issues:

1. Check logs: `docker-compose logs`
2. Review [Development Guide](DEVELOPMENT.md) for debugging
3. Open an issue on GitHub
