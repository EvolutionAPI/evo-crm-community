# Wizz Branding Audit

Date: 2026-05-06

## Result
Wizz branding **is present** in this repository and submodules.

## Key evidence
- Root README and links:
  - `README.md` contains `WizzDesk`, `wizzcomms.com`, docs/community/contribute links.
- Frontend branding:
  - `evo-ai-frontend-community/index.html` title/description with `WizzDesk`.
  - `evo-ai-frontend-community/public/` includes `logo.png`, `logo.svg`, `logo-dark.png`, `logo-icon.png`.
  - Multiple UI files use logo alt text as `WizzDesk`.
- CRM backend branding:
  - `evo-ai-crm-community/config/installation_config.yml` defines `BRAND_NAME=WizzDesk`, brand URLs and logo paths.
  - `evo-ai-crm-community/lib/tasks/branding.rake` defaults to WizzDesk brand values.
  - `evo-ai-crm-community/public/manifest.json` uses `WizzDesk` for app name.
  - `evo-ai-crm-community/db/seeds.rb` sets default account name to `WizzDesk`.
- Root assets:
  - `public/logo.png`, `public/logo.svg`, `public/logo-dark.png`, `public/logo-icon.png`.

## Notes
- This audit intentionally tracks branding presence only.
- No rebrand changes were applied.
