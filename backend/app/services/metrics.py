from typing import Dict, Any, List, Optional
from datetime import datetime, date
from decimal import Decimal

from app.models.finance import (
    VGVData, 
    VSOData, 
    MonthlyTarget,
    DashboardMetrics
)


class MetricsCalculator:
    """Serviço para cálculo de métricas financeiras"""
    
    @staticmethod
    def calculate_vso(
        stock_value: float,
        sold_value: float,
        period: str = "current_month"
    ) -> VSOData:
        """
        Calcula VSO (Vendas sobre o Estoque)
        Fórmula: (Valor Vendido / Valor em Estoque) * 100
        """
        if stock_value <= 0:
            vso_percentage = 0.0
        else:
            vso_percentage = (sold_value / stock_value) * 100
        
        return VSOData(
            period=period,
            vso_percentage=round(vso_percentage, 2),
            stock_value=stock_value,
            sold_value=sold_value,
            target_value=0.0,  # Will be set based on targets
        )
    
    @staticmethod
    def calculate_vso_target(
        monthly_targets: List[MonthlyTarget],
        current_month: int,
        current_year: int
    ) -> float:
        """
        Calcula meta de VSO baseada nas metas mensais
        """
        current_target = None
        for target in monthly_targets:
            if target.month == current_month and target.year == current_year:
                current_target = target
                break
        
        if not current_target:
            return 0.0
        
        return current_target.vso_target
    
    @staticmethod
    def validate_vso_target(
        vso_percentage: float,
        vso_target: float
    ) -> Dict[str, Any]:
        """
        Valida se o VSO realizado atinge a meta
        """
        is_achieved = vso_percentage >= vso_target
        variance = vso_percentage - vso_target
        
        return {
            "is_achieved": is_achieved,
            "variance_percentage": round(variance, 2),
            "performance_level": MetricsCalculator._get_performance_level(
                vso_percentage, vso_target
            )
        }
    
    @staticmethod
    def _get_performance_level(
        actual: float, 
        target: float
    ) -> str:
        """
        Classifica o nível de performance baseado na meta
        """
        if target <= 0:
            return "Sem meta definida"
        
        percentage_achieved = (actual / target) * 100
        
        if percentage_achieved >= 100:
            return "Meta atingida"
        elif percentage_achieved >= 80:
            return "Dentro do esperado"
        elif percentage_achieved >= 60:
            return "Abaixo do esperado"
        else:
            return "Crítico"
    
    @staticmethod
    def calculate_vgv_completion(
        vgv_data: VGVData,
        annual_target: float
    ) -> Dict[str, Any]:
        """
        Calcula completion de VGV anual
        """
        if annual_target <= 0:
            completion_percentage = 0.0
        else:
            completion_percentage = (vgv_data.realized_vgv / annual_target) * 100
        
        return {
            "completion_percentage": round(completion_percentage, 2),
            "realized_vgv": vgv_data.realized_vgv,
            "annual_target": annual_target,
            "remaining_target": max(0, annual_target - vgv_data.realized_vgv),
            "performance_level": MetricsCalculator._get_performance_level(
                completion_percentage, 100.0
            )
        }
    
    @staticmethod
    def calculate_units_metrics(
        total_units: int,
        sold_units: int,
        available_units: int,
        monthly_target: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Calcula métricas de unidades
        """
        sold_percentage = (sold_units / total_units * 100) if total_units > 0 else 0
        available_percentage = (available_units / total_units * 100) if total_units > 0 else 0
        
        metrics = {
            "total_units": total_units,
            "sold_units": sold_units,
            "available_units": available_units,
            "sold_percentage": round(sold_percentage, 2),
            "available_percentage": round(available_percentage, 2),
        }
        
        if monthly_target:
            monthly_completion = (sold_units / monthly_target * 100) if monthly_target > 0 else 0
            metrics.update({
                "monthly_target": monthly_target,
                "monthly_completion_percentage": round(monthly_completion, 2),
                "monthly_performance": MetricsCalculator._get_performance_level(
                    monthly_completion, 100.0
                )
            })
        
        return metrics
    
    @staticmethod
    def aggregate_metrics_by_city(
        metrics_list: List[Dict[str, Any]],
        cities: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Agrega métricas por cidade
        """
        city_metrics = {}
        
        for city in cities:
            city_data = [m for m in metrics_list if m.get("city") == city]
            
            if city_data:
                city_metrics[city] = {
                    "vgv_total": sum(m.get("vgv_total", 0) for m in city_data),
                    "units_sold": sum(m.get("units_sold", 0) for m in city_data),
                    "vso_percentage": sum(m.get("vso_percentage", 0) for m in city_data) / len(city_data),
                    "enterprises_count": len(set(m.get("enterprise_id") for m in city_data)),
                }
            else:
                city_metrics[city] = {
                    "vgv_total": 0,
                    "units_sold": 0,
                    "vso_percentage": 0,
                    "enterprises_count": 0,
                }
        
        return city_metrics
    
    @staticmethod
    def calculate_dashboard_metrics(
        vgv_data: VGVData,
        vso_data: VSOData,
        monthly_targets: List[MonthlyTarget],
        current_month: int,
        current_year: int,
        city: Optional[str] = None
    ) -> DashboardMetrics:
        """
        Calcula todas as métricas para o dashboard
        """
        # Get current month target
        current_target = None
        for target in monthly_targets:
            if target.month == current_month and target.year == current_year:
                current_target = target
                break
        
        annual_target = current_target.vgv_target if current_target else 0
        vso_target = current_target.vso_target if current_target else 0
        
        # Update VSO with target
        vso_data.target_value = vso_target
        
        # Calculate metrics
        metrics = DashboardMetrics(
            meta_anual_vgv=annual_target,
            vgv_em_estoque=vgv_data.stock_vgv,
            realizado_vgv=vgv_data.realized_vgv,
            unidades_vendidas=vgv_data.units_sold,
            vso_meta=vso_target,
            vso_estoque=vso_data.stock_value,
            vso_realizado=vso_data.sold_value,
        )
        
        # Add city-specific data if provided
        if city:
            # This would be calculated based on city-filtered data
            # For now, using placeholder logic
            if city == "Rio de Janeiro":
                metrics.vgv_rj = vgv_data.realized_vgv * 0.6  # Example: 60% from RJ
                metrics.unidades_rj = int(vgv_data.units_sold * 0.6)
            elif city == "Campinas":
                metrics.vgv_sp = vgv_data.realized_vgv * 0.4  # Example: 40% from SP
                metrics.unidades_sp = int(vgv_data.units_sold * 0.4)
        
        return metrics
    
    @staticmethod
    def validate_data_consistency(
        vgv_data: VGVData,
        vso_data: VSOData,
        units_data: Dict[str, Any]
    ) -> List[str]:
        """
        Valida consistência dos dados
        """
        warnings = []
        
        # Check if stock VGV matches available units value
        if abs(vgv_data.stock_vgv - vso_data.stock_value) > 0.01:
            warnings.append("Inconsistência entre VGV em estoque e valor do estoque VSO")
        
        # Check if sold VGV matches sold units value
        if abs(vgv_data.realized_vgv - vso_data.sold_value) > 0.01:
            warnings.append("Inconsistência entre VGV realizado e valor vendido VSO")
        
        # Check if units count makes sense
        if units_data.get("sold_units", 0) != vgv_data.units_sold:
            warnings.append("Inconsistência na contagem de unidades vendidas")
        
        # Check for negative values
        if vgv_data.stock_vgv < 0 or vgv_data.realized_vgv < 0:
            warnings.append("Valores de VGV negativos detectados")
        
        if vso_data.vso_percentage < 0:
            warnings.append("VSO percentage negativo detectado")
        
        return warnings


# Singleton instance
metrics_calculator = MetricsCalculator()
