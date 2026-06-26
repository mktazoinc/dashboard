import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop para a sessão de testes"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    """Cliente de teste para a API FastAPI"""
    from httpx import AsyncClient
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_firebase_auth():
    """Mock para autenticação Firebase"""
    with patch('firebase_admin.auth') as mock_auth:
        # Mock user
        mock_user = AsyncMock()
        mock_user.uid = "test_user_123"
        mock_user.email = "test@example.com"
        mock_user.custom_claims = {"role": "admin"}
        
        mock_auth.get_user.return_value = mock_user
        mock_auth.get_user_by_email.return_value = mock_user
        mock_auth.create_user.return_value = mock_user
        mock_auth.update_user.return_value = mock_user
        mock_auth.delete_user.return_value = None
        mock_auth.set_custom_user_claims.return_value = None
        mock_auth.list_users.return_value = AsyncMock(users=[])
        mock_auth.verify_id_token.return_value = {
            "uid": "test_user_123",
            "email": "test@example.com",
            "role": "admin"
        }
        
        yield mock_auth


@pytest.fixture
def mock_redis():
    """Mock para cliente Redis"""
    with patch('redis.asyncio.from_url') as mock_redis:
        redis_client = AsyncMock()
        redis_client.get.return_value = None
        redis_client.set.return_value = True
        redis_client.setex.return_value = True
        redis_client.delete.return_value = 1
        redis_client.exists.return_value = 1
        redis_client.incrby.return_value = 1
        redis_client.ttl.return_value = 3600
        redis_client.ping.return_value = True
        
        mock_redis.return_value = redis_client
        yield redis_client


@pytest.fixture
def mock_supabase():
    """Mock para cliente Supabase"""
    with patch('app.services.supabase.supabase') as mock_supabase:
        client = AsyncMock()
        mock_table = AsyncMock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.gte.return_value = mock_table
        mock_table.lte.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.offset.return_value = mock_table
        mock_table.execute.return_value = AsyncMock(data=[])
        
        client.table.return_value = mock_table
        mock_supabase.return_value = client
        
        yield mock_supabase


@pytest.fixture
def sample_user_token():
    """Token JWT de exemplo para testes"""
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test.token"


@pytest.fixture
def admin_user_data():
    """Dados de usuário admin para testes"""
    return {
        "uid": "admin_user_123",
        "email": "admin@example.com",
        "role": "admin",
        "custom_claims": {"role": "admin"}
    }


@pytest.fixture
def marketing_user_data():
    """Dados de usuário marketing para testes"""
    return {
        "uid": "marketing_user_123",
        "email": "marketing@example.com",
        "role": "marketing_rj",
        "custom_claims": {"role": "marketing_rj"}
    }


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


@pytest.fixture
def sample_financial_data():
    """Dados financeiros de exemplo"""
    return {
        "total_receita": 1000000.0,
        "total_despesa": 600000.0,
        "lucro_liquido": 400000.0,
        "margem_lucro": 40.0,
        "vendas_mes": 800000.0,
        "meta_mes": 1000000.0,
        "perc_meta": 80.0,
        "tickets_medio": 50000.0,
        "total_vendas": 16,
        "taxa_conversao": 25.0,
        "receita_diaria": [
            {"data": "2024-01-01", "valor": 50000.0},
            {"data": "2024-01-02", "valor": 75000.0},
            {"data": "2024-01-03", "valor": 60000.0}
        ],
        "despesas_categoria": [
            {"categoria": "Marketing", "valor": 150000.0},
            {"categoria": "Operacional", "valor": 250000.0},
            {"categoria": "Pessoal", "valor": 200000.0}
        ],
        "vendas_corretor": [
            {"corretor": "Pedro", "vendas": 5, "valor": 250000.0},
            {"corretor": "Ana", "vendas": 4, "valor": 200000.0},
            {"corretor": "Carlos", "vendas": 3, "valor": 150000.0}
        ]
    }


@pytest.fixture
def mock_settings():
    """Mock para configurações do sistema"""
    with patch('app.core.config.settings') as mock_settings:
        mock_settings.REDIS_URL = "redis://localhost:6379"
        mock_settings.SUPABASE_URL = "https://test.supabase.co"
        mock_settings.SUPABASE_SERVICE_KEY = "test_key"
        mock_settings.FIREBASE_CREDENTIALS_PATH = "/path/to/credentials.json"
        mock_settings.ALGORITHM = "HS256"
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        yield mock_settings


@pytest.fixture
def mock_psutil():
    """Mock para psutil (métricas de sistema)"""
    with patch('psutil') as mock_psutil:
        # Mock CPU
        mock_psutil.cpu_percent.return_value = 45.5
        
        # Mock Memory
        mock_memory = AsyncMock()
        mock_memory.percent = 67.8
        mock_memory.total = 8589934592  # 8GB
        mock_memory.available = 2768240640  # ~2.5GB
        mock_psutil.virtual_memory.return_value = mock_memory
        
        # Mock Disk
        mock_disk = AsyncMock()
        mock_disk.percent = 78.2
        mock_disk.total = 500000000000  # 500GB
        mock_disk.used = 390000000000  # 390GB
        mock_psutil.disk_usage.return_value = mock_disk
        
        # Mock Network
        mock_network = AsyncMock()
        mock_network.bytes_sent = 1000000
        mock_network.bytes_recv = 2000000
        mock_psutil.net_io_counters.return_value = mock_network
        
        yield mock_psutil
