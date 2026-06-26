# Cronograma de Implementação — Dashboard Azo

> **Metodologia:** Spec Driven Development (SDD)  
> **Stack:** Next.js (frontend) + Python FastAPI (backend) + Firebase + Supabase + Redis + Cloud Run  
> **Status:** Baseado na `spec.md` v0.3

---

## 1. Visão geral

O desenvolvimento será dividido em **fases controladas**. Cada fase possui entregas claras, responsáveis definidos e critérios de passagem. As conversas entre agentes acontecem nos **pontos de colaboração** marcados em cada fase.

### Fases principais

1. **Fase 0 — Fundação:** repositório, infra, variáveis, projeto base.
2. **Fase 1 — Autenticação e RBAC:** login, roles, seed admin, guards.
3. **Fase 2 — Infraestrutura de dados:** Supabase, Firestore, Redis, Sienge.
4. **Fase 3 — Sistema 1 (Financeiro/Vendas):** dashboard, lançamentos, metas, timeline.
5. **Fase 4 — Sistema 2 (Marketing):** resultados gerais, corretores, mídia paga.
6. **Fase 5 — Admin e segurança:** gestão de usuários, hardening, testes de invasão.
7. **Fase 6 — QA, performance e deploy final:** testes, otimização, produção.

---

## 2. Princípios SpecDriven

- Nenhuma fase começa sem a `spec.md` validada para aquele escopo.
- Cada agente revisa sua parte da spec antes de codar.
- Mudanças de escopo durante a fase são documentadas na spec e comunicadas a todos.
- QA e DevOps participam desde o início, não apenas no final.
- Todo bug crítico ou de segurança bloqueia a passagem de fase.

---

## 3. Detalhamento por fase

### Fase 0 — Fundação
**Duração estimada:** 1–2 sprints  
**Objetivo:** Ter o projeto base rodando localmente e os ambientes configurados.

| Sprint | Entrega | Responsável | Colaboração |
|---|---|---|---|
| 0.1 | Criar repositório GitHub com estrutura monorepo (`frontend/` e `backend/`). | DevOps | — |
| 0.2 | Configurar projeto Next.js 14 + Tailwind + shadcn/ui + Zod + React Query. | UX/UI | DevOps (Vercel) |
| 0.3 | Configurar projeto Python FastAPI + Pydantic + SQLAlchemy 2.0 + pytest + ruff + Docker. | Backend | DevOps (Cloud Run) |
| 0.4 | Criar Firebase project (Auth, Firestore, Storage) e configurar Vercel + Cloud Run. | DevOps | Backend, UX/UI |
| 0.5 | Configurar variáveis de ambiente (locais, Vercel, GitHub Secrets, Cloud Run secrets). | DevOps | Backend |
| 0.6 | Configurar CI/CD básico: lint, testes, build, deploy. | DevOps | QA |

**Critérios de passagem:**
- `frontend` roda com `npm run dev` sem erros.
- `backend` roda com `docker compose up` ou `uvicorn` e responde `/health`.
- Deploy inicial na Vercel e Cloud Run (ambiente de dev) funcionando.
- CI/CD executa lint e build com sucesso.

---

### Fase 1 — Autenticação e RBAC
**Duração estimada:** 2 sprints  
**Objetivo:** Usuários conseguem fazer login, ter role definida e acessar apenas o permitido.

| Sprint | Entrega | Responsável | Colaboração |
|---|---|---|---|
| 1.1 | Implementar Firebase Auth no frontend (login, logout, recuperação de senha). | UX/UI | DevOps |
| 1.2 | Implementar validação de JWT e custom claims no backend Python. | Backend | DevOps |
| 1.3 | Criar middleware/guard de role no Next.js e no FastAPI. | Backend + UX/UI | DevOps |
| 1.4 | Implementar seed do Mestre do Universo (`ADMIN_SEED_EMAIL`/`PASSWORD`). | Backend | DevOps |
| 1.5 | Criar tela Home com cards visíveis por role. | UX/UI | Backend (contrato de roles) |

**Critérios de passagem:**
- Login com e-mail/senha funciona.
- Recuperação de senha envia e-mail.
- Usuário sem role correta não acessa cards/telas restritas.
- Seed cria o Mestre do Universo se não existir.
- QA testa bypass de autenticação e tentativas de acesso não autorizado.

**Conversas entre agentes:**
- Backend ↔ UX/UI: formato do token e da role no client.
- DevOps ↔ Backend: CORS e headers entre Vercel e Cloud Run.
- QA ↔ DevOps: cenários de ataque para testar.

---

### Fase 2 — Infraestrutura de dados
**Duração estimada:** 2–3 sprints  
**Objetivo:** Backend conectado a todas as fontes de dados e com cache funcionando.

| Sprint | Entrega | Responsável | Colaboração |
|---|---|---|---|
| 2.1 | Mapear schema do Supabase e criar models/repositories SQLAlchemy. | Backend | — |
| 2.2 | Implementar conexão read-only ao Supabase com connection pool. | Backend | DevOps |
| 2.3 | Configurar Redis/Upstash e implementar cache helper no backend. | Backend | DevOps |
| 2.4 | Conectar backend ao Firestore (dados próprios: metas, lançamentos, timeline). | Backend | DevOps |
| 2.5 | Integrar Sienge API: autenticação, endpoints de VGV/vendas/lançamentos. | Backend | DevOps (secrets) |
| 2.6 | Criar endpoints base `/health`, `/version`, `/auth/me` e documentação OpenAPI. | Backend | UX/UI |

**Critérios de passagem:**
- Backend conecta ao Supabase e retorna dados de teste.
- Cache funciona: segunda requisição idêntica é mais rápida.
- Sienge API responde corretamente (teste com dados reais, com cuidado).
- Firestore grava e lê documentos de teste.

**Conversas entre agentes:**
- Backend ↔ DevOps: string de conexão Supabase, Redis URL, secrets Sienge.
- Backend ↔ UX/UI: contratos de API iniciais.
- QA ↔ Backend: validar contratos e resiliência a falhas.

---

### Fase 3 — Sistema 1: Financeiro e Vendas
**Duração estimada:** 4–5 sprints  
**Objetivo:** Dashboard financeiro, lançamentos, metas e timeline funcionando.

| Sprint | Entrega | Responsável | Colaboração |
|---|---|---|---|
| 3.1 | **Dashboard Sistema 1:** big numbers VGV, metas, vendas, investimentos, estoque. | Backend + UX/UI | QA |
| 3.2 | Gráficos: Origem x Investimento, Planejado x Realizado, Leads/Visitas/%Conversão. | UX/UI | Backend |
| 3.3 | **Lançamentos:** popup de novo lançamento, basal, histórico. | UX/UI | Backend |
| 3.4 | Backend: CRUD de lançamentos no Firestore. | Backend | DevOps |
| 3.5 | **Comercial > Metas e Vendas:** wizard de 5 passos, VSO Meta/Estoque. | UX/UI | Backend |
| 3.6 | Backend: cálculo e persistência de metas anuais/trimestrais. | Backend | QA |
| 3.7 | **Timeline:** popup de nova ação, upload de imagem, visualização. | UX/UI | Backend + DevOps (Storage) |
| 3.8 | **Institucional:** cópia da tela de lançamentos com categorias institucionais. | UX/UI | Backend |

**Critérios de passagem:**
- Dashboard exibe dados reais do Sienge e Supabase (se possível) ou mocks consistentes.
- Lançamentos são salvos no Firestore e refletidos no dashboard.
- Wizard de metas valida soma dos trimestres.
- Timeline exibe ações com cores por empreendimento e upload de PNG ≤ 5MB.
- QA valida todos os fluxos e DevOps testa segurança (injeção, upload malicioso, IDOR).

**Conversas entre agentes:**
- UX/UI ↔ Backend: formatos de dados para gráficos e tabelas.
- Backend ↔ QA: validação de cálculos (VSO, CPL, %Conversão).
- DevOps ↔ UX/UI: CSP, headers, segurança de upload.

---

### Fase 4 — Sistema 2: Marketing
**Duração estimada:** 3–4 sprints  
**Objetivo:** Dashboard de marketing com Resultados Gerais, Corretores e Mídia Paga.

| Sprint | Entrega | Responsável | Colaboração |
|---|---|---|---|
| 4.1 | **Resultados Gerais:** big numbers, filtros, gráficos de status, funil, origem, cancelamentos. | Backend + UX/UI | QA |
| 4.2 | **Corretores:** leads por corretor, TMR, ações no CV. | Backend + UX/UI | QA |
| 4.3 | Backend: agregações otimizadas do Supabase com cache Redis. | Backend | DevOps |
| 4.4 | **Mídia Paga:** integração Meta Ads API (leads, CPL, gasto, clicks). | Backend | DevOps (OAuth) |
| 4.5 | **Mídia Paga:** integração Google Ads API (leads, CPL, gasto, clicks). | Backend | DevOps (OAuth) |
| 4.6 | Cruzamento de leads Meta/Google × qualificação no Supabase. | Backend | QA |

**Critérios de passagem:**
- Marketing dashboard exibe dados do Supabase com filtros funcionando.
- Mídia Paga traz dados reais ou mocks consistentes da Meta e Google.
- Cache reduz carga no Supabase.
- QA valida filtros, roles (Marketing RJ/SP) e cálculos.

**Conversas entre agentes:**
- Backend ↔ DevOps: setup OAuth2 Meta e Google.
- UX/UI ↔ Backend: design dos gráficos e tabelas de mídia paga.
- QA ↔ DevOps: testes de segurança nas integrações externas.

---

### Fase 5 — Admin e Segurança
**Duração estimada:** 2 sprints  
**Objetivo:** Gestão de usuários completa e revisão de segurança ofensiva.

| Sprint | Entrega | Responsável | Colaboração |
|---|---|---|---|
| 5.1 | Tela Admin: listar usuários, criar, editar role, resetar senha. | UX/UI | Backend |
| 5.2 | Backend: CRUD de usuários e regras de role (Mestre/Admin/inferiores). | Backend | DevOps |
| 5.3 | Revisão de segurança: scan de dependências, secrets, SAST. | DevOps | QA |
| 5.4 | Testes ofensivos: tentativas de injeção, XSS, CSRF, IDOR, escalada de privilégio. | DevOps | QA + Backend |
| 5.5 | Hardening: CSP, headers, CORS, regras Firestore/Storage, rate limiting. | DevOps | Backend + UX/UI |

**Critérios de passagem:**
- Admin consegue criar/editar usuários e resetar senhas conforme hierarquia de roles.
- Nenhuma vulnerabilidade crítica ou alta aberta.
- Testes de segurança documentados com reprodução e mitigação.
- Ambientes de preview não expõem dados sensíveis reais.

**Conversas entre agentes:**
- DevOps ↔ Backend: validação de RBAC e custom claims.
- DevOps ↔ UX/UI: CSP e headers de segurança.
- QA ↔ DevOps: execução e validação dos testes de segurança.

---

### Fase 6 — QA, Performance e Deploy Final
**Duração estimada:** 2–3 sprints  
**Objetivo:** Sistema testado, otimizado e em produção.

| Sprint | Entrega | Responsável | Colaboração |
|---|---|---|---|
| 6.1 | Testes E2E com Playwright cobrindo fluxos críticos. | QA | UX/UI |
| 6.2 | Testes de integração backend com pytest. | QA | Backend |
| 6.3 | Otimização de performance: cache, queries, bundle size. | Backend + UX/UI | DevOps |
| 6.4 | Documentação: README, API docs, deploy docs, runbooks. | Todos | — |
| 6.5 | Deploy em produção (Vercel + Cloud Run). | DevOps | Backend + UX/UI |
| 6.6 | Monitoramento inicial: logs, uptime, alertas básicos. | DevOps | QA |

**Critérios de passagem:**
- 95% dos testes E2E e de integração passando.
- Tempo de resposta da API < 300ms com cache.
- Deploy produção funcional e acessível.
- Nenhum bug crítico ou alto aberto.

---

## 4. Matriz de responsabilidade por fase

| Fase | UX/UI | Backend | DevOps | QA |
|---|---|---|---|---|
| 0 — Fundação | ● | ● | ●● | ○ |
| 1 — Auth/RBAC | ●● | ●● | ● | ● |
| 2 — Dados | ○ | ●● | ● | ● |
| 3 — Sistema 1 | ●● | ●● | ● | ● |
| 4 — Sistema 2 | ●● | ●● | ● | ● |
| 5 — Admin/Segurança | ● | ● | ●● | ●● |
| 6 — QA/Deploy | ● | ● | ●● | ●● |

> **Legenda:** ●● = principal responsável, ● = participa ativamente, ○ = acompanha.

---

## 5. Pontos de colaboração obrigatórios

Antes de cada fase, os agentes envolvidos devem se alinhar sobre:

1. **Kickoff da fase:** revisão da `spec.md` para o escopo da fase.
2. **Contratos de API:** UX/UI e Backend definem formatos de request/response.
3. **Revisão de segurança:** DevOps valida cada integração e tela antes do merge.
4. **Handoff para QA:** Backend e UX/UI entregam feature com instruções de teste.
5. **Retrospectiva de fase:** o que funcionou, bugs encontrados, ajustes na spec.

---

## 6. Ritmo sugerido

- **Sprint:** 1 semana.
- **Daily:** 15 min entre agentes ativos na fase (assíncrona, via comentários/status).
- **Review de fase:** ao final de cada fase, todos os agentes revisam entregas.
- **Deploy contínuo:** cada sprint deve ter deploy no ambiente de dev; staging a cada fase; produção apenas na Fase 6.

---

## 7. Riscos e mitigações

| Risco | Impacto | Mitigação |
|---|---|---|
| Sienge API instável ou lenta | Alto | Cache Redis agressivo, fallback para dados anteriores. |
| Meta/Google OAuth demorado | Médio | Iniciar setup já na Fase 2, usar mocks durante desenvolvimento. |
| Supabase free tier limitado | Médio | Cache, queries paginadas, evitar SELECT *. |
| Vazamento de secrets | Alto | GitLeaks no CI, .gitignore, secrets apenas em cofres. |
| Bugs de segurança em produção | Alto | Testes ofensivos na Fase 5, nada deploya sem aprovação de QA/DevOps. |
| Crescimento de dados > 100k | Médio | Arquitetura Python + cache preparada para escalar. |

---

## 8. Próximo passo imediato

1. Revisar e aprovar este cronograma.
2. Iniciar **Fase 0 — Fundação** (criar monorepo e configurar ambientes).
