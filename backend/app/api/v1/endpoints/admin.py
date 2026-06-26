from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime, timedelta
import psutil
import redis

from app.core.security import require_any_role
from app.core.config import settings

router = APIRouter()


@router.get("/dashboard")
async def get_admin_dashboard(
    current_user: Dict[str, Any] = Depends(
        require_any_role(["admin", "mestre_do_universo"])
    )
):
    """Get admin dashboard with system metrics - admin only"""
    try:
        # Get system metrics
        system_metrics = await get_system_metrics()
        
        # Get user statistics
        user_stats = await get_user_statistics()
        
        # Get security metrics
        security_metrics = await get_security_metrics()
        
        # Determine system health
        system_health = determine_system_health(system_metrics, security_metrics)
        
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            "metrics": {
                "total_users": user_stats["total"],
                "active_users": user_stats["active"],
                "logins_today": user_stats["logins_today"],
                "logins_this_week": user_stats["logins_week"],
                "systems_status": {
                    "finance": True,  # TODO: Check actual system status
                    "marketing": True,
                    "auth": True,
                    "cache": system_metrics["cache_status"],
                    "database": system_metrics["database_status"]
                },
                "security_alerts": security_metrics,
                "performance": system_metrics["performance"]
            },
            "system_health": system_health,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error fetching admin dashboard: {e}")
        return {
            "user": current_user["email"],
            "role": current_user["role"],
            "metrics": get_mock_metrics(),
            "system_health": "warning",
            "last_updated": datetime.now().isoformat(),
            "error": str(e)
        }


async def get_system_metrics() -> Dict[str, Any]:
    """Get system performance metrics"""
    try:
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network stats
        network = psutil.net_io_counters()
        
        # Check Redis connection
        cache_status = False
        try:
            if settings.REDIS_URL:
                r = redis.from_url(settings.REDIS_URL)
                r.ping()
                cache_status = True
        except:
            pass
        
        # Check database connection (simplified)
        database_status = True  # TODO: Implement actual DB health check
        
        return {
            "cache_status": cache_status,
            "database_status": database_status,
            "performance": {
                "avg_response_time": 150,  # TODO: Implement actual response time tracking
                "cpu_usage": round(cpu_percent, 1),
                "memory_usage": round(memory.percent, 1),
                "disk_usage": round(disk.percent, 1)
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv
            }
        }
        
    except Exception as e:
        print(f"Error getting system metrics: {e}")
        return {
            "cache_status": False,
            "database_status": False,
            "performance": {
                "avg_response_time": 0,
                "cpu_usage": 0,
                "memory_usage": 0,
                "disk_usage": 0
            },
            "network": {
                "bytes_sent": 0,
                "bytes_recv": 0
            }
        }


async def get_user_statistics() -> Dict[str, Any]:
    """Get user statistics from Firebase"""
    try:
        from firebase_admin import auth
        
        # Get all users (this is expensive, in production use database)
        users = auth.list_users().users
        
        total_users = len(users)
        
        # Count active users (logged in within last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_users = sum(
            1 for user in users 
            if user.user_metadata and 
               user.user_metadata.last_sign_in_timestamp and 
               datetime.fromtimestamp(user.user_metadata.last_sign_in_timestamp / 1000) > thirty_days_ago
        )
        
        # Count logins today and this week
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        logins_today = sum(
            1 for user in users 
            if user.user_metadata and 
               user.user_metadata.last_sign_in_timestamp and 
               datetime.fromtimestamp(user.user_metadata.last_sign_in_timestamp / 1000).date() == today
        )
        
        logins_week = sum(
            1 for user in users 
            if user.user_metadata and 
               user.user_metadata.last_sign_in_timestamp and 
               datetime.fromtimestamp(user.user_metadata.last_sign_in_timestamp / 1000).date() >= week_ago
        )
        
        return {
            "total": total_users,
            "active": active_users,
            "logins_today": logins_today,
            "logins_week": logins_week
        }
        
    except Exception as e:
        print(f"Error getting user statistics: {e}")
        return {
            "total": 0,
            "active": 0,
            "logins_today": 0,
            "logins_week": 0
        }


async def get_security_metrics() -> Dict[str, Any]:
    """Get security metrics"""
    # TODO: Implement actual security tracking
    # For now, return mock data
    return {
        "failed_logins": 0,
        "suspicious_activities": 0,
        "blocked_ips": 0
    }


def determine_system_health(system_metrics: Dict[str, Any], security_metrics: Dict[str, Any]) -> str:
    """Determine overall system health"""
    issues = []
    
    # Check performance
    perf = system_metrics.get("performance", {})
    if perf.get("cpu_usage", 0) > 80:
        issues.append("high_cpu")
    if perf.get("memory_usage", 0) > 85:
        issues.append("high_memory")
    if perf.get("disk_usage", 0) > 90:
        issues.append("high_disk")
    
    # Check services
    if not system_metrics.get("cache_status"):
        issues.append("cache_down")
    if not system_metrics.get("database_status"):
        issues.append("database_down")
    
    # Check security
    total_alerts = (
        security_metrics.get("failed_logins", 0) +
        security_metrics.get("suspicious_activities", 0)
    )
    if total_alerts > 10:
        issues.append("security_alerts")
    
    # Determine health status
    if len(issues) == 0:
        return "healthy"
    elif len(issues) <= 2 and "database_down" not in issues:
        return "warning"
    else:
        return "critical"


def get_mock_metrics() -> Dict[str, Any]:
    """Return mock metrics when services are unavailable"""
    return {
        "total_users": 0,
        "active_users": 0,
        "logins_today": 0,
        "logins_this_week": 0,
        "systems_status": {
            "finance": False,
            "marketing": False,
            "auth": False,
            "cache": False,
            "database": False
        },
        "security_alerts": {
            "failed_logins": 0,
            "suspicious_activities": 0,
            "blocked_ips": 0
        },
        "performance": {
            "avg_response_time": 0,
            "cpu_usage": 0,
            "memory_usage": 0,
            "disk_usage": 0
        }
    }
