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

- **Docker — `auth_storage`**: substituído volume nomeado por bind mount, corrigindo `permission denied` ao gravar arquivos no serviço de autenticação. Bind mount estendido também para o `sidekiq` com `mkdir` defensivo no entrypoint. (#65, #72)
- **Docker — Alpine compat**: trocado `bash -c` por `sh -c` em scripts internos para compatibilidade com imagens Alpine. (#31)
- **Docker — healthcheck**: corrigido path do healthcheck do `evo-core`. (#26)
- **Env validation (EVO-985)**: bloqueio de `BACKEND_URL` / `FRONTEND_URL` apontando para `localhost` em produção — falha rápida no boot ao invés de servir URLs inválidas para clientes externos. (#75)
- **Submodules**: retargeting de SHAs órfãos para branches públicas (`develop` / `main`). Eliminado erro de checkout no CI causado por SHAs perdidos.

### Changed

- **CI**: workflow `validate-compose` e `lint-dockerfiles` agora rodam em PRs contra `develop` (não só `main`). (#59)
- **Submódulos**: bumps coordenados para incorporar correções dos serviços individuais ao longo do ciclo (Evolution Go admin cleanup, EVO-975, EVO-1005, EVO-1012, etc.).

### Pendente para a tag final

- PR #69 (`fix(setup): seed sequence`) — em rebase com `develop` no momento do corte. Pode ser incluída via fast-follow se rebase estiver pronto antes da tag.

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
