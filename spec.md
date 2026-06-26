# Dashboard Azo — Especificação do Produto

> **Status:** Rascunho  
> **Última atualização:** 2026-06-22  
> **Dono:** Bruno Henrique Pedroso  
> **Revisores:** UX/UI Specialist, Backend Dev Specialist, DevOps/Security Specialist, QA Specialist

---

## 1. Visão geral

### 1.1 Propósito
O **Dashboard Azo** é um webapp de visualização e análise de dados imobiliários da AZO INC. Após autenticação, o usuário escolhe entre dois sistemas: **Financeiro/Vendas** (Sistema 1) e **Marketing** (Sistema 2). Cada sistema possui dashboards, formulários de lançamento, metas e administrativo, compartilhando filtros globais e controle de acesso baseado em papéis.

### 1.2 Escopo
- Autenticação e gerenciamento de usuários (roles).
- Tela inicial com cards de acesso aos sistemas 1 e 2 (visibilidade por role).
- Sistema 1: dashboard financeiro/vendas, lançamentos, comercial, institucional, timeline.
- Sistema 2: dashboard de marketing com abas Resultados Gerais, Corretores e Mídia Paga.
- Integrações: Sienge API, Supabase PostgreSQL, Meta Ads API, Google Ads API.
- Filtros globais persistentes aplicáveis a todas as páginas.

### 1.3 Fora de escopo (v1)
- Aplicativo mobile nativo.
- Processamento de pagamentos ou transações financeiras.
- Sistemas legados não mapeados (exceto Sienge e Supabase).

---

## 2. Objetivos e personas

### 2.1 Objetivos de negócio
- Centralizar KPIs de financeiro, vendas, marketing e investimentos em um único painel.
- Reduzir tempo de consolidação de relatórios manuais entre Sienge, Supabase e planilhas.
- Permitir acompanhamento em tempo real de VGV, metas, leads, investimentos e ações de marketing.
- Controlar acessos e ações de lançamento por perfil de usuário.

### 2.2 Personas / Roles
- **Mestre do Universo:** acesso total, cria usuários, altera perfis e senhas de qualquer role (inclusive Admin e próprio). Role exclusiva do dono do produto.
- **Admin:** gerencia usuários e senhas de roles inferiores; não altera Mestre do Universo.
- **Comercial RJ:** acompanha VGV, metas, vendas e lançamentos comerciais do Rio de Janeiro.
- **Comercial SP:** acompanha VGV, metas, vendas e lançamentos comerciais de São Paulo (Campinas).
- **Marketing RJ:** acompanha leads, visitas, corretores, mídia paga e timeline do Rio de Janeiro.
- **Marketing SP:** acompanha leads, visitas, corretores, mídia paga e timeline de São Paulo (Campinas).
- **Diretoria:** acompanha visão agregada comercial de SP e RJ, sem acesso a marketing.

---

## 3. Fluxo de navegação

1. **Login:** e-mail e senha via Firebase Auth.
2. **Home:** após autenticação, exibir cards com ícones para:
   - **Sistema 1 — Financeiro e Vendas**
   - **Sistema 2 — Marketing**
   - Visibilidade dos cards controlada por role.
3. **Sistema 1:** sidebar com **Marketing** (dashboard), **Lançamentos**, **Comercial** (subitens: Metas e Vendas, Pipeline, Visitas), **Institucional**, **Timeline**, **Admin**.
4. **Sistema 2:** topo com seletor de abas **Resultados Gerais**, **Corretores**, **Mídia Paga**.
5. **Home — visibilidade dos cards por role:**
   - **Sistema 1 — Financeiro e Vendas:** Comercial RJ, Comercial SP, Diretoria, Admin, Mestre do Universo.
   - **Sistema 2 — Marketing:** Marketing RJ, Marketing SP, Admin, Mestre do Universo.
   - **Acesso ao Admin:** Admin, Mestre do Universo (via menu ou card dedicado).
   - Usuários sem acesso a nenhum sistema devem ver mensagem informativa.
6. **Filtros globais:** visíveis em todas as páginas (Ano, Mês, Cidade, Empreendimento).
7. **Recuperação de senha:** link “Esqueci minha senha” na tela de login. Envio de e-mail de reset via Firebase Auth.
8. **Logout:** opção disponível no header ou sidebar para todos os usuários autenticados.

---

## 4. Filtros globais e persistência

### 4.1 Filtros
- **Ano**
- **Mês**
- **Cidade:** Campinas | Rio de Janeiro
- **Empreendimento:**
  - Campinas: Ares, Verter, Casa da Mata
  - Rio de Janeiro: Ar Ipanema, Gávea 99, A Noite, Insigna Peninsula

### 4.2 Comportamento
- Filtros aplicam-se a todas as páginas/sessões do dashboard.
- Filtros e abas selecionadas devem persistir ao recarregar a página (localStorage/sessionStorage).
- Filtros de cidade e empreendimento respeitam o escopo da role:
  - **Comercial RJ / Marketing RJ:** apenas Rio de Janeiro e seus empreendimentos.
  - **Comercial SP / Marketing SP:** apenas Campinas e seus empreendimentos.
  - **Diretoria:** ambas as cidades, mas apenas dados comerciais.
  - **Admin / Mestre do Universo:** todas as cidades e empreendimentos.
- Opções fora do escopo da role devem ficar desabilitadas ou ocultas.

---

## 5. Sistema 1 — Financeiro e Vendas

### 5.1 Dashboard principal

#### Big numbers — linha superior
- VGV do Produto
- VGV em Estoque
- VGV Realizado
- Meta de Vendas
- Vendas Realizadas

#### Big numbers — linha inferior
- Investimento MKT
- Investimento Stand
- Investimento Produto
- Estoque de Unid.

**Fontes:** Sienge API + inputs manuais das telas **Lançamentos** e **Comercial**.

#### Gráficos e indicadores
- **Origem x Investimento:** gráfico de barras alimentado por lançamentos.
- **Planejado x Realizado por Empreendimento:** alimentado por lançamentos.
- **Leads, Visitas On, Visitas Off, %Conversão:** Leads e Visitas On alimentados pelo PostgreSQL do Supabase. `%Conversão = Visitas ÷ Leads Totais`.
- **Evolução de Leads x Investimento:** alimentado por Supabase + lançamentos.
- **Previsão de Orçamentos e Realizado Lançamentos:** descritivo com base em lançamentos.
- **Timeline de Ações:** exibição mensal/anual com cores por empreendimento, alimentada pelo menu Timeline.

### 5.2 Lançamentos

#### Botão “Novo Lançamento”
Popup único com:
- Data
- Cidade (Campinas | Rio de Janeiro)
- Empreendimento (lista filtrada por cidade)
- Tipo: Publicidade | Manutenção de Stand | Produtos
- Categoria (condicional ao tipo):
  - **Publicidade:** Agência OFF, Agência On, Promoção, Produção Gráfica, Produção de Comunicação Visual, Produção Audiovisual, Eventos, Reuniões Mensais Imobs, Mídia On, Mídia Off
  - **Manutenção de Stand:** Desmobilização, Manutenção, Casa Decorada
  - **Produtos:** Produtos Gerais
- Descrição (opcional)
- Valor R$
- Ação: Salvar Lançamento

#### Conteúdo da tela
- **Basal Publicidade** — resumo descritivo das ações de publicidade do período filtrado: total investido, número de ações e lista compacta por categoria.
- **Basal Manut. Stand** — resumo descritivo das ações de manutenção de stand do período filtrado: total investido, número de ações e lista compacta por categoria.
- **Basal Produtos** — resumo descritivo das ações de produtos do período filtrado: total investido, número de ações e lista compacta por categoria.
- **Histórico de Lançamentos do Mês** — tabela completa com todos os lançamentos, filtros por tipo/categoria e paginação.

### 5.3 Comercial

#### 5.3.1 Metas e Vendas

##### Big numbers
- Meta Anual (VGV) VP
- VGV em Estoque
- Realizado VGV VP
- Unidades Vendidas
- **VSO Meta** = (Unidades Vendidas ÷ Meta de Unidades) × 100
- **VSO Estoque** = (Unidades Vendidas ÷ Oferta Total) × 100

##### Meta de Vendas — Projetos Ativos
Visão anual distribuída por trimestres e praças (São Paulo e Rio de Janeiro).

###### Botão “Configurar Metas” — wizard de 5 passos
- **Passo 1 — Definição Anual:**
  - Ano base da meta (seletor de ano).
  - Seletor de projetos ativos (empreendimentos) em formato de checkbox em botões.
  - Campo para digitar novo projeto.
  - Tabela: Projeto | Meta de Unidades | Meta VGV VP R$.
- **Passos 2 a 5 — Metas por Trimestre:**
  - Passo 2: 1º Tri
  - Passo 3: 2º Tri
  - Passo 4: 3º Tri
  - Passo 5: 4º Tri (botão **Salvar Metas** em vez de próximo).
- Metas podem ser reeditadas a qualquer momento pelo mesmo botão.
- A soma das metas dos 4 trimestres deve ser igual à meta anual definida no Passo 1.
- O sistema deve exibir alerta de inconsistência caso a soma trimestral seja diferente da meta anual.
- Ao alterar a meta anual, os trimestres devem ser ajustáveis manualmente pelo usuário.

###### Descritivo de metas
- Tabela separada por **São Paulo** e **Rio de Janeiro**, com total por estado.
- **Total Geral** ao final.
- Para cada trimestre: Meta, Vendas e VGV Realizado (do Sienge).
- Semáforo visual: verde quando realizado ≥ meta; vermelho quando abaixo.

###### Lançamentos Comerciais
- Tabela: Data | Empreendimento | Tipo | Detalhes (dados do Sienge).
- Paginação estilo Google, máximo 3–4 vendas por página.

#### 5.3.2 Pipeline e Visitas
- Ocultos do menu até estarem prontos.

### 5.4 Institucional

Cópia da tela de Lançamentos, porém com base institucional.

#### Botão “Novo Lançamento”
Popup único com:
- Data
- Cidade
- Empreendimento
- Tipo: Institucional
- Categoria:
  - Agência Institucional
  - Assessoria de Imprensa
  - Brindes Azo Evs
  - Mídia Off
  - Eventos | Ativação
  - Patrocínios
  - Prêmios de Mercado
  - Software | Plataformas
  - Site | Manutenção
  - Marcas e Patentes
  - Hospedagem | Domínios
- Descrição (opcional)
- Valor R$

### 5.5 Timeline

#### Botão “Nova Ação”
Popup com:
- Data
- Empreendimento
- Título da Ação
- Local
- Imagem (opcional, PNG, máximo 5MB)
- Descrição da Ação

#### Visualização
- Timeline mensal/anual com cor por empreendimento.
- Exibir título e imagem do pin.
- Clique no pin abre popup com detalhes da ação.

---

## 6. Sistema 2 — Marketing

Alimentado pelos dados do **PostgreSQL do Supabase**. Topo com seletor de abas: **Resultados Gerais**, **Corretores**, **Mídia Paga**.

### 6.0 Modelo de filtro duplo de data (vida util do lead)

#### Contexto de negocio
A vida util de um lead na AZO varia de **180 a 240 dias**. Um lead captado em fevereiro pode realizar sua primeira visita em junho. Para preservar esse contexto e evitar perda de insights, o Sistema 2 possui **dois seletores de data independentes**:

| Seletor | Nome na UI | Significado |
|---|---|---|
| Filtro 1 | **Data de Entrada** | Quando o lead foi captado/cadastrado no Supabase. |
| Filtro 2 | **Data de Acao** | Quando ocorreu uma acao do lead (visita, agendamento, etc.). |

#### Comportamento
- **Ambos os filtros sao opcionais e independentes.**
  - Filtro 1 vazio -> ignora data de entrada do lead.
  - Filtro 2 vazio -> ignora data de acao.
  - Ambos vazios -> retorna todos os leads sem restricao de data.
- **Quando ambos preenchidos -> logica AND (intersecao):** retorna apenas leads que entraram no periodo 1 **E** tiveram uma acao no periodo 2.
- Cada filtro aceita intervalo de datas (data inicio + data fim).

#### Exemplo pratico
> Lead entra em `02/02/2026` e faz visita em `27/06/2026`.
> Com Filtro 1 = fev/2026 e Filtro 2 = jun/2026, esse lead **aparece** nos resultados, conectando a origem da captacao com a acao recente.

#### Impacto no backend
- Queries ao Supabase devem suportar filtragem por `data_cadastro` **E/OU** data de acao especifica.
- Metricas de captacao (Leads Totais, CPL) usam preferencialmente o Filtro 1.
- Metricas de atividade (Visitas, Agendamentos) usam preferencialmente o Filtro 2.
- Quando ambos ativos: `WHERE data_cadastro BETWEEN ? AND ? AND data_acao BETWEEN ? AND ?`
- O backend deve mapear os campos exatos do schema Supabase e documentar a correspondencia.

---

### 6.1 Resultados Gerais

#### Filtros
- **Data de Entrada** (Filtro 1): intervalo de datas de cadastro do lead. Opcional.
- **Data de Acao** (Filtro 2): intervalo de datas de acao do lead (visita, agendamento, etc.). Opcional.
- Quando ambos preenchidos: logica AND. Ver secao 6.0.
- **Visao Atual:** padrao Atual (Tempo Real), permitindo selecionar mes ou periodo especifico.
- Empreendimento, Corretor, Origem, Status.

#### Big numbers
- Leads Totais
- Descartados
- Em Atendimento
- Agendamentos
- Visitas
- Reservas
- Vendas Realizadas

#### Gráficos e análises
- Evolução dos status nos meses.
- Funil de status atual.
- Motivo de cancelamentos.
- Origem.
- Evolução de leads por empreendimento.
- Visitas e agendamentos por origem e por empreendimento.
- Submotivos de cancelamento além dos motivos principais.

### 6.2 Corretores

- Leads por corretor.
- TMR (tempo médio de recepção) — dado da tabela do Supabase.
- Ações no CV (quantidade de ações do corretor no CV CRM no período filtrado) — dado da tabela do Supabase.

> **CV** = CV CRM, CRM próprio da AZO usado para extrair dados de leads e alimentar o Supabase.

### 6.3 Mídia Paga

Integração oficial com **Meta Ads API** e **Google Ads API**.

#### Métricas a exibir
- Quantidade de leads
- CPL (Custo Por Lead = leads ÷ valor investido)
- Total Gasto
- Clicks
- Leads por empreendimento
- Evolução de leads Meta vs Google
- Evolução de leads qualificados Meta vs Google (cruzamento de origem × qualificação dos leads no Supabase)

> **Pendente:** criar contas de desenvolvedor, credenciais OAuth2 e fluxo de autorização.

---

## 7. Administração

### 7.1 Roles
- **Mestre do Universo:** acesso total. Cria usuários, altera perfis e senhas de Admin e de qualquer role inferior, inclusive a própria. Role exclusiva do dono do produto, criada por seed inicial.
- **Admin:** executa ações de criação/alteração de senha apenas sobre roles inferiores.
- **Comercial RJ:** acessa apenas a parte comercial do Rio de Janeiro.
- **Comercial SP:** acessa apenas a parte comercial de São Paulo (Campinas).
- **Marketing RJ:** acessa apenas dados de marketing do Rio de Janeiro em ambos os dashboards.
- **Marketing SP:** acessa apenas dados de marketing de São Paulo (Campinas) em ambos os dashboards.
- **Diretoria:** acessa apenas a parte comercial de São Paulo e Rio de Janeiro (visão agregada, sem acesso a marketing).

> **Nota:** visibilidade dos cards na home e dos itens de menu é controlada por role. Filtros de cidade/empreendimento também devem respeitar o escopo da role.

### 7.2 Criação de usuário
- E-mail
- Senha
- Perfil de acesso (role)

### 7.3 Comportamento de permissões
- Ações e locais restritos devem ficar **ocultos** para usuários sem acesso.

### 7.4 Seed do primeiro administrador
- Ao iniciar o sistema, se não existir nenhum usuário com role **Mestre do Universo**, o backend deve criar automaticamente um usuário seed usando as variáveis de ambiente:
  - `ADMIN_SEED_EMAIL`
  - `ADMIN_SEED_PASSWORD`
- A senha do seed deve ser considerada temporária e alterada no primeiro login.
- O seed deve ser idempotente: se o usuário já existir, não deve ser recriado nem ter a senha resetada.
- Somente o Mestre do Universo pode criar outros usuários com essa role (se necessário) e gerenciar Admins.

---

## 8. Requisitos não-funcionais

### 8.1 Performance
- Carregamento o mais rápido possível, respeitando a complexidade das integrações e as boas práticas do Google PageSpeed.
- Tempo de resposta da API < 300ms para 95% das requisições com cache ativo.
- **Supabase:** usar realtime subscriptions quando viável; para agregações pesadas, usar cache Redis com TTL de 5 min.
- **Sienge:** polling controlado a cada 5 min (não há realtime nativo), com cache Redis.
- **Meta/Google Ads:** sincronização controlada por rate limits, com cache Redis.
- Suportar até 50 usuários simultâneos na v1.
- Todos os dashboards devem usar cache por combinação de filtros.

### 8.2 Usabilidade
- Interface responsiva (desktop, tablet, mobile).
- Acessibilidade mínima WCAG 2.1 nível AA.
- Design baseado na identidade AZO (cor oficial `#61072E`) e mood de cada empreendimento, a ser estudado no site azo.inc.
- Cards com ícones na tela inicial para facilitar a compreensão.
- Filtros e abas persistem ao recarregar.

### 8.3 Confiabilidade
- Backup dos dados próprios do sistema (metas, lançamentos, timeline, usuários) que não estão em bancos externos.
- Logs de auditoria para ações críticas (login, criação de usuário, alteração de senha, salvar lançamento, salvar meta).

---

## 9. Arquitetura e stack

| Camada | Tecnologia | Responsável pela revisão |
|--------|------------|--------------------------|
| Repositório | GitHub | DevOps/Security |
| Frontend | Next.js + React + TypeScript + TailwindCSS | UX/UI Specialist |
| Hospedagem frontend | Vercel (free tier) | DevOps/Security |
| Backend API | Python 3.12 + FastAPI + Pydantic + SQLAlchemy 2.0 | Backend Dev Specialist |
| Hospedagem backend | Google Cloud Run (free tier) — padrão. Fly.io (free tier) como alternativa. | DevOps/Security |
| Cache | Redis (Upstash free tier) | Backend Dev + DevOps/Security |
| Banco de dados do sistema | Firebase (Firestore + Auth + Storage) | Backend Dev + DevOps/Security |
| Dados de marketing | Supabase PostgreSQL (somente leitura) | Backend Dev Specialist |
| Dados financeiros | Sienge API | Backend Dev Specialist |
| Mídia paga | Meta Ads API + Google Ads API | Backend Dev + DevOps/Security |
| CI/CD | GitHub Actions | DevOps/Security |
| Testes | Frontend: Jest/Vitest + Playwright; Backend: pytest | QA Specialist |

> **Nota:** Python foi escolhido para o backend devido ao volume crescente de dados do Supabase (40k+ registros) e à necessidade de agregações eficientes, cache e integrações resilientes.

---

## 10. Integrações e fontes de dados

### 10.1 Sienge API
- Documentação: https://api.sienge.com.br/docs/
- Autenticação: usuário, senha e subdomain.
- Dados consumidos: VGV, VGV em estoque, vendas realizadas, lançamentos comerciais.
- A API já existe, mas deve ser testada e validada pelos agentes.

### 10.2 Supabase PostgreSQL
- Conexão somente leitura para os dashboards de marketing.
- Schema a ser mapeado após conexão fornecida pelo dono do produto de forma segura.
- Dados: leads, corretores, visitas, status, origem, submotivos de cancelamento, TMR, ações no CV.
- **Atenção:** credenciais de conexão devem ser compartilhadas por canal seguro (não no chat). Preferencialmente via Firebase Secret Manager, Vercel server-side env vars ou cofre de senhas.

### 10.3 Meta Ads / Google Ads
- Conta de desenvolvedor e IDs de conta de anúncio disponíveis.
- Criação de API/OAuth2 e fluxo de autorização ainda deve ser implementada.
- Dados: leads, CPL, gasto, clicks, leads por empreendimento, evolução Meta vs Google, leads qualificados.

### 10.4 Firebase Storage
- Armazenamento de imagens da Timeline.
- Limite: 5MB por arquivo.
- Formato: PNG.
- Validação básica de MIME type e dimensões; verificação de conteúdo (opcional) pode incluir scan de malware.

---

## 11. Modelo de dados (rascunho)

### 11.1 Entidades do sistema (Firebase Firestore)
- `users` (id, email, role, created_at, updated_at, last_login_at)
- `roles` (id, name, permissions, level)
- `lancamentos` (id, data, cidade, empreendimento, tipo, categoria, descricao, valor, created_by, created_at)
- `lancamentos_institucionais` (id, data, cidade, empreendimento, categoria, descricao, valor, created_by, created_at)
- `metas_anuais` (id, ano, projeto_id, meta_unidades, meta_vgv_vp, created_by, updated_at)
- `metas_trimestrais` (id, ano, trimestre, projeto_id, meta_unidades, meta_vgv_vp, created_by, updated_at)
- `projetos_ativos` (id, ano, nome, cidade, ativo, created_by)
- `timeline_acoes` (id, data, empreendimento, titulo, local, imagem_url, descricao, created_by, created_at)
- `audit_logs` (id, user_id, action, resource_type, resource_id, ip_address, created_at)

### 11.2 Entidades externas (somente leitura)
- Supabase: leads, corretores, visitas, status, origem, submotivos, TMR, ações no CV.
- Sienge: VGV, vendas, estoque, lançamentos comerciais.
- Meta/Google Ads: campanhas, gastos, leads, clicks.

> **Atenção:** campos sensíveis devem ser criptografados e nunca expostos em logs ou respostas.

---

## 12. Contratos de API (rascunho)

### 12.1 Endpoints prioritários
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/financeiro/dashboard`
- `GET /api/v1/financeiro/lancamentos`
- `POST /api/v1/financeiro/lancamentos`
- `GET /api/v1/comercial/metas`
- `POST /api/v1/comercial/metas`
- `GET /api/v1/comercial/lancamentos`
- `GET /api/v1/institucional/lancamentos`
- `POST /api/v1/institucional/lancamentos`
- `GET /api/v1/timeline`
- `POST /api/v1/timeline`
- `GET /api/v1/marketing/resultados-gerais`
- `GET /api/v1/marketing/corretores`
- `GET /api/v1/marketing/midia-paga`
- `GET /api/v1/admin/users`
- `POST /api/v1/admin/users`
- `PUT /api/v1/admin/users/:id/role`
- `POST /api/v1/admin/users/:id/reset-password`

### 12.2 Padrões
- Respostas em JSON padronizado: `{ success, data, error, message }`.
- Códigos HTTP adequados (200, 201, 400, 401, 403, 404, 500).
- Paginação: `limit`, `offset`, `total`.
- Rate limiting em endpoints sensíveis e de integração externa.

---

## 13. Requisitos de interface (UI/UX)

- Login limpo com feedback de erro.
- Home com cards de acesso por sistema, com ícones e visibilidade por role.
- Layout com sidebar navegável e header fixo.
- Filtros globais sempre visíveis, exceto em telas de login e home.
- Dashboards com cards, gráficos e tabelas.
- Popups de formulário em etapa única para lançamentos, ações e criação de usuário.
- Wizard de 5 passos para configuração de metas de vendas.
- Tabela de lançamentos comerciais com paginação estilo Google.
- Timeline visual com cores por empreendimento.
- Componentes acessíveis: contraste, foco visível, labels, ARIA.
- Identidade visual AZO: cor primária `#61072E`; paleta de empreendimentos proposta abaixo (sujeita a aprovação):
  - **Ares Home (Campinas):** `#C67D5B` — terracota, remete a casas e acolhimento.
  - **Vërtër Cambuí (Campinas):** `#5B7C8D` — azul acinzentado, sofisticação urbana.
  - **Casa da Mata (Campinas):** `#6B8E5A` — verde natural, integração com o verde.
  - **Ar Ipanema (Rio):** `#4A8C9B` — azul oceano, leveza e praia.
  - **Gávea 99 (Rio):** `#3D6B5B` — verde profundo, bossa e natureza.
  - **A Noite (Rio):** `#5A4A6A` — roxo noturno, urbano e contemporâneo.
  - **Insigna Península (Rio):** `#B8956A` — dourado, luxo e exclusividade.

---

## 14. Requisitos de segurança

- Autenticação via Firebase Auth com e-mail/senha.
- Roles armazenadas como **custom claims** no Firebase Auth e como string no Firestore (perfil do usuário).
- Senhas com hash forte pelo Firebase Auth.
- Tokens JWT validados tanto no frontend quanto no backend Python.
- Proteção contra SQL Injection, XSS, CSRF, injection em geral.
- Validação de entrada em todos os endpoints.
- Criptografia de dados sensíveis em trânsito (TLS 1.2+) e em repouso.
- Controle de acesso baseado em papéis (RBAC): ações restritas ocultas para usuários sem permissão.
- Segredos de Sienge, Meta, Google e Supabase armazenados de forma segura (a definir: Firebase Secret Manager ou Vercel server-side env vars).
- Revisão de dependências contra vulnerabilidades conhecidas.
- Upload de imagens limitado a PNG, 5MB, com validação de MIME type.

---

## 15. Requisitos de deploy e infraestrutura

- Repositório no GitHub (monorepo com `frontend/` e `backend/`).
- Frontend Next.js hospedado na Vercel (free tier).
- Backend Python FastAPI hospedado no **Google Cloud Run** (free tier) ou **Fly.io** (free tier).
- Firebase projeto a ser criado (Auth, Firestore, Storage).
- Redis Upstash para cache (free tier).
- Ambientes: desenvolvimento, homologação (staging) e produção.
- Pipeline CI/CD com stages: lint, testes, build, segurança, deploy.
- CORS/HTTPS configurados para Vercel ↔ Python API ↔ Firebase ↔ Supabase ↔ Sienge.
- Backup dos dados próprios do sistema (metas, lançamentos, timeline, usuários) — Firebase Firestore oferece backups automáticos em planos pagos; no free tier, exportar periodicamente via script.
- Monitoramento básico de uptime e logs.
- **Free tier aware:** limitar payload, requisições e conexões simultâneas; monitorar quotas de Supabase, Firebase, Vercel e Cloud Run.

---

## 16. Critérios de aceitação e QA

- Todos os requisitos funcionais possuem testes automatizados ou manuais mapeados.
- Cobertura mínima de testes unitários: 70%.
- Testes de integração para fluxos críticos (login, criação de usuário, lançamentos, metas, timeline).
- Testes de segurança: revisão de OWASP Top 10 e tentativas de injeção.
- Testes de usabilidade e acessibilidade em desktop e mobile.
- Validação de cálculos: VSO Geral, CPL, TMR, leads qualificados, semáforo de metas.
- Páginas “em construção” (Pipeline, Visitas) não devem aparecer no menu até estarem prontas.
- Nenhum bug crítico ou alto aberto antes do deploy para produção.

---

## 17. Riscos e suposições

- **Risco:** APIs de terceiros (Sienge, Meta, Google) podem sofrer indisponibilidade ou rate limit. Mitigação: avisos na tela e tentativa de refresh.
- **Risco:** Testes serão realizados diretamente em produção por falta de ambientes sandbox. Mitigação: validação cuidadosa e backups antes de alterações.
- **Risco:** Schema do Supabase ainda não mapeado. Mitigação: backend deve mapear após recebimento da conexão.
- **Suposição:** Firebase, Vercel e Supabase serão utilizados como plataformas principais.
- **Suposição:** Dados de leads não serão armazenados no Firebase; apenas consultados no Supabase.

---

## 18. Histórico de revisões

| Data | Versão | Autor | Alterações |
|------|--------|-------|------------|
| 2026-06-22 | 0.1 | Bruno Henrique Pedroso | Criação da estrutura inicial da especificação |
| 2026-06-22 | 0.2 | Bruno Henrique Pedroso | Estrutura detalhada com Sistema 1, Sistema 2, integrações, roles e stack definidos |
| 2026-06-22 | 0.3 | Bruno Henrique Pedroso | Ajustes finais: visibilidade por role, filtros por role, VSO Meta/Estoque, seed admin, recuperação de senha, basal, validação de metas, Cloud Run como padrão |

---

## 19. Checklist de aprovação

- [ ] UX/UI Specialist revisou e aprovou requisitos de interface e usabilidade.
- [ ] Backend Dev Specialist revisou e aprovou stack, modelo de dados e contratos de API.
- [ ] DevOps/Security Specialist revisou e aprovou requisitos de segurança, deploy e infraestrutura.
- [ ] QA Specialist revisou e aprovou critérios de aceitação e cobertura de testes.
