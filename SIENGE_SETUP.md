# Configuração da API do Sienge

Este guia explica como configurar a integração com a API do Sienge baseada na sua implementação existente.

## Diferenças da Implementação Original

Sua implementação JavaScript usa:
- `VITE_SIENGE_SUBDOMAIN` para o subdomínio
- Endpoints: `/vendas`, `/custos/marketing`, `/empreendimentos`, `/empreendimentos/{id}/estoque`
- Estrutura de dados simplificada com `vendas`, `vgv`, `estoque`, `vgvEstoque`

Nossa implementação Python segue exatamente essa estrutura.

## Configuração do Backend

### 1. Variáveis de Ambiente

No arquivo `backend/.env`:

```bash
# Sienge API Integration
SIENGE_SUBDOMAIN=seu_subdomain_aqui
SIENGE_API_TOKEN=seu_token_aqui
```

### 2. Estrutura da API

Base URL: `https://{subdomain}.sienge.com.br/api`

#### Endpoints Implementados

**GET /vendas**
```bash
?vdataInicio=2024-01-01&dataFim=2024-01-31
```
Retorno:
```json
{
  "vendas": 10,
  "vgv": 1500000,
  "unidades": 10,
  "data": [...]
}
```

**GET /custos/marketing**
```bash
?dataInicio=2024-01-01&dataFim=2024-01-31
```
Retorno:
```json
{
  "custos": [
    {
      "data": "2024-01-15",
      "valor": 5000,
      "descricao": "Facebook Ads"
    }
  ]
}
```

**GET /empreendimentos**
Retorno:
```json
{
  "empreendimentos": [
    {
      "id": "emp_001",
      "nome": "Residencial AZO RJ",
      "cidade": "Rio de Janeiro"
    }
  ]
}
```

**GET /empreendimentos/{id}/estoque**
Retorno:
```json
{
  "disponiveis": 50,
  "vgvEstoque": 8000000,
  "total": 100
}
```

## Configuração do Frontend

### 1. Variáveis de Ambiente

No arquivo `frontend/.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 2. Uso no Dashboard

O dashboard financeiro (`/finance`) automaticamente:
- Busca dados do mês atual
- Calcula VSO: `(vgv / vgvEstoque) * 100`
- Exibe métricas com validações
- Aplica filtros por role (RJ/SP)

## Endpoints do Backend

### Dashboard Financeiro
```bash
GET /api/v1/finance/dashboard
Authorization: Bearer {firebase_token}
```

### Vendas
```bash
GET /api/v1/finance/sales?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {firebase_token}
```

### Empreendimentos
```bash
GET /api/v1/finance/enterprises
Authorization: Bearer {firebase_token}
```

## Cache

Os dados são cacheados para melhor performance:
- Dashboard: 10 minutos
- Vendas: 10 minutos  
- Empreendimentos: 1 hora

## Exemplo de Uso

```javascript
// No frontend
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/finance/dashboard`, {
  headers: {
    'Authorization': `Bearer ${await user.getIdToken()}`
  }
});

const data = await response.json();
console.log(data.metrics); // { meta_anual_vgv: ..., vgv_em_estoque: ..., ... }
```

## Validação de Dados

O sistema automaticamente valida:
- Consistência entre VGV e estoque
- Cálculo de VSO vs meta
- Completion de metas anuais
- Performance levels (Meta atingida, Dentro do esperado, etc.)

## Troubleshooting

### Erro: "Sienge API not configured"
- Verifique se `SIENGE_SUBDOMAIN` e `SIENGE_API_TOKEN` estão configurados

### Erro: "Sienge API token expired or invalid"
- Verifique se o token está válido e não expirou

### Dados zerados
- Verifique se as datas estão corretas
- Confirme se os endpoints retornam dados no Postman/Insomnia

### Performance lenta
- Verifique se o Redis está configurado
- Cache automático deve melhorar após primeira requisição

---

**Nota**: Esta implementação segue exatamente sua estrutura JavaScript existente, adaptada para Python com FastAPI e cache Redis.
