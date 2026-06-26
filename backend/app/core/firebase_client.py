import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, auth
from app.core.config import settings


class FirebaseClient:
    """Cliente Firebase com suporte para Environment Variables e arquivo JSON"""
    
    def __init__(self):
        self._app = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Inicializa Firebase com método preferencial (env vars > arquivo JSON)"""
        try:
            # Método 1: Environment Variables (prioridade)
            if self._use_env_vars():
                cred_dict = self._build_credentials_from_env()
                firebase_creds = credentials.Certificate(cred_dict)
                print("🔥 Firebase inicializado com Environment Variables")
            # Método 2: Arquivo JSON (fallback)
            elif self._use_json_file():
                firebase_creds = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
                print("🔥 Firebase inicializado com arquivo JSON")
            else:
                raise ValueError("❌ Firebase: Configure environment variables ou arquivo JSON")
            
            # Inicializar app Firebase
            self._app = firebase_admin.initialize_app(firebase_creds, name='dashboard-azo')
            print("✅ Firebase Admin SDK inicializado com sucesso")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar Firebase: {e}")
            raise
    
    def _use_env_vars(self) -> bool:
        """Verifica se deve usar environment variables"""
        return all([
            settings.FIREBASE_PROJECT_ID,
            settings.FIREBASE_PRIVATE_KEY,
            settings.FIREBASE_CLIENT_EMAIL
        ])
    
    def _use_json_file(self) -> bool:
        """Verifica se deve usar arquivo JSON"""
        return (
            settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH and 
            Path(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH).exists()
        )
    
    def _build_credentials_from_env(self) -> Dict[str, Any]:
        """Constrói dicionário de credenciais a partir das environment variables"""
        return {
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key": settings.FIREBASE_PRIVATE_KEY,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL}"
        }
    
    def get_auth_client(self) -> auth.Client:
        """Retorna cliente de autenticação Firebase"""
        if not self._app:
            raise RuntimeError("Firebase não inicializado")
        return auth.Client(self._app)
    
    def verify_token(self, id_token: str) -> Dict[str, Any]:
        """Verifica token JWT do Firebase"""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"❌ Erro ao verificar token: {e}")
            raise
    
    def get_user(self, uid: str) -> auth.UserRecord:
        """Obtém usuário pelo UID"""
        try:
            return auth.get_user(uid)
        except Exception as e:
            print(f"❌ Erro ao obter usuário {uid}: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> auth.UserRecord:
        """Obtém usuário pelo email"""
        try:
            return auth.get_user_by_email(email)
        except Exception as e:
            print(f"❌ Erro ao obter usuário por email {email}: {e}")
            raise
    
    def create_user(self, email: str, password: Optional[str] = None, **kwargs) -> auth.UserRecord:
        """Cria novo usuário"""
        try:
            user_properties = {"email": email}
            if password:
                user_properties["password"] = password
            user_properties.update(kwargs)
            
            return auth.create_user(**user_properties)
        except Exception as e:
            print(f"❌ Erro ao criar usuário {email}: {e}")
            raise
    
    def update_user(self, uid: str, **kwargs) -> auth.UserRecord:
        """Atualiza usuário existente"""
        try:
            return auth.update_user(uid, **kwargs)
        except Exception as e:
            print(f"❌ Erro ao atualizar usuário {uid}: {e}")
            raise
    
    def delete_user(self, uid: str) -> None:
        """Deleta usuário"""
        try:
            auth.delete_user(uid)
            print(f"✅ Usuário {uid} deletado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao deletar usuário {uid}: {e}")
            raise
    
    def set_custom_claims(self, uid: str, claims: Dict[str, Any]) -> None:
        """Define custom claims para usuário"""
        try:
            auth.set_custom_user_claims(uid, claims)
            print(f"✅ Custom claims definidos para usuário {uid}")
        except Exception as e:
            print(f"❌ Erro ao definir claims para usuário {uid}: {e}")
            raise
    
    def list_users(self, limit: Optional[int] = None) -> list:
        """Lista usuários (com paginação)"""
        try:
            users = []
            page = auth.list_users(limit=limit)
            users.extend(page.users)
            
            while page.next_page_token:
                page = auth.list_users(page_token=page.next_page_token, limit=limit)
                users.extend(page.users)
            
            return users
        except Exception as e:
            print(f"❌ Erro ao listar usuários: {e}")
            raise
    
    def get_config_info(self) -> Dict[str, Any]:
        """Retorna informações de configuração para debugging"""
        return {
            "initialized": self._app is not None,
            "method": "env_vars" if self._use_env_vars() else "json_file" if self._use_json_file() else "none",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "json_file_exists": (
                Path(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH).exists() 
                if settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH else False
            )
        }


# Singleton instance
firebase_client = FirebaseClient()


# Funções de conveniência para compatibilidade
def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """Verifica token Firebase (wrapper para compatibilidade)"""
    return firebase_client.verify_token(id_token)


def get_firebase_user(uid: str) -> auth.UserRecord:
    """Obtém usuário Firebase (wrapper para compatibilidade)"""
    return firebase_client.get_user(uid)


def get_firebase_user_by_email(email: str) -> auth.UserRecord:
    """Obtém usuário Firebase por email (wrapper para compatibilidade)"""
    return firebase_client.get_user_by_email(email)


def create_firebase_user(email: str, password: Optional[str] = None, **kwargs) -> auth.UserRecord:
    """Cria usuário Firebase (wrapper para compatibilidade)"""
    return firebase_client.create_user(email, password, **kwargs)


def update_firebase_user(uid: str, **kwargs) -> auth.UserRecord:
    """Atualiza usuário Firebase (wrapper para compatibilidade)"""
    return firebase_client.update_user(uid, **kwargs)


def delete_firebase_user(uid: str) -> None:
    """Deleta usuário Firebase (wrapper para compatibilidade)"""
    firebase_client.delete_user(uid)


def set_firebase_custom_claims(uid: str, claims: Dict[str, Any]) -> None:
    """Define custom claims Firebase (wrapper para compatibilidade)"""
    firebase_client.set_custom_claims(uid, claims)


def list_firebase_users(limit: Optional[int] = None) -> list:
    """Lista usuários Firebase (wrapper para compatibilidade)"""
    return firebase_client.list_users(limit)


# Função de diagnóstico
def diagnose_firebase_config() -> Dict[str, Any]:
    """Diagnostica configuração Firebase"""
    return firebase_client.get_config_info()
