---
title: 'Open Source Community Infrastructure Setup'
slug: 'oss-community-infrastructure'
created: '2026-03-19'
status: 'ready-for-dev'
stepsCompleted: [1, 2, 3, 4]
tech_stack:
  - 'Docker / Docker Compose'
  - 'GitHub Actions (CI/CD)'
  - 'GitHub Container Registry (ghcr.io)'
  - 'Shell scripting (bash)'
  - 'GNU Make'
  - 'Trivy (security scanning)'
  - 'Dependabot'
  - 'YAML / Markdown'
files_to_modify:
  - 'README.md (revamp)'
  - '.github/workflows/ci.yml (create)'
  - '.github/workflows/release.yml (create)'
  - '.github/workflows/security.yml (create)'
  - '.github/dependabot.yml (create)'
  - '.github/ISSUE_TEMPLATE/bug_report.yml (create)'
  - '.github/ISSUE_TEMPLATE/feature_request.yml (create)'
  - '.github/ISSUE_TEMPLATE/question.yml (create)'
  - '.github/ISSUE_TEMPLATE/config.yml (create)'
  - '.github/PULL_REQUEST_TEMPLATE.md (create)'
  - '.github/FUNDING.yml (create)'
  - '.github/CODEOWNERS (create)'
  - 'docker-compose.yml (create)'
  - '.env.example (create)'
  - 'Makefile (create)'
  - 'setup.sh (create)'
  - 'CODE_OF_CONDUCT.md (create)'
  - 'CONTRIBUTING.md (create)'
  - 'SECURITY.md (create)'
  - 'SUPPORT.md (create)'
  - 'CHANGELOG.md (create)'
  - 'docs/QUICK-START.md (create)'
  - 'docs/SETUP-GUIDE.md (create)'
  - 'docs/TROUBLESHOOTING.md (create)'
code_patterns:
  - 'Monorepo with 5 Git submodules under EvolutionAPI org'
  - 'Each service has own Dockerfile with multi-stage builds'
  - 'Shared PostgreSQL database: evo_community (pgvector/pgvector:pg16)'
  - 'Shared Redis (alpine) with password auth'
  - 'Service entrypoints handle migrations automatically'
  - 'Auth seeds must run before CRM seeds (user dependency)'
  - 'JWT/SECRET_KEY_BASE shared across auth, CRM, and core-service'
  - 'ENCRYPTION_KEY shared between core-service and processor'
  - 'Frontend builds as static SPA served via nginx on port 80'
  - 'Frontend needs build-time VITE_* env vars for API URLs'
test_patterns: []
---

# Tech-Spec: Open Source Community Infrastructure Setup

**Created:** 2026-03-19

## Overview

### Problem Statement

The evo-crm-community is an AI-powered CRM with 5 microservices (auth, CRM, frontend, AI processor, core service), but it lacks the complete open source project infrastructure required for community adoption. Currently, setting up the project requires navigating 5 separate READMEs with individual configurations — an insurmountable barrier for the target audience of non-technical consultancies, implementers, and SMBs.

### Solution

Create the full OSS infrastructure at the monorepo root: GitHub Actions with versioned releases by git tags, issue/PR templates, community health files, unified docker-compose, single .env with working defaults, setup scripts, and step-by-step documentation written for beginners.

**CRITICAL CONSTRAINT:** All files are created exclusively in the root monorepo. NO modifications inside submodule repositories. Submodule Dockerfiles and configs are referenced but never changed.

### Scope

**In Scope:**
- GitHub Actions workflows (CI, release by tag v0.0.0, release latest, security scan)
- Dependabot configuration
- Issue templates (bug report, feature request, question) + PR template
- Community health files (CODE_OF_CONDUCT, CONTRIBUTING, SUPPORT, SECURITY, CODEOWNERS, FUNDING)
- Unified docker-compose.yml (5 services + PostgreSQL + Redis + Sidekiq workers + Mailhog)
- Unified .env.example with sensible defaults that work out of the box
- Makefile (setup, start, stop, logs, clean, seed targets)
- Interactive setup.sh script for beginners
- Revamped README.md (hero section, badges, quick start, feature list, architecture)
- docs/QUICK-START.md (5-step copy-paste guide)
- docs/SETUP-GUIDE.md (detailed multi-OS guide)
- docs/TROUBLESHOOTING.md (common errors FAQ)
- CHANGELOG.md

**Out of Scope:**
- ANY changes inside submodule repositories
- External landing page / website
- Setup video
- GitHub UI config (Labels, Milestones, Discussions — manual)
- Enterprise features
- ScyllaDB optional setup

## Context for Development

### Codebase Patterns

**Monorepo Structure:**
- Root repo with 5 Git submodules under `EvolutionAPI` GitHub org
- Each submodule is an independent repo with its own Dockerfile, .env.example, Makefile
- All new files go in the ROOT repo only

**Docker Patterns (read-only reference from submodules):**
- CRM: `evo-ai-crm-community/docker/Dockerfile` — Ruby 3.4.4 Alpine, port 3000, entrypoint `docker/entrypoints/rails.sh`
- Auth: `evo-auth-service-community/Dockerfile` — Ruby 3.4.4-slim, port 3001, has HEALTHCHECK
- Frontend: `evo-ai-frontend-community/Dockerfile` — Node 20 -> nginx:alpine, port 80, needs VITE_* build args
- Processor: `evo-ai-processor-community/Dockerfile` — Python 3.11-slim, port 8000, auto-runs alembic + seeders
- Core: `evo-ai-core-service-community/Dockerfile` — Go 1.24 -> Alpine, port 5555, auto-runs migrations via entrypoint.sh

**Seed Order (Critical):**
1. Auth service seeds FIRST: creates account "Evolution Community" + user `support@evo-auth-service-community.com` / `Password@123`
2. CRM service seeds SECOND: expects the auth user to exist

**Shared Secrets (must be identical across services in .env.example):**
- `SECRET_KEY_BASE` / `JWT_SECRET_KEY`: auth, CRM, core-service
- `ENCRYPTION_KEY` (Fernet): core-service, processor
- `EVOAI_CRM_API_TOKEN`: auth, CRM, processor
- `REDIS_PASSWORD`: all services

### Files to Reference

| File | Purpose |
| ---- | ------- |
| `README.md` | Current root README — revamp (fix MIT -> Apache 2.0) |
| `LICENSE` | Apache 2.0 — exists, do NOT modify |
| `NOTICE` | Copyright — exists, do NOT modify |
| `TRADEMARKS.md` | Brand policy — exists, do NOT modify |
| `.gitmodules` | Submodule definitions (EvolutionAPI GitHub repos) |
| `evo-ai-crm-community/docker-compose.yaml` | Reference for CRM Docker patterns |
| `evo-ai-crm-community/docker/Dockerfile` | Reference: CRM build (Ruby 3.4.4 Alpine) |
| `evo-ai-crm-community/docker/entrypoints/rails.sh` | Reference: CRM entrypoint (waits for PG) |
| `evo-ai-crm-community/.env.example` | Reference: CRM env vars (~258 lines) |
| `evo-auth-service-community/Dockerfile` | Reference: Auth build (Ruby 3.4.4-slim) |
| `evo-auth-service-community/.env.example` | Reference: Auth env vars |
| `evo-auth-service-community/db/seeds.rb` | Reference: creates account + admin user |
| `evo-ai-frontend-community/Dockerfile` | Reference: Frontend build (Node 20 -> nginx) |
| `evo-ai-frontend-community/nginx.conf` | Reference: SPA nginx config |
| `evo-ai-frontend-community/.env.example` | Reference: Frontend VITE_* vars |
| `evo-ai-processor-community/Dockerfile` | Reference: Processor build (Python 3.11) |
| `evo-ai-processor-community/.env.example` | Reference: Processor env vars |
| `evo-ai-core-service-community/Dockerfile` | Reference: Core build (Go 1.24) |
| `evo-ai-core-service-community/entrypoint.sh` | Reference: Core entrypoint (migrate + main) |
| `evo-ai-core-service-community/.env.example` | Reference: Core env vars |

### Technical Decisions

- **All files in root repo only** — submodules are read-only references
- **Docker Registry:** ghcr.io/evolutionapi — free for public repos
- **Release Strategy:** git tag `v*.*.*` triggers multi-image build/push with version tag + `:latest`
- **PostgreSQL:** pgvector/pgvector:pg16 — required by CRM for vector operations
- **Redis:** redis:alpine with password authentication
- **Sidekiq Workers:** Separate containers for CRM sidekiq + Auth sidekiq
- **Mailhog:** Included for local email testing (port 8025 web UI)
- **Frontend Port Mapping:** Container port 80 (nginx) mapped to host 5173
- **Seed Automation:** `make setup` runs auth seeds before CRM seeds
- **Pre-generated Secrets:** .env.example ships with dev secrets so `cp .env.example .env` works without edits
- **Code of Conduct:** Contributor Covenant v2.1
- **docker-compose uses Docker DNS:** services reference `postgres`, `redis` (not localhost)
- **Health Checks:** compose uses `depends_on` with `condition: service_healthy`
- **No version key in compose** — modern Docker Compose format

## Implementation Plan

### Tasks

#### Phase 1: Deploy Infrastructure (docker-compose + env + scripts)

- [ ] Task 1: Create unified `.env.example` at root
  - File: `.env.example`
  - Action: Create a single .env.example that consolidates all env vars from the 5 submodule .env.example files. Group by section (Database, Redis, Auth Service, CRM Service, Core Service, Processor Service, Frontend). Use Docker internal hostnames (postgres, redis). Include pre-generated development secrets for SECRET_KEY_BASE, JWT_SECRET_KEY, ENCRYPTION_KEY, EVOAI_CRM_API_TOKEN, REDIS_PASSWORD so the file works with zero edits after copy. Comment every variable with a one-line explanation in plain English.
  - Notes: Reference all 5 submodule .env.example files. Only include vars needed for docker-compose setup — skip optional APM/monitoring/social-channel vars but include them commented with "Optional" label. VITE_* vars use localhost URLs for host-browser access (not Docker DNS).

- [ ] Task 2: Create unified `docker-compose.yml` at root
  - File: `docker-compose.yml`
  - Action: Create docker-compose that orchestrates all services. Services: `postgres` (pgvector/pgvector:pg16, healthcheck with pg_isready), `redis` (redis:alpine with password, healthcheck with redis-cli ping), `evo-auth` (build from evo-auth-service-community/Dockerfile, port 3001, depends_on postgres+redis healthy, env_file .env), `evo-auth-sidekiq` (same build as evo-auth, command override for sidekiq, depends_on postgres+redis), `evo-crm` (build from evo-ai-crm-community/docker/Dockerfile, port 3000, depends_on postgres+redis+evo-auth healthy, env_file .env, entrypoint docker/entrypoints/rails.sh, command rails s), `evo-crm-sidekiq` (same build, command sidekiq), `evo-core` (build from evo-ai-core-service-community/Dockerfile, port 5555, depends_on postgres healthy, env_file .env), `evo-processor` (build from evo-ai-processor-community/Dockerfile, port 8000, depends_on postgres+redis healthy, env_file .env), `evo-frontend` (build from evo-ai-frontend-community/Dockerfile, port 5173:80, build args VITE_* from .env), `mailhog` (mailhog/mailhog, ports 1025+8025). Use named volumes for postgres_data and redis_data. No `version:` key. All services on default network.
  - Notes: CRM Dockerfile path is `docker/Dockerfile` relative to its context. Auth Dockerfile is `Dockerfile` at submodule root. Frontend needs build args (not env vars) for VITE_*. Processor CMD already runs migrations+seeders. Core entrypoint.sh already runs migrations. Health checks on all backend services.

- [ ] Task 3: Create `Makefile` at root
  - File: `Makefile`
  - Action: Create Makefile with targets: `help` (default, shows all targets with descriptions), `setup` (copies .env.example to .env if not exists, runs docker compose build, starts infra services, waits for healthy, runs auth seeds, then CRM seeds), `start` (docker compose up -d), `stop` (docker compose down), `restart` (stop + start), `logs` (docker compose logs -f, accepts SERVICE= arg), `clean` (docker compose down -v, removes volumes), `seed-auth` (runs rails db:create db:migrate db:seed in evo-auth container), `seed-crm` (runs rails db:create db:migrate db:seed in evo-crm container), `seed` (seed-auth then seed-crm), `status` (docker compose ps), `build` (docker compose build --no-cache), `shell-crm` / `shell-auth` / `shell-core` / `shell-processor` (exec bash into container). All targets with `.PHONY`. Include banner with Evo AI ASCII art.
  - Notes: Use `docker compose` (v2) not `docker-compose` (v1). Seed targets use `docker compose exec` or `docker compose run`. Wait-for-healthy logic uses a simple loop checking `docker compose ps --format json`.

- [ ] Task 4: Create `setup.sh` interactive script
  - File: `setup.sh`
  - Action: Create beginner-friendly interactive bash script. Flow: 1) Print welcome banner with Evo AI branding, 2) Check prerequisites (git, docker, docker compose) with clear error messages and install links if missing, 3) Check if submodules are initialized, if not run `git submodule update --init --recursive`, 4) Copy .env.example to .env (ask before overwriting if exists), 5) Run `docker compose build` with progress output, 6) Run `docker compose up -d` for postgres+redis first, 7) Wait for healthy with spinner animation, 8) Run auth seeds, 9) Run CRM seeds, 10) Start all remaining services, 11) Print success message with URLs (Frontend: http://localhost:5173, CRM API: http://localhost:3000, Auth: http://localhost:3001, Processor: http://localhost:8000, Core: http://localhost:5555, Mailhog: http://localhost:8025) and default credentials (email: support@evo-auth-service-community.com, password: Password@123). Include `set -e` for fail-fast. Use color output (with fallback for no-color terminals). Add `chmod +x setup.sh` note in docs.
  - Notes: Must work on Mac (zsh), Linux (bash), and Windows WSL2 (bash). No dependencies beyond git, docker, docker compose. Use POSIX-compatible shell where possible.

#### Phase 2: CI/CD (GitHub Actions)

- [ ] Task 5: Create CI workflow
  - File: `.github/workflows/ci.yml`
  - Action: Create workflow triggered on pull_request to main. Jobs: `validate-compose` (runs `docker compose config` to validate compose file), `lint-dockerfiles` (uses hadolint on each Dockerfile), `lint-docs` (optional: markdownlint on .md files). Use ubuntu-latest runner. Keep simple — actual service tests run in submodule repos.
  - Notes: Submodule checkout requires `submodules: recursive` in actions/checkout. Don't run full build/test of services here — that belongs in each submodule's own CI.

- [ ] Task 6: Create Release workflow (tag-based)
  - File: `.github/workflows/release.yml`
  - Action: Create workflow triggered on push tags `v*.*.*`. Jobs: `release` with matrix strategy for all 5 services. Steps: 1) Checkout with submodules, 2) Set up Docker Buildx, 3) Login to ghcr.io using GITHUB_TOKEN, 4) Extract version from tag (strip `v` prefix), 5) Build and push each service image with tags `ghcr.io/evolutionapi/{service-name}:{version}` AND `ghcr.io/evolutionapi/{service-name}:latest`. 6) Create GitHub Release with auto-generated release notes. Use docker/build-push-action. Service image names: `evo-auth-service-community`, `evo-ai-crm-community`, `evo-ai-frontend-community`, `evo-ai-processor-community`, `evo-ai-core-service-community`. Frontend build args should use production-ready placeholder URLs (overridable at runtime via env).
  - Notes: Each service has its Dockerfile in a different relative path. CRM is at `docker/Dockerfile` with context `.`. Auth/Frontend/Processor/Core are at `Dockerfile` with context `.`. Use matrix to avoid duplication. GITHUB_TOKEN has built-in write:packages permission for ghcr.io.

- [ ] Task 7: Create Security scan workflow
  - File: `.github/workflows/security.yml`
  - Action: Create workflow triggered on push to main (weekly schedule + on push). Use Trivy to scan each service's Dockerfile for vulnerabilities. Use aquasecurity/trivy-action. Report results as GitHub Security tab alerts (sarif format). Scan for HIGH and CRITICAL only.
  - Notes: Schedule with cron `0 6 * * 1` (Monday 6 AM UTC). Needs submodule checkout.

- [ ] Task 8: Create Dependabot configuration
  - File: `.github/dependabot.yml`
  - Action: Create dependabot config with update entries for: `github-actions` (directory `/`, weekly), `docker` (directory `/`, weekly for compose file). Individual submodule dependency updates (bundler, pip, gomod, npm) should be configured in their own repos, not here.
  - Notes: Keep minimal — only what applies to root repo files.

#### Phase 3: GitHub Templates

- [ ] Task 9: Create Bug Report issue template
  - File: `.github/ISSUE_TEMPLATE/bug_report.yml`
  - Action: Create YAML form-based template. Fields: `name` (Bug Report), `description`, `title` (prefix `[Bug]: `), body fields: `description` (textarea, required), `service` (dropdown: Auth/CRM/Frontend/Processor/Core/Unknown, required), `steps-to-reproduce` (textarea, required), `expected-behavior` (textarea, required), `actual-behavior` (textarea, required), `environment` (textarea: OS, Docker version, browser — required), `screenshots` (textarea, optional), `logs` (textarea with code render, optional). Labels: `bug`, `triage`.
  - Notes: Use YAML form syntax (not markdown template). Clear placeholders in Portuguese+English for international community.

- [ ] Task 10: Create Feature Request issue template
  - File: `.github/ISSUE_TEMPLATE/feature_request.yml`
  - Action: Create YAML form template. Fields: `name` (Feature Request), `description`, `title` (prefix `[Feature]: `), body: `problem` (textarea — what problem does this solve, required), `solution` (textarea — proposed solution, required), `alternatives` (textarea — alternatives considered, optional), `service` (dropdown: Auth/CRM/Frontend/Processor/Core/General, required), `additional-context` (textarea, optional). Labels: `enhancement`.
  - Notes: Keep concise — don't overwhelm users with too many required fields.

- [ ] Task 11: Create Question issue template
  - File: `.github/ISSUE_TEMPLATE/question.yml`
  - Action: Create YAML form template. Fields: `name` (Question), `description`, `title` (prefix `[Question]: `), body: `question` (textarea, required), `context` (textarea — what are you trying to do, optional), `service` (dropdown, optional). Labels: `question`.

- [ ] Task 12: Create issue template config
  - File: `.github/ISSUE_TEMPLATE/config.yml`
  - Action: Create config with `blank_issues_enabled: false` and `contact_links` pointing to documentation (docs/TROUBLESHOOTING.md) and community channels (if Discord/Telegram exists, add link — otherwise just docs).

- [ ] Task 13: Create Pull Request template
  - File: `.github/PULL_REQUEST_TEMPLATE.md`
  - Action: Create PR template with sections: `## Description` (what and why), `## Type of Change` (checkboxes: bug fix, feature, docs, CI/CD, refactor, other), `## Service(s) Affected` (checkboxes for each service + root/infra), `## Checklist` (checkboxes: tested locally, docs updated if needed, no breaking changes, follows contributing guidelines), `## Screenshots` (if UI changes).

#### Phase 4: Community Health Files

- [ ] Task 14: Create `CODE_OF_CONDUCT.md`
  - File: `CODE_OF_CONDUCT.md`
  - Action: Use Contributor Covenant v2.1 full text. Set enforcement contact to a generic email (e.g., `community@evoai.com` or placeholder for Davidson to fill). Include both English content (standard).

- [ ] Task 15: Create `CONTRIBUTING.md`
  - File: `CONTRIBUTING.md`
  - Action: Create unified contributing guide. Sections: 1) Welcome + quick overview, 2) Code of Conduct reference, 3) How to Report Bugs (link to issue template), 4) How to Request Features (link to template), 5) Development Setup (reference QUICK-START.md), 6) Making Changes (fork, branch naming: `feat/`, `fix/`, `docs/`, commit messages with conventional commits encouraged), 7) Pull Request Process (fill template, pass CI, await review), 8) Project Structure (brief monorepo overview, explain submodules, where to make changes for each service), 9) Style Guidelines (defer to each service's own standards), 10) License (Apache 2.0, contributions licensed same). Written in English (document_output_language).

- [ ] Task 16: Create `SECURITY.md`
  - File: `SECURITY.md`
  - Action: Create security policy. Sections: Supported Versions (table with current version supported), Reporting a Vulnerability (email to security contact, expected response time, responsible disclosure process), What to Report, What NOT to Report. Standard OSS security policy format.

- [ ] Task 17: Create `SUPPORT.md`
  - File: `SUPPORT.md`
  - Action: Create support guide. Sections: Where to Get Help (GitHub Issues for bugs, GitHub Discussions for questions, documentation links), Before Opening an Issue (check TROUBLESHOOTING.md, search existing issues), Commercial Support (mention Evo AI offers paid support/hosted options — link to evoai website or placeholder).

- [ ] Task 18: Create `CODEOWNERS`
  - File: `.github/CODEOWNERS`
  - Action: Create CODEOWNERS mapping: `* @EvolutionAPI/core-team` (catch-all), specific paths for each submodule if there are known maintainers (use generic team for now). Include root infra files (docker-compose, Makefile, .github/) owned by core team.

- [ ] Task 19: Create `FUNDING.yml`
  - File: `.github/FUNDING.yml`
  - Action: Create funding config. Include `github: EvolutionAPI` (GitHub Sponsors). Add placeholder for other platforms (Open Collective, etc.) as comments for Davidson to enable later.

#### Phase 5: Documentation

- [ ] Task 20: Revamp `README.md`
  - File: `README.md`
  - Action: Complete rewrite. Structure: 1) Hero section with logo placeholder (`<!-- TODO: Add banner image -->`), project name, one-line description, badges (license Apache 2.0, latest release, Docker pulls, GitHub stars, PRs welcome), 2) Screenshot placeholder, 3) "What is Evo AI Community?" — 3-sentence elevator pitch, 4) Key Features (bullet list: multi-channel messaging, AI agents, CRM pipeline, real-time conversations, multi-language, self-hosted), 5) Architecture diagram (text-based or mermaid), 6) Quick Start (condensed 5-step: clone, cp env, docker compose up, open browser, login — with link to full QUICK-START.md), 7) Default Credentials box, 8) Service URLs table, 9) Documentation links (QUICK-START, SETUP-GUIDE, TROUBLESHOOTING, CONTRIBUTING), 10) Community section (issues, discussions, contributing), 11) License (Apache 2.0 — FIX from current MIT), 12) Trademark notice (brief, link to TRADEMARKS.md). Written in English. Keep it scannable — headers, bullets, tables, code blocks. Maximum 200 lines.
  - Notes: MUST fix the current incorrect MIT license reference to Apache 2.0.

- [ ] Task 21: Create `docs/QUICK-START.md`
  - File: `docs/QUICK-START.md`
  - Action: Create the "recipe book" guide. Pure copy-paste, 5 steps, zero decisions. Structure: Title "Quick Start — Running Evo AI in 5 Minutes", Prerequisites box (Docker Desktop link for each OS, Git), Step 1: Clone (`git clone --recurse-submodules ...`), Step 2: Configure (`cp .env.example .env`), Step 3: Start (`docker compose up -d`), Step 4: Wait & Seed (`make setup` or manual commands for those without make), Step 5: Open browser (http://localhost:5173, credentials). Each step with: the command to copy, what to expect (output sample), how long it takes ("~2 minutes"), what success looks like. End with "Next Steps" linking to SETUP-GUIDE.md for customization.
  - Notes: Include both `make setup` path AND manual docker commands for users without make. Must work for someone who has never used a terminal.

- [ ] Task 22: Create `docs/SETUP-GUIDE.md`
  - File: `docs/SETUP-GUIDE.md`
  - Action: Create detailed setup guide. Sections: 1) Prerequisites (Docker Desktop install for Windows/Mac/Linux with links, Git install, minimum specs: 8GB RAM, 20GB disk), 2) Step-by-step with explanations (what each command does and why), 3) Configuration Guide (every .env section explained: what it does, when to change it, default value rationale), 4) Service Architecture (which service does what, ports, dependencies), 5) First Login walkthrough, 6) Customization (changing ports, adding SSL, connecting WhatsApp channel, configuring email SMTP), 7) Updating (how to pull latest, `git submodule update --remote`), 8) Stopping & Cleaning Up. Include `<!-- screenshot: description -->` placeholders where screenshots should go.

- [ ] Task 23: Create `docs/TROUBLESHOOTING.md`
  - File: `docs/TROUBLESHOOTING.md`
  - Action: Create FAQ-style troubleshooting guide. Format: Problem -> Cause -> Solution for each entry. Entries to include: "Port already in use" (how to change ports or kill process), "Docker daemon not running" (how to start Docker Desktop), "Permission denied on setup.sh" (chmod +x), "Database connection refused" (wait for healthy, check postgres logs), "Frontend shows blank page" (VITE_* env vars not set, rebuild frontend), "Cannot login" (seeds not run, check auth service logs), "Submodules empty after clone" (forgot --recurse-submodules, run git submodule update), "Docker compose version error" (v1 vs v2, upgrade Docker Desktop), "Out of memory" (increase Docker Desktop RAM allocation), "Services keep restarting" (check logs with `make logs SERVICE=evo-crm`), "Redis connection refused" (REDIS_PASSWORD mismatch), "CORS errors in browser" (check CORS_ORIGINS in .env).

- [ ] Task 24: Create `CHANGELOG.md`
  - File: `CHANGELOG.md`
  - Action: Create changelog following Keep a Changelog format (keepachangelog.com). Initial entry: `## [0.1.0] - 2026-03-19` with `### Added` section listing: initial community open source release, unified docker-compose setup, GitHub Actions CI/CD, documentation for setup and contribution. Include header with links to Keep a Changelog and Semantic Versioning.

### Acceptance Criteria

#### Deploy Infrastructure
- [ ] AC 1: Given a fresh clone with submodules, when user runs `cp .env.example .env && docker compose up -d`, then all 8 services (postgres, redis, auth, auth-sidekiq, crm, crm-sidekiq, core, processor, frontend, mailhog) start and become healthy within 5 minutes
- [ ] AC 2: Given running services, when user opens http://localhost:5173, then the Evo AI frontend login page loads
- [ ] AC 3: Given seeds have been run (`make seed`), when user logs in with `support@evo-auth-service-community.com` / `Password@123`, then authentication succeeds and dashboard loads
- [ ] AC 4: Given a non-technical user, when they run `bash setup.sh`, then the script checks prerequisites, builds, seeds, and starts all services with clear progress messages
- [ ] AC 5: Given any `make` target is run, when `make help` is executed, then all available targets are listed with descriptions

#### CI/CD
- [ ] AC 6: Given a PR is opened against main, when CI runs, then the docker-compose config is validated successfully
- [ ] AC 7: Given a tag `v1.0.0` is pushed, when the release workflow runs, then 5 Docker images are built and pushed to ghcr.io with both `:1.0.0` and `:latest` tags
- [ ] AC 8: Given the release workflow completes, when checking GitHub Releases, then a new release exists with auto-generated notes
- [ ] AC 9: Given the security workflow runs on schedule, when vulnerabilities are found, then they appear in GitHub Security tab

#### GitHub Templates
- [ ] AC 10: Given a user clicks "New Issue", when the template chooser appears, then Bug Report, Feature Request, and Question options are shown as structured forms
- [ ] AC 11: Given a user creates a PR, when the PR form loads, then the PR template with checklist is pre-populated

#### Community Health Files
- [ ] AC 12: Given a visitor views the GitHub repo, when they click "Community" insights tab, then CODE_OF_CONDUCT, CONTRIBUTING, SECURITY, and SUPPORT show as present
- [ ] AC 13: Given the CONTRIBUTING.md is read, when a new contributor follows it, then they can fork, develop, and submit a PR successfully

#### Documentation
- [ ] AC 14: Given a non-technical user reads QUICK-START.md, when they follow all 5 steps exactly as written (copy-paste), then Evo AI is running locally
- [ ] AC 15: Given a user encounters an error, when they search TROUBLESHOOTING.md, then the most common setup errors are covered with clear solutions
- [ ] AC 16: Given the README.md is viewed on GitHub, when scanning for 10 seconds, then the user understands what Evo AI is, how to start it, and where to find help
- [ ] AC 17: Given the README.md license section, when read, then it correctly states Apache 2.0 (not MIT)

## Additional Context

### Dependencies

- **GitHub Container Registry (ghcr.io):** Free for public repos, automatic GITHUB_TOKEN auth
- **GitHub Actions:** Free for public repos (2,000 minutes/month)
- **Dependabot:** Built into GitHub, zero config beyond yaml file
- **Trivy:** Open source, used via aquasecurity/trivy-action
- **Contributor Covenant v2.1:** Standard OSS Code of Conduct text
- **Docker Buildx:** Required for multi-platform builds in release workflow
- **actions/checkout@v4:** Must use `submodules: recursive` for monorepo

### Testing Strategy

- **docker-compose.yml:** Validate with `docker compose config`; full startup test on clean machine
- **setup.sh:** Test on clean Mac (zsh), Ubuntu (bash), Windows WSL2 (bash)
- **Makefile:** Test each target individually; verify `make help` output
- **CI workflow:** Create test PR to validate
- **Release workflow:** Push test tag `v0.0.1-rc.1` to validate image builds
- **Templates:** Create test issues to validate form rendering
- **Documentation:** Walk-through by someone unfamiliar with the project (Davidson's target audience)

### Notes

- **README License Fix:** Current README line 107 says "MIT" — must be corrected to "Apache 2.0"
- **CRM Dockerfile .git dependency:** The CRM Dockerfile runs `git rev-parse HEAD > .git_sha`. In docker-compose build context this should work since the submodule directory is the build context and contains `.git`. If it fails, add a `GIT_SHA` build arg to docker-compose.yml.
- **Frontend runtime config:** The frontend bakes VITE_* URLs at build time. For docker-compose local dev, these point to localhost. For production, users need to rebuild the frontend image with correct URLs or use a runtime config injection approach (future enhancement, out of scope).
- **Auth Dockerfile is development-focused:** It has `RAILS_ENV=development` hardcoded. The release workflow should override this with build args for production builds.
- **Submodule branch tracking:** docker-compose builds use whatever commit the submodules point to. Users update with `git submodule update --remote --merge`.
- **Future enhancements (out of scope):** One-click deploy buttons (Railway, Render, DigitalOcean), Helm chart for Kubernetes, Terraform modules, production SSL/reverse-proxy guide, ScyllaDB optional config.
