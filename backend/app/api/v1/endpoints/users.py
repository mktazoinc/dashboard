from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.core.security import (
    get_current_user,
    require_role,
    require_any_role,
)

router = APIRouter()


# Models
class UserCreate(BaseModel):
    """Modelo para criação de usuário"""
    email: EmailStr
    role: str
    display_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class UserUpdate(BaseModel):
    """Modelo para atualização de usuário"""
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    display_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class UserRoleUpdate(BaseModel):
    role: str


class UserResponse(BaseModel):
    """Modelo para resposta de usuário"""
    uid: str
    email: str
    display_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None
    last_sign_in: Optional[str] = None
    custom_claims: Optional[Dict[str, Any]] = None


class UserListResponse(BaseModel):
    """Modelo para lista de usuários paginada"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get("/me")
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current user profile with role information"""
    return {
        "uid": current_user["uid"],
        "email": current_user["email"],
        "role": current_user["role"],
        "custom_claims": current_user["custom_claims"],
    }


@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    search: Optional[str] = Query(None, description="Buscar por email ou nome"),
    role: Optional[str] = Query(None, description="Filtrar por role"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status"),
    current_user: Dict[str, Any] = Depends(
        require_any_role(["admin", "mestre_do_universo"])
    )
):
    """List users with pagination and filters - admin only"""
    from firebase_admin import auth
    
    try:
        # Calculate pagination
        offset = (page - 1) * page_size
        
        # Get users from Firebase Auth
        users = []
        page_users = auth.list_users(page=page, limit=page_size)
        
        for user in page_users.users:
            user_data = UserResponse(
                uid=user.uid,
                email=user.email,
                display_name=user.display_name,
                phone=user.phone_number,
                role=user.custom_claims.get('role') if user.custom_claims else None,
                is_active=user.disabled == False,
                created_at=user.user_metadata.creation_timestamp if user.user_metadata else None,
                last_sign_in=user.user_metadata.last_sign_in_timestamp if user.user_metadata else None,
                custom_claims=user.custom_claims
            )
            
            # Apply filters
            if search and not (
                search.lower() in user.email.lower() or 
                (user.display_name and search.lower() in user.display_name.lower())
            ):
                continue
                
            if role and user.role != role:
                continue
                
            if is_active is not None and user.is_active != is_active:
                continue
            
            users.append(user_data)
        
        # Get total count (simplified - in production would use database)
        total_users = len(users)  # Firebase doesn't provide total count easily
        
        return UserListResponse(
            users=users,
            total=total_users,
            page=page,
            page_size=page_size,
            total_pages=(total_users + page_size - 1) // page_size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing users: {str(e)}"
        )


@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: Dict[str, Any] = Depends(
        require_any_role(["admin", "mestre_do_universo"])
    )
):
    """Create new user - admin only"""
    from firebase_admin import auth
    
    valid_roles = [
        "comercial_rj", "comercial_sp", "marketing_rj", "marketing_sp",
        "diretoria", "admin"
    ]
    
    # Only mestre_do_universo can create admin users
    if user_data.role == "admin" and current_user["role"] != "mestre_do_universo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Mestre do Universo can create admin users"
        )
    
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    try:
        # Check if user already exists
        try:
            existing_user = auth.get_user_by_email(user_data.email)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        except auth.UserNotFoundError:
            pass
        
        # Create user in Firebase
        user_kwargs = {
            "email": user_data.email,
            "email_verified": True,
        }
        
        if user_data.password:
            user_kwargs["password"] = user_data.password
        
        if user_data.display_name:
            user_kwargs["display_name"] = user_data.display_name
        
        if user_data.phone:
            user_kwargs["phone_number"] = user_data.phone
        
        firebase_user = auth.create_user(**user_kwargs)
        
        # Set custom claims
        auth.set_custom_user_claims(firebase_user.uid, {
            "role": user_data.role,
            "created_by": current_user["email"],
            "created_at": datetime.now().isoformat()
        })
        
        return UserResponse(
            uid=firebase_user.uid,
            email=firebase_user.email,
            display_name=firebase_user.display_name,
            phone=firebase_user.phone_number,
            role=user_data.role,
            is_active=True,
            created_at=firebase_user.user_metadata.creation_timestamp if firebase_user.user_metadata else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.get("/{user_uid}", response_model=UserResponse)
async def get_user(
    user_uid: str,
    current_user: Dict[str, Any] = Depends(
        require_any_role(["admin", "mestre_do_universo"])
    )
):
    """Get user by UID - admin only"""
    from firebase_admin import auth
    
    try:
        user = auth.get_user(user_uid)
        
        return UserResponse(
            uid=user.uid,
            email=user.email,
            display_name=user.display_name,
            phone=user.phone_number,
            role=user.custom_claims.get('role') if user.custom_claims else None,
            is_active=user.disabled == False,
            created_at=user.user_metadata.creation_timestamp if user.user_metadata else None,
            last_sign_in=user.user_metadata.last_sign_in_timestamp if user.user_metadata else None,
            custom_claims=user.custom_claims
        )
        
    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user: {str(e)}"
        )


@router.put("/{user_uid}", response_model=UserResponse)
async def update_user(
    user_uid: str,
    user_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(
        require_any_role(["admin", "mestre_do_universo"])
    )
):
    """Update user - admin only"""
    from firebase_admin import auth
    
    try:
        user = auth.get_user(user_uid)
        
        # Update user properties
        update_kwargs = {}
        
        if user_data.email and user_data.email != user.email:
            update_kwargs["email"] = user_data.email
        
        if user_data.display_name is not None:
            update_kwargs["display_name"] = user_data.display_name
        
        if user_data.phone is not None:
            update_kwargs["phone_number"] = user_data.phone
        
        if user_data.is_active is not None:
            update_kwargs["disabled"] = not user_data.is_active
        
        if update_kwargs:
            auth.update_user(user_uid, **update_kwargs)
        
        # Update custom claims if role changed
        current_claims = user.custom_claims or {}
        new_claims = current_claims.copy()
        
        if user_data.role is not None and user_data.role != current_claims.get('role'):
            # Only mestre_do_universo can assign admin role
            if user_data.role == "admin" and current_user["role"] != "mestre_do_universo":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only Mestre do Universo can assign admin role"
                )
            
            new_claims["role"] = user_data.role
            new_claims["updated_by"] = current_user["email"]
            new_claims["updated_at"] = datetime.now().isoformat()
            
            auth.set_custom_user_claims(user_uid, new_claims)
        
        # Get updated user
        updated_user = auth.get_user(user_uid)
        
        return UserResponse(
            uid=updated_user.uid,
            email=updated_user.email,
            display_name=updated_user.display_name,
            phone=updated_user.phone_number,
            role=updated_user.custom_claims.get('role') if updated_user.custom_claims else None,
            is_active=updated_user.disabled == False,
            created_at=updated_user.user_metadata.creation_timestamp if updated_user.user_metadata else None,
            last_sign_in=updated_user.user_metadata.last_sign_in_timestamp if updated_user.user_metadata else None,
            custom_claims=updated_user.custom_claims
        )
        
    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )


@router.delete("/{user_uid}")
async def delete_user(
    user_uid: str,
    current_user: Dict[str, Any] = Depends(
        require_role("mestre_do_universo")
    )
):
    """Delete user - Mestre do Universo only"""
    from firebase_admin import auth
    
    try:
        # Prevent self-deletion
        if user_uid == current_user["uid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        user = auth.get_user(user_uid)
        
        # Prevent deletion of other mestre_do_universo users
        if user.custom_claims and user.custom_claims.get('role') == 'mestre_do_universo':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete Mestre do Universo users"
            )
        
        auth.delete_user(user_uid)
        
        return {
            "message": "User deleted successfully",
            "user_uid": user_uid,
            "deleted_by": current_user["email"]
        }
        
    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )


@router.post("/{user_uid}/set-role")
async def set_user_role(
    user_uid: str,
    role: str,
    current_user: Dict[str, Any] = Depends(
        require_role("mestre_do_universo")
    )
):
    """Set user role - Mestre do Universo only"""
    valid_roles = [
        "comercial_rj",
        "comercial_sp", 
        "marketing_rj",
        "marketing_sp",
        "diretoria",
        "admin",
        "mestre_do_universo"
    ]
    
    if role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # This would typically update custom claims in Firebase
    # For now, return a placeholder
    return {
        "message": "User role updated",
        "user_uid": user_uid,
        "new_role": role,
        "updated_by": current_user["email"],
    }


@router.post("/seed-admin")
async def seed_admin_user():
    """Seed initial Mestre do Universo user - environment variables only"""
    import os
    from firebase_admin import auth
    
    admin_email = os.getenv("ADMIN_SEED_EMAIL")
    admin_password = os.getenv("ADMIN_SEED_PASSWORD")
    
    if not admin_email or not admin_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ADMIN_SEED_EMAIL and ADMIN_SEED_PASSWORD environment variables are required"
        )
    
    try:
        # Check if user already exists
        try:
            user = auth.get_user_by_email(admin_email)
            
            # User exists, check if already has mestre_do_universo role
            if user.custom_claims and user.custom_claims.get('role') == 'mestre_do_universo':
                return {
                    "message": "Mestre do Universo user already exists",
                    "email": admin_email,
                    "uid": user.uid,
                    "role": "mestre_do_universo",
                }
            
            # Update existing user to mestre_do_universo role
            auth.set_custom_user_claims(user.uid, {
                'role': 'mestre_do_universo',
                'is_seed': True,
            })
            
            return {
                "message": "Existing user updated to Mestre do Universo role",
                "email": admin_email,
                "uid": user.uid,
                "role": "mestre_do_universo",
            }
            
        except auth.UserNotFoundError:
            # User doesn't exist, create new one
            user = auth.create_user(
                email=admin_email,
                password=admin_password,
                email_verified=True,
            )
            
            # Set custom claims for the new user
            auth.set_custom_user_claims(user.uid, {
                'role': 'mestre_do_universo',
                'is_seed': True,
            })
            
            return {
                "message": "New Mestre do Universo user created",
                "email": admin_email,
                "uid": user.uid,
                "role": "mestre_do_universo",
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error seeding admin user: {str(e)}"
        )
