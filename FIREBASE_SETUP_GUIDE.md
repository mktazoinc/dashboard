# 🔥 Firebase Setup - Guia Rápido

## ✅ Problema Resolvido

O backend agora suporta **ambos** os métodos de configuração Firebase:
1. **Environment Variables** (recomendado para produção)
2. **Arquivo JSON** (fallback para desenvolvimento)

---

## 🛠️ Método 1: Environment Variables (Recomendado)

### Passo 1: Obter credenciais no Firebase Console
1. Vá para: Firebase Console > Project Settings > Service Accounts
2. Clique "Generate new private key"
3. Abra o arquivo JSON e copie estes valores:

```json
{
  "project_id": "seu-project-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\nSUA_CHAVE\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxx@seu-project.iam.gserviceaccount.com"
}
```

### Passo 2: Configurar no .env
```bash
# backend/.env
FIREBASE_PROJECT_ID=seu-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
SUA_CHAVE_PRIVADA_AQUI
-----END PRIVATE KEY-----"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@seu-project.iam.gserviceaccount.com
```

### Passo 3: Testar
```bash
cd backend
python seed_admin.py
```

---

## 📁 Método 2: Arquivo JSON (Alternativa)

### Passo 1: Baixar arquivo JSON
1. Firebase Console > Project Settings > Service Accounts
2. "Generate new private key"
3. Salve como `serviceAccount.json` na pasta `backend/`

### Passo 2: Configurar no .env
```bash
# backend/.env
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=./serviceAccount.json
```

---

## 🧪 Diagnóstico Automático

Use os endpoints de diagnóstico para verificar configuração:

```bash
# Após fazer login, acesse:
curl -H "Authorization: Bearer SEU_TOKEN" \
  http://localhost:8000/api/v1/diagnostics/firebase

curl -H "Authorization: Bearer SEU_TOKEN" \
  http://localhost:8000/api/v1/diagnostics/system

curl -H "Authorization: Bearer SEU_TOKEN" \
  http://localhost:8000/api/v1/diagnostics/test-firebase-connection
```

---

## 🚀 Deploy no Vercel

### Backend (se usar Vercel para backend)
```bash
# Environment Variables no Vercel
FIREBASE_PROJECT_ID=seu-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----..."
FIREBASE_CLIENT_EMAIL=firebase@seuprojeto.iam.gserviceaccount.com
```

### Frontend
```bash
# Environment Variables no Vercel
NEXT_PUBLIC_API_URL=https://seu-backend.vercel.app
NEXT_PUBLIC_FIREBASE_PROJECT_ID=seu-project-id
```

---

## 🔧 Troubleshooting

### Erro: "Firebase não inicializado"
```bash
# Verifique as variáveis
echo $FIREBASE_PROJECT_ID
echo $FIREBASE_PRIVATE_KEY
echo $FIREBASE_CLIENT_EMAIL
```

### Erro: "Invalid credentials"
- Verifique se a private key tem as quebras de linha `\n`
- Use aspas duplas no .env
- Confirme o project_id está correto

### Erro: "Arquivo não encontrado"
```bash
# Verifique se o arquivo existe
ls -la serviceAccount.json
```

---

## 📊 Como o Sistema Decide

O backend segue esta prioridade:

1. **Environment Variables** (se todas 3 estiverem presentes)
2. **Arquivo JSON** (se existir)
3. **Erro** (se nenhum método configurado)

### Log de inicialização:
```
🔥 Firebase inicializado com Environment Variables
✅ Firebase Admin SDK inicializado com sucesso
```

ou

```
🔥 Firebase inicializado com arquivo JSON
✅ Firebase Admin SDK inicializado com sucesso
```

---

## ✅ Verificação Final

Execute o seed e verifique a saída:

```bash
cd backend
python seed_admin.py
```

Saída esperada:
```
🔧 Configurando Firebase Admin...
📊 Config Firebase: {
  "initialized": true,
  "method": "env_vars",
  "project_id": "seu-project-id",
  "client_email": "firebase@seuprojeto.iam.gserviceaccount.com",
  "json_file_exists": false
}
✅ Firebase Admin inicializado com sucesso
👤 Usuário encontrado: abc123...
✅ Usuário já tem role 'mestre_do_universo'
```

**Se vir essa saída, está tudo funcionando!** 🎉
