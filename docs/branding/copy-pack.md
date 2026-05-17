# WizzDesk — Copy Pack

> Referência canónica de toda a copy de marca do WizzDesk.
> Usado para preencher os overlays en-GB, seeds, env vars e meta tags.
> Actualizado em: 2026-05-17

---

## 1. Identidade central (imutável em ambos os idiomas)

| Campo              | Valor                          |
|--------------------|-------------------------------|
| Nome do produto    | **WizzDesk**                   |
| Empresa-mãe        | **Wizz! comms.**               |
| Tagline (pt-BR)    | **Comunica. Cresce. Repete.**  |
| Tagline (en-GB)    | **Communicate. Grow. Repeat.** |
| Site institucional | https://wizzcomms.com          |
| App / produto      | https://desk.wizzcomms.com     |
| Suporte público    | support@wizzcomms.com          |
| Transacional       | noreply@wizzcomms.com          |
| Cor primária       | #FF4500 (Wizz Orange)          |
| Font               | Space Grotesk                  |

---

## 2. Meta tags / SEO

### `evo-ai-frontend-community/index.html`

| Campo            | pt-BR (estado actual)                                         | en-GB (a implementar)                                           |
|------------------|---------------------------------------------------------------|-----------------------------------------------------------------|
| `<title>`        | WizzDesk                                                      | WizzDesk                                                        |
| `<meta name="description">` | WizzDesk — Central de atendimento AI para o teu negócio | WizzDesk — AI-powered customer service for your business |

### `evo-ai-crm-community/public/manifest.json`

| Campo              | Valor                   |
|--------------------|------------------------|
| `name`             | WizzDesk               |
| `short_name`       | WizzDesk               |
| `theme_color`      | #FF4500 *(a alterar)*  |
| `background_color` | #FF4500 *(a alterar)*  |

---

## 3. Footer & copyright

Chave i18n: `layout.sidebar.footer.*`

| Chave           | pt-BR                                         | en-GB                                         |
|-----------------|-----------------------------------------------|-----------------------------------------------|
| `brand`         | WizzDesk                                      | WizzDesk                                      |
| `copyright`     | © {{year}} Wizz! comms. Todos os direitos reservados. | © {{year}} Wizz! comms. All rights reserved. |
| `documentation` | Documentação                                  | Documentation                                 |
| `support`       | Preciso de suporte                            | I need support                                |

---

## 4. Setup wizard (primeiro admin)

Chave i18n: `setup.*`

| Chave            | pt-BR                                                                 | en-GB                                                                      |
|------------------|-----------------------------------------------------------------------|----------------------------------------------------------------------------|
| `title`          | Configure sua instância                                               | Set up your instance                                                       |
| `subtitle`       | Crie a conta de administrador para começar                           | Create your administrator account to get started                          |
| `form.submit.idle` | Criar conta e continuar                                            | Create account and continue                                               |
| `form.submit.loading` | Configurando...                                               | Setting up…                                                               |
| `success.title`  | Configuração concluída!                                               | Setup complete!                                                            |
| `success.description` | Agora você pode entrar com suas credenciais.                  | You can now sign in with your credentials.                                |
| `error.generic`  | Ocorreu um erro durante a configuração. Tente novamente.              | An error occurred during setup. Please try again.                         |
| `error.alreadySetup` | Esta instância já foi configurada.                               | This instance has already been set up.                                    |
| `footer`         | Isso criará a conta de administrador da sua instância WizzDesk.      | This will create the administrator account for your WizzDesk instance.    |

---

## 5. Autenticação

Chave i18n: `auth.*`

| Chave                          | pt-BR                                              | en-GB                                                |
|--------------------------------|----------------------------------------------------|------------------------------------------------------|
| `auth.login.title`             | Entrar na sua conta                                | Sign in to your account                              |
| `auth.login.subtitle`          | Digite suas credenciais para acessar o sistema     | Enter your credentials to access the system          |
| `auth.login.signIn`            | Entrar                                             | Sign in                                              |
| `auth.register.title`          | Criar nova conta                                   | Create new account                                   |
| `auth.register.subtitle`       | Preencha os dados para criar sua conta             | Fill in your details to create an account            |
| `auth.register.createAccount`  | Criar conta                                        | Create account                                       |
| `auth.forgotPassword.title`    | Recuperar senha                                    | Reset your password                                  |
| `auth.forgotPassword.subtitle` | Digite seu email para receber as instruções de recuperação | Enter your email address to receive reset instructions |
| `auth.sessionExpired.title`    | Sessão expirada                                    | Session expired                                      |
| `auth.sessionExpired.description` | Sua sessão expirou. Faça login novamente para continuar. | Your session has expired. Please sign in again to continue. |

---

## 6. Onboarding / survey inicial

Chave i18n: `onboarding.survey.*`

| Chave                    | pt-BR                                              | en-GB                                                  |
|--------------------------|----------------------------------------------------|--------------------------------------------------------|
| `title`                  | Personalize sua experiência                        | Personalise your experience                            |
| `subtitle`               | Essas perguntas nos ajudam a configurar o sistema de acordo com a sua operação. | These questions help us configure the system to suit your operation. |
| `goal.label`             | Qual é o seu principal objetivo com o WizzDesk?    | What is your main goal with WizzDesk?                  |
| `goal.options[0]`        | Organizar o atendimento                            | Organise customer service                              |
| `goal.options[1]`        | Automatizar com IA                                 | Automate with AI                                       |
| `goal.options[2]`        | Escalar a equipe                                   | Scale the team                                         |
| `goal.options[3]`        | Centralizar canais                                 | Centralise channels                                    |
| `pain.options[1]`        | Atendimento desorganizado                          | Disorganised service                                   |

> **Nota:** Apenas strings com diferença de ortografia britânica (organise/ise, centralise, personalise) ou com menção explícita ao produto precisam estar no overlay en-GB. O resto herda de `en/`.

---

## 7. Documentação in-app

Chave i18n: `documentation.*`

| Chave                 | pt-BR                                             | en-GB                                                     |
|-----------------------|---------------------------------------------------|-----------------------------------------------------------|
| `title`               | Introdução ao WizzDesk                            | Introduction to WizzDesk                                  |
| `welcome.title`       | 🚀 Bem-vindo ao WizzDesk!                         | 🚀 Welcome to WizzDesk!                                   |
| `welcome.description` | Esta documentação irá guiá-lo por todos os recursos e funcionalidades da nossa plataforma. | This documentation will guide you through all the features and resources of our platform. |
| `whatIs.title`        | O que é o WizzDesk?                               | What is WizzDesk?                                         |
| `whatIs.description`  | O WizzDesk é a sua plataforma de suporte ao cliente tudo-em-um, criada para equipas que gerem conversas via WhatsApp, Instagram, email e mais — com IA no centro. | WizzDesk is your all-in-one customer support platform, built for teams that manage conversations across WhatsApp, Instagram, email, and more — with AI at the core. |
| `support.email`       | Email: support@wizzcomms.com                      | Email: support@wizzcomms.com                              |

---

## 8. Perfil / API Token

Chave i18n: `profile.accessToken.*`

| Chave         | pt-BR                                                                           | en-GB                                                                             |
|---------------|---------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| `title`       | Token de Acesso à API                                                           | API Access Token                                                                  |
| `description` | Use este token para acessar a API do WizzDesk. Guarde-o em segurança e não compartilhe. | Use this token to access the WizzDesk API. Keep it secure and do not share it. |

---

## 9. Emails transacionais (mailers — via GlobalConfig)

Estes valores são injectados via `global_config['BRAND_NAME']` e `global_config['BRAND_URL']` no `base.liquid`. Não há strings hardcoded — apenas a configuração env/DB.

| Variável env / DB key | Valor              |
|-----------------------|--------------------|
| `BRAND_NAME`          | WizzDesk           |
| `BRAND_URL`           | https://wizzcomms.com |
| `MAILER_SUPPORT_EMAIL` | support@wizzcomms.com |
| `MAILER_SENDER_EMAIL` *(env)* | noreply@wizzcomms.com |

### Textos em que `BRAND_NAME` aparece nos mailers

| Ficheiro mailer                                  | Localização                  |
|--------------------------------------------------|------------------------------|
| `layouts/mailer/base.liquid`                     | Footer "Powered by {{BRAND_NAME}}" |
| `email_collect.rb` (fallback hardcoded)          | Lines 20, 32 — `|| 'WizzDesk'` *(a corrigir nos .rb)* |
| `dynamic_oauth_service.rb` (fallback hardcoded)  | Line 88 — `'WizzDesk'` *(a corrigir)* |

---

## 10. Seeds (first-run one-shot)

### `evo-ai-crm-community/db/seeds.rb`

| Linha | Campo               | Valor actual (stale)              | Valor correcto          |
|-------|---------------------|-----------------------------------|-------------------------|
| 42    | lookup email        | support@evo-auth-service-community.com | support@wizzcomms.com |
| 45    | lookup email (dup.) | support@evo-auth-service-community.com | support@wizzcomms.com |
| 58    | default inbox name  | Acme Support                      | WizzDesk Support        |

### `evo-auth-service-community/db/seeds.rb`

| Linha | Campo          | Valor actual (stale)                   | Valor correcto              |
|-------|----------------|----------------------------------------|-----------------------------|
| 3     | puts banner    | Seeding Evo Auth Service (Community)...| Seeding Wizz! comms. Auth... |
| 16    | account name   | Evolution Community                    | Wizz! comms.               |
| 18    | support_email  | support@evolution.com                  | support@wizzcomms.com       |

---

## 11. Env vars (raiz `.env.example`)

| Chave                  | Valor                             |
|------------------------|-----------------------------------|
| `BRAND_NAME`           | WizzDesk                          |
| `ORGANIZATION_NAME`    | Wizz! comms.                      |
| `ORGANIZATION_URL`     | https://wizzcomms.com             |
| `MAILER_SENDER_EMAIL`  | noreply@wizzcomms.com             |
| `SMTP_DOMAIN`          | wizzcomms.com                     |
| `MFA_ISSUER`           | WizzDesk                          |
| `API_DESCRIPTION`      | WizzDesk API                      |
| `TERMS_URL`            | https://wizzcomms.com/terms       |
| `PRIVACY_URL`          | https://wizzcomms.com/privacy     |

### `evo-ai-crm-community/.env.example` (patches adicionais)

| Chave                  | Valor stale                       | Valor correcto              |
|------------------------|-----------------------------------|-----------------------------|
| `ANDROID_BUNDLE_ID`    | com.chatwoot.app                  | com.wizzcomms.wizzdesk      |
| `MAILER_SENDER_EMAIL`  | noreply@evolution-api.com         | noreply@wizzcomms.com       |

### `evo-auth-service-community/.env.example`

| Chave                 | Valor stale                    | Valor correcto         |
|-----------------------|--------------------------------|------------------------|
| `MAILER_SENDER_EMAIL` | noreply@evo-auth-service.com   | noreply@wizzcomms.com  |

---

## 12. Strings hardcoded a manter sem alteração

As 67 ocorrências de **"Evolution API"** nos locale JSONs (`channels`, `integrations`, `whatsapp`, `adminSettings`) referem-se ao gateway externo de WhatsApp Evolution API — um produto de terceiros que o WizzDesk integra. **Não alterar.**

A string de health check em `useChannelSubmission.ts`:
> `'Health check falhou. Verifique se a URL da Evolution API está correta e acessível.'`

É igualmente sobre o produto externo. **Manter como está.**

---

## 13. Voz e tom da marca

### pt-BR
- Directo, próximo, sem floreio
- Frases curtas (≤12 palavras idealmente)
- Tratamento: "você" (não "tu")
- Imperativo de respeito: "Configure", "Crie", "Entre"
- Nunca: "hey!", "incrível!", "fantástico!"
- Tom: "Comunica. Cresce. Repete." — seco, confiante

### en-GB
- British English: **colour, organise, customise, licence (noun), practice (noun), centre, behaviour**
- Same direct tone — no exclamation padding
- "Sign in" (not "Log in"), "Forgot password" (not "Forgot your password?")
- CTAs: no trailing period on short phrases ("Create account", "Sign in")
- Formal register where US would say "awesome": use "excellent" or omit altogether
- Dates: DD/MM/YYYY when contextually needed
