# List all available commands
default:
    @just --list

# Build Docker images
build:
    docker compose build

# Start all services
up:
    docker compose up -d

# Stop all services
down:
    docker compose down

# Restart all services
restart:
    just down
    just up

# Show last 250 lines of logs
logs:
    docker compose logs --tail=250

# Stop services and remove volumes/images
clean:
    docker compose down -v --rmi local
