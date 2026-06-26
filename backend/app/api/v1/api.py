from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, marketing, finance, query, admin, audit, diagnostics

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(marketing.router, prefix="/marketing", tags=["marketing"])
api_router.include_router(finance.router, prefix="/finance", tags=["finance"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(diagnostics.router, prefix="/diagnostics", tags=["diagnostics"])
