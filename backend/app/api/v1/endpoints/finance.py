from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional, List
from datetime import datetime, date

from app.core.security import require_any_role
from app.services.sienge_v2 import sienge_client_v2
from app.services.cache import cache_service, CacheKeys, cached_call
from app.services.metrics import metrics_calculator
from app.models.finance import (
    DashboardMetrics, 
    Enterprise, 
    Realtor, 
    Sale, 
    FilterOptions,
    VGVData,
    VSOData,
    MonthlyTarget
)

router = APIRouter()


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_finance_dashboard(
    enterprise_id: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["comercial_rj", "comercial_sp", "diretoria", "admin", "mestre_do_universo"])
    )
):
    """Get finance dashboard data with Sienge integration and role-based filters"""
    user_role = current_user["role"]
    user_email = current_user["email"]
    
    # Apply role-based city filtering
    if city and city not in ["Rio de Janeiro", "Campinas"]:
        city = None
    
    if user_role in ["comercial_rj", "marketing_rj"]:
        city = "Rio de Janeiro"
    elif user_role in ["comercial_sp", "marketing_sp"]:
        city = "Campinas"
    
    # Generate cache key based on filters and role
    cache_key = CacheKeys.dashboard_metrics(user_role, city)
    
    async def fetch_dashboard_data():
        # Check if Sienge is configured
        if not sienge_client_v2.is_configured():
            return {
                "user": user_email,
                "role": user_role,
                "city": city,
                "metrics": {
                    "meta_anual_vgv": 0,
                    "vgv_em_estoque": 0,
                    "realizado_vgv": 0,
                    "unidades_vendidas": 0,
                    "vso_meta": 0,
                    "vso_estoque": 0,
                    "vso_realizado": 0,
                },
                "sienge_configured": False,
                "error": "Sienge API not configured",
                "last_updated": datetime.now().isoformat(),
            }
        
        # Calculate date range (current month)
        now = datetime.now()
        start_date = now.replace(day=1).strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")
        
        # Fetch data using Sienge V2 (similar to useSiengeIntegration)
        dashboard_data = await cached_call(
            f"sienge:dashboard:{start_date}:{end_date}",
            600,  # 10 minutes cache
            sienge_client_v2.get_dashboard_data,
            start_date,
            end_date
        )
        
        # Calculate VSO using the metrics calculator
        vso_data = metrics_calculator.calculate_vso(
            stock_value=dashboard_data.get("vgvEstoque", 0),
            sold_value=dashboard_data.get("vgv", 0),
            period="current_month"
        )
        
        # Create metrics object
        metrics = DashboardMetrics(
            meta_anual_vgv=dashboard_data.get("vgv", 0) * 12 / max(now.month, 1),  # Estimate annual target
            vgv_em_estoque=dashboard_data.get("vgvEstoque", 0),
            realizado_vgv=dashboard_data.get("vgv", 0),
            unidades_vendidas=dashboard_data.get("vendas", 0),
            vso_meta=15.0,  # Default VSO target
            vso_estoque=dashboard_data.get("vgvEstoque", 0),
            vso_realizado=dashboard_data.get("vgv", 0),
        )
        
        # Calculate VSO validation
        vso_validation = metrics_calculator.validate_vso_target(
            vso_percentage=vso_data.vso_percentage,
            vso_target=metrics.vso_meta
        )
        
        # Calculate VGV completion
        vgv_completion = metrics_calculator.calculate_vgv_completion(
            vgv_data=VGVData(
                enterprise_id=enterprise_id,
                year=now.year,
                total_vgv=dashboard_data.get("vgvEstoque", 0) + dashboard_data.get("vgv", 0),
                stock_vgv=dashboard_data.get("vgvEstoque", 0),
                sold_vgv=dashboard_data.get("vgv", 0),
                realized_vgv=dashboard_data.get("vgv", 0),
                units_sold=dashboard_data.get("vendas", 0),
                units_available=dashboard_data.get("estoque", 0),
            ),
            annual_target=metrics.meta_anual_vgv
        )
        
        return {
            "user": user_email,
            "role": user_role,
            "city": city,
            "metrics": metrics.dict(),
            "sienge_data": dashboard_data,
            "validations": {
                "vso": vso_validation,
                "vgv_completion": vgv_completion,
            },
            "sienge_configured": True,
            "last_updated": datetime.now().isoformat(),
        }
    
    dashboard_data = await cached_call(
        cache_key,
        900,  # 15 minutes cache
        fetch_dashboard_data
    )
    
    return dashboard_data


@router.get("/sales", response_model=Dict[str, Any])
async def get_sales_data(
    enterprise_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    realtor_id: Optional[str] = Query(None),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["comercial_rj", "comercial_sp", "diretoria", "admin", "mestre_do_universo"])
    )
):
    """Get sales data with filters - commercial roles only"""
    user_role = current_user["role"]
    
    # Apply role-based filtering
    if user_role in ["comercial_rj", "marketing_rj"]:
        # RJ users can only see RJ data
        pass  # Would filter by enterprise city
    elif user_role in ["comercial_sp", "marketing_sp"]:
        # SP users can only see SP data
        pass  # Would filter by enterprise city
    
    cache_key = CacheKeys.sales(enterprise_id, f"{start_date}_{end_date}")
    
    async def fetch_sales():
        sales = await sienge_client.get_sales(
            enterprise_id=enterprise_id,
            start_date=start_date,
            end_date=end_date,
            realtor_id=realtor_id
        )
        
        return {
            "user": current_user["email"],
            "role": user_role,
            "filters": {
                "enterprise_id": enterprise_id,
                "start_date": start_date,
                "end_date": end_date,
                "realtor_id": realtor_id,
            },
            "sales": sales,
            "total_count": len(sales),
            "last_updated": datetime.now().isoformat(),
        }
    
    sales_data = await cached_call(
        cache_key,
        600,  # 10 minutes cache
        fetch_sales
    )
    
    return sales_data


@router.get("/enterprises", response_model=Dict[str, Any])
async def get_enterprises(
    current_user: Dict[str, Any] = Depends(
        require_any_role(["comercial_rj", "comercial_sp", "diretoria", "admin", "mestre_do_universo"])
    )
):
    """Get enterprises list - commercial roles only"""
    user_role = current_user["role"]
    
    async def fetch_enterprises():
        enterprises = await cached_call(
            CacheKeys.enterprises(),
            3600,  # 1 hour cache
            sienge_client.get_enterprises
        )
        
        # Apply role-based city filtering
        if user_role in ["comercial_rj", "marketing_rj"]:
            enterprises = [e for e in enterprises if e.get("city") == "Rio de Janeiro"]
        elif user_role in ["comercial_sp", "marketing_sp"]:
            enterprises = [e for e in enterprises if e.get("city") == "Campinas"]
        
        return {
            "enterprises": enterprises,
            "total_count": len(enterprises),
            "user_role": user_role,
        }
    
    return await cached_call(
        f"enterprises:filtered:{user_role}",
        1800,  # 30 minutes cache
        fetch_enterprises
    )


@router.get("/realtors", response_model=Dict[str, Any])
async def get_realtors(
    current_user: Dict[str, Any] = Depends(
        require_any_role(["comercial_rj", "comercial_sp", "diretoria", "admin", "mestre_do_universo"])
    )
):
    """Get realtors list - commercial roles only"""
    user_role = current_user["role"]
    
    async def fetch_realtors():
        realtors = await cached_call(
            CacheKeys.realtors(),
            3600,  # 1 hour cache
            sienge_client.get_realtors
        )
        
        # Apply role-based city filtering
        if user_role in ["comercial_rj", "marketing_rj"]:
            realtors = [r for r in realtors if r.get("city") == "Rio de Janeiro"]
        elif user_role in ["comercial_sp", "marketing_sp"]:
            realtors = [r for r in realtors if r.get("city") == "Campinas"]
        
        return {
            "realtors": realtors,
            "total_count": len(realtors),
            "user_role": user_role,
        }
    
    return await cached_call(
        f"realtors:filtered:{user_role}",
        1800,  # 30 minutes cache
        fetch_realtors
    )


@router.get("/vgv", response_model=Dict[str, Any])
async def get_vgv_data(
    enterprise_id: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["comercial_rj", "comercial_sp", "diretoria", "admin", "mestre_do_universo"])
    )
):
    """Get VGV data - commercial roles only"""
    if not year:
        year = datetime.now().year
    
    cache_key = CacheKeys.vgv(enterprise_id, year)
    
    vgv_data = await cached_call(
        cache_key,
        1800,  # 30 minutes cache
        sienge_client.get_vgv_data,
        enterprise_id,
        year
    )
    
    return {
        "user": current_user["email"],
        "role": current_user["role"],
        "filters": {
            "enterprise_id": enterprise_id,
            "year": year,
        },
        "vgv_data": vgv_data,
        "last_updated": datetime.now().isoformat(),
    }


@router.get("/vso", response_model=Dict[str, Any])
async def get_vso_data(
    enterprise_id: Optional[str] = Query(None),
    period: str = Query("current_month", regex="^(current_month|last_month|year_to_date)$"),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["comercial_rj", "comercial_sp", "diretoria", "admin", "mestre_do_universo"])
    )
):
    """Get VSO data - commercial roles only"""
    cache_key = CacheKeys.vso(enterprise_id, period)
    
    vso_data = await cached_call(
        cache_key,
        1800,  # 30 minutes cache
        sienge_client.get_vso_data,
        enterprise_id,
        period
    )
    
    return {
        "user": current_user["email"],
        "role": current_user["role"],
        "filters": {
            "enterprise_id": enterprise_id,
            "period": period,
        },
        "vso_data": vso_data,
        "last_updated": datetime.now().isoformat(),
    }
