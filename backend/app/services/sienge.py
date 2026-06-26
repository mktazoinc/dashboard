import httpx
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import asyncio

from app.core.config import settings


class SiengeClient:
    """Cliente para integração com API do Sienge"""
    
    def __init__(self):
        self.base_url = settings.SIENGE_API_URL
        self.token = settings.SIENGE_API_TOKEN
        self.username = settings.SIENGE_API_USERNAME
        self._headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Faz requisição para API do Sienge com retry e error handling"""
        
        if not self.token or not self.username:
            raise ValueError("SIENGE_API_TOKEN and SIENGE_API_USERNAME must be configured")
        
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
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
                        # Token expired, would need refresh logic here
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
    
    async def get_enterprises(self) -> List[Dict[str, Any]]:
        """Obter lista de empreendimentos"""
        try:
            data = await self._make_request("GET", "/enterprises")
            return data.get("enterprises", [])
        except Exception as e:
            print(f"Error fetching enterprises: {e}")
            return []
    
    async def get_sales(
        self, 
        enterprise_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        realtor_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obter dados de vendas com filtros opcionais"""
        params = {}
        
        if enterprise_id:
            params["enterprise_id"] = enterprise_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if realtor_id:
            params["realtor_id"] = realtor_id
        
        try:
            data = await self._make_request("GET", "/sales", params=params)
            return data.get("sales", [])
        except Exception as e:
            print(f"Error fetching sales: {e}")
            return []
    
    async def get_vgv_data(
        self, 
        enterprise_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Obter dados de VGV (Valor Geral de Vendas)"""
        params = {}
        
        if enterprise_id:
            params["enterprise_id"] = enterprise_id
        if year:
            params["year"] = year
        else:
            params["year"] = datetime.now().year
        
        try:
            data = await self._make_request("GET", "/vgv", params=params)
            return data
        except Exception as e:
            print(f"Error fetching VGV data: {e}")
            return {"total_vgv": 0, "stock_vgv": 0, "sold_vgv": 0}
    
    async def get_units_available(
        self, 
        enterprise_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obter unidades disponíveis em estoque"""
        params = {}
        
        if enterprise_id:
            params["enterprise_id"] = enterprise_id
        
        try:
            data = await self._make_request("GET", "/units/available", params=params)
            return data.get("units", [])
        except Exception as e:
            print(f"Error fetching available units: {e}")
            return []
    
    async def get_realtors(self) -> List[Dict[str, Any]]:
        """Obter lista de corretores"""
        try:
            data = await self._make_request("GET", "/realtors")
            return data.get("realtors", [])
        except Exception as e:
            print(f"Error fetching realtors: {e}")
            return []
    
    async def get_monthly_targets(
        self, 
        enterprise_id: Optional[str] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Obter metas mensais"""
        params = {}
        
        if enterprise_id:
            params["enterprise_id"] = enterprise_id
        if year:
            params["year"] = year
        else:
            params["year"] = datetime.now().year
        
        try:
            data = await self._make_request("GET", "/targets/monthly", params=params)
            return data
        except Exception as e:
            print(f"Error fetching monthly targets: {e}")
            return {"monthly_targets": {}}
    
    async def get_vso_data(
        self, 
        enterprise_id: Optional[str] = None,
        period: str = "current_month"
    ) -> Dict[str, Any]:
        """Obter dados de VSO (Vendas sobre o Estoque)"""
        params = {"period": period}
        
        if enterprise_id:
            params["enterprise_id"] = enterprise_id
        
        try:
            data = await self._make_request("GET", "/vso", params=params)
            return data
        except Exception as e:
            print(f"Error fetching VSO data: {e}")
            return {"vso_percentage": 0, "vso_target": 0, "vso_actual": 0}


# Singleton instance
sienge_client = SiengeClient()
