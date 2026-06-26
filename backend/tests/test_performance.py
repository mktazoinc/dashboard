import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_api_response_times(client: AsyncClient, mock_firebase_auth):
    """Testa tempos de resposta das APIs críticas"""
    # Mock de autenticação
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "test_user_123",
        "email": "test@example.com",
        "role": "admin"
    }
    
    # Mock de dados
    with patch('app.api.v1.endpoints.admin.get_system_metrics') as mock_metrics:
        mock_metrics.return_value = {
            "cache_status": True,
            "database_status": True,
            "performance": {
                "avg_response_time": 100,
                "cpu_usage": 45,
                "memory_usage": 67,
                "disk_usage": 78
            }
        }
        
        # Testar tempo de resposta do dashboard admin
        start_time = time.time()
        response = await client.get("/api/v1/admin/dashboard", headers={
            "Authorization": "Bearer valid_token"
        })
        response_time = (time.time() - start_time) * 1000  # Converter para ms
        
        assert response.status_code == 200
        assert response_time < 1000  # Deve responder em menos de 1 segundo
        
        # Verificar se o tempo de resposta está sendo registrado
        data = response.json()
        assert "metrics" in data
        assert "performance" in data["metrics"]


@pytest.mark.asyncio
async def test_concurrent_requests(client: AsyncClient, mock_firebase_auth):
    """Testa capacidade de lidar com requisições concorrentes"""
    # Mock de autenticação
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "test_user_123",
        "email": "test@example.com",
        "role": "admin"
    }
    
    # Mock de dados
    with patch('app.api.v1.endpoints.admin.get_system_metrics'):
        # Criar múltiplas requisições concorrentes
        tasks = []
        for _ in range(10):
            task = client.get("/api/v1/admin/dashboard", headers={
                "Authorization": "Bearer valid_token"
            })
            tasks.append(task)
        
        # Medir tempo total
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Verificar se todas as requisições foram bem-sucedidas
        for response in responses:
            assert response.status_code == 200
        
        # Verificar se o tempo total é razoável (deve ser paralelo)
        assert total_time < 5.0  # 10 requisições em menos de 5 segundos


@pytest.mark.asyncio
async def test_cache_performance(client: AsyncClient, mock_firebase_auth, mock_redis):
    """Testa performance do cache"""
    # Mock de autenticação
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "test_user_123",
        "email": "test@example.com",
        "role": "marketing_rj"
    }
    
    # Mock de dados do Supabase
    with patch('app.services.supabase.supabase') as mock_supabase:
        mock_table = AsyncMock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.gte.return_value = mock_table
        mock_table.lte.return_value = mock_table
        mock_table.execute.return_value = AsyncMock(data=[
            {"id": 1, "nome": "João", "status": "novo"}
        ])
        mock_supabase.return_value.table.return_value = mock_table
        
        # Primeira requisição (cache miss)
        mock_redis.get.return_value = None
        start_time = time.time()
        response1 = await client.get("/api/v1/marketing/dashboard", headers={
            "Authorization": "Bearer valid_token"
        })
        first_request_time = (time.time() - start_time) * 1000
        
        # Segunda requisição (cache hit)
        cached_data = '{"metrics": {"total_leads": 1}}'
        mock_redis.get.return_value = cached_data
        start_time = time.time()
        response2 = await client.get("/api/v1/marketing/dashboard", headers={
            "Authorization": "Bearer valid_token"
        })
        second_request_time = (time.time() - start_time) * 1000
        
        # Verificar respostas
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Cache hit deve ser significativamente mais rápido
        assert second_request_time < first_request_time * 0.5


@pytest.mark.asyncio
async def test_database_query_performance():
    """Testa performance de consultas ao banco de dados"""
    from app.services.supabase import SupabaseService
    
    service = SupabaseService()
    
    # Mock do cliente Supabase
    with patch.object(service, 'client') as mock_client:
        mock_table = AsyncMock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.gte.return_value = mock_table
        mock_table.lte.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.offset.return_value = mock_table
        
        # Simular diferentes tamanhos de dados
        test_cases = [
            {"data_size": 10, "expected_max_time": 0.1},
            {"data_size": 100, "expected_max_time": 0.3},
            {"data_size": 1000, "expected_max_time": 0.5}
        ]
        
        for case in test_cases:
            # Criar dados mock
            mock_data = [
                {"id": i, "nome": f"Lead {i}", "status": "novo"}
                for i in range(case["data_size"])
            ]
            mock_table.execute.return_value = AsyncMock(data=mock_data)
            
            # Medir tempo da consulta
            start_time = time.time()
            result = await service.get_leads()
            query_time = time.time() - start_time
            
            # Verificar performance
            assert query_time < case["expected_max_time"]
            assert len(result["leads"]) == case["data_size"]


@pytest.mark.asyncio
async def test_memory_usage():
    """Testa uso de memória das operações críticas"""
    import psutil
    import os
    
    # Obter processo atual
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Simular operação intensiva de memória
    from app.services.audit import AuditService
    
    audit_service = AuditService()
    
    # Criar muitos logs (simulando uso intenso)
    with patch('app.services.audit.cache_service') as mock_cache:
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        
        for i in range(1000):
            await audit_service.log_action(
                action="user_login",
                user_id=f"user_{i}",
                user_email=f"user{i}@example.com",
                user_role="user",
                details={"iteration": i}
            )
    
    # Verificar uso de memória
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = final_memory - initial_memory
    
    # Memória não deve aumentar excessivamente
    assert memory_increase < 100  # Menos de 100MB de aumento


@pytest.mark.asyncio
async def test_rate_limiting_performance(client: AsyncClient, mock_redis):
    """Testa performance do rate limiting"""
    # Mock do Redis
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.incrby.return_value = 1
    
    # Fazer múltiplas requisições para testar rate limiting
    tasks = []
    for _ in range(50):
        task = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        tasks.append(task)
    
    start_time = time.time()
    responses = await asyncio.gather(*tasks)
    total_time = time.time() - start_time
    
    # Verificar se rate limiting não impactou muito a performance
    successful_requests = sum(1 for r in responses if r.status_code == 200)
    assert successful_requests >= 45  # Pelo menos 90% devem ser bem-sucedidas
    assert total_time < 10.0  # Menos de 10 segundos para 50 requisições


@pytest.mark.asyncio
async def test_large_data_handling():
    """Testa manipulação de grandes volumes de dados"""
    from app.services.supabase import SupabaseService
    
    service = SupabaseService()
    
    # Mock com grande volume de dados
    with patch.object(service, 'client') as mock_client:
        mock_table = AsyncMock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.gte.return_value = mock_table
        mock_table.lte.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.offset.return_value = mock_table
        
        # Criar 10.000 leads
        large_dataset = [
            {
                "id": i,
                "nome": f"Lead {i}",
                "email": f"lead{i}@example.com",
                "status": "novo",
                "origem": "facebook",
                "cidade": "RJ" if i % 2 == 0 else "SP",
                "valor": str(100000 + i * 1000)
            }
            for i in range(10000)
        ]
        
        mock_table.execute.return_value = AsyncMock(data=large_dataset)
        
        # Medir performance
        start_time = time.time()
        result = await service.get_leads()
        processing_time = time.time() - start_time
        
        # Verificar resultados
        assert len(result["leads"]) == 10000
        assert processing_time < 2.0  # Deve processar em menos de 2 segundos
        
        # Verificar cálculo de métricas
        metrics = service._calculate_metrics(large_dataset)
        assert metrics["total_leads"] == 10000
        assert metrics["leads_by_status"]["novo"] == 10000


@pytest.mark.asyncio
async def test_concurrent_user_simulation():
    """Simula múltiplos usuários acessando o sistema simultaneamente"""
    from app.services.audit import AuditService
    
    audit_service = AuditService()
    
    # Mock do cache
    with patch('app.services.audit.cache_service') as mock_cache:
        mock_cache.get.return_value = None
        mock_cache.set.return_value = True
        
        # Simular 100 usuários fazendo login simultaneamente
        tasks = []
        for i in range(100):
            task = audit_service.log_action(
                action="user_login",
                user_id=f"user_{i}",
                user_email=f"user{i}@example.com",
                user_role="user"
            )
            tasks.append(task)
        
        # Medir tempo total
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Verificar se todos os logs foram criados
        successful_logs = sum(1 for r in results if r)
        assert successful_logs == 100
        assert total_time < 5.0  # 100 logs em menos de 5 segundos


@pytest.mark.asyncio
async def test_api_stress_test(client: AsyncClient, mock_firebase_auth):
    """Teste de stress da API"""
    # Mock de autenticação
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "test_user_123",
        "email": "test@example.com",
        "role": "admin"
    }
    
    # Mock de dados
    with patch('app.api.v1.endpoints.admin.get_system_metrics'):
        # Teste de stress: 1000 requisições em 30 segundos
        tasks = []
        for i in range(1000):
            task = client.get("/api/v1/admin/dashboard", headers={
                "Authorization": "Bearer valid_token"
            })
            tasks.append(task)
        
        # Executar em lotes para não sobrecarregar
        batch_size = 50
        all_responses = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_responses = await asyncio.gather(*batch)
            all_responses.extend(batch_responses)
            
            # Pequena pausa entre batches
            await asyncio.sleep(0.1)
        
        # Verificar resultados
        successful_responses = sum(1 for r in all_responses if r.status_code == 200)
        success_rate = successful_responses / len(all_responses)
        
        # Taxa de sucesso deve ser alta
        assert success_rate > 0.95  # Pelo menos 95% de sucesso


def test_memory_leak_detection():
    """Detecta possíveis vazamentos de memória"""
    import gc
    import psutil
    import os
    
    # Forçar garbage collection
    gc.collect()
    
    # Medir memória inicial
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Criar e destruir muitos objetos
    objects = []
    for i in range(10000):
        objects.append({
            "id": i,
            "data": "x" * 1000,  # 1KB por objeto
            "nested": {"value": i}
        })
    
    # Limpar referências
    del objects
    gc.collect()
    
    # Medir memória final
    final_memory = process.memory_info().rss
    memory_diff = final_memory - initial_memory
    
    # Memória não deve aumentar muito após GC
    assert memory_diff < 50 * 1024 * 1024  # Menos de 50MB


@pytest.mark.asyncio
async def test_database_connection_pool():
    """Testa eficiência do pool de conexões com o banco"""
    # Este teste simularia múltiplas conexões com o banco
    # Como estamos usando mocks, verificamos se o serviço lida bem com múltiplas chamadas
    
    from app.services.supabase import SupabaseService
    
    services = [SupabaseService() for _ in range(10)]
    
    # Mock do cliente
    with patch('app.services.supabase.supabase') as mock_supabase:
        mock_client = AsyncMock()
        mock_table = AsyncMock()
        mock_table.select.return_value = mock_table
        mock_table.execute.return_value = AsyncMock(data=[])
        
        mock_client.table.return_value = mock_table
        mock_supabase.return_value = mock_client
        
        # Executar operações concorrentes
        tasks = []
        for service in services:
            task = service.get_leads()
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # Todas as operações devem ser bem-sucedidas
        for result in results:
            assert "leads" in result
            assert "total" in result
