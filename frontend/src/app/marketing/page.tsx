'use client'

import { useState, useEffect } from 'react'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RoleGuard } from '@/components/RoleGuard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Users, 
  TrendingUp, 
  Calendar, 
  DollarSign, 
  Phone,
  UserCheck,
  UserX,
  Activity,
  Download,
  Filter
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

interface MarketingMetrics {
  leads_totais: number
  descartados: number
  em_atendimento: number
  agendamentos: number
  visitas: number
  reservas: number
  vendas_realizadas: number
  cpl_medio: number
  taxa_conversao: number
  origens: Record<string, number>
  cidades: Record<string, number>
  status_distribuicao: Record<string, number>
}

interface MarketingData {
  user: string
  role: string
  city: string
  metrics: MarketingMetrics
  filters: {
    data_inicio: string
    data_fim: string
    cidade: string
  }
  filter_options: {
    origens: string[]
    status: string[]
    cidades: string[]
  }
  supabase_configured: boolean
  last_updated: string
}

function MarketingPage() {
  const { user } = useAuth()
  const [data, setData] = useState<MarketingData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filters, setFilters] = useState({
    data_inicio: '',
    data_fim: '',
    cidade: '',
    status: '',
    origem: ''
  })

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value)
  }

  const formatPercentage = (value: number) => {
    return `${value.toFixed(1)}%`
  }

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const token = await user?.getIdToken()
      if (!token) throw new Error('No authentication token')
      
      // Build query params
      const params = new URLSearchParams()
      if (filters.data_inicio) params.append('data_inicio', filters.data_inicio)
      if (filters.data_fim) params.append('data_fim', filters.data_fim)
      if (filters.cidade) params.append('cidade', filters.cidade)
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/marketing/dashboard?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (!response.ok) throw new Error('Failed to fetch dashboard data')
      const dashboardData = await response.json()
      setData(dashboardData)
      
      // Update filters with returned values
      if (dashboardData.filters) {
        setFilters(prev => ({
          ...prev,
          data_inicio: dashboardData.filters.data_inicio || prev.data_inicio,
          data_fim: dashboardData.filters.data_fim || prev.data_fim,
          cidade: dashboardData.filters.cidade || prev.cidade,
        }))
      }
      
    } catch (err) {
      console.error('Error fetching dashboard data:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      fetchDashboardData()
    }
  }, [user])

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const applyFilters = () => {
    fetchDashboardData()
  }

  const clearFilters = () => {
    setFilters({
      data_inicio: '',
      data_fim: '',
      cidade: '',
      status: '',
      origem: ''
    })
    setTimeout(fetchDashboardData, 100)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin text-azo-blue mx-auto mb-4" />
          <p className="text-gray-600">Carregando dados de marketing...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="text-center py-8">
            <p className="text-red-600 mb-4">Erro ao carregar dados: {error}</p>
            <Button onClick={fetchDashboardData}>
              Tentar novamente
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const metrics = data?.metrics

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-2xl font-bold text-azo-blue">Sistema 2 - Marketing</h1>
              <p className="text-sm text-gray-600">
                {data?.user} • {data?.city || 'Todas as cidades'}
                {!data?.supabase_configured && (
                  <span className="ml-2 text-yellow-600">• Supabase não configurado (dados mock)</span>
                )}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" asChild>
                <a href="/marketing/leads">
                  Ver Todos os Leads
                </a>
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filtros */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center text-lg">
              <Filter className="h-5 w-5 mr-2" />
              Filtros
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div>
                <Label htmlFor="data_inicio">Data Início</Label>
                <Input
                  id="data_inicio"
                  type="date"
                  value={filters.data_inicio}
                  onChange={(e) => handleFilterChange('data_inicio', e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="data_fim">Data Fim</Label>
                <Input
                  id="data_fim"
                  type="date"
                  value={filters.data_fim}
                  onChange={(e) => handleFilterChange('data_fim', e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="cidade">Cidade</Label>
                <Select value={filters.cidade} onValueChange={(value) => handleFilterChange('cidade', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Todas" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Todas</SelectItem>
                    {data?.filter_options?.cidades?.map((cidade) => (
                      <SelectItem key={cidade} value={cidade}>
                        {cidade}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="status">Status</Label>
                <Select value={filters.status} onValueChange={(value) => handleFilterChange('status', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Todos" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Todos</SelectItem>
                    {data?.filter_options?.status?.map((status) => (
                      <SelectItem key={status} value={status}>
                        {status}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="origem">Origem</Label>
                <Select value={filters.origem} onValueChange={(value) => handleFilterChange('origem', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Todas" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Todas</SelectItem>
                    {data?.filter_options?.origens?.map((origem) => (
                      <SelectItem key={origem} value={origem}>
                        {origem}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex space-x-2 mt-4">
              <Button onClick={applyFilters}>
                Aplicar Filtros
              </Button>
              <Button variant="outline" onClick={clearFilters}>
                Limpar
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Big Numbers */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Leads Totais</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.leads_totais || 0}</div>
              <p className="text-xs text-muted-foreground">Total no período</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Em Atendimento</CardTitle>
              <Phone className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.em_atendimento || 0}</div>
              <p className="text-xs text-muted-foreground">Leads ativos</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Visitas</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.visitas || 0}</div>
              <p className="text-xs text-muted-foreground">Visitas realizadas</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Vendas</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.vendas_realizadas || 0}</div>
              <p className="text-xs text-muted-foreground">
                {formatPercentage(metrics?.taxa_conversao || 0)} conversão
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Métricas Adicionais */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">CPL Médio</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(metrics?.cpl_medio || 0)}</div>
              <p className="text-xs text-muted-foreground">Custo por lead</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Agendamentos</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.agendamentos || 0}</div>
              <p className="text-xs text-muted-foreground">Visitas agendadas</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Descartados</CardTitle>
              <UserX className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.descartados || 0}</div>
              <p className="text-xs text-muted-foreground">Leads perdidos</p>
            </CardContent>
          </Card>
        </div>

        {/* Distribuição por Status */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Distribuição por Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(metrics?.status_distribuicao || {}).map(([status, count]) => (
                  <div key={status} className="flex justify-between items-center">
                    <span className="text-sm font-medium">{status}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-azo-blue h-2 rounded-full"
                          style={{ 
                            width: `${((count || 0) / (metrics?.leads_totais || 1)) * 100}%` 
                          }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 w-8 text-right">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Origens dos Leads</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(metrics?.origens || {}).map(([origem, count]) => (
                  <div key={origem} className="flex justify-between items-center">
                    <span className="text-sm font-medium">{origem}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full"
                          style={{ 
                            width: `${((count || 0) / (metrics?.leads_totais || 1)) * 100}%` 
                          }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 w-8 text-right">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

export default function Marketing() {
  return (
    <ProtectedRoute requireAuth={true}>
      <RoleGuard requiredSystem="marketing">
        <MarketingPage />
      </RoleGuard>
    </ProtectedRoute>
  )
}
