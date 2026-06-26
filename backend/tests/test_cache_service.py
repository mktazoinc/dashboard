import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
from datetime import timedelta

from app.services.cache import CacheService


@pytest.fixture
def mock_redis():
    """Mock para cliente Redis"""
    with patch('redis.asyncio.from_url') as mock_redis:
        redis_client = AsyncMock()
        mock_redis.return_value = redis_client
        yield redis_client


@pytest.fixture
def cache_service(mock_redis):
    """Fixture para o serviço de cache"""
    with patch('app.services.cache.settings') as mock_settings:
        mock_settings.REDIS_URL = "redis://localhost:6379"
        service = CacheService()
        service.redis_client = mock_redis
        yield service


@pytest.mark.asyncio
async def test_cache_service_initialization():
    """Teste de inicialização do serviço de cache"""
    with patch('app.services.cache.settings') as mock_settings:
        mock_settings.REDIS_URL = "redis://localhost:6379"
        with patch('redis.asyncio.from_url') as mock_redis:
            redis_client = AsyncMock()
            mock_redis.return_value = redis_client
            
            service = CacheService()
            
            assert service.redis_client == redis_client
            mock_redis.assert_called_once_with("redis://localhost:6379", decode_responses=True)


@pytest.mark.asyncio
async def test_set_cache_string(cache_service, mock_redis):
    """Teste de armazenamento de string no cache"""
    # Arrange
    key = "test_key"
    value = "test_value"
    expire_seconds = 3600
    
    # Act
    result = await cache_service.set(key, value, expire_seconds)
    
    # Assert
    assert result is True
    mock_redis.setex.assert_called_once_with(key, expire_seconds, value)


@pytest.mark.asyncio
async def test_set_cache_dict(cache_service, mock_redis):
    """Teste de armazenamento de dicionário no cache"""
    # Arrange
    key = "test_dict"
    value = {"name": "test", "count": 42}
    expire_seconds = 1800
    
    # Act
    result = await cache_service.set(key, value, expire_seconds)
    
    # Assert
    assert result is True
    expected_value = json.dumps(value)
    mock_redis.setex.assert_called_once_with(key, expire_seconds, expected_value)


@pytest.mark.asyncio
async def test_get_cache_string_exists(cache_service, mock_redis):
    """Teste de obtenção de string que existe no cache"""
    # Arrange
    key = "test_key"
    expected_value = "test_value"
    mock_redis.get.return_value = expected_value
    
    # Act
    result = await cache_service.get(key)
    
    # Assert
    assert result == expected_value
    mock_redis.get.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_get_cache_dict_exists(cache_service, mock_redis):
    """Teste de obtenção de dicionário que existe no cache"""
    # Arrange
    key = "test_dict"
    expected_value = {"name": "test", "count": 42}
    mock_redis.get.return_value = json.dumps(expected_value)
    
    # Act
    result = await cache_service.get(key)
    
    # Assert
    assert result == expected_value
    mock_redis.get.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_get_cache_not_exists(cache_service, mock_redis):
    """Teste de obtenção de chave que não existe no cache"""
    # Arrange
    key = "non_existent_key"
    mock_redis.get.return_value = None
    
    # Act
    result = await cache_service.get(key)
    
    # Assert
    assert result is None
    mock_redis.get.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_get_cache_invalid_json(cache_service, mock_redis):
    """Teste de obtenção de JSON inválido no cache"""
    # Arrange
    key = "invalid_json_key"
    mock_redis.get.return_value = "invalid json {"
    
    # Act
    result = await cache_service.get(key)
    
    # Assert
    assert result == "invalid json {"


@pytest.mark.asyncio
async def test_delete_cache_exists(cache_service, mock_redis):
    """Teste de deleção de chave que existe no cache"""
    # Arrange
    key = "test_key"
    mock_redis.delete.return_value = 1
    
    # Act
    result = await cache_service.delete(key)
    
    # Assert
    assert result is True
    mock_redis.delete.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_delete_cache_not_exists(cache_service, mock_redis):
    """Teste de deleção de chave que não existe no cache"""
    # Arrange
    key = "non_existent_key"
    mock_redis.delete.return_value = 0
    
    # Act
    result = await cache_service.delete(key)
    
    # Assert
    assert result is False
    mock_redis.delete.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_exists_cache_true(cache_service, mock_redis):
    """Teste de verificação de existência de chave que existe"""
    # Arrange
    key = "test_key"
    mock_redis.exists.return_value = 1
    
    # Act
    result = await cache_service.exists(key)
    
    # Assert
    assert result is True
    mock_redis.exists.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_exists_cache_false(cache_service, mock_redis):
    """Teste de verificação de existência de chave que não existe"""
    # Arrange
    key = "non_existent_key"
    mock_redis.exists.return_value = 0
    
    # Act
    result = await cache_service.exists(key)
    
    # Assert
    assert result is False
    mock_redis.exists.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_increment_cache(cache_service, mock_redis):
    """Teste de incremento de valor no cache"""
    # Arrange
    key = "counter_key"
    amount = 5
    mock_redis.incrby.return_value = 15
    
    # Act
    result = await cache_service.increment(key, amount)
    
    # Assert
    assert result == 15
    mock_redis.incrby.assert_called_once_with(key, amount)


@pytest.mark.asyncio
async def test_get_ttl_cache_exists(cache_service, mock_redis):
    """Teste de obtenção de TTL de chave que existe"""
    # Arrange
    key = "test_key"
    mock_redis.ttl.return_value = 3600
    
    # Act
    result = await cache_service.get_ttl(key)
    
    # Assert
    assert result == 3600
    mock_redis.ttl.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_get_ttl_cache_not_exists(cache_service, mock_redis):
    """Teste de obtenção de TTL de chave que não existe"""
    # Arrange
    key = "non_existent_key"
    mock_redis.ttl.return_value = -1
    
    # Act
    result = await cache_service.get_ttl(key)
    
    # Assert
    assert result == -1
    mock_redis.ttl.assert_called_once_with(key)


@pytest.mark.asyncio
async def test_set_with_ttl(cache_service, mock_redis):
    """Teste de armazenamento com TTL específico"""
    # Arrange
    key = "test_key"
    value = "test_value"
    ttl = timedelta(hours=2)
    
    # Act
    result = await cache_service.set(key, value, ttl=ttl)
    
    # Assert
    assert result is True
    expected_expire_seconds = int(ttl.total_seconds())
    mock_redis.setex.assert_called_once_with(key, expected_expire_seconds, value)


@pytest.mark.asyncio
async def test_cache_service_no_redis_url():
    """Teste quando não há URL do Redis configurada"""
    with patch('app.services.cache.settings') as mock_settings:
        mock_settings.REDIS_URL = None
        
        service = CacheService()
        
        # Operações devem retornar valores padrão quando não há Redis
        assert await service.set("key", "value") is False
        assert await service.get("key") is None
        assert await service.delete("key") is False
        assert await service.exists("key") is False
        assert await service.increment("key") == 0
        assert await service.get_ttl("key") == -1


@pytest.mark.asyncio
async def test_cache_service_redis_exception(cache_service, mock_redis):
    """Teste de tratamento de exceções do Redis"""
    # Arrange
    key = "test_key"
    mock_redis.get.side_effect = Exception("Redis connection error")
    
    # Act
    result = await cache_service.get(key)
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_cached_call_decorator(cache_service, mock_redis):
    """Teste do decorador cached_call"""
    from app.services.cache import cached_call
    
    # Arrange
    @cached_call(cache_service, ttl=300)
    async def expensive_function(param1, param2):
        return f"result_{param1}_{param2}"
    
    key = "expensive_function:param1:param2"
    mock_redis.get.return_value = None  # Primeira chamada, cache miss
    
    # Act
    result1 = await expensive_function("param1", "param2")
    
    # Assert
    assert result1 == "result_param1_param2"
    mock_redis.get.assert_called_with(key)
    mock_redis.setex.assert_called_with(key, 300, "result_param1_param2")


@pytest.mark.asyncio
async def test_cached_call_decorator_hit(cache_service, mock_redis):
    """Teste do decorador cached_call com cache hit"""
    from app.services.cache import cached_call
    
    # Arrange
    @cached_call(cache_service, ttl=300)
    async def expensive_function(param1, param2):
        return f"result_{param1}_{param2}"
    
    key = "expensive_function:param1:param2"
    cached_result = "cached_result"
    mock_redis.get.return_value = cached_result  # Cache hit
    
    # Act
    result = await expensive_function("param1", "param2")
    
    # Assert
    assert result == cached_result
    mock_redis.get.assert_called_with(key)
    # Não deve chamar setex quando há cache hit
    mock_redis.setex.assert_not_called()
