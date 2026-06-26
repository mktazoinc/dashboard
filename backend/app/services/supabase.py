import os
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import httpx
from supabase import create_client, Client

from app.core.config import settings


class SupabaseService:
    """Serviço para integração com Supabase - dados de leads e marketing"""
    
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL
        self.supabase_key = settings.SUPABASE_SERVICE_KEY
        self._client: Optional[Client] = None
    
    def get_client(self) -> Client:
        """Obter cliente Supabase (lazy initialization)"""
        if self._client is None:
            if not self.supabase_url or not self.supabase_key:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be configured")
            
            self._client = create_client(self.supabase_url, self.supabase_key)
        
        return self._client
    
    def is_configured(self) -> bool:
        """Verifica se Supabase está configurado"""
        return bool(self.supabase_url and self.supabase_key)
    
    async def get_leads(
        self,
        data_entrada_inicio: Optional[str] = None,
        data_entrada_fim: Optional[str] = None,
        data_acao_inicio: Optional[str] = None,
        data_acao_fim: Optional[str] = None,
        cidade: Optional[str] = None,
        status: Optional[str] = None,
        origem: Optional[str] = None,
        empreendimento: Optional[str] = None,
        corretor: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obter leads com filtros duplos de data conforme spec seção 6.0
        """
        if not self.is_configured():
            return {
                "leads": [],
                "total": 0,
                "error": "Supabase not configured"
            }
        
        try:
            client = self.get_client()
            query = client.table("leads").select("*", count="exact")
            
            # Aplicar filtros de data de entrada
            if data_entrada_inicio:
                query = query.gte("data_entrada", data_entrada_inicio)
            if data_entrada_fim:
                query = query.lte("data_entrada", data_entrada_fim)
            
            # Aplicar filtros de data de ação
            if data_acao_inicio:
                query = query.gte("data_acao", data_acao_inicio)
            if data_acao_fim:
                query = query.lte("data_acao", data_acao_fim)
            
            # Aplicar outros filtros
            if cidade:
                query = query.eq("cidade", cidade)
            if status:
                query = query.eq("status", status)
            if origem:
                query = query.eq("origem", origem)
            if empreendimento:
                query = query.eq("empreendimento", empreendimento)
            if corretor:
                query = query.eq("corretor", corretor)
            
            # Aplicar paginação
            if offset:
                query = query.range(offset, offset + (limit or 1000) - 1)
            elif limit:
                query = query.limit(limit)
            
            # Ordenar por data de entrada (mais recentes primeiro)
            query = query.order("data_entrada", desc=True)
            
            result = query.execute()
            
            return {
                "leads": result.data or [],
                "total": result.count or 0,
                "filters_applied": {
                    "data_entrada_inicio": data_entrada_inicio,
                    "data_entrada_fim": data_entrada_fim,
                    "data_acao_inicio": data_acao_inicio,
                    "data_acao_fim": data_acao_fim,
                    "cidade": cidade,
                    "status": status,
                    "origem": origem,
                    "empreendimento": empreendimento,
                    "corretor": corretor,
                }
            }
            
        except Exception as e:
            print(f"Error fetching leads from Supabase: {e}")
            return {
                "leads": [],
                "total": 0,
                "error": str(e)
            }
    
    async def get_marketing_metrics(
        self,
        data_inicio: Optional[str] = None,
        data_fim: Optional[str] = None,
        cidade: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obter métricas de marketing calculadas dos leads
        """
        if not self.is_configured():
            return self._get_mock_metrics()
        
        try:
            # Buscar leads no período
            leads_result = await self.get_leads(
                data_entrada_inicio=data_inicio,
                data_entrada_fim=data_fim,
                cidade=cidade,
                limit=10000  # Buscar todos para cálculo
            )
            
            leads = leads_result.get("leads", [])
            
            # Calcular métricas
            metrics = self._calculate_metrics(leads)
            
            return {
                "metrics": metrics,
                "period": {
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "cidade": cidade
                },
                "total_leads": len(leads),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error calculating marketing metrics: {e}")
            return self._get_mock_metrics()
    
    def _calculate_metrics(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcular métricas de marketing a partir dos leads
        """
        if not leads:
            return {
                "leads_totais": 0,
                "descartados": 0,
                "em_atendimento": 0,
                "agendamentos": 0,
                "visitas": 0,
                "reservas": 0,
                "vendas_realizadas": 0,
                "cpl_medio": 0,
                "taxa_conversao": 0,
                "origens": {},
                "cidades": {},
                "status_distribuicao": {}
            }
        
        # Contar por status
        status_counts = {}
        origem_counts = {}
        cidade_counts = {}
        
        for lead in leads:
            status = lead.get("status", "Não informado")
            origem = lead.get("origem", "Não informado")
            cidade = lead.get("cidade", "Não informado")
            
            status_counts[status] = status_counts.get(status, 0) + 1
            origem_counts[origem] = origem_counts.get(origem, 0) + 1
            cidade_counts[cidade] = cidade_counts.get(cidade, 0) + 1
        
        # Mapear status para métricas
        metrics = {
            "leads_totais": len(leads),
            "descartados": status_counts.get("Descartado", 0),
            "em_atendimento": status_counts.get("Em atendimento", 0),
            "agendamentos": status_counts.get("Agendado", 0),
            "visitas": status_counts.get("Visitou", 0),
            "reservas": status_counts.get("Reservado", 0),
            "vendas_realizadas": status_counts.get("Vendido", 0),
            "cpl_medio": self._calculate_cpl(leads),
            "taxa_conversao": self._calculate_conversion_rate(leads),
            "origens": origem_counts,
            "cidades": cidade_counts,
            "status_distribuicao": status_counts
        }
        
        return metrics
    
    def _calculate_cpl(self, leads: List[Dict[str, Any]]) -> float:
        """
        Calcular CPL (Custo por Lead) médio
        """
        total_cost = 0
        valid_leads = 0
        
        for lead in leads:
            custo = lead.get("custo_aquisicao", 0)
            if custo and custo > 0:
                total_cost += custo
                valid_leads += 1
        
        return total_cost / valid_leads if valid_leads > 0 else 0
    
    def _calculate_conversion_rate(self, leads: List[Dict[str, Any]]) -> float:
        """
        Calcular taxa de conversão (leads para vendas)
        """
        if not leads:
            return 0
        
        total_leads = len(leads)
        vendas = sum(1 for lead in leads if lead.get("status") == "Vendido")
        
        return (vendas / total_leads) * 100 if total_leads > 0 else 0
    
    def _get_mock_metrics(self) -> Dict[str, Any]:
        """
        Retornar métricas mock quando Supabase não está configurado
        """
        return {
            "metrics": {
                "leads_totais": 0,
                "descartados": 0,
                "em_atendimento": 0,
                "agendamentos": 0,
                "visitas": 0,
                "reservas": 0,
                "vendas_realizadas": 0,
                "cpl_medio": 0,
                "taxa_conversao": 0,
                "origens": {},
                "cidades": {},
                "status_distribuicao": {}
            },
            "period": {
                "data_inicio": None,
                "data_fim": None,
                "cidade": None
            },
            "total_leads": 0,
            "last_updated": datetime.now().isoformat(),
            "error": "Supabase not configured - using mock data"
        }
    
    async def get_lead_sources(self) -> List[str]:
        """
        Obter lista de origens de leads distintas
        """
        if not self.is_configured():
            return ["Facebook", "Google", "Instagram", "Indicação", "Site", "Outros"]
        
        try:
            client = self.get_client()
            result = client.table("leads").select("origem").execute()
            
            origens = set()
            for lead in result.data or []:
                if lead.get("origem"):
                    origens.add(lead["origem"])
            
            return sorted(list(origens))
            
        except Exception as e:
            print(f"Error fetching lead sources: {e}")
            return ["Facebook", "Google", "Instagram", "Indicação", "Site", "Outros"]
    
    async def get_lead_status_options(self) -> List[str]:
        """
        Obter lista de status possíveis para leads
        """
        return [
            "Novo",
            "Em atendimento", 
            "Agendado",
            "Visitou",
            "Reservado",
            "Vendido",
            "Descartado",
            "Perdido"
        ]


# Singleton instance
supabase_service = SupabaseService()
