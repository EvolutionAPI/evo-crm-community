# Changelog

All notable changes to **evo-crm-community** (umbrella) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Este repositório é o guarda-chuva da família CRM Community: orquestra os 7 submódulos via Docker Compose. Para detalhes por serviço, ver `CHANGELOG.md` dentro de cada submódulo.

## [Unreleased]

### Added

- N/A

### Changed

- N/A

### Fixed

- N/A

## [v1.0.0-rc2] - 2026-05-05

Release de estabilização posterior ao `v1.0.0-rc1` (2026-04-24). Foco em fixes de Docker / setup, atualização coordenada dos submódulos e correções de orquestração para deploy em produção.

### Fixed

- **`Makefile` — sequência de setup do banco**: `make setup` agora cria o DB no CRM, faz `db:schema:load` (carrega o schema mestre, incluindo todas as tabelas que o auth-service usa), marca migrations do auth como aplicadas via `rails runner` com `.sort` determinístico e `rescue ActiveRecord::RecordNotUnique` específico, e só então faz `db:seed` no CRM seguido do auth. Sem isso, `make setup` em fresh install falhava com `PG::UndefinedTable: roles`. (cherry-pick do PR #69 — autoria de @andersonlemesc preservada)
- **Docker — `auth_storage`**: substituído volume nomeado por bind mount, corrigindo `permission denied` ao gravar arquivos no serviço de autenticação. Bind mount estendido também para o `sidekiq` com `mkdir` defensivo no entrypoint. (#65, #72)
- **Docker — Alpine compat**: trocado `bash -c` por `sh -c` em scripts internos para compatibilidade com imagens Alpine. (#31)
- **Docker — healthcheck**: corrigido path do healthcheck do `evo-core`. (#26)
- **Env validation (EVO-985)**: bloqueio de `BACKEND_URL` / `FRONTEND_URL` apontando para `localhost` em produção — falha rápida no boot ao invés de servir URLs inválidas para clientes externos. (#75)
- **Submodules**: retargeting de SHAs órfãos para branches públicas (`develop` / `main`). Eliminado erro de checkout no CI causado por SHAs perdidos.

### Changed

- **CI**: workflow `validate-compose` e `lint-dockerfiles` agora rodam em PRs contra `develop` (não só `main`). (#59)
- **Submódulos**: bumps coordenados ao longo da janela do rc2 para incorporar todas as correções dos serviços individuais — ver changelog de cada submódulo para detalhes:
  - `evo-ai-crm-community`: 17 PRs (incluindo automation rules EVO-989, navigation EVO-1007, idempotent migrations, EvoGo fixes, contact import, etc.)
  - `evo-ai-frontend-community`: 9 PRs (UI / UX, brand colors, automation UI, role select, team members, etc.)
  - `evo-auth-service-community`: novo role `super_admin` + migration de upgrade automático para PROD existente, fix de password forwarding na criação de user
  - `evo-ai-processor-community`: `python -m` para alembic/uvicorn + idempotência
  - Demais submódulos: ajustes de CI

### Notas para upgrade de PROD existente

- O `db:migrate` do `evo-auth-service-community` neste release **promove o usuário bootstrap original para o novo role `super_admin`** e revoga seus tokens ativos — operador será forçado a fazer logout/login uma vez na primeira requisição após o upgrade. Isso é esperado e necessário para o JWT refletir o novo role.
- Outros usuários `account_owner` perdem acesso ao painel `/settings/admin` — comportamento intencional (panel reservado a operação de instalação, não a gestão de conta).

## [v1.0.0-rc1] - 2026-04-24

### Added

- Primeiro release candidate público do **CRM Community**.
- Composição inicial de 7 submódulos via Docker Compose:
  - `evo-ai-crm-community`
  - `evo-ai-frontend-community`
  - `evo-ai-core-service-community`
  - `evo-ai-processor-community`
  - `evo-auth-service-community`
  - `evo-bot-runtime`
  - `evolution-api`, `evolution-go` (provedores WhatsApp)
- `Makefile` com targets de setup, seed, dashboard.
- Scripts de bootstrap (`setup.sh`) e exemplos de `docker-compose` (dev, prod-test, swarm).
- Templates de `.env` e licença `Apache 2.0`.

---

[Unreleased]: https://github.com/EvolutionAPI/evo-crm-community/compare/v1.0.0-rc2...HEAD
[v1.0.0-rc2]: https://github.com/EvolutionAPI/evo-crm-community/compare/v1.0.0-rc1...v1.0.0-rc2
[v1.0.0-rc1]: https://github.com/EvolutionAPI/evo-crm-community/releases/tag/v1.0.0-rc1
