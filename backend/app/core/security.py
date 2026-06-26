import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings
from app.core.firebase_client import firebase_client

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Validate Firebase JWT token and return user info with custom claims
    """
    try:
        # Verify the Firebase ID token usando o novo cliente
        decoded_token = firebase_client.verify_token(credentials.credentials)
        
        # Get user info from Firebase
        uid = decoded_token.get('uid')
        email = decoded_token.get('email')
        
        if not uid or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user information",
            )
        
        # Extract custom claims
        role = decoded_token.get('role', 'comercial_rj')
        
        return {
            'uid': uid,
            'email': email,
            'role': role,
            'custom_claims': decoded_token,
        }
        
    except Exception as e:
        # O novo cliente já trata os diferentes tipos de erro
        error_msg = str(e).lower()
        if "expired" in error_msg:
            detail = "Token has expired"
        elif "invalid" in error_msg:
            detail = "Invalid token"
        else:
            detail = f"Token validation error: {str(e)}"
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current active user (additional validation can be added here)
    """
    # Add any additional user validation here
    # For example, check if user is active in your database
    return current_user


def require_role(required_role: str):
    """
    Dependency factory to require specific role
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get('role')
        
        if user_role != required_role and user_role != 'mestre_do_universo':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        
        return current_user
    
    return role_checker


def require_any_role(roles: list[str]):
    """
    Dependency factory to require any of the specified roles
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get('role')
        
        if user_role not in roles and user_role != 'mestre_do_universo':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        
        return current_user
    
    return role_checker


# Role hierarchy for permission checking
ROLE_HIERARCHY = {
    'comercial_rj': 1,
    'comercial_sp': 1,
    'marketing_rj': 1,
    'marketing_sp': 1,
    'diretoria': 2,
    'admin': 3,
    'mestre_do_universo': 4,
}


def has_permission(user_role: str, required_role: str) -> bool:
    """
    Check if user has sufficient permission based on role hierarchy
    """
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level = ROLE_HIERARCHY.get(required_role, 0)
    
    return user_level >= required_level


def create_access_token(data: dict) -> str:
    """
    Create JWT token for internal API authentication (if needed)
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
