from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.core.security import get_current_user

router = APIRouter()


class QueryRequest(BaseModel):
    """Modelo para requests do Supabase mock"""
    table: str
    select: str = "*"
    filters: List[Dict[str, Any]] = []
    inFilters: List[Dict[str, Any]] = []
    limit: Optional[int] = None
    order: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Modelo para responses do Supabase mock"""
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    count: Optional[int] = None


@router.post("/query", response_model=QueryResponse)
async def supabase_query(
    request: QueryRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Endpoint compatível com Supabase JS client mock
    Processa queries no formato Supabase e traduz para as fontes de dados reais
    """
    user_role = current_user.get("role")
    user_email = current_user.get("email")
    
    try:
        # Log da query para debug
        print(f"[Query API] User {user_email} ({user_role}) querying {request.table}")
        print(f"[Query API] Filters: {request.filters}")
        print(f"[Query API] In filters: {request.inFilters}")
        
        # Processar based on table name
        if request.table == "leads":
            return await process_leads_query(request, user_role)
        elif request.table == "marketing_data":
            return await process_marketing_query(request, user_role)
        elif request.table == "sales_data":
            return await process_sales_query(request, user_role)
        elif request.table == "empreendimentos":
            return await process_enterprises_query(request, user_role)
        elif request.table == "corretores":
            return await process_realtors_query(request, user_role)
        else:
            # Tabela genérica - placeholder
            return QueryResponse(
                data=[],
                error=f"Table '{request.table}' not implemented yet"
            )
            
    except Exception as e:
        print(f"[Query API] Error processing query: {e}")
        return QueryResponse(
            data=None,
            error=str(e)
        )


async def process_leads_query(request: QueryRequest, user_role: str) -> QueryResponse:
    """Processa queries para tabela leads - Sistema 2 (Marketing)"""
    from app.services.sienge_v2 import sienge_client_v2
    
    # Aplicar role-based filtering
    city_filter = None
    if user_role in ["marketing_rj"]:
        city_filter = "Rio de Janeiro"
    elif user_role in ["marketing_sp"]:
        city_filter = "Campinas"
    
    # Simular dados de leads (seria integrado com Supabase real)
    mock_leads = [
        {
            "id": "lead_001",
            "nome": "João Silva",
            "email": "joao@email.com",
            "telefone": "21999999999",
            "cidade": "Rio de Janeiro",
            "data_entrada": "2024-01-15",
            "data_acao": "2024-01-16",
            "status": "Em atendimento",
            "origem": "Facebook",
            "empreendimento": "Residencial AZO RJ",
            "corretor": "Maria Santos"
        },
        {
            "id": "lead_002", 
            "nome": "Maria Oliveira",
            "email": "maria@email.com",
            "telefone": "11999999999",
            "cidade": "Campinas",
            "data_entrada": "2024-01-16",
            "data_acao": "2024-01-17",
            "status": "Visitou",
            "origem": "Google",
            "empreendimento": "Residencial AZO SP",
            "corretor": "João Santos"
        }
    ]
    
    # Aplicar filtros
    filtered_leads = mock_leads
    
    for filter_item in request.filters:
        column = filter_item.get("column")
        operator = filter_item.get("operator")
        value = filter_item.get("value")
        
        if operator == "eq" and column and value is not None:
            filtered_leads = [
                lead for lead in filtered_leads 
                if str(lead.get(column)) == str(value)
            ]
        elif operator == "gte" and column and value is not None:
            filtered_leads = [
                lead for lead in filtered_leads 
                if lead.get(column) and lead.get(column) >= value
            ]
        elif operator == "lte" and column and value is not None:
            filtered_leads = [
                lead for lead in filtered_leads 
                if lead.get(column) and lead.get(column) <= value
            ]
        elif operator == "ilike" and column and value is not None:
            filtered_leads = [
                lead for lead in filtered_leads 
                if lead.get(column) and value.lower() in str(lead.get(column)).lower()
            ]
    
    # Aplicar filtros IN
    for in_filter in request.inFilters:
        column = in_filter.get("column")
        values = in_filter.get("values", [])
        
        if column and values:
            filtered_leads = [
                lead for lead in filtered_leads 
                if lead.get(column) in values
            ]
    
    # Aplicar city filter baseado no role
    if city_filter:
        filtered_leads = [
            lead for lead in filtered_leads 
            if lead.get("cidade") == city_filter
        ]
    
    # Aplicar ordenação
    if request.order:
        column = request.order.get("column")
        ascending = request.order.get("ascending", True)
        
        if column:
            filtered_leads.sort(
                key=lambda x: x.get(column, ""),
                reverse=not ascending
            )
    
    # Aplicar limite
    if request.limit:
        filtered_leads = filtered_leads[:request.limit]
    
    return QueryResponse(
        data=filtered_leads,
        count=len(filtered_leads)
    )


async def process_marketing_query(request: QueryRequest, user_role: str) -> QueryResponse:
    """Processa queries para tabela marketing_data"""
    # Simular dados de marketing
    mock_data = [
        {
            "id": "mkt_001",
            "data": "2024-01-15",
            "canal": "Facebook",
            "leads": 25,
            "custo": 1500.00,
            "cpl": 60.00,
            "cidade": "Rio de Janeiro"
        },
        {
            "id": "mkt_002",
            "data": "2024-01-16", 
            "canal": "Google",
            "leads": 18,
            "custo": 1200.00,
            "cpl": 66.67,
            "cidade": "Campinas"
        }
    ]
    
    # Aplicar filtros similares ao leads
    filtered_data = mock_data
    
    for filter_item in request.filters:
        column = filter_item.get("column")
        operator = filter_item.get("operator")
        value = filter_item.get("value")
        
        if operator == "eq" and column and value is not None:
            filtered_data = [
                item for item in filtered_data 
                if str(item.get(column)) == str(value)
            ]
    
    return QueryResponse(
        data=filtered_data,
        count=len(filtered_data)
    )


async def process_sales_query(request: QueryRequest, user_role: str) -> QueryResponse:
    """Processa queries para tabela sales_data - Sistema 1 (Financeiro)"""
    from app.services.sienge_v2 import sienge_client_v2
    
    if not sienge_client_v2.is_configured():
        return QueryResponse(
            data=[],
            error="Sienge API not configured"
        )
    
    try:
        # Buscar dados reais do Sienge
        now = datetime.now()
        start_date = now.replace(day=1).strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")
        
        vendas_data = await sienge_client_v2.get_vendas(start_date, end_date)
        
        # Transformar para formato compatível
        sales_data = []
        if vendas_data.get("data"):
            for sale in vendas_data["data"]:
                sales_data.append({
                    "id": sale.get("id"),
                    "data_venda": sale.get("data"),
                    "valor": sale.get("valor"),
                    "cliente": sale.get("cliente"),
                    "empreendimento": sale.get("empreendimento"),
                    "corretor": sale.get("corretor"),
                    "cidade": sale.get("cidade"),
                    "status": sale.get("status", "Confirmada")
                })
        
        return QueryResponse(
            data=sales_data,
            count=len(sales_data)
        )
        
    except Exception as e:
        return QueryResponse(
            data=[],
            error=str(e)
        )


async def process_enterprises_query(request: QueryRequest, user_role: str) -> QueryResponse:
    """Processa queries para tabela empreendimentos"""
    from app.services.sienge_v2 import sienge_client_v2
    
    try:
        if sienge_client_v2.is_configured():
            enterprises = await sienge_client_v2.get_empreendimentos()
        else:
            # Dados mock
            enterprises = [
                {
                    "id": "emp_001",
                    "nome": "Residencial AZO RJ",
                    "cidade": "Rio de Janeiro",
                    "status": "Ativo"
                },
                {
                    "id": "emp_002",
                    "nome": "Residencial AZO SP", 
                    "cidade": "Campinas",
                    "status": "Ativo"
                }
            ]
        
        # Aplicar role-based city filtering
        if user_role in ["marketing_rj", "comercial_rj"]:
            enterprises = [e for e in enterprises if e.get("cidade") == "Rio de Janeiro"]
        elif user_role in ["marketing_sp", "comercial_sp"]:
            enterprises = [e for e in enterprises if e.get("cidade") == "Campinas"]
        
        return QueryResponse(
            data=enterprises,
            count=len(enterprises)
        )
        
    except Exception as e:
        return QueryResponse(
            data=[],
            error=str(e)
        )


async def process_realtors_query(request: QueryRequest, user_role: str) -> QueryResponse:
    """Processa queries para tabela corretores"""
    from app.services.sienge_v2 import sienge_client_v2
    
    try:
        if sienge_client_v2.is_configured():
            corretores = await sienge_client_v2.get_corretores()
        else:
            # Dados mock
            corretores = [
                {
                    "id": "corr_001",
                    "nome": "Maria Santos",
                    "email": "maria@azo.com",
                    "cidade": "Rio de Janeiro",
                    "comissao": 0.05
                },
                {
                    "id": "corr_002",
                    "nome": "João Santos",
                    "email": "joao@azo.com", 
                    "cidade": "Campinas",
                    "comissao": 0.05
                }
            ]
        
        # Aplicar role-based city filtering
        if user_role in ["marketing_rj", "comercial_rj"]:
            corretores = [c for c in corretores if c.get("cidade") == "Rio de Janeiro"]
        elif user_role in ["marketing_sp", "comercial_sp"]:
            corretores = [c for c in corretores if c.get("cidade") == "Campinas"]
        
        return QueryResponse(
            data=corretores,
            count=len(corretores)
        )
        
    except Exception as e:
        return QueryResponse(
            data=[],
            error=str(e)
        )
