import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

from app.services.cache import cache_service

class AuditAction(str, Enum):
    """Tipos de ações auditadas"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    ROLE_CHANGED = "role_changed"
    PASSWORD_CHANGED = "password_changed"
    DATA_ACCESSED = "data_accessed"
    DATA_EXPORTED = "data_exported"
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    SECURITY_BREACH = "security_breach"
    FAILED_LOGIN = "failed_login"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class AuditSeverity(str, Enum):
    """Níveis de severidade"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditService:
    """Serviço de auditoria para ações críticas"""
    
    def __init__(self):
        self.cache_key_prefix = "audit:"
        self.retention_days = 90  # Dias para manter logs
    
    async def log_action(
        self,
        action: AuditAction,
        user_id: str,
        user_email: str,
        user_role: str,
        severity: AuditSeverity = AuditSeverity.MEDIUM,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra uma ação no audit log
        """
        try:
            timestamp = datetime.now().isoformat()
            
            audit_entry = {
                "id": f"{timestamp}_{user_id}_{action.value}",
                "timestamp": timestamp,
                "action": action.value,
                "severity": severity.value,
                "user": {
                    "id": user_id,
                    "email": user_email,
                    "role": user_role
                },
                "resource": {
                    "type": resource_type,
                    "id": resource_id
                } if resource_type else None,
                "details": details or {},
                "metadata": {
                    "ip_address": ip_address,
                    "user_agent": user_agent,
                    "success": success,
                    "error_message": error_message
                }
            }
            
            # Armazenar no cache (Redis)
            cache_key = f"{self.cache_key_prefix}{audit_entry['id']}"
            await cache_service.set(cache_key, audit_entry, expire_seconds=self.retention_days * 24 * 3600)
            
            # Adicionar à lista de logs recentes para consulta rápida
            recent_logs_key = f"{self.cache_key_prefix}recent:{severity.value}"
            recent_logs = await cache_service.get(recent_logs_key) or []
            recent_logs.append(audit_entry)
            
            # Manter apenas os 1000 logs mais recentes por severidade
            if len(recent_logs) > 1000:
                recent_logs = recent_logs[-1000:]
            
            await cache_service.set(recent_logs_key, recent_logs, expire_seconds=24 * 3600)
            
            # Adicionar à lista de logs do usuário
            user_logs_key = f"{self.cache_key_prefix}user:{user_id}"
            user_logs = await cache_service.get(user_logs_key) or []
            user_logs.append(audit_entry)
            
            # Manter apenas os 500 logs mais recentes por usuário
            if len(user_logs) > 500:
                user_logs = user_logs[-500:]
            
            await cache_service.set(user_logs_key, user_logs, expire_seconds=self.retention_days * 24 * 3600)
            
            # Log crítico também vai para uma lista especial
            if severity in [AuditSeverity.HIGH, AuditSeverity.CRITICAL]:
                critical_logs_key = f"{self.cache_key_prefix}critical"
                critical_logs = await cache_service.get(critical_logs_key) or []
                critical_logs.append(audit_entry)
                
                # Manter apenas os 100 logs críticos mais recentes
                if len(critical_logs) > 100:
                    critical_logs = critical_logs[-100:]
                
                await cache_service.set(critical_logs_key, critical_logs, expire_seconds=7 * 24 * 3600)
            
            return audit_entry
            
        except Exception as e:
            print(f"Error logging audit action: {e}")
            # Não falhar a operação principal se auditoria falhar
            return {}
    
    async def get_user_logs(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Obtém logs de um usuário específico
        """
        try:
            user_logs_key = f"{self.cache_key_prefix}user:{user_id}"
            user_logs = await cache_service.get(user_logs_key) or []
            
            # Aplicar paginação
            total = len(user_logs)
            logs = user_logs[offset:offset + limit]
            
            return {
                "logs": logs,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
            
        except Exception as e:
            print(f"Error getting user logs: {e}")
            return {"logs": [], "total": 0, "limit": limit, "offset": offset, "has_more": False}
    
    async def get_recent_logs(
        self,
        severity: Optional[AuditSeverity] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Obtém logs recentes filtrados por severidade
        """
        try:
            if severity:
                recent_logs_key = f"{self.cache_key_prefix}recent:{severity.value}"
            else:
                # Buscar de todas as severidades
                all_logs = []
                for sev in AuditSeverity:
                    recent_logs_key = f"{self.cache_key_prefix}recent:{sev.value}"
                    logs = await cache_service.get(recent_logs_key) or []
                    all_logs.extend(logs)
                
                # Ordenar por timestamp (mais recentes primeiro)
                all_logs.sort(key=lambda x: x["timestamp"], reverse=True)
                
                total = len(all_logs)
                logs = all_logs[offset:offset + limit]
                
                return {
                    "logs": logs,
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total
                }
            
            logs = await cache_service.get(recent_logs_key) or []
            total = len(logs)
            logs = logs[offset:offset + limit]
            
            return {
                "logs": logs,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
            
        except Exception as e:
            print(f"Error getting recent logs: {e}")
            return {"logs": [], "total": 0, "limit": limit, "offset": offset, "has_more": False}
    
    async def get_critical_logs(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Obtém logs críticos (HIGH e CRITICAL)
        """
        try:
            critical_logs_key = f"{self.cache_key_prefix}critical"
            critical_logs = await cache_service.get(critical_logs_key) or []
            
            total = len(critical_logs)
            logs = critical_logs[offset:offset + limit]
            
            return {
                "logs": logs,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
            
        except Exception as e:
            print(f"Error getting critical logs: {e}")
            return {"logs": [], "total": 0, "limit": limit, "offset": offset, "has_more": False}
    
    async def search_logs(
        self,
        query: str,
        action: Optional[AuditAction] = None,
        severity: Optional[AuditSeverity] = None,
        user_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Busca logs com filtros avançados
        """
        try:
            # Para implementação completa, seria necessário um banco de dados
            # Por ora, busca nos logs recentes
            all_logs = []
            
            if user_id:
                result = await self.get_user_logs(user_id, limit=1000)
                all_logs = result["logs"]
            else:
                result = await self.get_recent_logs(limit=1000)
                all_logs = result["logs"]
            
            # Aplicar filtros
            filtered_logs = []
            for log in all_logs:
                # Filtro de query
                if query:
                    query_lower = query.lower()
                    log_text = json.dumps(log).lower()
                    if query_lower not in log_text:
                        continue
                
                # Filtro de action
                if action and log.get("action") != action.value:
                    continue
                
                # Filtro de severity
                if severity and log.get("severity") != severity.value:
                    continue
                
                # Filtro de data
                if start_date and log.get("timestamp") < start_date:
                    continue
                
                if end_date and log.get("timestamp") > end_date:
                    continue
                
                filtered_logs.append(log)
            
            # Paginação
            total = len(filtered_logs)
            logs = filtered_logs[offset:offset + limit]
            
            return {
                "logs": logs,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total,
                "filters": {
                    "query": query,
                    "action": action.value if action else None,
                    "severity": severity.value if severity else None,
                    "user_id": user_id,
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
            
        except Exception as e:
            print(f"Error searching logs: {e}")
            return {"logs": [], "total": 0, "limit": limit, "offset": offset, "has_more": False}
    
    async def get_audit_statistics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Obtém estatísticas de auditoria
        """
        try:
            # Buscar logs recentes
            result = await self.get_recent_logs(limit=10000)
            logs = result["logs"]
            
            # Filtrar por período
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            recent_logs = [log for log in logs if log.get("timestamp", "") >= cutoff_date]
            
            # Calcular estatísticas
            stats = {
                "total_actions": len(recent_logs),
                "unique_users": len(set(log["user"]["id"] for log in recent_logs)),
                "actions_by_type": {},
                "actions_by_severity": {},
                "actions_by_user": {},
                "failed_actions": 0,
                "critical_actions": 0
            }
            
            for log in recent_logs:
                # Contar por tipo
                action = log.get("action", "unknown")
                stats["actions_by_type"][action] = stats["actions_by_type"].get(action, 0) + 1
                
                # Contar por severidade
                severity = log.get("severity", "unknown")
                stats["actions_by_severity"][severity] = stats["actions_by_severity"].get(severity, 0) + 1
                
                # Contar por usuário
                user_email = log["user"]["email"]
                stats["actions_by_user"][user_email] = stats["actions_by_user"].get(user_email, 0) + 1
                
                # Contar falhas
                if not log.get("metadata", {}).get("success", True):
                    stats["failed_actions"] += 1
                
                # Contar críticos
                if severity in [AuditSeverity.HIGH.value, AuditSeverity.CRITICAL.value]:
                    stats["critical_actions"] += 1
            
            return stats
            
        except Exception as e:
            print(f"Error getting audit statistics: {e}")
            return {
                "total_actions": 0,
                "unique_users": 0,
                "actions_by_type": {},
                "actions_by_severity": {},
                "actions_by_user": {},
                "failed_actions": 0,
                "critical_actions": 0
            }

# Singleton instance
audit_service = AuditService()
