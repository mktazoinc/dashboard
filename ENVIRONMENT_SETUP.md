# 🚀 Setup de Environment Variables - Simplificado

## 📋 Resumo Rápido

**Firebase**: Use environment variables diretas (não precisa do JSON)  
**Vercel**: A maioria das variáveis é automática com GitHub integration  
**Backend**: Só as essenciais (DB, Redis, APIs externas)  

---

## 🔥 Firebase - Setup Simplificado

### Opção 1: Environment Variables (Recomendado)

No Firebase Console > Project Settings > Service Accounts:
1. Clique "Generate new private key"
2. Copie os valores do JSON para as variáveis:

```bash
# backend/.env
FIREBASE_PROJECT_ID=seu-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
SUA_CHAVE_PRIVADA_AQUI
-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@seu-project.iam.gserviceaccount.com
```

### Opção 2: Firebase Client SDK (Frontend apenas)

Se só precisa de autenticação, use só no frontend:

```javascript
// frontend/.env.local
NEXT_PUBLIC_FIREBASE_API_KEY=sua_api_key
NEXT_PUBLIC_FIREBASE_PROJECT_ID=seu_project_id
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=seu_project.firebaseapp.com
```

---

## 🚀 Vercel - Setup Automático

### Frontend (Next.js)
No dashboard Vercel > Settings > Environment Variables:

```bash
# Essenciais
NEXT_PUBLIC_API_URL=https://seu-backend.vercel.app
NEXT_PUBLIC_FIREBASE_API_KEY=sua_api_key
NEXT_PUBLIC_FIREBASE_PROJECT_ID=seu_project_id

# Opcional (se usar Firebase Client SDK)
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=seu_project.firebaseapp.com
```

### Backend (FastAPI)
Se usar Vercel para o backend:

```bash
# Banco de dados
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379

# APIs externas
SUPABASE_URL=https://seuprojeto.supabase.co
SUPABASE_SERVICE_KEY=sua_service_key

# Segurança
SECRET_KEY=sua_chave_secreta
```

---

## 🛠️ Configuração Mínima Funcional

### Para Desenvolvimento Local:

```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
FIREBASE_PROJECT_ID=seu_project_id
FIREBASE_PRIVATE_KEY="sua_chave_privada"
FIREBASE_CLIENT_EMAIL=firebase@seuprojeto.iam.gserviceaccount.com
SECRET_KEY=chave_secreta

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Para Produção (Vercel):

```bash
# Frontend Vercel Variables
NEXT_PUBLIC_API_URL=https://backend.vercel.app
NEXT_PUBLIC_FIREBASE_PROJECT_ID=seu_project_id

# Backend Vercel Variables
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
FIREBASE_PROJECT_ID=seu_project_id
FIREBASE_PRIVATE_KEY="sua_chave_privada"
FIREBASE_CLIENT_EMAIL=firebase@seuprojeto.iam.gserviceaccount.com
```

---

## ✅ O que você NÃO precisa se usar Vercel + GitHub:

❌ `VERCEL_URL` - Automático  
❌ `VERCEL_ENV` - Automático  
❌ GitHub tokens - Automático com integration  
❌ Build configs - Detectado automaticamente  

---

## 🔧 Troubleshooting Comum

### Firebase: "Invalid credentials"
- Verifique se a private key tem as quebras de linha corretas
- Use aspas duplas no .env: `"-----BEGIN..."`
- Confirme o project_id está correto

### Vercel: "Database connection failed"
- Use URL completa com postgresql:// (não postgres+asyncpg)
- Verifique se o IP está na allowlist do database
- Teste a conexão local primeiro

### CORS: "No Access-Control-Allow-Origin"
- Adicione o domínio Vercel em ALLOWED_ORIGINS
- Use NEXT_PUBLIC_ para variáveis do frontend

---

## 📱 Exemplo Prático

### 1. Firebase Console
```bash
# Pegue estes 3 valores:
Project ID: dashboard-azo-123
Private Key: -----BEGIN PRIVATE KEY-----...
Client Email: firebase-adminsdk-abc@dashboard-azo-123.iam.gserviceaccount.com
```

### 2. Vercel Frontend
```bash
NEXT_PUBLIC_API_URL=https://dashboard-azo-api.vercel.app
NEXT_PUBLIC_FIREBASE_PROJECT_ID=dashboard-azo-123
```

### 3. Vercel Backend
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
FIREBASE_PROJECT_ID=dashboard-azo-123
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-abc@dashboard-azo-123.iam.gserviceaccount.com
```

**Pronto! Sistema funcionando sem arquivos JSON extras.** 🎉
