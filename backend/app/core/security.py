import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from app.core.config import settings

# Initialize Firebase Admin
try:
    cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Firebase initialization error: {e}")

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Validate Firebase JWT token and return user info with custom claims
    """
    try:
        # Verify the Firebase ID token
        decoded_token = auth.verify_id_token(credentials.credentials)
        
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
        
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation error: {str(e)}",
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
