# Configuração do Firebase Project

Este guia explica como configurar o Firebase para o Dashboard AZO.

## 1. Criar Projeto Firebase

1. Acesse [Firebase Console](https://console.firebase.google.com/)
2. Clique em "Adicionar projeto"
3. Nome do projeto: `dashboard-azo-prod`
4. Continue com as configurações padrão
5. Ative Google Analytics para o projeto

## 2. Configurar Authentication

1. No menu lateral, vá para **Authentication** → **Sign-in method**
2. Habilite **Email/Password**
3. Configure domínios autorizados em **Configurações** → **Domínios autorizados**:
   - `localhost` (desenvolvimento)
   - `seu-dominio.vercel.app` (produção)

## 3. Configurar Firestore

1. Vá para **Firestore Database** → **Criar banco de dados**
2. Escolha **Iniciar em modo de teste** (temporarily)
3. Selecione uma localização (ex: `southamerica-east1`)
4. Crie as coleções iniciais:
   - `users` (para metadados adicionais)
   - `audit_logs` (para logs de auditoria)

## 4. Configurar Storage

1. Vá para **Storage** → **Começar**
2. Escolha **Iniciar em modo de teste**
3. Configure regras de segurança (ver abaixo)

## 5. Gerar Chave de Service Account

1. Vá para **Configurações do projeto** → **Contas de serviço**
2. Clique em **Gerar nova chave privada**
3. Selecione **JSON** e clique em **Gerar**
4. Salve o arquivo como `serviceAccount.json` na pasta `backend/`
5. **NUNCA** commit este arquivo no Git!

## 6. Configurar Variáveis de Ambiente

### Frontend (`.env.local`)

```bash
# Firebase Configuration
NEXT_PUBLIC_FIREBASE_API_KEY=sua_api_key_aqui
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=dashboard-azo-prod.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=dashboard-azo-prod
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=dashboard-azo-prod.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=123456789
NEXT_PUBLIC_FIREBASE_APP_ID=1:123456789:web:abcdef

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (`.env`)

```bash
# Firebase
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=./serviceAccount.json

# Seed Admin User
ADMIN_SEED_EMAIL=mestre@azo.inc
ADMIN_SEED_PASSWORD=senha_segura_123
```

## 7. Regras de Segurança

### Firestore Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own profile
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Only authenticated users can read audit logs
    match /audit_logs/{logId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.token.role in ['admin', 'mestre_do_universo'];
    }
    
    // Deny all other access
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

### Storage Rules

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Only authenticated users can access files
    match /{allPaths=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 8. Seed do Mestre do Universo

Após configurar as variáveis de ambiente, execute:

```bash
cd backend
python seed_admin.py
```

Ou via API:

```bash
curl -X POST http://localhost:8000/api/v1/users/seed-admin
```

## 9. Testar Integração

1. Inicie o backend: `cd backend && uvicorn app.main:app --reload`
2. Inicie o frontend: `cd frontend && npm run dev`
3. Acesse `http://localhost:3000`
4. Faça login com as credenciais do Mestre do Universo
5. Verifique se todos os sistemas estão acessíveis

## 10. Deploy

### Frontend (Vercel)

1. Conecte o repositório ao Vercel
2. Configure as variáveis de ambiente no dashboard
3. Deploy automático em cada push

### Backend (Cloud Run)

1. Build da imagem Docker
2. Upload da chave de serviço para Secret Manager
3. Configure variáveis de ambiente
4. Deploy via `gcloud run deploy`

---

## Troubleshooting

### Erro: "Firebase initialization error"

- Verifique se o arquivo `serviceAccount.json` está no local correto
- Confirme se as variáveis de ambiente estão configuradas

### Erro: "Invalid token"

- Verifique se as chaves do Firebase no frontend estão corretas
- Confirme se o domínio está autorizado no Firebase Auth

### Erro: "Insufficient permissions"

- Verifique se o usuário tem os custom claims configurados
- Execute o seed do admin novamente

---

**Importante**: Mantenha suas chaves e senhas seguras! Nunca commit arquivos de configuração sensíveis.
