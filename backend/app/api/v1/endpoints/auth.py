from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.core.security import get_current_user

router = APIRouter()


@router.post("/verify-token")
async def verify_token(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Verify Firebase JWT token and return user info with custom claims"""
    return {
        "uid": current_user["uid"],
        "email": current_user["email"],
        "role": current_user["role"],
        "custom_claims": current_user["custom_claims"],
    }


@router.post("/refresh-claims")
async def refresh_custom_claims(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Force refresh of custom claims from Firebase"""
    # This would typically involve calling Firebase Admin SDK to refresh claims
    # For now, return current claims
    return {
        "message": "Custom claims refreshed",
        "user": current_user,
    }


@router.post("/logout")
async def logout():
    """Logout endpoint - client-side token invalidation"""
    # Firebase JWT tokens are invalidated on the client side
    # Backend can maintain a blacklist if needed
    return {"message": "Logout successful"}
