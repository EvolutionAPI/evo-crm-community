#!/usr/bin/env bash
# =============================================================================
# Evo AI Community — Interactive Setup Script
# =============================================================================
# This script sets up the entire Evo AI platform from scratch.
# It checks prerequisites, builds Docker images, seeds the database,
# and starts all services.
#
# Usage:
#   bash setup.sh
# =============================================================================

set -e

# Ensure we're running under bash (required for string slicing in spinner)
if [ -z "$BASH_VERSION" ]; then
  echo "This script requires bash. Please run: bash setup.sh"
  exit 1
fi

# ---------------------------------------------------------------------------
# Colors (with fallback for no-color terminals)
# ---------------------------------------------------------------------------
if [ -t 1 ] && command -v tput > /dev/null 2>&1; then
  GREEN=$(tput setaf 2)
  CYAN=$(tput setaf 6)
  RED=$(tput setaf 1)
  YELLOW=$(tput setaf 3)
  BOLD=$(tput bold)
  RESET=$(tput sgr0)
else
  GREEN="" CYAN="" RED="" YELLOW="" BOLD="" RESET=""
fi

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
info()    { echo "${CYAN}[INFO]${RESET}  $1"; }
success() { echo "${GREEN}[OK]${RESET}    $1"; }
warn()    { echo "${YELLOW}[WARN]${RESET}  $1"; }
fail()    { echo "${RED}[ERROR]${RESET} $1"; exit 1; }

wait_for_service() {
  local msg=$1
  shift
  local max=${1:?max retries required}; shift
  local spin='|/-\'
  local i=0
  local retries=0
  printf "${CYAN}[....]${RESET} %s %s" "$msg" "${spin:0:1}"
  until "$@" > /dev/null 2>&1; do
    retries=$((retries + 1))
    if [ "$retries" -ge "$max" ]; then
      printf "\n"
      fail "$msg — timed out. Check: docker compose logs"
    fi
    i=$(( (i+1) % 4 ))
    printf "\r${CYAN}[....]${RESET} %s %s" "$msg" "${spin:$i:1}"
    sleep 2
  done
  printf "\r${GREEN}[OK]${RESET}    %s   \n" "$msg"
}

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------
echo ""
echo "${GREEN}${BOLD}"
echo "  ╔═══════════════════════════════════════════╗"
echo "  ║         Evo AI Community Setup            ║"
echo "  ║   Open-Source AI-Powered CRM Platform     ║"
echo "  ╚═══════════════════════════════════════════╝"
echo "${RESET}"
echo ""

# ---------------------------------------------------------------------------
# Step 1: Check prerequisites
# ---------------------------------------------------------------------------
info "Checking prerequisites..."

# Git
if command -v git > /dev/null 2>&1; then
  success "Git found: $(git --version)"
else
  fail "Git is not installed. Install it from https://git-scm.com/downloads"
fi

# Docker
if command -v docker > /dev/null 2>&1; then
  success "Docker found: $(docker --version)"
else
  fail "Docker is not installed. Install Docker Desktop from https://www.docker.com/products/docker-desktop/"
fi

# Docker Compose (v2)
if docker compose version > /dev/null 2>&1; then
  success "Docker Compose found: $(docker compose version --short)"
else
  fail "Docker Compose v2 not found. Please update Docker Desktop to the latest version."
fi

# Docker daemon running
if docker info > /dev/null 2>&1; then
  success "Docker daemon is running"
else
  fail "Docker daemon is not running. Please start Docker Desktop and try again."
fi

echo ""

# ---------------------------------------------------------------------------
# Step 2: Initialize submodules
# ---------------------------------------------------------------------------
info "Checking Git submodules..."

needs_init=false
for dir in evo-auth-service-community evo-ai-crm-community evo-ai-frontend-community evo-ai-processor-community evo-ai-core-service-community; do
  if [ ! -f "$dir/Dockerfile" ] && [ ! -f "$dir/docker/Dockerfile" ] && [ ! -f "$dir/package.json" ]; then
    needs_init=true
    break
  fi
done

if [ "$needs_init" = true ]; then
  info "Initializing submodules (this may take a few minutes)..."
  git submodule update --init --recursive
  success "Submodules initialized"
else
  success "Submodules already initialized"
fi

echo ""

# ---------------------------------------------------------------------------
# Step 3: Configure environment
# ---------------------------------------------------------------------------
info "Configuring environment..."

if [ -f .env ]; then
  warn ".env file already exists."
  read -r -p "  Overwrite with defaults? [y/N] " response
  case "$response" in
    [yY][eE][sS]|[yY])
      cp .env.example .env
      success "Overwrote .env with defaults"
      ;;
    *)
      success "Keeping existing .env"
      ;;
  esac
else
  cp .env.example .env
  success "Created .env from .env.example"
fi

echo ""

# ---------------------------------------------------------------------------
# Step 4: Build Docker images
# ---------------------------------------------------------------------------
info "Building Docker images (this takes 5-15 minutes on first run)..."
echo ""

docker compose build

echo ""
success "All images built successfully"
echo ""

# ---------------------------------------------------------------------------
# Step 5: Start infrastructure (Postgres + Redis)
# ---------------------------------------------------------------------------
info "Starting database and cache..."
docker compose up -d postgres redis mailhog

# Read Redis password from .env (fallback to default)
REDIS_PASS=$(grep -E '^REDIS_PASSWORD=' .env 2>/dev/null | cut -d= -f2- || echo "evoai_redis_pass")
REDIS_PASS=${REDIS_PASS:-evoai_redis_pass}

wait_for_service "Waiting for PostgreSQL to be ready..." 30 \
  docker compose exec -T postgres pg_isready -U postgres

wait_for_service "Waiting for Redis to be ready..." 30 \
  docker compose exec -T redis redis-cli --no-auth-warning -a "$REDIS_PASS" ping

echo ""

# ---------------------------------------------------------------------------
# Step 6: Seed Auth service (must be first)
# ---------------------------------------------------------------------------
info "Seeding Auth service (creating default account and user)..."
docker compose run --rm evo-auth bash -c "bundle exec rails db:create db:migrate db:seed"
success "Auth service seeded"

echo ""

# ---------------------------------------------------------------------------
# Step 7: Seed CRM service
# ---------------------------------------------------------------------------
info "Seeding CRM service (creating default inbox)..."
docker compose run --rm evo-crm bash -c "bundle exec rails db:create db:migrate db:seed"
success "CRM service seeded"

echo ""

# ---------------------------------------------------------------------------
# Step 8: Start all services
# ---------------------------------------------------------------------------
info "Starting all services..."
docker compose up -d

echo ""
info "Waiting for services to become healthy (this may take 1-2 minutes)..."
sleep 10

echo ""
echo "${GREEN}${BOLD}"
echo "  ╔═══════════════════════════════════════════════════════╗"
echo "  ║           Evo AI Community is running!                ║"
echo "  ╚═══════════════════════════════════════════════════════╝"
echo "${RESET}"
echo ""
echo "  ${BOLD}Service URLs:${RESET}"
echo "  ─────────────────────────────────────────────"
echo "  Frontend:    ${CYAN}http://localhost:5173${RESET}"
echo "  CRM API:     ${CYAN}http://localhost:3000${RESET}"
echo "  Auth API:    ${CYAN}http://localhost:3001${RESET}"
echo "  Processor:   ${CYAN}http://localhost:8000${RESET}"
echo "  Core API:    ${CYAN}http://localhost:5555${RESET}"
echo "  Mailhog:     ${CYAN}http://localhost:8025${RESET}  (email testing)"
echo ""
echo "  ${BOLD}Default Login:${RESET}"
echo "  ─────────────────────────────────────────────"
echo "  Email:       ${GREEN}support@evo-auth-service-community.com${RESET}"
echo "  Password:    ${GREEN}Password@123${RESET}"
echo ""
echo "  ${BOLD}Useful Commands:${RESET}"
echo "  ─────────────────────────────────────────────"
echo "  make status   — Check service status"
echo "  make logs     — View logs (all services)"
echo "  make stop     — Stop all services"
echo "  make start    — Start all services"
echo "  make clean    — Remove all data and start fresh"
echo ""
