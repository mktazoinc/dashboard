import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from app.services.audit import AuditService, AuditAction, AuditSeverity


@pytest.fixture
def audit_service():
    """Fixture para o serviço de auditoria"""
    return AuditService()


@pytest.fixture
def mock_cache_service():
    """Mock para o cache service"""
    with patch('app.services.audit.cache_service') as mock:
        mock.get = AsyncMock(return_value=None)
        mock.set = AsyncMock(return_value=True)
        yield mock


@pytest.mark.asyncio
async def test_log_action_basic(audit_service, mock_cache_service):
    """Teste básico de logging de ação"""
    # Arrange
    action = AuditAction.USER_LOGIN
    user_id = "test_user_123"
    user_email = "test@example.com"
    user_role = "admin"
    
    # Act
    result = await audit_service.log_action(
        action=action,
        user_id=user_id,
        user_email=user_email,
        user_role=user_role
    )
    
    # Assert
    assert result is not None
    assert result["action"] == action.value
    assert result["user"]["id"] == user_id
    assert result["user"]["email"] == user_email
    assert result["user"]["role"] == user_role
    assert result["severity"] == AuditSeverity.MEDIUM.value
    assert result["metadata"]["success"] is True
    
    # Verifica se o cache foi chamado
    mock_cache_service.set.assert_called()


@pytest.mark.asyncio
async def test_log_action_with_details(audit_service, mock_cache_service):
    """Teste de logging com detalhes adicionais"""
    # Arrange
    action = AuditAction.USER_CREATED
    user_id = "admin_user"
    user_email = "admin@example.com"
    user_role = "admin"
    resource_type = "user"
    resource_id = "new_user_456"
    details = {"created_role": "marketing_rj"}
    ip_address = "192.168.1.1"
    user_agent = "Mozilla/5.0"
    
    # Act
    result = await audit_service.log_action(
        action=action,
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        severity=AuditSeverity.HIGH,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Assert
    assert result["action"] == action.value
    assert result["severity"] == AuditSeverity.HIGH.value
    assert result["resource"]["type"] == resource_type
    assert result["resource"]["id"] == resource_id
    assert result["details"] == details
    assert result["metadata"]["ip_address"] == ip_address
    assert result["metadata"]["user_agent"] == user_agent


@pytest.mark.asyncio
async def test_log_action_failed(audit_service, mock_cache_service):
    """Teste de logging de ação falha"""
    # Arrange
    action = AuditAction.FAILED_LOGIN
    user_id = "failed_user"
    user_email = "failed@example.com"
    user_role = "user"
    error_message = "Invalid credentials"
    
    # Act
    result = await audit_service.log_action(
        action=action,
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        severity=AuditSeverity.HIGH,
        success=False,
        error_message=error_message
    )
    
    # Assert
    assert result["action"] == action.value
    assert result["severity"] == AuditSeverity.HIGH.value
    assert result["metadata"]["success"] is False
    assert result["metadata"]["error_message"] == error_message


@pytest.mark.asyncio
async def test_get_user_logs_empty(audit_service, mock_cache_service):
    """Teste de obtenção de logs de usuário quando não há logs"""
    # Arrange
    user_id = "test_user"
    mock_cache_service.get.return_value = []
    
    # Act
    result = await audit_service.get_user_logs(user_id=user_id)
    
    # Assert
    assert result["logs"] == []
    assert result["total"] == 0
    assert result["limit"] == 100
    assert result["offset"] == 0
    assert result["has_more"] is False


@pytest.mark.asyncio
async def test_get_user_logs_with_data(audit_service, mock_cache_service):
    """Teste de obtenção de logs de usuário com dados existentes"""
    # Arrange
    user_id = "test_user"
    mock_logs = [
        {
            "id": "log1",
            "action": "user_login",
            "user": {"id": user_id, "email": "test@example.com"},
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": "log2",
            "action": "data_accessed",
            "user": {"id": user_id, "email": "test@example.com"},
            "timestamp": datetime.now().isoformat()
        }
    ]
    mock_cache_service.get.return_value = mock_logs
    
    # Act
    result = await audit_service.get_user_logs(user_id=user_id, limit=10)
    
    # Assert
    assert len(result["logs"]) == 2
    assert result["total"] == 2
    assert result["limit"] == 10
    assert result["has_more"] is False


@pytest.mark.asyncio
async def test_get_recent_logs_by_severity(audit_service, mock_cache_service):
    """Teste de obtenção de logs recentes filtrados por severidade"""
    # Arrange
    severity = AuditSeverity.CRITICAL
    mock_logs = [
        {
            "id": "critical_log1",
            "action": "security_breach",
            "severity": severity.value,
            "timestamp": datetime.now().isoformat()
        }
    ]
    mock_cache_service.get.return_value = mock_logs
    
    # Act
    result = await audit_service.get_recent_logs(severity=severity)
    
    # Assert
    assert len(result["logs"]) == 1
    assert result["logs"][0]["severity"] == severity.value
    mock_cache_service.get.assert_called_with(f"audit:recent:{severity.value}")


@pytest.mark.asyncio
async def test_get_critical_logs(audit_service, mock_cache_service):
    """Teste de obtenção de logs críticos"""
    # Arrange
    mock_logs = [
        {
            "id": "high_log",
            "action": "role_changed",
            "severity": AuditSeverity.HIGH.value,
            "timestamp": datetime.now().isoformat()
        },
        {
            "id": "critical_log",
            "action": "security_breach",
            "severity": AuditSeverity.CRITICAL.value,
            "timestamp": datetime.now().isoformat()
        }
    ]
    mock_cache_service.get.return_value = mock_logs
    
    # Act
    result = await audit_service.get_critical_logs()
    
    # Assert
    assert len(result["logs"]) == 2
    mock_cache_service.get.assert_called_with("audit:critical")


@pytest.mark.asyncio
async def test_search_logs(audit_service, mock_cache_service):
    """Teste de busca de logs com filtros"""
    # Arrange
    query = "login"
    action = AuditAction.USER_LOGIN
    mock_logs = [
        {
            "id": "login_log1",
            "action": action.value,
            "user": {"email": "user@example.com"},
            "timestamp": datetime.now().isoformat()
        }
    ]
    mock_cache_service.get.return_value = mock_logs
    
    # Act
    result = await audit_service.search_logs(
        query=query,
        action=action,
        limit=50
    )
    
    # Assert
    assert len(result["logs"]) == 1
    assert result["logs"][0]["action"] == action.value
    assert result["filters"]["query"] == query
    assert result["filters"]["action"] == action.value


@pytest.mark.asyncio
async def test_get_audit_statistics(audit_service, mock_cache_service):
    """Teste de obtenção de estatísticas de auditoria"""
    # Arrange
    base_time = datetime.now()
    mock_logs = [
        {
            "action": "user_login",
            "user": {"id": "user1", "email": "user1@example.com"},
            "severity": "low",
            "timestamp": (base_time - timedelta(days=1)).isoformat(),
            "metadata": {"success": True}
        },
        {
            "action": "user_login",
            "user": {"id": "user2", "email": "user2@example.com"},
            "severity": "medium",
            "timestamp": (base_time - timedelta(days=2)).isoformat(),
            "metadata": {"success": False}
        },
        {
            "action": "security_breach",
            "user": {"id": "user1", "email": "user1@example.com"},
            "severity": "critical",
            "timestamp": (base_time - timedelta(days=3)).isoformat(),
            "metadata": {"success": True}
        }
    ]
    mock_cache_service.get.return_value = mock_logs
    
    # Act
    result = await audit_service.get_audit_statistics(days=30)
    
    # Assert
    assert result["total_actions"] == 3
    assert result["unique_users"] == 2
    assert result["actions_by_type"]["user_login"] == 2
    assert result["actions_by_type"]["security_breach"] == 1
    assert result["actions_by_severity"]["low"] == 1
    assert result["actions_by_severity"]["medium"] == 1
    assert result["actions_by_severity"]["critical"] == 1
    assert result["failed_actions"] == 1
    assert result["critical_actions"] == 1


@pytest.mark.asyncio
async def test_log_action_cache_failure(audit_service, mock_cache_service):
    """Teste de logging quando o cache falha"""
    # Arrange
    mock_cache_service.set.side_effect = Exception("Cache error")
    
    # Act
    result = await audit_service.log_action(
        action=AuditAction.USER_LOGIN,
        user_id="test_user",
        user_email="test@example.com",
        user_role="user"
    )
    
    # Assert
    # Não deve falhar a operação principal se auditoria falhar
    assert result == {}


@pytest.mark.asyncio
async def test_get_user_logs_cache_failure(audit_service, mock_cache_service):
    """Teste de obtenção de logs quando o cache falha"""
    # Arrange
    user_id = "test_user"
    mock_cache_service.get.side_effect = Exception("Cache error")
    
    # Act
    result = await audit_service.get_user_logs(user_id=user_id)
    
    # Assert
    assert result["logs"] == []
    assert result["total"] == 0
