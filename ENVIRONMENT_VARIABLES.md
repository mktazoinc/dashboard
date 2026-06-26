# Variáveis de Ambiente — Dashboard Azo

> **Arquivo de referência.**  
> Não contém valores reais. Configure os valores nos painéis do Vercel, Firebase, GitHub Secrets e backend Python.

---

## ⚠️ Avisos de segurança

- **NUNCA** comite arquivos `.env`, `.env.local`, `.env*.local` ou qualquer valor real de segredo no repositório.
- Este arquivo é um **template**. Os valores reais devem ser inseridos nos dashboards de cada plataforma.
- Credenciais de produção (senhas, tokens, client secrets) devem ser tratadas como segredos.
- Para desenvolvimento local, crie arquivos `.env.local` no `frontend/` e `backend/` e inclua `.env*` no `.gitignore`.
- Compartilhe segredos reais apenas por canais seguros (cofre de senhas, Vercel/Firebase dashboard, GitHub Secrets, Cloud Run secrets) — **não pelo chat**.

---

## Legenda

| Prefixo | Significado | Exemplo |
|---|---|---|
| `NEXT_PUBLIC_*` | Visível no client (navegador). | Configuração pública do Firebase. |
| Sem prefixo | Apenas server-side (Vercel/Next.js ou Python). | Senhas de APIs, tokens. |
| `GITHUB_*` | Configurado em GitHub > Settings > Secrets and variables > Actions. | Tokens de deploy. |

---

## 1. GitHub Secrets (CI/CD)

Configurar em: `Repositório > Settings > Secrets and variables > Actions > New repository secret`.

| Nome | Obrigatório | Origem | Descrição |
|---|---|---|---|
| `VERCEL_TOKEN` | Sim | Vercel | Token para deploy do frontend via GitHub Actions. |
| `VERCEL_ORG_ID` | Sim | Vercel | ID da organização/equipe. |
| `VERCEL_PROJECT_ID` | Sim | Vercel | ID do projeto no Vercel. |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Sim | Firebase | JSON da service account do Firebase Admin SDK. |
| `SUPABASE_DATABASE_URL` | Sim | Supabase | URL completa de conexão PostgreSQL. |
| `REDIS_URL` | Sim | Upstash | URL do Redis (ex.: `redis://...` ou `rediss://...`). |
| `SIENGE_PASSWORD` | Sim | Sienge | Senha da conta Sienge. |
| `META_APP_SECRET` | Sim | Meta | App Secret do app Meta. |
| `META_ACCESS_TOKEN` | Sim | Meta | Long-lived access token. |
| `GOOGLE_CLIENT_SECRET` | Sim | Google | Client Secret do OAuth 2.0. |
| `GOOGLE_ADS_REFRESH_TOKEN` | Sim | Google | Refresh Token. |
| `GCP_SA_KEY` | Sim | Google Cloud | JSON da service account para deploy no Cloud Run (se usar Cloud Run). |
| `FLY_API_TOKEN` | Alternativa | Fly.io | Token para deploy no Fly.io (se usar Fly.io). |

**Exemplo de `SUPABASE_DATABASE_URL`:**
```
postgresql://postgres.gmvmdryoisurvhtdrppb:SENHA_AQUI@aws-1-sa-east-1.pooler.supabase.com:6543/postgres
```

---

## 2. Vercel Environment Variables (frontend Next.js)

Configurar em: `Projeto Vercel > Settings > Environment Variables`.

### 2.1 Firebase público (client-side)

| Nome | Obrigatório | Origem | Descrição |
|---|---|---|---|
| `NEXT_PUBLIC_FIREBASE_API_KEY` | Sim | Firebase | `apiKey`. |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | Sim | Firebase | `authDomain`. |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Sim | Firebase | `projectId`. |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | Sim | Firebase | `storageBucket`. |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | Sim | Firebase | `messagingSenderId`. |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | Sim | Firebase | `appId`. |
| `NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID` | Opcional | Firebase | `measurementId`. |

### 2.2 Firebase server-side

| Nome | Obrigatório | Origem | Descrição |
|---|---|---|---|
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Sim | Firebase | JSON da service account. |

### 2.3 APIs externas (server-side no Next.js)

| Nome | Obrigatório | Descrição |
|---|---|---|
| `API_BASE_URL` | Sim | URL do backend Python FastAPI, ex: `https://api-dashboard-azo-xxx.run.app` ou `https://dashboard-azo.fly.dev`. |
| `SUPABASE_DATABASE_URL` | Sim | URL do PostgreSQL do Supabase. |
| `REDIS_URL` | Sim | URL do Redis/Upstash. |
| `SIENGE_API_BASE_URL` | Sim | Base URL da Sienge. |
| `SIENGE_USERNAME` | Sim | Usuário Sienge. |
| `SIENGE_PASSWORD` | Sim | Senha Sienge. |
| `SIENGE_SUBDOMAIN` | Sim | Subdomain Sienge. |
| `META_APP_ID` | Sim | App ID Meta. |
| `META_APP_SECRET` | Sim | App Secret Meta. |
| `META_ACCESS_TOKEN` | Sim | Access token Meta. |
| `META_AD_ACCOUNT_ID` | Sim | ID da conta de anúncio. |
| `GOOGLE_CLIENT_ID` | Sim | Client ID Google. |
| `GOOGLE_CLIENT_SECRET` | Sim | Client Secret Google. |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Sim | Developer Token Google Ads. |
| `GOOGLE_ADS_CUSTOMER_ID` | Sim | Customer ID Google Ads. |
| `GOOGLE_ADS_REFRESH_TOKEN` | Sim | Refresh Token Google Ads. |
| `ADMIN_SEED_EMAIL` | Sim | E-mail do Mestre do Universo. |
| `ADMIN_SEED_PASSWORD` | Sim | Senha temporária. |

---

## 3. Backend Python (FastAPI) — Environment Variables

Configurar no Cloud Run, Fly.io ou `.env` local no diretório `backend/`.

| Nome | Obrigatório | Descrição |
|---|---|---|
| `PORT` | Sim | Porta da aplicação (ex.: `8000`). Cloud Run injeta automaticamente. |
| `ENVIRONMENT` | Sim | `development`, `staging` ou `production`. |
| `CORS_ORIGINS` | Sim | Domínios permitidos, ex: `https://dashboard-azo.vercel.app,http://localhost:3000`. |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Sim | JSON da service account Firebase. |
| `SUPABASE_DATABASE_URL` | Sim | URL do PostgreSQL do Supabase. |
| `REDIS_URL` | Sim | URL do Redis. |
| `SIENGE_API_BASE_URL` | Sim | Base URL da Sienge. |
| `SIENGE_USERNAME` | Sim | Usuário Sienge. |
| `SIENGE_PASSWORD` | Sim | Senha Sienge. |
| `SIENGE_SUBDOMAIN` | Sim | Subdomain Sienge. |
| `META_APP_ID` | Sim | App ID Meta. |
| `META_APP_SECRET` | Sim | App Secret Meta. |
| `META_ACCESS_TOKEN` | Sim | Access token Meta. |
| `META_AD_ACCOUNT_ID` | Sim | ID da conta de anúncio. |
| `GOOGLE_CLIENT_ID` | Sim | Client ID Google. |
| `GOOGLE_CLIENT_SECRET` | Sim | Client Secret Google. |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Sim | Developer Token. |
| `GOOGLE_ADS_CUSTOMER_ID` | Sim | Customer ID. |
| `GOOGLE_ADS_REFRESH_TOKEN` | Sim | Refresh Token. |
| `ADMIN_SEED_EMAIL` | Sim | E-mail do Mestre do Universo. |
| `ADMIN_SEED_PASSWORD` | Sim | Senha temporária. |

---

## 4. Firebase Console — Configurações manuais

### 4.1 Authentication
- Habilitar **Email/Password** provider.
- Configurar templates de e-mail (recuperação de senha).
- Definir **Authorized domains** (domínios Vercel, Cloud Run, Fly.io, localhost).

### 4.2 Firestore Database
- Criar banco em modo **production**.
- Configurar **Security Rules** iniciais (bloquear tudo, liberar por autenticação/role).
- No free tier, exportar dados periodicamente via script de backup.

### 4.3 Storage
- Criar bucket padrão.
- Configurar **Security Rules** para upload apenas de usuários autenticados.
- Limitar PNG e 5MB.

### 4.4 Service Account
- Firebase Project Settings > Service Accounts > Generate new private key.
- Esse JSON é o valor de `FIREBASE_SERVICE_ACCOUNT_JSON`.

---

## 5. Desenvolvimento local

### 5.1 Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=...
NEXT_PUBLIC_FIREBASE_PROJECT_ID=...
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=...
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=...
NEXT_PUBLIC_FIREBASE_APP_ID=...
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 5.2 Backend (`backend/.env`)

```env
ENVIRONMENT=development
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
FIREBASE_SERVICE_ACCOUNT_JSON={...}
SUPABASE_DATABASE_URL=postgresql://...:...@.../postgres
REDIS_URL=redis://localhost:6379

SIENGE_API_BASE_URL=https://api.sienge.com.br/
SIENGE_USERNAME=...
SIENGE_PASSWORD=...
SIENGE_SUBDOMAIN=...

META_APP_ID=...
META_APP_SECRET=...
META_ACCESS_TOKEN=...
META_AD_ACCOUNT_ID=...

GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_ADS_DEVELOPER_TOKEN=...
GOOGLE_ADS_CUSTOMER_ID=...
GOOGLE_ADS_REFRESH_TOKEN=...

ADMIN_SEED_EMAIL=...
ADMIN_SEED_PASSWORD=...
```

---

## 6. Checklist de configuração

- [ ] Criar projeto Firebase (Auth, Firestore, Storage).
- [ ] Criar projeto Vercel e vincular ao repositório GitHub.
- [ ] Criar backend Python FastAPI e configurar deploy no Cloud Run ou Fly.io.
- [ ] Criar instância Redis na Upstash (free tier).
- [ ] Configurar GitHub Secrets para CI/CD.
- [ ] Configurar Vercel Environment Variables.
- [ ] Configurar variáveis do backend Python.
- [ ] Configurar Firebase Authentication, Firestore Rules e Storage Rules.
- [ ] Configurar Supabase connection string.
- [ ] Configurar credenciais Sienge.
- [ ] Criar app Meta e configurar OAuth/token.
- [ ] Criar projeto Google Cloud, ativar Google Ads API e configurar OAuth.
- [ ] Criar seed do Mestre do Universo.
