# Relatório de Análise para Whitelabel - Evo CRM Community

**Data:** 2024-05-24
**Analista:** EVO Master
**Projeto:** Evo CRM Community Monorepo

## 1. Introdução
Este documento detalha a análise técnica necessária para transformar o projeto Evo CRM Community em uma solução 100% Whitelabel. O objetivo é permitir que a marca "Evolution" ou "Evo CRM" seja facilmente substituída por qualquer outra identidade visual e nominal através de configurações simples.

## 2. Levantamento de Pontos de Marca (Branding)

### 2.1. Frontend (`evo-ai-frontend-community`)
O frontend é a área com maior visibilidade e contém diversas referências fixas.

*   **Ativos Estáticos (Public):**
    *   `public/logo.svg`: Logo principal do sistema.
    *   `public/favicon.svg`: Ícone do navegador.
    *   `public/hover-evolution.png`: Logo usado em estados específicos (como visto no README).
*   **Textos e Títulos:**
    *   `index.html`: O `<title>` está fixo como "Evo CRM".
    *   `src/components/layout/components/Sidebar.tsx`: Referência ao nome da empresa via i18n e link de suporte do WhatsApp fixo.
    *   `src/pages/Setup/OnboardingPage.tsx`: Imagem de logo com `alt="Evo CRM"`.
*   **Traduções (i18n):**
    *   `src/i18n/locales/*/layout.json`: Chave `"brand": "Evo CRM"`.
    *   `src/i18n/locales/*/onboarding.json`: Diversas referências ao nome em perguntas de setup.
    *   `src/i18n/locales/*/tours.json`: Títulos de tours de boas-vindas.

### 2.2. Backend CRM (`evo-ai-crm-community`)
O backend lida com comunicações externas (e-mails) e metadados de API.

*   **Configuração Global (`GlobalConfig`):**
    *   O sistema já possui uma estrutura de `GlobalConfig` que busca `BRAND_NAME` e `BRAND_URL`.
    *   Muitos controllers e serviços usam `GlobalConfig.get('BRAND_NAME') || 'Evolution'`.
*   **E-mails (Mailers):**
    *   `app/views/layouts/mailer/base.liquid`: Usa `global_config['BRAND_NAME']` e `BRAND_URL`.
    *   `app/views/mailers/`: Diversos templates em `.erb` e `.liquid` contêm o texto "Evolution" ou "Team Evolution" de forma fixa (ex: `account_deleted.liquid`).
*   **Seeds:**
    *   `db/seeds.rb`: Define nomes e e-mails de suporte padrão como `support@evolution.com`.

### 2.3. Backend Auth (`evo-auth-service-community`)
*   **Seeds:**
    *   `db/seeds.rb`: Cria a conta padrão com o nome "Evolution Community".
*   **Configurações de OAuth:**
    *   `config/initializers/doorkeeper.rb`: Realm definido como 'Evolution API'.

## 3. Estratégia de Implementação Sugerida

### 3.1. Centralização no Frontend
*   Implementar variáveis de ambiente `VITE_` para o nome da aplicação, logo URL e links de suporte.
*   Substituir as strings fixas nos arquivos de tradução por variáveis dinâmicas ou garantir que o `layout.json` seja a única fonte da verdade, alimentada pelo build/env.

### 3.2. Padronização no Backend
*   Assegurar que todas as referências a "Evolution" nos mailers utilizem o `GlobalConfig`.
*   Criar um serviço de "Branding" centralizado que retorne todos os assets e nomes, facilitando a alteração em um único lugar.

### 3.3. Configuração via .env
*   Expandir o `.env.example` para incluir:
    *   `BRAND_NAME`
    *   `BRAND_LOGO_URL`
    *   `BRAND_FAVICON_URL`
    *   `SUPPORT_EMAIL`
    *   `SUPPORT_WHATSAPP`

## 4. Checklist de Modificações

- [ ] Criar variáveis `VITE_APP_NAME` e `VITE_SUPPORT_URL` no frontend.
- [ ] Atualizar `Sidebar.tsx` para usar variáveis de ambiente ou config da API.
- [ ] Revisar todos os arquivos `.liquid` e `.erb` em `app/views/mailers` no CRM.
- [ ] Parametrizar os scripts de `seeds.rb` para ler do `.env`.
- [ ] Criar documentação específica para o processo de troca de marca (Setup Whitelabel).

---
*Relatório gerado automaticamente pelo EVO Master.*
