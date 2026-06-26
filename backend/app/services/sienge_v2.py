import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from app.core.config import settings


class SiengeClientV2:
    """Cliente para integração com API do Sienge - versão simplificada baseada na implementação existente"""
    
    def __init__(self):
        self.subdomain = getattr(settings, 'SIENGE_SUBDOMAIN', None)
        self.base_url = f"https://{self.subdomain}.sienge.com.br/api" if self.subdomain else None
        self.token = getattr(settings, 'SIENGE_API_TOKEN', None)
        self._headers = {
            "Authorization": f"Bearer {self.token}" if self.token else None,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    def is_configured(self) -> bool:
        """Verifica se o cliente está configurado"""
        return bool(self.subdomain and self.token)
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Faz requisição para API do Sienge com retry e error handling"""
        
        if not self.is_configured():
            raise ValueError("SIENGE_SUBDOMAIN and SIENGE_API_TOKEN must be configured")
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(3):  # Retry up to 3 times
                try:
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=self._headers,
                        params=params,
                        json=data,
                    )
                    
                    if response.status_code == 401:
                        raise Exception("Sienge API token expired or invalid")
                    
                    response.raise_for_status()
                    return response.json()
                    
                except httpx.HTTPStatusError as e:
                    if e.response.status_code >= 500 and attempt < 2:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    raise Exception(f"Sienge API error: {e.response.status_code} - {e.response.text}")
                    
                except httpx.RequestError as e:
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise Exception(f"Sienge API request failed: {str(e)}")
    
    async def get_vendas(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Obter dados de vendas - similar à implementação existente"""
        params = {
            "dataInicio": start_date,
            "dataFim": end_date,
        }
        
        try:
            data = await self._make_request("GET", "/vendas", params=params)
            return {
                "vendas": data.get("vendas", 0),
                "vgv": data.get("vgv", 0),
                "unidades": data.get("unidades", 0),
                "data": data.get("data", []),
            }
        except Exception as e:
            print(f"Error fetching vendas: {e}")
            return {"vendas": 0, "vgv": 0, "unidades": 0, "data": []}
    
    async def get_custos_marketing(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Obter custos de marketing - similar à implementação existente"""
        params = {
            "dataInicio": start_date,
            "dataFim": end_date,
        }
        
        try:
            data = await self._make_request("GET", "/custos/marketing", params=params)
            return data.get("custos", [])
        except Exception as e:
            print(f"Error fetching custos marketing: {e}")
            return []
    
    async def get_empreendimentos(self) -> List[Dict[str, Any]]:
        """Obter lista de empreendimentos - similar à implementação existente"""
        try:
            data = await self._make_request("GET", "/empreendimentos")
            return data.get("empreendimentos", [])
        except Exception as e:
            print(f"Error fetching empreendimentos: {e}")
            return []
    
    async def get_estoque(self, enterprise_id: str) -> Dict[str, Any]:
        """Obter dados de estoque de um empreendimento - similar à implementação existente"""
        try:
            data = await self._make_request("GET", f"/empreendimentos/{enterprise_id}/estoque")
            return {
                "disponiveis": data.get("disponiveis", 0),
                "vgvEstoque": data.get("vgvEstoque", 0),
                "total": data.get("total", 0),
            }
        except Exception as e:
            print(f"Error fetching estoque for enterprise {enterprise_id}: {e}")
            return {"disponiveis": 0, "vgvEstoque": 0, "total": 0}
    
    async def get_corretores(self) -> List[Dict[str, Any]]:
        """Obter lista de corretores"""
        try:
            data = await self._make_request("GET", "/corretores")
            return data.get("corretores", [])
        except Exception as e:
            print(f"Error fetching corretores: {e}")
            return []
    
    async def get_dashboard_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Obter dados consolidados para o dashboard - similar ao hook useSiengeIntegration"""
        if not self.is_configured():
            return {
                "vendas": 0,
                "vgv": 0,
                "estoque": 0,
                "vgvEstoque": 0,
                "custos": [],
                "loading": False,
                "is_configured": False,
            }
        
        try:
            # Paralelizar as requisições como na implementação original
            [vendas_data, custos_data, empreendimentos] = await Promise.all([
                self.get_vendas(start_date, end_date),
                self.get_custos_marketing(start_date, end_date),
                self.get_empreendimentos()
            ])
            
            # Calcular estoque total
            sum_estoque = 0
            sum_vgv_estoque = 0
            
            if empreendimentos and len(empreendimentos) > 0:
                estoques = await Promise.all([
                    self.get_estoque(emp["id"]) for emp in empreendimentos
                ])
                
                for est in estoques:
                    sum_estoque += est.get("disponiveis", 0)
                    sum_vgv_estoque += est.get("vgvEstoque", 0)
            
            return {
                "vendas": vendas_data.get("vendas", 0),
                "vgv": vendas_data.get("vgv", 0),
                "estoque": sum_estoque,
                "vgvEstoque": sum_vgv_estoque,
                "custos": custos_data,
                "loading": False,
                "is_configured": True,
                "empreendimentos": empreendimentos,
                "vendas_data": vendas_data,
            }
            
        except Exception as e:
            print(f"Error fetching dashboard data: {e}")
            return {
                "vendas": 0,
                "vgv": 0,
                "estoque": 0,
                "vgvEstoque": 0,
                "custos": [],
                "loading": False,
                "is_configured": True,
                "error": str(e),
            }


# Helper function para simular Promise.all do JavaScript
async def Promise_all(tasks: List):
    """Simula Promise.all do JavaScript para asyncio"""
    return await asyncio.gather(*tasks)


# Singleton instance
sienge_client_v2 = SiengeClientV2()
