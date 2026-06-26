import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.main import app


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Teste do endpoint de health check"""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_auth_login_success(client: AsyncClient, mock_firebase_auth):
    """Teste de login com sucesso"""
    # Arrange
    login_data = {
        "email": "test@example.com",
        "password": "test_password"
    }
    
    mock_firebase_auth.get_user_by_email.return_value = AsyncMock(
        uid="test_user_123",
        email="test@example.com",
        custom_claims={"role": "admin"}
    )
    
    # Act
    response = await client.post("/api/v1/auth/login", json=login_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["role"] == "admin"


@pytest.mark.asyncio
async def test_auth_login_invalid_credentials(client: AsyncClient, mock_firebase_auth):
    """Teste de login com credenciais inválidas"""
    # Arrange
    login_data = {
        "email": "invalid@example.com",
        "password": "wrong_password"
    }
    
    mock_firebase_auth.get_user_by_email.side_effect = Exception("Invalid credentials")
    
    # Act
    response = await client.post("/api/v1/auth/login", json=login_data)
    
    # Assert
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient, mock_firebase_auth):
    """Teste de obtenção do perfil do usuário atual"""
    # Arrange
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "test_user_123",
        "email": "test@example.com",
        "role": "admin"
    }
    
    # Act
    response = await client.get("/api/v1/users/me", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == "test_user_123"
    assert data["email"] == "test@example.com"
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_get_marketing_dashboard(client: AsyncClient, mock_firebase_auth, mock_supabase):
    """Teste de obtenção do dashboard de marketing"""
    # Arrange
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "marketing_user_123",
        "email": "marketing@example.com",
        "role": "marketing_rj"
    }
    
    # Mock Supabase response
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.execute.return_value = AsyncMock(data=[
        {
            "id": 1,
            "nome": "João Silva",
            "status": "novo",
            "origem": "facebook",
            "cidade": "RJ",
            "data_entrada": "2024-01-15"
        }
    ])
    
    mock_supabase.return_value.table.return_value = mock_table
    
    # Act
    response = await client.get("/api/v1/marketing/dashboard", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "user" in data
    assert data["user"] == "marketing@example.com"


@pytest.mark.asyncio
async def test_get_marketing_leads(client: AsyncClient, mock_firebase_auth, mock_supabase):
    """Teste de obtenção de leads de marketing"""
    # Arrange
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "marketing_user_123",
        "email": "marketing@example.com",
        "role": "marketing_rj"
    }
    
    # Mock Supabase response
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.execute.return_value = AsyncMock(data=[
        {
            "id": 1,
            "nome": "João Silva",
            "email": "joao@example.com",
            "status": "novo",
            "cidade": "RJ"
        }
    ])
    
    mock_supabase.return_value.table.return_value = mock_table
    
    # Act
    response = await client.get("/api/v1/marketing/leads", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "leads" in data
    assert "total" in data
    assert "page" in data
    assert len(data["leads"]) == 1


@pytest.mark.asyncio
async def test_get_finance_dashboard(client: AsyncClient, mock_firebase_auth):
    """Teste de obtenção do dashboard financeiro"""
    # Arrange
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "finance_user_123",
        "email": "finance@example.com",
        "role": "comercial_rj"
    }
    
    # Act
    response = await client.get("/api/v1/finance/dashboard", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "user" in data
    assert data["user"] == "finance@example.com"


@pytest.mark.asyncio
async def test_get_admin_dashboard(client: AsyncClient, mock_firebase_auth, mock_redis, mock_psutil):
    """Teste de obtenção do dashboard admin"""
    # Arrange
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "admin_user_123",
        "email": "admin@example.com",
        "role": "admin"
    }
    
    # Act
    response = await client.get("/api/v1/admin/dashboard", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "system_health" in data
    assert data["user"] == "admin@example.com"


@pytest.mark.asyncio
async def test_get_audit_logs(client: AsyncClient, mock_firebase_auth, mock_redis):
    """Teste de obtenção de logs de auditoria"""
    # Arrange
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "admin_user_123",
        "email": "admin@example.com",
        "role": "admin"
    }
    
    # Mock Redis response
    mock_redis.get.return_value = [
        {
            "id": "audit_log_1",
            "action": "user_login",
            "user": {"email": "admin@example.com"},
            "timestamp": "2024-01-15T10:00:00",
            "severity": "medium"
        }
    ]
    
    # Act
    response = await client.get("/api/v1/audit/logs", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert "total" in data
    assert len(data["logs"]) == 1


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, mock_firebase_auth):
    """Teste de criação de usuário"""
    # Arrange
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    user_data = {
        "email": "newuser@example.com",
        "role": "marketing_rj",
        "display_name": "New User",
        "password": "secure_password"
    }
    
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "admin_user_123",
        "email": "admin@example.com",
        "role": "admin"
    }
    
    mock_firebase_auth.get_user_by_email.side_effect = Exception("User not found")
    mock_firebase_auth.create_user.return_value = AsyncMock(
        uid="new_user_123",
        email="newuser@example.com",
        display_name="New User"
    )
    
    # Act
    response = await client.post("/api/v1/users/", json=user_data, headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "marketing_rj"


@pytest.mark.asyncio
async def test_update_user_role(client: AsyncClient, mock_firebase_auth):
    """Teste de atualização de role de usuário"""
    # Arrange
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    user_uid = "target_user_123"
    update_data = {"role": "marketing_sp"}
    
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "mestre_user_123",
        "email": "mestre@example.com",
        "role": "mestre_do_universo"
    }
    
    mock_firebase_auth.get_user.return_value = AsyncMock(
        uid=user_uid,
        email="target@example.com",
        custom_claims={"role": "marketing_rj"}
    )
    
    # Act
    response = await client.put(f"/api/v1/users/{user_uid}", json=update_data, headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "marketing_sp"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Teste de acesso não autorizado"""
    # Act
    response = await client.get("/api/v1/admin/dashboard")
    
    # Assert
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_forbidden_access(client: AsyncClient, mock_firebase_auth):
    """Teste de acesso proibido (role insuficiente)"""
    # Arrange
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "regular_user_123",
        "email": "user@example.com",
        "role": "marketing_rj"
    }
    
    # Act - Tentar acessar endpoint admin com role de marketing
    response = await client.get("/api/v1/admin/dashboard", headers=headers)
    
    # Assert
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_role_based_data_filtering(client: AsyncClient, mock_firebase_auth, mock_supabase):
    """Teste de filtragem de dados baseada em role"""
    # Arrange
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "marketing_rj_user_123",
        "email": "marketing_rj@example.com",
        "role": "marketing_rj"
    }
    
    # Mock Supabase response
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.execute.return_value = AsyncMock(data=[
        {
            "id": 1,
            "nome": "João Silva",
            "cidade": "RJ"  # Apenas leads do RJ
        }
    ])
    
    mock_supabase.return_value.table.return_value = mock_table
    
    # Act
    response = await client.get("/api/v1/marketing/leads", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data["leads"]) == 1
    assert data["leads"][0]["cidade"] == "RJ"
    
    # Verifica se o filtro de cidade foi aplicado
    mock_table.eq.assert_any_call("cidade", "RJ")


@pytest.mark.asyncio
async def test_api_rate_limiting(client: AsyncClient, mock_redis):
    """Teste de rate limiting da API"""
    # Arrange
    mock_redis.get.return_value = None  # Primeira requisição
    mock_redis.set.return_value = True
    
    # Act - Fazer múltiplas requisições
    responses = []
    for _ in range(5):
        response = await client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "test_password"
        })
        responses.append(response)
    
    # Assert - As primeiras requisições devem passar
    assert responses[0].status_code == 200
    
    # Verifica se o contador foi incrementado
    mock_redis.incrby.assert_called()


@pytest.mark.asyncio
async def test_api_error_handling(client: AsyncClient, mock_firebase_auth):
    """Teste de tratamento de erros da API"""
    # Arrange
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "admin_user_123",
        "email": "admin@example.com",
        "role": "admin"
    }
    
    # Simular erro no serviço
    with patch('app.api.v1.endpoints.admin.get_system_metrics') as mock_metrics:
        mock_metrics.side_effect = Exception("Database connection failed")
        
        # Act
        response = await client.get("/api/v1/admin/dashboard", headers=headers)
        
        # Assert
        assert response.status_code == 200  # Não deve falhar completamente
        data = response.json()
        assert "error" in data  # Deve indicar que houve erro
        assert "metrics" in data  # Mas ainda retorna dados mock


@pytest.mark.asyncio
async def test_api_validation_errors(client: AsyncClient):
    """Teste de validação de dados da API"""
    # Arrange - Dados inválidos
    invalid_user_data = {
        "email": "invalid-email",  # Email inválido
        "role": "invalid_role"     # Role inválida
    }
    
    # Act
    response = await client.post("/api/v1/users/", json=invalid_user_data)
    
    # Assert - Deve retornar erro de validação
    assert response.status_code == 422  # Unprocessable Entity


@pytest.mark.asyncio
async def test_api_caching(client: AsyncClient, mock_firebase_auth, mock_redis):
    """Teste de cache da API"""
    # Arrange
    token = "valid_token"
    headers = {"Authorization": f"Bearer {token}"}
    
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "marketing_user_123",
        "email": "marketing@example.com",
        "role": "marketing_rj"
    }
    
    # Primeira requisição - cache miss
    mock_redis.get.return_value = None
    
    # Act
    response1 = await client.get("/api/v1/marketing/dashboard", headers=headers)
    
    # Segunda requisição - cache hit
    cached_data = '{"metrics": {"total_leads": 10}}'
    mock_redis.get.return_value = cached_data
    
    response2 = await client.get("/api/v1/marketing/dashboard", headers=headers)
    
    # Assert
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Verifica se o cache foi consultado
    assert mock_redis.get.call_count == 2
