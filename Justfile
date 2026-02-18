# List all available commands
default:
    @just --list

_ports_env_file := if path_exists("envs/.env.ports") { "--env-file envs/.env.ports" } else { "" }

# Build Docker images
build:
    docker compose {{_ports_env_file}} build

# Start all services
up:
    docker compose {{_ports_env_file}} up -d

# Stop all services
down:
    docker compose {{_ports_env_file}} down

# Restart all services
restart:
    just down
    just up

# Show last 250 lines of logs
logs:
    docker compose {{_ports_env_file}} logs --tail=250

# Stop services and remove volumes/images
clean:
    docker compose {{_ports_env_file}} down -v --rmi local
