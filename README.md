<p align="center">
  <a href="https://evolutionfoundation.com.br">
    <img src="./public/hover-evolution.png" alt="Evolution" />
  </a>
</p>

<h1 align="center">EVO CRM Community</h1>

<p align="center">
  Open-source, single-tenant AI-powered customer support platform.
</p>

<p align="center">
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache 2.0" /></a>
  <a href="https://docs.evolutionfoundation.com.br"><img src="https://img.shields.io/badge/Docs-evolutionfoundation.com.br-00ffa7" alt="Documentation" /></a>
  <a href="https://evolutionfoundation.com.br/community"><img src="https://img.shields.io/badge/Community-Join%20us-white" alt="Community" /></a>
</p>

<p align="center">
  <a href="https://evolutionfoundation.com.br">Website</a> &middot;
  <a href="https://docs.evolutionfoundation.com.br">Documentation</a> &middot;
  <a href="https://evolutionfoundation.com.br/community">Community</a> &middot;
  <a href="https://evolutionfoundation.com.br/contribute">Support the project</a>
</p>

---

EVO CRM Community is the open-source edition of the EVO CRM platform — a complete suite for AI-assisted customer support. It brings together authentication, CRM, AI agents, agent processing and a modern frontend into a unified, self-hostable stack.

This repository is the **monorepo entrypoint**: it aggregates all community services as Git submodules, giving you a single place to clone, update and orchestrate the entire platform.

---

## Architecture

The platform is composed of 5 independent services:

| Service                                                            | Role                                         | Stack                     | Default Port |
| ------------------------------------------------------------------ | -------------------------------------------- | ------------------------- | ------------ |
| [`evo-auth-service-community`](./evo-auth-service-community)       | Authentication, RBAC, OAuth2, token issuance | Ruby 3.4 / Rails 7.1      | `3001`       |
| [`evo-ai-crm-community`](./evo-ai-crm-community)                   | Conversations, contacts, inboxes, messaging  | Ruby 3.4 / Rails 7.1      | `3000`       |
| [`evo-ai-frontend-community`](./evo-ai-frontend-community)         | Web interface                                | React / TypeScript / Vite | `5173`       |
| [`evo-ai-processor-community`](./evo-ai-processor-community)       | AI agent execution, sessions, tools, MCP     | Python 3.10 / FastAPI     | `8000`       |
| [`evo-ai-core-service-community`](./evo-ai-core-service-community) | Agent management, API keys, folders          | Go / Gin                  | `5555`       |

### Design principles (Community Edition)

- **Single-tenant** — one account, no multi-tenancy overhead
- **No super-admin** — all configuration via seed data and environment variables
- **No billing / plans** — all limits removed, features unlocked by default
- **Role hierarchy**: `account_owner` and `agent` — no intermediate roles
- **Account resolution** via token — no `account-id` header required between services

---

## Getting started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/) with submodule support
- `make`

### 1. Clone with submodules

```bash
git clone --recurse-submodules git@github.com:EvolutionAPI/evo-crm-community.git
cd evo-crm-community
```

If you already cloned without submodules:

```bash
git submodule update --init --recursive
```

### 2. Update all submodules to latest

```bash
git submodule update --remote --merge
```

### 3. Configure environment

```bash
cp .env.example .env
```

### 4. Run setup

```bash
make setup
```

This single command builds all images, starts the infrastructure, runs database migrations and seeds all services in the correct order. The first run may take **15–20 minutes** depending on your machine and internet connection.

### 5. Access the application

Once setup completes, the platform is available at:

```
http://localhost:5173
```

For detailed configuration and production deployment instructions, visit the [full documentation](https://docs.evolutionfoundation.com.br).

---

## Cloud Storage (S3 / Cloudflare R2)

By default the platform stores uploaded files on the local filesystem. For production or to persist files across restarts, configure an S3-compatible storage backend (e.g. Cloudflare R2, DigitalOcean Spaces, MinIO).

Add the following variables to your `.env`:

```bash
ACTIVE_STORAGE_SERVICE=s3_compatible

STORAGE_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com   # Cloudflare R2 endpoint
STORAGE_BUCKET_NAME=your-bucket-name
STORAGE_ACCESS_KEY_ID=your-access-key-id
STORAGE_SECRET_ACCESS_KEY=your-secret-access-key
STORAGE_REGION=auto   # Use "auto" for Cloudflare R2; set region for AWS S3
```

Both `evo-auth` (profile photos) and `evo-crm` (message attachments) read these variables and must share the same bucket so that avatars and attachments are accessible across services.

> **Note:** When using local storage (`ACTIVE_STORAGE_SERVICE=local`) on Docker, files are stored in named volumes (`auth_storage` for the auth service, `crm_storage` for the CRM service) and persist across container restarts.

### Cloudflare R2 — Required CORS configuration

When using Cloudflare R2 as storage backend, you must configure CORS on your bucket so that the browser can upload files and load images directly from R2. In the R2 bucket settings (Cloudflare Dashboard → R2 → your bucket → Settings → CORS Policy), add:

```json
[
  {
    "AllowedOrigins": ["http://localhost:5173", "https://your-production-domain.com"],
    "AllowedMethods": ["GET", "PUT", "HEAD"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3600
  }
]
```

Without this CORS policy, avatar uploads and image messages will silently fail or produce 404 errors even when the Rails API returns a 200 response.

---

## Service dependencies

```
evo-ai-frontend-community
    └── evo-auth-service-community  (authentication)
    └── evo-ai-crm-community        (conversations, contacts)
    └── evo-ai-core-service-community (agents, tools, API keys)
    └── evo-ai-processor-community  (agent execution, sessions)
```

All inter-service communication uses Bearer token authentication. The token issued by `evo-auth-service-community` is forwarded between services — no additional headers required.

---

## Submodules reference

| Submodule                       | Repository                                                                                                  |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `evo-auth-service-community`    | [EvolutionAPI/evo-auth-service-community](https://github.com/EvolutionAPI/evo-auth-service-community)       |
| `evo-ai-crm-community`          | [EvolutionAPI/evo-ai-crm-community](https://github.com/EvolutionAPI/evo-ai-crm-community)                   |
| `evo-ai-frontend-community`     | [EvolutionAPI/evo-ai-frontend-community](https://github.com/EvolutionAPI/evo-ai-frontend-community)         |
| `evo-ai-processor-community`    | [EvolutionAPI/evo-ai-processor-community](https://github.com/EvolutionAPI/evo-ai-processor-community)       |
| `evo-ai-core-service-community` | [EvolutionAPI/evo-ai-core-service-community](https://github.com/EvolutionAPI/evo-ai-core-service-community) |

---

## Contributing

Contributions are welcome! Please open an issue or pull request in the relevant submodule repository.

Join the [community](https://evolutionfoundation.com.br/community) to discuss ideas, ask questions and collaborate.

Want to support the project? Visit [evolutionfoundation.com.br/contribute](https://evolutionfoundation.com.br/contribute).

## License

Apache 2.0 — see [LICENSE](./LICENSE) for details.

Made with love by [Evolution Foundation](https://evolutionfoundation.com.br).
