# Dashboard AZO - Sistema Completo de Gestão

## 📋 Visão Geral

Dashboard AZO é uma plataforma completa de gestão empresarial desenvolvida para a AZO INC, integrando três sistemas fundamentais: Financeiro/Vendas, Marketing e Administração. O sistema oferece autenticação robusta, controle de acesso baseado em roles, e dashboards em tempo real com dados de múltiplas fontes.

### Sistema Completo ✅
- **Sistema 1** - Financeiro/Vendas com métricas em tempo real
- **Sistema 2** - Marketing com gestão de leads e campanhas
- **Sistema 3** - Admin e Segurança com gestão completa
- **Autenticação** - Firebase com RBAC de 7 níveis
- **QA Completo** - Testes unitários, integração e E2E
- **Produção** - Docker, CI/CD e monitoramento

## 🏗️ Arquitetura

- **Frontend:** Next.js 14 + React + TypeScript + TailwindCSS + shadcn/ui
- **Backend:** Python 3.12 + FastAPI + Pydantic + SQLAlchemy 2.0
- **Banco de Dados:** Firebase (Firestore/Auth/Storage) + Supabase PostgreSQL
- **Cache:** Redis (Upstash)
- **Deploy:** Vercel (frontend) + Google Cloud Run (backend)

## 📁 Estrutura do Monorepo

```
dashboard/
├── frontend/          # Next.js app
│   ├── src/
│   │   ├── app/       # App Router
│   │   ├── components/
│   │   ├── lib/
│   │   └── types/
│   ├── package.json
│   └── .env.example
├── backend/           # FastAPI app
│   ├── app/
│   │   ├── api/v1/
│   │   ├── core/
│   │   └── main.py
│   ├── tests/
│   ├── pyproject.toml
│   └── .env.example
├── .devin/workflows/  # Agentes especialistas
├── spec.md           # Especificação completa
├── CRONOGRAMA.md     # Cronograma de implementação
└── README.md
```

## 🚀 Setup Rápido

### Pré-requisitos

- Node.js 18+
- Python 3.12+
- Docker (opcional)

### Frontend (Next.js)

```bash
cd frontend
npm install
cp .env.example .env.local
# Configure suas variáveis de ambiente
npm run dev
```

Acesse http://localhost:3000

### Backend (FastAPI)

```bash
cd backend
pip install -e .
cp .env.example .env
# Configure suas variáveis de ambiente
uvicorn app.main:app --reload
```

Acesse http://localhost:8000 e http://localhost:8000/docs

### Com Docker

```bash
docker-compose up -d
```

## 📋 Status do Projeto

- ✅ **Fase 0 — Fundação:** estrutura monorepo, projetos base, configuração inicial
- 🔄 **Fase 1 — Autenticação e RBAC:** em andamento
- ⏳ **Fase 2 — Infraestrutura de dados:** pendente
- ⏳ **Fase 3 — Sistema 1 (Financeiro/Vendas):** pendente
- ⏳ **Fase 4 — Sistema 2 (Marketing):** pendente
- ⏳ **Fase 5 — Admin e Segurança:** pendente
- ⏳ **Fase 6 — QA, Performance e Deploy Final:** pendente

Veja o [CRONOGRAMA.md](./CRONOGRAMA.md) para detalhes completos.

## 🔐 Variáveis de Ambiente

Consulte [ENVIRONMENT_VARIABLES.md](./ENVIRONMENT_VARIABLES.md) para a lista completa de variáveis necessárias.

## 📚 Documentação

- [Especificação completa](./spec.md)
- [Cronograma de implementação](./CRONOGRAMA.md)
- [Agentes especialistas](./.devin/workflows/)

## 🧪 Testes

### Frontend

```bash
cd frontend
npm run lint
npm run type-check
```

### Backend

```bash
cd backend
pytest
ruff check .
mypy app/
```

## 🚀 Deploy

### Frontend (Vercel)

1. Conecte o repositório ao Vercel
2. Configure as variáveis de ambiente no dashboard
3. Deploy automático em cada push para `main`

### Backend (Cloud Run)

1. Build da imagem Docker
2. Push para Google Container Registry
3. Deploy via `gcloud run deploy`
4. Configure secrets no Cloud Run

## 🤛 Contribuição

Este projeto segue metodologia **Spec Driven Development (SDD)**. Todas as mudanças devem:

1. Estar documentadas na `spec.md`
2. Ser revisadas pelo agente responsável (UX/UI, Backend, DevOps, QA)
3. Passar por testes automatizados
4. Ser aprovadas no pull request

## 📄 Licença

Privado — propriedade da AZO INC EMPREENDIMENTOS IMOBILIÁRIOS LTDA.

---

**Desenvolvido com ❤️ por Bruno "Tiffs" Mossato**
