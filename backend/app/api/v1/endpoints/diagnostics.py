from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.core.security import get_current_user
from app.core.firebase_client import diagnose_firebase_config
from app.core.config import settings

router = APIRouter()


@router.get("/firebase", summary="Diagnóstico da configuração Firebase")
async def diagnose_firebase(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Diagnostica a configuração do Firebase.
    Apenas usuários admin podem acessar.
    """
    if current_user.get('role') not in ['admin', 'mestre_do_universo']:
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem acessar diagnósticos"
        )
    
    config_info = diagnose_firebase_config()
    
    # Adicionar informações úteis para debugging
    diagnostics = {
        "firebase_config": config_info,
        "environment_variables": {
            "FIREBASE_PROJECT_ID": bool(settings.FIREBASE_PROJECT_ID),
            "FIREBASE_PRIVATE_KEY": bool(settings.FIREBASE_PRIVATE_KEY),
            "FIREBASE_CLIENT_EMAIL": bool(settings.FIREBASE_CLIENT_EMAIL),
            "FIREBASE_SERVICE_ACCOUNT_KEY_PATH": bool(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH),
        },
        "recommendations": []
    }
    
    # Gerar recomendações baseadas no diagnóstico
    if not config_info["initialized"]:
        diagnostics["recommendations"].append(
            "Firebase não está inicializado. Configure as environment variables ou arquivo JSON."
        )
    
    if config_info["method"] == "none":
        diagnostics["recommendations"].append(
            "Nenhuma configuração Firebase encontrada. Use environment variables para produção."
        )
    
    if config_info["method"] == "json_file" and not config_info["json_file_exists"]:
        diagnostics["recommendations"].append(
            "Arquivo JSON do Firebase não encontrado. Verifique o caminho em FIREBASE_SERVICE_ACCOUNT_KEY_PATH."
        )
    
    if config_info["method"] == "env_vars":
        diagnostics["recommendations"].append(
            "✅ Usando environment variables (recomendado para produção)"
        )
    
    return diagnostics


@router.get("/system", summary="Diagnóstico geral do sistema")
async def diagnose_system(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Diagnostica configurações gerais do sistema.
    Apenas usuários admin podem acessar.
    """
    if current_user.get('role') not in ['admin', 'mestre_do_universo']:
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem acessar diagnósticos"
        )
    
    import os
    from pathlib import Path
    
    diagnostics = {
        "app_info": {
            "name": settings.PROJECT_NAME,
            "version": settings.APP_VERSION,
            "environment": os.getenv("ENVIRONMENT", "development"),
        },
        "database": {
            "database_url_configured": bool(settings.DATABASE_URL),
            "database_url_type": type(settings.DATABASE_URL).__name__,
        },
        "redis": {
            "redis_url_configured": bool(settings.REDIS_URL),
            "redis_url": settings.REDIS_URL,
        },
        "security": {
            "secret_key_configured": bool(settings.SECRET_KEY),
            "secret_key_length": len(settings.SECRET_KEY) if settings.SECRET_KEY else 0,
            "algorithm": settings.ALGORITHM,
        },
        "cors": {
            "allowed_origins_count": len(settings.BACKEND_CORS_ORIGINS),
            "allowed_origins": [str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        },
        "external_apis": {
            "supabase_configured": bool(settings.SUPABASE_URL),
            "sienge_configured": bool(settings.SIENGE_API_TOKEN),
            "meta_configured": bool(settings.META_APP_ID),
        }
    }
    
    # Adicionar recomendações
    recommendations = []
    
    if not settings.DATABASE_URL:
        recommendations.append("Configure DATABASE_URL para conexão com banco de dados")
    
    if not settings.REDIS_URL:
        recommendations.append("Configure REDIS_URL para cache e sessões")
    
    if not settings.SECRET_KEY or len(settings.SECRET_KEY) < 32:
        recommendations.append("Use uma SECRET_KEY mais forte (mínimo 32 caracteres)")
    
    if not settings.SUPABASE_URL:
        recommendations.append("Configure SUPABASE_URL para integração com marketing")
    
    diagnostics["recommendations"] = recommendations
    
    return diagnostics


@router.post("/test-firebase-connection", summary="Testar conexão com Firebase")
async def test_firebase_connection(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Testa a conexão com o Firebase tentando operações básicas.
    Apenas usuários admin podem acessar.
    """
    if current_user.get('role') not in ['admin', 'mestre_do_universo']:
        raise HTTPException(
            status_code=403,
            detail="Apenas administradores podem acessar diagnósticos"
        )
    
    from app.core.firebase_client import firebase_client
    
    results = {
        "connection_test": False,
        "operations": {},
        "error": None
    }
    
    try:
        # Testar verificação de token (com token inválido)
        try:
            firebase_client.verify_token("invalid_token")
            results["operations"]["token_verification"] = "success"
        except Exception as e:
            results["operations"]["token_verification"] = f"expected_error: {str(e)}"
        
        # Testar listagem de usuários (limitado)
        try:
            users = firebase_client.list_users(limit=1)
            results["operations"]["list_users"] = f"success: {len(users)} users found"
        except Exception as e:
            results["operations"]["list_users"] = f"error: {str(e)}"
        
        # Testar obtenção de usuário pelo email do admin
        try:
            admin_user = firebase_client.get_user_by_email(current_user["email"])
            results["operations"]["get_user_by_email"] = f"success: {admin_user.uid}"
        except Exception as e:
            results["operations"]["get_user_by_email"] = f"error: {str(e)}"
        
        results["connection_test"] = True
        
    except Exception as e:
        results["error"] = str(e)
    
    return results
