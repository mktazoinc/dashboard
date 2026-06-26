from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class CityEnum(str, Enum):
    RIO_DE_JANEIRO = "Rio de Janeiro"
    CAMPINAS = "Campinas"


class UnitStatus(str, Enum):
    AVAILABLE = "Disponível"
    RESERVED = "Reservado"
    SOLD = "Vendido"
    CANCELLED = "Cancelado"


class Enterprise(BaseModel):
    """Modelo para empreendimentos"""
    id: str
    name: str
    city: CityEnum
    address: str
    total_units: int
    launch_date: date
    vgv_total: float
    is_active: bool = True
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }


class Realtor(BaseModel):
    """Modelo para corretores"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    city: CityEnum
    commission_rate: float = Field(ge=0, le=1)  # 0-100%
    is_active: bool = True


class Unit(BaseModel):
    """Modelo para unidades imobiliárias"""
    id: str
    enterprise_id: str
    unit_number: str
    type: str  # Apartamento, Casa, etc.
    bedrooms: int
    area: float  # m²
    price: float
    status: UnitStatus
    floor: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Sale(BaseModel):
    """Modelo para vendas"""
    id: str
    unit_id: str
    enterprise_id: str
    realtor_id: str
    client_name: str
    client_document: str
    sale_date: date
    contract_value: float
    financed_amount: Optional[float] = None
    commission_amount: float
    status: str  # Confirmada, Cancelada, etc.
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }


class MonthlyTarget(BaseModel):
    """Modelo para metas mensais"""
    enterprise_id: str
    year: int
    month: int
    vgv_target: float
    units_target: int
    vso_target: float  # percentage
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VGVData(BaseModel):
    """Modelo para dados de VGV"""
    enterprise_id: Optional[str] = None
    year: int
    month: Optional[int] = None
    total_vgv: float
    stock_vgv: float
    sold_vgv: float
    realized_vgv: float
    units_sold: int
    units_available: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VSOData(BaseModel):
    """Modelo para dados de VSO (Vendas sobre o Estoque)"""
    enterprise_id: Optional[str] = None
    period: str  # current_month, last_month, year_to_date
    vso_percentage: float
    vso_target: float
    stock_value: float
    sold_value: float
    target_value: float
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DashboardMetrics(BaseModel):
    """Modelo para métricas do dashboard financeiro"""
    meta_anual_vgv: float
    vgv_em_estoque: float
    realizado_vgv: float
    unidades_vendidas: int
    vso_meta: float
    vso_estoque: float
    vso_realizado: float
    
    # Dados adicionais por cidade
    vgv_rj: Optional[float] = None
    vgv_sp: Optional[float] = None
    unidades_rj: Optional[int] = None
    unidades_sp: Optional[int] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FilterOptions(BaseModel):
    """Modelo para opções de filtro"""
    enterprises: List[Enterprise]
    realtors: List[Realtor]
    cities: List[CityEnum]
    date_range: Dict[str, str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SalesChart(BaseModel):
    """Modelo para dados de gráficos de vendas"""
    period: str
    data: List[Dict[str, Any]]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EnterprisePerformance(BaseModel):
    """Modelo para performance por empreendimento"""
    enterprise: Enterprise
    vgv_total: float
    units_sold: int
    vso_percentage: float
    target_completion: float
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
