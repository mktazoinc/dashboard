#!/usr/bin/env python3
"""
Script para criar/atualizar o usuário Mestre do Universo
Uso: python seed_admin.py
"""

import os
import sys
import asyncio
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent))

from app.core.config import settings
from app.core.security import get_current_user
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException
import httpx


async def seed_admin():
    """Seed initial Mestre do Universo user"""
    
    print("🔧 Configurando Firebase Admin...")
    
    # Initialize Firebase Admin
    try:
        cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin inicializado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao inicializar Firebase: {e}")
        return
    
    admin_email = os.getenv("ADMIN_SEED_EMAIL")
    admin_password = os.getenv("ADMIN_SEED_PASSWORD")
    
    if not admin_email or not admin_password:
        print("❌ Variáveis de ambiente não encontradas:")
        print("   - ADMIN_SEED_EMAIL")
        print("   - ADMIN_SEED_PASSWORD")
        print("\nConfigure estas variáveis no arquivo .env")
        return
    
    print(f"📧 Email do admin: {admin_email}")
    
    try:
        # Check if user already exists
        try:
            user = auth.get_user_by_email(admin_email)
            print(f"👤 Usuário encontrado: {user.uid}")
            
            # Check if already has mestre_do_universo role
            if user.custom_claims and user.custom_claims.get('role') == 'mestre_do_universo':
                print("✅ Usuário já tem role 'mestre_do_universo'")
                print(f"   UID: {user.uid}")
                print(f"   Email: {user.email}")
                print(f"   Role: {user.custom_claims.get('role')}")
                return
            
            # Update existing user to mestre_do_universo role
            auth.set_custom_user_claims(user.uid, {
                'role': 'mestre_do_universo',
                'is_seed': True,
            })
            
            print("✅ Usuário atualizado para role 'mestre_do_universo'")
            print(f"   UID: {user.uid}")
            print(f"   Email: {user.email}")
            print(f"   Role: mestre_do_universo")
            
        except auth.UserNotFoundError:
            print("👤 Usuário não encontrado, criando novo...")
            
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
            
            print("✅ Novo usuário 'mestre_do_universo' criado")
            print(f"   UID: {user.uid}")
            print(f"   Email: {user.email}")
            print(f"   Role: mestre_do_universo")
            print(f"   Senha: {admin_password}")
            
    except Exception as e:
        print(f"❌ Erro ao criar/atualizar usuário: {e}")
        return
    
    print("\n🎉 Seed do Mestre do Universo concluído com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Faça login no frontend com as credenciais acima")
    print("2. Verifique se o role 'mestre_do_universo' aparece no perfil")
    print("3. Acesse todos os sistemas (Financeiro, Marketing, Admin)")


if __name__ == "__main__":
    asyncio.run(seed_admin())
