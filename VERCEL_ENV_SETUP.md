# 🚀 Configuração de Environment Variables - Vercel

## 📋 Visão Geral

Guia completo para configurar environment variables no Vercel baseado nas descobertas do pentest e melhores práticas de segurança.

---

## 🔥 Backend (API) - Environment Variables

### ⚠️ CRÍTICO - Rate Limiting & Segurança

```bash
# Security Headers (CRÍTICO - Pentest Finding)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10
RATE_LIMIT_LOGIN_REQUESTS_PER_MINUTE=5
RATE_LIMIT_LOGIN_BURST=2

# Security Headers (CRÍTICO - Pentest Finding)
SECURITY_HEADERS_ENABLED=true
SECURITY_CSP_DEFAULT_SRC="'self'"
SECURITY_HSTS_ENABLED=true
SECURITY_HSTS_MAX_AGE=31536000
```

### 🔐 Firebase Configuration

```bash
# Firebase (Método 1: Environment Variables - RECOMENDADO)
FIREBASE_PROJECT_ID=seu_project_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nSUA_CHAVE_AQUI\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@seu_project.iam.gserviceaccount.com
```

### 🗄️ Database & Cache

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/db
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=100

# Redis (Rate Limiting & Cache)
REDIS_URL=redis://host:6379/0
REDIS_CACHE_TTL=3600
REDIS_RATE_LIMIT_TTL=300
```

### 🛡️ Segurança Essencial

```bash
# Security
SECRET_KEY=sua_chave_secreta_minimo_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
DEBUG=false
```

### 🌐 CORS (Seguro)

```bash
# CORS Configuration
CORS_ALLOWED_ORIGINS=["https://dashboard.azo.inc", "https://dashboard-azo.vercel.app"]
CORS_ALLOWED_METHODS=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_ALLOWED_HEADERS=["Authorization", "Content-Type", "X-Requested-With"]
```

---

## 🎨 Frontend (Next.js) - Environment Variables

### 🔗 API Configuration

```bash
# API URL
NEXT_PUBLIC_API_URL=https://seu-backend.vercel.app
NEXT_PUBLIC_API_VERSION=v1
NEXT_PUBLIC_API_TIMEOUT=30000
```

### 🔥 Firebase Client

```bash
# Firebase Client (Frontend)
NEXT_PUBLIC_FIREBASE_API_KEY=sua_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=seu_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=seu_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=seu_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789012
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789012:web:abcdef123456
```

### 🔒 Segurança Frontend

```bash
# Security
NEXT_PUBLIC_ENABLE_CSP=true
NEXT_PUBLIC_CORS_MODE=strict
NEXT_PUBLIC_SESSION_TIMEOUT=1800000
NEXT_PUBLIC_ENVIRONMENT=production
```

---

## 🔧 Configuração Passo a Passo

### 1. Backend Vercel

1. **Acesse** Vercel Dashboard > Seu Projeto Backend
2. **Vá para** Settings > Environment Variables
3. **Adicione as variáveis:**

#### 🔴 CRÍTICO (Pentest Findings)
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_LOGIN_REQUESTS_PER_MINUTE=5
SECURITY_HEADERS_ENABLED=true
SECURITY_HSTS_ENABLED=true
```

#### 🟡 Essencial
```bash
FIREBASE_PROJECT_ID=seu_project_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
FIREBASE_CLIENT_EMAIL=firebase@seuprojeto.iam.gserviceaccount.com
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
SECRET_KEY=sua_chave_secreta_32_chars
```

### 2. Frontend Vercel

1. **Acesse** Vercel Dashboard > Seu Projeto Frontend  
2. **Vá para** Settings > Environment Variables
3. **Adicione as variáveis:**

```bash
NEXT_PUBLIC_API_URL=https://seu-backend.vercel.app
NEXT_PUBLIC_FIREBASE_PROJECT_ID=seu_project_id
NEXT_PUBLIC_FIREBASE_API_KEY=sua_api_key
NEXT_PUBLIC_ENABLE_CSP=true
NEXT_PUBLIC_ENVIRONMENT=production
```

---

## 🚨 Variáveis Obrigatórias (Mínimo para Funcionar)

### Backend
```bash
# Mínimo para funcionar
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
FIREBASE_PROJECT_ID=seu_project_id
FIREBASE_PRIVATE_KEY="sua_chave"
FIREBASE_CLIENT_EMAIL=firebase@seuprojeto.iam.gserviceaccount.com
SECRET_KEY=sua_chave_secreta_min_32_chars
```

### Frontend  
```bash
# Mínimo para funcionar
NEXT_PUBLIC_API_URL=https://seu-backend.vercel.app
NEXT_PUBLIC_FIREBASE_PROJECT_ID=seu_project_id
NEXT_PUBLIC_FIREBASE_API_KEY=sua_api_key
```

---

## ✅ Verificação Pós-Deploy

### 1. Testar Rate Limiting
```bash
# Fazer múltiplos logins - deve bloquear após 5 tentativas
curl -X POST https://seu-backend.vercel.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrong"}'
```

### 2. Verificar Security Headers
```bash
# Deve retornar headers de segurança
curl -I https://seu-backend.vercel.app/health
```

Headers esperados:
- `x-content-type-options: nosniff`
- `x-frame-options: DENY`
- `strict-transport-security: max-age=31536000`

### 3. Testar CORS
```bash
# Origem não permitida deve ser bloqueada
curl -H "Origin: https://evil.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Authorization" \
     -X OPTIONS https://seu-backend.vercel.app/api/v1/auth/login
```

---

## 🔧 Troubleshooting Comum

### ❌ "Rate limiting não funciona"
**Verifique:**
```bash
# Redis está configurado?
REDIS_URL=redis://host:6379/0

# Rate limiting está habilitado?
RATE_LIMIT_ENABLED=true
```

### ❌ "Firebase authentication falha"
**Verifique:**
```bash
# Chave privada com quebras de linha corretas
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nSUA_CHAVE\n-----END PRIVATE KEY-----\n"

# Project ID correto
FIREBASE_PROJECT_ID=seu_project_id
```

### ❌ "CORS bloqueando frontend"
**Verifique:**
```bash
# Origem do frontend está na lista
CORS_ALLOWED_ORIGINS=["https://seu-frontend.vercel.app"]

# Headers permitidos
CORS_ALLOWED_HEADERS=["Authorization", "Content-Type"]
```

### ❌ "Security headers ausentes"
**Verifique:**
```bash
# Middleware habilitado
SECURITY_HEADERS_ENABLED=true
SECURITY_HSTS_ENABLED=true
```

---

## 📊 Environment-Specific Values

### Development
```bash
DEBUG=true
RATE_LIMIT_ENABLED=false
SECURITY_HEADERS_ENABLED=false
LOG_LEVEL=DEBUG
```

### Production  
```bash
DEBUG=false
RATE_LIMIT_ENABLED=true
SECURITY_HEADERS_ENABLED=true
LOG_LEVEL=WARNING
```

---

## 🔄 Deploy Automatizado

### GitHub Actions (CI/CD)
```yaml
# .github/workflows/deploy.yml
- name: Deploy to Vercel
  uses: amondnet/vercel-action@v20
  with:
    vercel-token: ${{ secrets.VERCEL_TOKEN }}
    vercel-org-id: ${{ secrets.ORG_ID }}
    vercel-project-id: ${{ secrets.PROJECT_ID }}
    vercel-args: '--prod'
```

### Environment Variables no GitHub
```bash
# Secrets do GitHub
VERCEL_TOKEN=vercel_token
ORG_ID=vercel_org_id  
PROJECT_ID=vercel_project_id
```

---

## 🎯 Checklist Final

### ✅ Backend
- [ ] Rate limiting configurado
- [ ] Security headers habilitados  
- [ ] Firebase environment variables
- [ ] Database e Redis URLs
- [ ] CORS restritivo
- [ ] SECRET_KEY forte

### ✅ Frontend
- [ ] NEXT_PUBLIC_API_URL correto
- [ ] Firebase client config
- [ ] CSP habilitado
- [ ] Environment = production

### ✅ Segurança
- [ ] Sem valores reais no código
- [ ] Secrets no Vercel
- [ ] HTTPS forçado
- [ ] Headers de segurança

---

## 📞 Suporte

Se tiver problemas:

1. **Verifique os logs** no Vercel Functions
2. **Teste localmente** com as mesmas variáveis
3. **Consulte o pentest report** para vulnerabilidades
4. **Contate o time de segurança** se necessário

**📧 Email:** security@azo.inc  
**📱 Slack:** #security-alerts  

---

*Este guia deve ser atualizado após cada mudança crítica de segurança.*
