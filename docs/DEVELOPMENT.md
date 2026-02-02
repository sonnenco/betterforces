# Development Guide

This guide covers setting up BetterForces for local development.

## Requirements

- Python 3.13+ with `uv`
- Node.js 20+ with `npm`
- Redis
- Or just Docker

## Quick Start

### Docker (Recommended)

```bash
git clone https://github.com/deyna256/betterforces.git
cd betterforces
cp .env.example .env
just build
just up
```

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/schema/swagger

### Local Development

```bash
# Install dependencies
just install

# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Backend
cd backend && just dev

# Frontend (in another terminal)
cd frontend && just dev
```

## Project Commands

All commands use [Just](https://github.com/casey/just) (a modern command runner).

To see all available commands with descriptions, run `just` in any directory:

```bash
# Root level (Docker commands)
just

# Backend commands
cd backend && just

# Frontend commands
cd frontend && just
```

### Most Used Commands

**Root level (Docker):**
```bash
just build     # Build Docker images
just up        # Start all services
just down      # Stop services
just logs      # View logs
```

**Backend (from `backend/` directory):**
```bash
just dev       # Run development server with hot reload
just test      # Run all tests
just check     # Run linting + type checking
```

**Frontend (from `frontend/` directory):**
```bash
just dev       # Run development server
just build     # Build for production
just typecheck # TypeScript type checking
```

## Testing

### Backend Tests

Run tests from the `backend/` directory:

```bash
cd backend
just test              # Run all tests
just test-coverage     # Run with coverage report
```

**Test Structure:**
- `backend/tests/unit/codeforces_client/` - CodeforcesClient tests (39 tests)
- `backend/tests/unit/abandoned_problems_service/` - Service tests (17 tests)
- `backend/tests/conftest.py` - Pytest fixtures

**Current coverage:** 91% (56 tests passing)

### Frontend Tests

Frontend uses TypeScript strict mode and ESLint for validation:

```bash
cd frontend
just typecheck    # TypeScript type checking
just lint         # ESLint
```

## Configuration

Configuration is managed through environment variables in `.env` file:

```bash
# Redis
REDIS_URL=redis://localhost:6379/0

# Codeforces API
CODEFORCES_API_BASE=https://codeforces.com/api

# Cache settings
CACHE_FRESH_TTL=14400    # Fresh cache TTL (4 hours)
CACHE_STALE_TTL=86400    # Stale cache TTL (24 hours)

# Worker settings
WORKER_RATE_LIMIT=5      # Max requests per second to Codeforces API
WORKER_QUEUE_KEY=fetch_queue

# Task settings
TASK_STATUS_TTL=300      # Task status TTL (5 minutes)
PENDING_TASK_TTL=60      # Pending task lock TTL (60 seconds)

# Rate limiting (API endpoints)
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=hour

# CORS
CORS_ALLOWED_ORIGINS=["http://localhost:3000"]

# Development
DEV_MODE=true            # Enable uvicorn reload
```

## Development Tools

### Backend

- **Package Manager**: [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- **Linter/Formatter**: [Ruff](https://docs.astral.sh/ruff/) - Fast Python linter and formatter
- **Type Checker**: [ty](https://github.com/linka-cloud/ty) - Fast type checker
- **Testing**: [pytest](https://docs.pytest.org/) with pytest-asyncio
- **Config Files**: `pyproject.toml`, `ruff.toml`, `ty.toml`, `pytest.ini`

### Frontend

- **Build Tool**: [Vite](https://vitejs.dev/) - Fast frontend build tool
- **Linter**: [ESLint](https://eslint.org/) with React hooks rules
- **Type Checker**: TypeScript strict mode
- **Config Files**: `tsconfig.json`, `vite.config.ts`, `.eslintrc.cjs`

## Monitoring & Debugging

### Check Docker Services

```bash
docker-compose ps         # Service status
docker-compose logs -f backend
docker-compose logs -f worker
docker-compose logs -f frontend
```

### Redis Monitoring

```bash
# Connect to Redis CLI
docker-compose exec redis redis-cli

# View all keys
KEYS "*"

# Check queue length
LLEN fetch_queue

# View specific key
GET submissions:tourist

# Monitor commands in real-time
MONITOR

# Memory usage
INFO memory

# Flush database (careful!)
FLUSHDB
```

### Worker Performance

```bash
# View worker logs
docker-compose logs -f worker

# Count processed tasks
docker-compose logs worker | grep "completed" | wc -l

# Check rate limiting
docker-compose logs worker | grep "rate"
```

### Backend Health

```bash
# Health check
curl http://localhost:8000/schema/openapi.json

# Test endpoint
curl http://localhost:8000/api/difficulty-distribution/tourist

# Check task status
curl http://localhost:8000/api/tasks/{task_id}
```

## Testing Async Processing

### Clear Redis Cache

```bash
docker-compose exec redis redis-cli FLUSHDB
```

### Test Deduplication

Make 3 concurrent requests and verify they return the same task_id:

```bash
curl http://localhost:8000/api/difficulty-distribution/newuser & \
curl http://localhost:8000/api/difficulty-distribution/newuser & \
curl http://localhost:8000/api/difficulty-distribution/newuser
```

### Test Rate Limiting

Enqueue 20 tasks and verify max 5 req/sec in worker logs:

```bash
for i in {1..20}; do
  curl http://localhost:8000/api/difficulty-distribution/user$i &
done
docker-compose logs -f worker
```

### Monitor Queue

```bash
# Check queue size
docker-compose exec redis redis-cli LLEN fetch_queue

# View queue items (without removing)
docker-compose exec redis redis-cli LRANGE fetch_queue 0 -1
```

## Common Issues

### Port Already in Use

```bash
# Kill process using port 3000
lsof -ti:3000 | xargs kill -9

# Or use different ports in docker-compose.yml
```

### Redis Connection Refused

```bash
# Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Or check if Redis container is running
docker-compose ps redis
```

### Worker Not Processing Tasks

```bash
# Check worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker

# Check Redis queue
docker-compose exec redis redis-cli LLEN fetch_queue
```

### Backend Hot Reload Not Working

Ensure `DEV_MODE=true` in `.env` file.

## Project Structure

See [Architecture Documentation](ARCHITECTURE.md) for detailed information about:
- Backend Clean Architecture layers
- Frontend component structure
- Data flow patterns
- File organization

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on:
- Branch naming conventions
- Pull request workflow
- CI requirements
- Code review process
