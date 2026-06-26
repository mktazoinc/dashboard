import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from app.services.supabase import SupabaseService


@pytest.fixture
def mock_supabase_client():
    """Mock para o cliente Supabase"""
    with patch('app.services.supabase.supabase') as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def supabase_service(mock_supabase_client):
    """Fixture para o serviço Supabase"""
    service = SupabaseService()
    service.client = mock_supabase_client
    return service


@pytest.fixture
def sample_leads_data():
    """Dados de exemplo para leads"""
    return [
        {
            "id": 1,
            "nome": "João Silva",
            "email": "joao@example.com",
            "telefone": "11999999999",
            "status": "novo",
            "origem": "facebook",
            "empreendimento": "Residencial A",
            "corretor": "Pedro",
            "data_entrada": "2024-01-15",
            "data_acao": "2024-01-16",
            "cidade": "RJ",
            "valor": "500000"
        },
        {
            "id": 2,
            "nome": "Maria Santos",
            "email": "maria@example.com",
            "telefone": "11888888888",
            "status": "em_atendimento",
            "origem": "google",
            "empreendimento": "Comercial B",
            "corretor": "Ana",
            "data_entrada": "2024-01-14",
            "data_acao": "2024-01-15",
            "cidade": "SP",
            "valor": "300000"
        }
    ]


@pytest.mark.asyncio
async def test_get_leads_basic(supabase_service, mock_supabase_client, sample_leads_data):
    """Teste básico de obtenção de leads"""
    # Arrange
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=sample_leads_data)
    
    mock_supabase_client.table.return_value = mock_table
    
    # Act
    result = await supabase_service.get_leads()
    
    # Assert
    assert result["leads"] == sample_leads_data
    assert result["total"] == len(sample_leads_data)
    assert result["page"] == 1
    assert result["page_size"] == 50
    assert result["total_pages"] == 1
    
    # Verifica se a tabela correta foi consultada
    mock_supabase_client.table.assert_called_with("leads")


@pytest.mark.asyncio
async def test_get_leads_with_filters(supabase_service, mock_supabase_client, sample_leads_data):
    """Teste de obtenção de leads com filtros"""
    # Arrange
    filters = {
        "status": "novo",
        "cidade": "RJ",
        "origem": "facebook",
        "data_inicio": "2024-01-01",
        "data_fim": "2024-01-31"
    }
    
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=sample_leads_data[:1])
    
    mock_supabase_client.table.return_value = mock_table
    
    # Act
    result = await supabase_service.get_leads(
        status=filters["status"],
        cidade=filters["cidade"],
        origem=filters["origem"],
        data_inicio=filters["data_inicio"],
        data_fim=filters["data_fim"]
    )
    
    # Assert
    assert len(result["leads"]) == 1
    assert result["leads"][0]["status"] == "novo"
    
    # Verifica se os filtros foram aplicados
    mock_table.eq.assert_any_call("status", "novo")
    mock_table.eq.assert_any_call("cidade", "RJ")
    mock_table.eq.assert_any_call("origem", "facebook")


@pytest.mark.asyncio
async def test_get_leads_with_pagination(supabase_service, mock_supabase_client, sample_leads_data):
    """Teste de obtenção de leads com paginação"""
    # Arrange
    page = 2
    page_size = 10
    
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=sample_leads_data)
    
    mock_supabase_client.table.return_value = mock_table
    
    # Act
    result = await supabase_service.get_leads(page=page, page_size=page_size)
    
    # Assert
    assert result["page"] == page
    assert result["page_size"] == page_size
    
    # Verifica se a paginação foi aplicada
    mock_table.limit.assert_called_with(page_size)
    mock_table.offset.assert_called_with((page - 1) * page_size)


@pytest.mark.asyncio
async def test_get_leads_with_sorting(supabase_service, mock_supabase_client, sample_leads_data):
    """Teste de obtenção de leads com ordenação"""
    # Arrange
    sort_by = "data_entrada"
    sort_order = "desc"
    
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=sample_leads_data)
    
    mock_supabase_client.table.return_value = mock_table
    
    # Act
    result = await supabase_service.get_leads(sort_by=sort_by, sort_order=sort_order)
    
    # Assert
    assert result["leads"] == sample_leads_data
    
    # Verifica se a ordenação foi aplicada
    mock_table.order.assert_called_with(sort_by, desc=(sort_order == "desc"))


@pytest.mark.asyncio
async def test_get_marketing_metrics(supabase_service, mock_supabase_client, sample_leads_data):
    """Teste de obtenção de métricas de marketing"""
    # Arrange
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=sample_leads_data)
    
    mock_supabase_client.table.return_value = mock_table
    
    # Act
    result = await supabase_service.get_marketing_metrics()
    
    # Assert
    assert result["total_leads"] == 2
    assert result["leads_by_status"]["novo"] == 1
    assert result["leads_by_status"]["em_atendimento"] == 1
    assert result["leads_by_origem"]["facebook"] == 1
    assert result["leads_by_origem"]["google"] == 1
    assert result["avg_cpl"] > 0  # CPL calculado


@pytest.mark.asyncio
async def test_get_marketing_metrics_with_filters(supabase_service, mock_supabase_client, sample_leads_data):
    """Teste de métricas de marketing com filtros"""
    # Arrange
    filters = {"cidade": "RJ"}
    
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=[sample_leads_data[0]])  # Apenas lead do RJ
    
    mock_supabase_client.table.return_value = mock_table
    
    # Act
    result = await supabase_service.get_marketing_metrics(cidade=filters["cidade"])
    
    # Assert
    assert result["total_leads"] == 1
    assert result["leads_by_status"]["novo"] == 1
    assert "em_atendimento" not in result["leads_by_status"]


@pytest.mark.asyncio
async def test_get_lead_sources(supabase_service, mock_supabase_client):
    """Teste de obtenção de fontes de leads"""
    # Arrange
    sources_data = [{"origem": "facebook"}, {"origem": "google"}, {"origem": "instagram"}]
    
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=sources_data)
    
    mock_supabase_client.table.return_value = mock_table
    
    # Act
    result = await supabase_service.get_lead_sources()
    
    # Assert
    assert len(result) == 3
    assert "facebook" in result
    assert "google" in result
    assert "instagram" in result


@pytest.mark.asyncio
async def test_get_lead_status_options(supabase_service, mock_supabase_client):
    """Teste de obtenção de opções de status de leads"""
    # Arrange
    status_data = [{"status": "novo"}, {"status": "em_atendimento"}, {"status": "visita_agendada"}]
    
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=status_data)
    
    mock_supabase_client.table.return_value = mock_table
    
    # Act
    result = await supabase_service.get_lead_status_options()
    
    # Assert
    assert len(result) == 3
    assert "novo" in result
    assert "em_atendimento" in result
    assert "visita_agendada" in result


@pytest.mark.asyncio
async def test_calculate_metrics(supabase_service):
    """Teste do cálculo de métricas"""
    # Arrange
    leads = [
        {"status": "novo", "origem": "facebook", "valor": "100000"},
        {"status": "novo", "origem": "google", "valor": "200000"},
        {"status": "em_atendimento", "origem": "facebook", "valor": "150000"},
        {"status": "visita_agendada", "origem": "instagram", "valor": "300000"}
    ]
    
    # Act
    result = supabase_service._calculate_metrics(leads)
    
    # Assert
    assert result["total_leads"] == 4
    assert result["leads_by_status"]["novo"] == 2
    assert result["leads_by_status"]["em_atendimento"] == 1
    assert result["leads_by_status"]["visita_agendada"] == 1
    assert result["leads_by_origem"]["facebook"] == 2
    assert result["leads_by_origem"]["google"] == 1
    assert result["leads_by_origem"]["instagram"] == 1


@pytest.mark.asyncio
async def test_calculate_cpl(supabase_service):
    """Teste do cálculo de CPL"""
    # Arrange
    leads = [
        {"valor": "100000"},
        {"valor": "200000"},
        {"valor": "150000"}
    ]
    
    # Act
    result = supabase_service._calculate_cpl(leads)
    
    # Assert
    # CPL médio = (100000 + 200000 + 150000) / 3 = 150000
    assert result == 150000.0


@pytest.mark.asyncio
async def test_calculate_conversion_rate(supabase_service):
    """Teste do cálculo de taxa de conversão"""
    # Arrange
    leads = [
        {"status": "novo"},
        {"status": "novo"},
        {"status": "visita_agendada"},
        {"status": "visita_agendada"},
        {"status": "venda"}
    ]
    
    # Act
    result = supabase_service._calculate_conversion_rate(leads)
    
    # Assert
    # Taxa = (visitas + vendas) / total = (2 + 1) / 5 = 0.6 = 60%
    assert result == 60.0


@pytest.mark.asyncio
async def test_get_leads_supabase_error(supabase_service, mock_supabase_client):
    """Teste de tratamento de erro do Supabase"""
    # Arrange
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.execute.side_effect = Exception("Supabase connection error")
    
    mock_supabase_client.table.return_value = mock_table
    
    # Act
    result = await supabase_service.get_leads()
    
    # Assert
    # Deve retornar dados mock quando há erro
    assert "leads" in result
    assert "total" in result
    assert result["supabase_configured"] is False


@pytest.mark.asyncio
async def test_get_leads_no_client(supabase_service):
    """Teste quando não há cliente Supabase configurado"""
    # Arrange
    supabase_service.client = None
    
    # Act
    result = await supabase_service.get_leads()
    
    # Assert
    # Deve retornar dados mock quando não há cliente
    assert "leads" in result
    assert "total" in result
    assert result["supabase_configured"] is False


@pytest.mark.asyncio
async def test_role_based_filtering_rj(supabase_service, mock_supabase_client, sample_leads_data):
    """Teste de filtragem por role (marketing_rj)"""
    # Arrange
    user_role = "marketing_rj"
    
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=[sample_leads_data[0]])  # Apenas lead do RJ
    
    mock_supabase_client.table.return_value = mock_table
    
    # Act
    result = await supabase_service.get_leads(user_role=user_role)
    
    # Assert
    assert len(result["leads"]) == 1
    assert result["leads"][0]["cidade"] == "RJ"
    
    # Verifica se o filtro de cidade foi aplicado
    mock_table.eq.assert_any_call("cidade", "RJ")


@pytest.mark.asyncio
async def test_role_based_filtering_sp(supabase_service, mock_supabase_client, sample_leads_data):
    """Teste de filtragem por role (marketing_sp)"""
    # Arrange
    user_role = "marketing_sp"
    
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=[sample_leads_data[1]])  # Apenas lead de SP
    
    mock_supabase_client.table.return_value = mock_table
    
    # Act
    result = await supabase_service.get_leads(user_role=user_role)
    
    # Assert
    assert len(result["leads"]) == 1
    assert result["leads"][0]["cidade"] == "SP"
    
    # Verifica se o filtro de cidade foi aplicado
    mock_table.eq.assert_any_call("cidade", "SP")


@pytest.mark.asyncio
async def test_role_based_filtering_admin(supabase_service, mock_supabase_client, sample_leads_data):
    """Teste de filtragem por role (admin - sem restrição)"""
    # Arrange
    user_role = "admin"
    
    mock_table = AsyncMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.gte.return_value = mock_table
    mock_table.lte.return_value = mock_table
    mock_table.order.return_value = mock_table
    mock_table.limit.return_value = mock_table
    mock_table.offset.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=sample_leads_data)
    
    mock_supabase_client.table.return_value = mock_table
    
    # Act
    result = await supabase_service.get_leads(user_role=user_role)
    
    # Assert
    assert len(result["leads"]) == 2  # Admin vê todos os leads
    
    # Verifica que NÃO foi aplicado filtro de cidade
    mock_table.eq.assert_not_called_with("cidade", "RJ")
    mock_table.eq.assert_not_called_with("cidade", "SP")
