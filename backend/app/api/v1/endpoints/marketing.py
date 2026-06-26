from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

from app.core.security import require_any_role
from app.services.supabase import supabase_service
from app.services.cache import cache_service, CacheKeys, cached_call

router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_marketing_dashboard(
    data_inicio: Optional[str] = Query(None, description="Data início - YYYY-MM-DD"),
    data_fim: Optional[str] = Query(None, description="Data fim - YYYY-MM-DD"),
    cidade: Optional[str] = Query(None, description="Filtrar por cidade"),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["marketing_rj", "marketing_sp", "admin", "mestre_do_universo"])
    )
):
    """Get marketing dashboard data with Supabase integration and role-based filters"""
    user_role = current_user["role"]
    user_email = current_user["email"]
    
    # Aplicar role-based city filtering
    if cidade and cidade not in ["Rio de Janeiro", "Campinas"]:
        cidade = None
    
    if user_role in ["marketing_rj"]:
        cidade = "Rio de Janeiro"
    elif user_role in ["marketing_sp"]:
        cidade = "Campinas"
    
    # Se não especificado, usar mês atual
    if not data_inicio or not data_fim:
        now = datetime.now()
        data_inicio = now.replace(day=1).strftime("%Y-%m-%d")
        data_fim = now.strftime("%Y-%m-%d")
    
    # Gerar cache key baseado nos filtros
    cache_key = f"marketing:dashboard:{user_role}:{cidade}:{data_inicio}:{data_fim}"
    
    async def fetch_dashboard_data():
        # Buscar métricas do Supabase
        metrics_result = await cached_call(
            f"supabase:metrics:{cidade}:{data_inicio}:{data_fim}",
            600,  # 10 minutos cache
            supabase_service.get_marketing_metrics,
            data_inicio,
            data_fim,
            cidade
        )
        
        # Buscar opções de filtros
        [origens, status_options] = await Promise.all([
            cached_call("supabase:origens", 3600, supabase_service.get_lead_sources),
            cached_call("supabase:status", 3600, supabase_service.get_lead_status_options)
        ])
        
        return {
            "user": user_email,
            "role": user_role,
            "city": cidade,
            "filters": {
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "cidade": cidade,
            },
            "metrics": metrics_result.get("metrics", {}),
            "filter_options": {
                "origens": origens,
                "status": status_options,
                "cidades": ["Rio de Janeiro", "Campinas"] if user_role in ["admin", "mestre_do_universo"] else [cidade]
            },
            "supabase_configured": supabase_service.is_configured(),
            "last_updated": metrics_result.get("last_updated"),
        }
    
    dashboard_data = await cached_call(
        cache_key,
        300,  # 5 minutos cache
        fetch_dashboard_data
    )
    
    return dashboard_data


@router.get("/leads", response_model=Dict[str, Any])
async def get_leads(
    data_entrada_inicio: Optional[str] = Query(None, description="Data de entrada - início"),
    data_entrada_fim: Optional[str] = Query(None, description="Data de entrada - fim"),
    data_acao_inicio: Optional[str] = Query(None, description="Data de ação - início"),
    data_acao_fim: Optional[str] = Query(None, description="Data de ação - fim"),
    cidade: Optional[str] = Query(None, description="Filtrar por cidade"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    origem: Optional[str] = Query(None, description="Filtrar por origem"),
    empreendimento: Optional[str] = Query(None, description="Filtrar por empreendimento"),
    corretor: Optional[str] = Query(None, description="Filtrar por corretor"),
    limit: Optional[int] = Query(50, description="Limite de resultados"),
    offset: Optional[int] = Query(0, description="Offset para paginação"),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["marketing_rj", "marketing_sp", "admin", "mestre_do_universo"])
    )
):
    """Get leads with dual date filters - marketing roles only"""
    user_role = current_user["role"]
    
    # Aplicar role-based city filtering
    if user_role in ["marketing_rj"]:
        cidade = "Rio de Janeiro"
    elif user_role in ["marketing_sp"]:
        cidade = "Campinas"
    
    # Gerar cache key baseado nos filtros
    cache_key = f"marketing:leads:{user_role}:{data_entrada_inicio}:{data_entrada_fim}:{data_acao_inicio}:{data_acao_fim}:{cidade}:{status}:{origem}:{empreendimento}:{corretor}:{limit}:{offset}"
    
    async def fetch_leads():
        leads_result = await cached_call(
            cache_key,
            300,  # 5 minutos cache
            supabase_service.get_leads,
            data_entrada_inicio,
            data_entrada_fim,
            data_acao_inicio,
            data_acao_fim,
            cidade,
            status,
            origem,
            empreendimento,
            corretor,
            limit,
            offset
        )
        
        return {
            "user": current_user["email"],
            "role": user_role,
            "filters": leads_result.get("filters_applied", {}),
            "leads": leads_result.get("leads", []),
            "pagination": {
                "total": leads_result.get("total", 0),
                "limit": limit,
                "offset": offset,
                "has_more": (offset or 0) + (limit or 50) < leads_result.get("total", 0)
            },
            "supabase_configured": supabase_service.is_configured(),
            "last_updated": datetime.now().isoformat(),
        }
    
    leads_data = await fetch_leads()
    return leads_data


@router.get("/leads/export", response_model=Dict[str, Any])
async def export_leads(
    data_entrada_inicio: Optional[str] = Query(None, description="Data de entrada - início"),
    data_entrada_fim: Optional[str] = Query(None, description="Data de entrada - fim"),
    data_acao_inicio: Optional[str] = Query(None, description="Data de ação - início"),
    data_acao_fim: Optional[str] = Query(None, description="Data de ação - fim"),
    cidade: Optional[str] = Query(None, description="Filtrar por cidade"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    format: str = Query("csv", description="Formato de exportação: csv, xlsx"),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["marketing_rj", "marketing_sp", "admin", "mestre_do_universo"])
    )
):
    """Export leads data - marketing roles only"""
    user_role = current_user["role"]
    
    # Aplicar role-based city filtering
    if user_role in ["marketing_rj"]:
        cidade = "Rio de Janeiro"
    elif user_role in ["marketing_sp"]:
        cidade = "Campinas"
    
    # Buscar todos os leads para exportação (sem limite)
    leads_result = await supabase_service.get_leads(
        data_entrada_inicio=data_entrada_inicio,
        data_entrada_fim=data_entrada_fim,
        data_acao_inicio=data_acao_inicio,
        data_acao_fim=data_acao_fim,
        cidade=cidade,
        status=status,
        limit=10000  # Limite alto para exportação
    )
    
    leads = leads_result.get("leads", [])
    
    if format.lower() == "csv":
        # TODO: Implementar CSV export
        return {
            "message": "CSV export to be implemented",
            "total_records": len(leads),
            "download_url": "#"
        }
    elif format.lower() == "xlsx":
        # TODO: Implementar Excel export
        return {
            "message": "Excel export to be implemented", 
            "total_records": len(leads),
            "download_url": "#"
        }
    else:
        return {
            "error": "Invalid format. Use 'csv' or 'xlsx'"
        }


# Helper function para simular Promise.all
async def Promise_all(tasks: List):
    """Simula Promise.all do JavaScript para asyncio"""
    return await asyncio.gather(*tasks)
