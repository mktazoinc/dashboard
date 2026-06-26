from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.security import require_any_role, get_current_user
from app.services.audit import audit_service, AuditAction, AuditSeverity

router = APIRouter()


@router.get("/logs")
async def get_audit_logs(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["admin", "mestre_do_universo"])
    )
):
    """Get audit logs with filters - admin only"""
    try:
        # Convert string to enum if provided
        severity_enum = None
        if severity:
            try:
                severity_enum = AuditSeverity(severity)
            except ValueError:
                return {"error": f"Invalid severity: {severity}"}
        
        result = await audit_service.get_recent_logs(
            severity=severity_enum,
            limit=limit,
            offset=offset
        )
        
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            **result
        }
        
    except Exception as e:
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            "error": str(e),
            "logs": [],
            "total": 0
        }


@router.get("/logs/critical")
async def get_critical_audit_logs(
    limit: int = Query(50, ge=1, le=500, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["admin", "mestre_do_universo"])
    )
):
    """Get critical audit logs (HIGH and CRITICAL) - admin only"""
    try:
        result = await audit_service.get_critical_logs(
            limit=limit,
            offset=offset
        )
        
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            **result
        }
        
    except Exception as e:
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            "error": str(e),
            "logs": [],
            "total": 0
        }


@router.get("/logs/user/{user_id}")
async def get_user_audit_logs(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["admin", "mestre_do_universo"])
    )
):
    """Get audit logs for a specific user - admin only"""
    try:
        result = await audit_service.get_user_logs(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            "target_user": user_id,
            **result
        }
        
    except Exception as e:
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            "target_user": user_id,
            "error": str(e),
            "logs": [],
            "total": 0
        }


@router.get("/logs/search")
async def search_audit_logs(
    query: str = Query(..., description="Search query"),
    action: Optional[str] = Query(None, description="Filter by action"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["admin", "mestre_do_universo"])
    )
):
    """Search audit logs with advanced filters - admin only"""
    try:
        # Convert strings to enums if provided
        action_enum = None
        if action:
            try:
                action_enum = AuditAction(action)
            except ValueError:
                return {"error": f"Invalid action: {action}"}
        
        severity_enum = None
        if severity:
            try:
                severity_enum = AuditSeverity(severity)
            except ValueError:
                return {"error": f"Invalid severity: {severity}"}
        
        result = await audit_service.search_logs(
            query=query,
            action=action_enum,
            severity=severity_enum,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )
        
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            **result
        }
        
    except Exception as e:
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            "error": str(e),
            "logs": [],
            "total": 0
        }


@router.get("/statistics")
async def get_audit_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["admin", "mestre_do_universo"])
    )
):
    """Get audit statistics - admin only"""
    try:
        stats = await audit_service.get_audit_statistics(days=days)
        
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            "period_days": days,
            "statistics": stats,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            "error": str(e),
            "statistics": {
                "total_actions": 0,
                "unique_users": 0,
                "actions_by_type": {},
                "actions_by_severity": {},
                "actions_by_user": {},
                "failed_actions": 0,
                "critical_actions": 0
            }
        }


@router.post("/log")
async def create_audit_log(
    action: str,
    severity: str = "medium",
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create an audit log entry - for manual logging"""
    try:
        # Convert strings to enums
        try:
            action_enum = AuditAction(action)
        except ValueError:
            return {"error": f"Invalid action: {action}"}
        
        try:
            severity_enum = AuditSeverity(severity)
        except ValueError:
            return {"error": f"Invalid severity: {severity}"}
        
        # Get request context (would need to be passed from the actual request)
        # For now, using placeholder values
        ip_address = "127.0.0.1"  # Would get from request.client.host
        user_agent = "API Request"  # Would get from request.headers.get("user-agent")
        
        audit_entry = await audit_service.log_action(
            action=action_enum,
            user_id=current_user["uid"],
            user_email=current_user["email"],
            user_role=current_user["role"],
            severity=severity_enum,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            error_message=error_message
        )
        
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            "audit_log": audit_entry,
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            "error": str(e)
        }
