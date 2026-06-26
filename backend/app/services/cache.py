import json
import pickle
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import asyncio

import redis.asyncio as redis

from app.core.config import settings


class CacheService:
    """Serviço de cache usando Redis"""
    
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self._redis: Optional[redis.Redis] = None
    
    async def get_redis(self) -> redis.Redis:
        """Obter conexão Redis (lazy initialization)"""
        if self._redis is None:
            self._redis = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
        return self._redis
    
    async def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache"""
        try:
            r = await self.get_redis()
            value = await r.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire_seconds: int = 3600
    ) -> bool:
        """Definir valor no cache com expiração"""
        try:
            r = await self.get_redis()
            serialized = json.dumps(value, default=str)
            await r.setex(key, expire_seconds, serialized)
            return True
        except Exception as e:
            print(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Deletar chave do cache"""
        try:
            r = await self.get_redis()
            await r.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Deletar chaves por padrão"""
        try:
            r = await self.get_redis()
            keys = await r.keys(pattern)
            if keys:
                return await r.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error for pattern {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Verificar se chave existe"""
        try:
            r = await self.get_redis()
            return await r.exists(key) > 0
        except Exception as e:
            print(f"Cache exists error for key {key}: {e}")
            return False
    
    async def close(self):
        """Fechar conexão Redis"""
        if self._redis:
            await self._redis.close()


# Singleton instance
cache_service = CacheService()


class CacheKeys:
    """Chaves de cache padronizadas"""
    
    @staticmethod
    def enterprises() -> str:
        return "sienge:enterprises"
    
    @staticmethod
    def realtors() -> str:
        return "sienge:realtors"
    
    @staticmethod
    def sales(enterprise_id: Optional[str] = None, date_range: Optional[str] = None) -> str:
        base = "sienge:sales"
        parts = [base]
        if enterprise_id:
            parts.append(f"enterprise:{enterprise_id}")
        if date_range:
            parts.append(f"dates:{date_range}")
        return ":".join(parts)
    
    @staticmethod
    def vgv(enterprise_id: Optional[str] = None, year: Optional[int] = None) -> str:
        base = "sienge:vgv"
        parts = [base]
        if enterprise_id:
            parts.append(f"enterprise:{enterprise_id}")
        if year:
            parts.append(f"year:{year}")
        return ":".join(parts)
    
    @staticmethod
    def vso(enterprise_id: Optional[str] = None, period: str = "current_month") -> str:
        base = "sienge:vso"
        parts = [base]
        if enterprise_id:
            parts.append(f"enterprise:{enterprise_id}")
        parts.append(f"period:{period}")
        return ":".join(parts)
    
    @staticmethod
    def monthly_targets(enterprise_id: Optional[str] = None, year: Optional[int] = None) -> str:
        base = "sienge:targets:monthly"
        parts = [base]
        if enterprise_id:
            parts.append(f"enterprise:{enterprise_id}")
        if year:
            parts.append(f"year:{year}")
        return ":".join(parts)
    
    @staticmethod
    def dashboard_metrics(user_role: str, city: Optional[str] = None) -> str:
        base = "dashboard:metrics"
        parts = [base, f"role:{user_role}"]
        if city:
            parts.append(f"city:{city}")
        return ":".join(parts)
    
    @staticmethod
    def units_available(enterprise_id: Optional[str] = None) -> str:
        base = "sienge:units:available"
        if enterprise_id:
            return f"{base}:enterprise:{enterprise_id}"
        return base


async def cached_call(
    cache_key: str,
    cache_duration: int,
    fetch_function: callable,
    *args,
    **kwargs
) -> Any:
    """
    Função utilitária para chamadas com cache
    Tenta obter do cache primeiro, se não existir, executa a função e cacheia o resultado
    """
    # Try to get from cache
    cached_result = await cache_service.get(cache_key)
    if cached_result is not None:
        return cached_result
    
    # Execute function and cache result
    if asyncio.iscoroutinefunction(fetch_function):
        result = await fetch_function(*args, **kwargs)
    else:
        result = fetch_function(*args, **kwargs)
    
    await cache_service.set(cache_key, result, cache_duration)
    return result
