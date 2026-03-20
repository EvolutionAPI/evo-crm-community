---
title: 'Epic 1: One-Command Local Setup'
status: 'ready-for-dev'
epic: 1
stories: [1.1, 1.2, 1.3, 1.4]
frs_covered: [FR1, FR2, FR3, FR4, FR5]
nfrs_addressed: [NFR1, NFR2, NFR3, NFR4, NFR5]
files_to_create:
  - '.env.example'
  - 'docker-compose.yml'
  - 'Makefile'
  - 'setup.sh'
---

# Epic 1: One-Command Local Setup

**Goal:** An adopter can clone the repo and have Evo AI running locally with a single command, without editing any configuration files. From zero to running CRM in minutes.

**Critical Constraint:** ZERO modifications inside submodule repositories. All files created at monorepo root only.

---

## Context for Development

### Monorepo Structure

- Root repo with 5 Git submodules under `EvolutionAPI` GitHub org
- Each submodule has its own Dockerfile, .env.example, and entrypoint

### Docker Patterns (read-only reference from submodules)

| Service | Dockerfile Path | Base Image | Port | Entrypoint |
|---------|----------------|------------|------|------------|
| CRM | `evo-ai-crm-community/docker/Dockerfile` | Ruby 3.4.4 Alpine | 3000 | `docker/entrypoints/rails.sh` |
| Auth | `evo-auth-service-community/Dockerfile` | Ruby 3.4.4-slim | 3001 | Has HEALTHCHECK |
| Frontend | `evo-ai-frontend-community/Dockerfile` | Node 20 → nginx:alpine | 80 | Needs VITE_* build args |
| Processor | `evo-ai-processor-community/Dockerfile` | Python 3.11-slim | 8000 | Auto-runs alembic + seeders |
| Core | `evo-ai-core-service-community/Dockerfile` | Go 1.24 → Alpine | 5555 | Auto-runs migrations via entrypoint.sh |

### Seed Order (Critical — FR5)

1. Auth service seeds FIRST: creates account "Evolution Community" + user `support@evo-auth-service-community.com` / `Password@123`
2. CRM service seeds SECOND: expects the auth user to exist

### Shared Secrets (must be identical across services)

- `SECRET_KEY_BASE` / `JWT_SECRET_KEY`: auth, CRM, core-service
- `ENCRYPTION_KEY` (Fernet): core-service, processor
- `EVOAI_CRM_API_TOKEN`: auth, CRM, processor
- `REDIS_PASSWORD`: all services

### Reference Files

- `evo-ai-crm-community/.env.example` — CRM env vars (~258 lines)
- `evo-auth-service-community/.env.example` — Auth env vars
- `evo-ai-frontend-community/.env.example` — Frontend VITE_* vars
- `evo-ai-processor-community/.env.example` — Processor env vars
- `evo-ai-core-service-community/.env.example` — Core env vars
- `evo-ai-crm-community/docker-compose.yaml` — Reference for CRM Docker patterns
- `evo-auth-service-community/db/seeds.rb` — Creates account + admin user

### Technical Decisions

- **PostgreSQL:** `pgvector/pgvector:pg16` — required by CRM for vector operations
- **Redis:** `redis:alpine` with password authentication
- **Frontend port:** Container port 80 (nginx) mapped to host 5173
- **Frontend env:** `VITE_*` vars are build args (baked at build time), not runtime. Use localhost URLs for dev.
- **Compose format:** No `version:` key (modern Docker Compose). Docker DNS internal hostnames. Health checks with `depends_on: condition: service_healthy`
- **Named volumes:** `postgres_data` and `redis_data`
- **Sidekiq:** Separate containers for CRM sidekiq + Auth sidekiq (same build, command override)
- **Mailhog:** Included for local email testing (port 1025 SMTP + 8025 web UI)
- **Use `docker compose` (v2)**, not `docker-compose` (v1)
- **Pre-generated secrets:** .env.example ships with dev secrets so `cp .env.example .env` works without edits

---

## Stories

### Story 1.1: Unified Environment Configuration

As a **project adopter**,
I want a single `.env.example` file at the monorepo root with all environment variables pre-configured,
So that I can start the entire platform by simply copying the file without editing anything.

**File:** `.env.example`

**Implementation Notes:**
- Consolidate all env vars from the 5 submodule .env.example files
- Group by section (Database, Redis, Auth Service, CRM Service, Core Service, Processor Service, Frontend)
- Use Docker internal hostnames (`postgres`, `redis`) for service-to-service URLs
- VITE_* vars use `localhost` URLs (for host-browser access, not Docker DNS)
- Only include vars needed for docker-compose setup
- Optional vars (APM, monitoring, social channels) included but commented with "Optional" label
- Comment every variable with a one-line explanation in plain English

**Acceptance Criteria:**

**Given** a fresh clone of the monorepo
**When** the user runs `cp .env.example .env`
**Then** the `.env` file contains all variables needed by all 5 services, PostgreSQL, and Redis
**And** variables are grouped by section (Database, Redis, Auth, CRM, Core, Processor, Frontend)
**And** every variable has a one-line comment explaining its purpose
**And** pre-generated development secrets are included for SECRET_KEY_BASE, JWT_SECRET_KEY, ENCRYPTION_KEY, EVOAI_CRM_API_TOKEN, and REDIS_PASSWORD
**And** shared secrets are identical across all service sections that reference them
**And** VITE_* variables use `localhost` URLs (for host-browser access, not Docker DNS)
**And** optional variables (APM, monitoring, social channels) are present but commented out with "Optional" label
**And** Docker internal hostnames (`postgres`, `redis`) are used for service-to-service URLs

---

### Story 1.2: Unified Docker Compose Orchestration

As a **project adopter**,
I want a single `docker-compose.yml` at the monorepo root that orchestrates all services,
So that I can start the entire platform with one `docker compose up -d` command.

**File:** `docker-compose.yml`

**Implementation Notes:**
- Services: postgres, redis, evo-auth, evo-auth-sidekiq, evo-crm, evo-crm-sidekiq, evo-core, evo-processor, evo-frontend, mailhog
- CRM Dockerfile path is `docker/Dockerfile` relative to its context `evo-ai-crm-community`
- Auth/Frontend/Processor/Core Dockerfiles are `Dockerfile` at submodule root
- Frontend needs build args (not env vars) for VITE_*
- Processor CMD already runs migrations+seeders
- Core entrypoint.sh already runs migrations
- CRM Dockerfile runs `git rev-parse HEAD > .git_sha` — may need `GIT_SHA` build arg if .git not available
- All services on default network
- Health checks on all backend services

**Acceptance Criteria:**

**Given** a valid `.env` file exists (from Story 1.1)
**When** the user runs `docker compose up -d`
**Then** the following services are started: `postgres` (pgvector/pgvector:pg16), `redis` (redis:alpine with password auth), `evo-auth` (port 3001), `evo-auth-sidekiq`, `evo-crm` (port 3000), `evo-crm-sidekiq`, `evo-core` (port 5555), `evo-processor` (port 8000), `evo-frontend` (port 5173→80), `mailhog` (ports 1025+8025)
**And** postgres has a healthcheck using `pg_isready`
**And** redis has a healthcheck using `redis-cli ping`
**And** backend services use `depends_on` with `condition: service_healthy` for postgres and redis
**And** `evo-crm` depends on `evo-auth` being healthy
**And** the compose file has no `version:` key (modern format)
**And** named volumes `postgres_data` and `redis_data` persist data between restarts
**And** the frontend service receives `VITE_*` variables as build args
**And** CRM Dockerfile is referenced at `docker/Dockerfile` relative to `evo-ai-crm-community` context
**And** no files inside submodule directories are created or modified

---

### Story 1.3: Developer Convenience Makefile

As a **project adopter**,
I want a `Makefile` with intuitive targets for common operations,
So that I can manage the platform with simple commands like `make start`, `make logs`, and `make seed` without memorizing docker compose syntax.

**File:** `Makefile`

**Implementation Notes:**
- Default target is `help`
- Include banner with Evo AI ASCII art
- Wait-for-healthy logic uses a simple loop checking `docker compose ps --format json`
- Seed targets use `docker compose exec` or `docker compose run`

**Acceptance Criteria:**

**Given** docker-compose.yml and .env exist
**When** the user runs `make help` (or just `make`)
**Then** all available targets are listed with descriptions and an Evo AI ASCII art banner is displayed
**And** `make setup` copies .env.example→.env if not exists, runs docker compose build, starts infra services, waits for healthy, runs auth seeds, then CRM seeds (in that order per FR5)
**And** `make start` runs `docker compose up -d`
**And** `make stop` runs `docker compose down`
**And** `make restart` runs stop then start
**And** `make logs` runs `docker compose logs -f` and accepts `SERVICE=` argument for filtering
**And** `make clean` runs `docker compose down -v` removing volumes
**And** `make seed-auth` runs `rails db:create db:migrate db:seed` in the evo-auth container
**And** `make seed-crm` runs `rails db:create db:migrate db:seed` in the evo-crm container
**And** `make seed` runs seed-auth THEN seed-crm sequentially
**And** `make status` runs `docker compose ps`
**And** `make build` runs `docker compose build --no-cache`
**And** `make shell-crm`, `shell-auth`, `shell-core`, `shell-processor` exec bash into the respective container
**And** all targets are declared as `.PHONY`
**And** all commands use `docker compose` (v2), not `docker-compose` (v1)

---

### Story 1.4: Interactive Setup Script for Beginners

As a **first-time, non-technical adopter**,
I want an interactive `setup.sh` script that guides me through the entire setup process,
So that I can get Evo AI running without understanding Docker, Git submodules, or terminal commands.

**File:** `setup.sh`

**Implementation Notes:**
- Must work on Mac (zsh), Linux (bash), and Windows WSL2 (bash) — use POSIX-compatible shell where possible
- No dependencies beyond git, docker, docker compose
- Use `set -e` for fail-fast
- Color output with fallback for no-color terminals

**Acceptance Criteria:**

**Given** the user runs `bash setup.sh` on a fresh clone
**When** the script executes
**Then** a welcome banner with Evo AI branding is displayed
**And** prerequisites are checked (git, docker, docker compose) with clear error messages and install links if missing
**And** if submodules are not initialized, the script runs `git submodule update --init --recursive`
**And** `.env.example` is copied to `.env` (with confirmation prompt before overwriting if `.env` already exists)
**And** `docker compose build` runs with visible progress
**And** postgres and redis start first and the script waits for healthy status with a spinner animation
**And** auth seeds run before CRM seeds (FR5 ordering enforced)
**And** all remaining services are started
**And** a success message displays all service URLs (Frontend: localhost:5173, CRM API: localhost:3000, Auth: localhost:3001, Processor: localhost:8000, Core: localhost:5555, Mailhog: localhost:8025) and default credentials (support@evo-auth-service-community.com / Password@123)
**And** the script uses `set -e` for fail-fast behavior
**And** color output is used with fallback for no-color terminals
**And** the script works on Mac (zsh), Linux (bash), and Windows WSL2 (bash) (NFR2)

---

## Review Follow-ups (AI)

_Code review performed on 2026-03-19 — Resolved on 2026-03-19_

### 🔴 HIGH — All Resolved

- [x] [AI-Review][HIGH] Missing `VITE_WS_URL` — Added to `.env.example` and `docker-compose.yml` build args.
- [x] [AI-Review][HIGH] Missing `VITE_APP_ENV` build arg — Added to `docker-compose.yml` build args.
- [x] [AI-Review][HIGH] Secret keys entropy reduced — Replaced with base64-derived 64-char alphanumeric secrets.
- [x] [AI-Review][HIGH] `evo-core` Redis dependency — Verified: core-service does NOT use Redis. No change needed.

### 🟡 MEDIUM — Resolved / Dismissed

- [x] [AI-Review][MEDIUM] Redis DB isolation undocumented — Added comments in `.env.example` explaining per-service DB overrides.
- [x] [AI-Review][MEDIUM] `setup.sh` hardcoded Redis password — Now reads from `.env` with fallback.
- [x] [AI-Review][MEDIUM] CRM volume mount — Intentional for dev hot-reload. No change needed.
- [x] [AI-Review][MEDIUM] Processor seeders idempotency — Seeders are empty stubs; patterns use ON CONFLICT. No change needed.
- [x] [AI-Review][MEDIUM] ACTIVE_STORAGE_SERVICE — `local` is a valid value and the Rails default. No change needed.

### 🟢 LOW — Resolved / Dismissed

- [x] [AI-Review][LOW] Non-existent doc references — Removed from `setup.sh`.
- [x] [AI-Review][LOW] Makefile clean sleep — Minor UX, kept as-is (safe default).
- [x] [AI-Review][LOW] Frontend `/health` route — Verified: exists in `nginx.conf`. No change needed.

### Re-review Follow-ups (2026-03-19)

- [x] [AI-Review][MEDIUM] `VITE_TINYMCE_API_KEY` — Added as build arg to `docker-compose.yml` frontend service.
- [x] [AI-Review][LOW] Makefile Redis password — Now reads from `.env` file via grep, mirroring `setup.sh` fix.
- [x] [AI-Review][LOW] `setup.sh` duplicate `echo ""` — Removed.

### Full AC Audit (2026-03-19)

_Systematic acceptance criteria verification across all 4 stories._

#### Story 1.1: Unified Environment Configuration

| AC | Status | Notes |
|----|--------|-------|
| All vars for 5 services, Postgres, Redis | PASS | All present |
| Grouped by section | PASS | Sections: Database, Redis, Shared Secrets, Auth, CRM, Core, Processor, Frontend, Optional |
| Every variable has a one-line comment | FAIL | ~60 variables lack individual explanatory comments |
| Pre-generated dev secrets included | PASS | SECRET_KEY_BASE, JWT_SECRET_KEY, ENCRYPTION_KEY, EVOAI_CRM_API_TOKEN, REDIS_PASSWORD all present |
| Shared secrets identical across sections | PASS | SECRET_KEY_BASE = JWT_SECRET_KEY = DOORKEEPER_JWT_SECRET_KEY |
| VITE_* use localhost URLs | PASS | All VITE_* vars use localhost |
| Optional vars commented with "Optional" label | FAIL | Section headers say "OPTIONAL" but individual vars lack "Optional" inline labels |
| Docker internal hostnames for service-to-service | PASS | All use postgres, redis, evo-auth, evo-crm, etc. |

- [x] [AI-Review][HIGH] **Story 1.1 AC**: Every variable now has a one-line comment explaining its purpose.
- [x] [AI-Review][LOW] **Story 1.1 AC**: Every optional variable now has "Optional:" inline label prefix.

#### Story 1.2: Unified Docker Compose Orchestration

| AC | Status | Notes |
|----|--------|-------|
| All 10 services present with correct images/ports | PASS | All verified |
| postgres healthcheck with pg_isready | PASS | Line 17 |
| redis healthcheck with redis-cli ping | PASS | Line 32 |
| Backend depends_on with service_healthy | PASS | All backends verified |
| evo-crm depends on evo-auth healthy | PASS | Lines 120-121 |
| No version: key | PASS | Modern format |
| Named volumes postgres_data and redis_data | PASS | Lines 257-258 |
| Frontend receives VITE_* as build args | PASS | Lines 234-241 |
| CRM Dockerfile at docker/Dockerfile | PASS | Lines 94-95 |

**Story 1.2: ALL 9 ACs PASS** — No action items.

#### Story 1.3: Developer Convenience Makefile

| AC | Status | Notes |
|----|--------|-------|
| make help lists targets + ASCII banner | PASS | Lines 21-34 |
| make setup full sequence with seed order | PASS | Lines 38-76 |
| make start | PASS | Line 79 |
| make stop | PASS | Line 82 |
| make restart | PASS | Lines 85-86 |
| make logs with SERVICE= | PASS | Lines 95-99 |
| make clean with -v | PASS | Line 105 |
| make seed-auth runs db:create db:migrate db:seed | FAIL | Uses `db:prepare && db:seed` instead |
| make seed-crm runs db:create db:migrate db:seed | FAIL | Uses `db:prepare && db:seed` instead |
| make seed runs auth then crm | PASS | Line 110 |
| make status | PASS | Line 92 |
| make build --no-cache | PASS | Line 89 |
| shell-crm, shell-auth, shell-core, shell-processor | PASS | Lines 124-134 |
| All targets .PHONY | PASS | Lines 15-17 |
| All use docker compose v2 | PASS | No docker-compose v1 usage |

- [x] [AI-Review][MEDIUM] **Story 1.3 AC**: Seed commands now use `rails db:create db:migrate db:seed` matching AC specification.

#### Story 1.4: Interactive Setup Script

| AC | Status | Notes |
|----|--------|-------|
| Welcome banner with Evo AI branding | PASS | Lines 61-68 |
| Prerequisites checked with error messages + install links | PASS | Lines 73-101 |
| Submodule init if needed | PASS | Lines 108-132 |
| .env copy with overwrite confirmation | PASS | Lines 139-156 |
| docker compose build with visible progress | PASS | Line 166 |
| postgres/redis start first, wait healthy with spinner | PASS | Lines 175-186 |
| Auth seeds before CRM seeds | PASS | Lines 191-204 |
| All remaining services started | PASS | Line 212 |
| Success message with all service URLs | PASS | Lines 227-232 |
| Default credentials displayed | PASS | Lines 236-237 |
| set -e for fail-fast | PASS | Line 13 |
| Color output with no-color fallback | PASS | Lines 18-27 |
| Works on Mac (zsh), Linux (bash), WSL2 (bash) | FAIL | Uses bash-specific features |

- [x] [AI-Review][MEDIUM] **Story 1.4 AC**: Removed bash arrays (replaced with POSIX `for` loop). Added bash guard at script start to fail with clear message if run under zsh. String slicing retained (requires bash, enforced by guard).
