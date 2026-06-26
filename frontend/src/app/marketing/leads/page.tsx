'use client'

import { useState, useEffect } from 'react'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RoleGuard } from '@/components/RoleGuard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  ChevronLeft, 
  ChevronRight, 
  Search, 
  Filter,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Download,
  Eye,
  Edit,
  Trash2
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

interface Lead {
  id: string
  nome: string
  email: string
  telefone: string
  cidade: string
  data_entrada: string
  data_acao: string
  status: string
  origem: string
  empreendimento: string
  corretor: string
  custo_aquisicao?: number
}

interface LeadsResponse {
  user: string
  role: string
  filters: Record<string, any>
  leads: Lead[]
  pagination: {
    total: number
    limit: number
    offset: number
    has_more: boolean
  }
  supabase_configured: boolean
  last_updated: string
}

type SortField = 'data_entrada' | 'data_acao' | 'nome' | 'status' | 'cidade' | 'origem'
type SortDirection = 'asc' | 'desc'

function LeadsPage() {
  const { user } = useAuth()
  const [data, setData] = useState<LeadsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(0)
  const [pageSize, setPageSize] = useState(50)
  const [sortField, setSortField] = useState<SortField>('data_entrada')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')
  const [filters, setFilters] = useState({
    data_entrada_inicio: '',
    data_entrada_fim: '',
    data_acao_inicio: '',
    data_acao_fim: '',
    cidade: '',
    status: '',
    origem: '',
    empreendimento: '',
    corretor: ''
  })

  const fetchLeads = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const token = await user?.getIdToken()
      if (!token) throw new Error('No authentication token')
      
      // Build query params
      const params = new URLSearchParams()
      
      // Add filters
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value)
      })
      
      // Add pagination
      params.append('limit', pageSize.toString())
      params.append('offset', (currentPage * pageSize).toString())
      
      // Add sorting
      params.append('sort', sortField)
      params.append('order', sortDirection)
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/marketing/leads?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (!response.ok) throw new Error('Failed to fetch leads')
      const leadsData = await response.json()
      setData(leadsData)
      
    } catch (err) {
      console.error('Error fetching leads:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      fetchLeads()
    }
  }, [user, currentPage, pageSize, sortField, sortDirection])

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const applyFilters = () => {
    setCurrentPage(0) // Reset to first page
    fetchLeads()
  }

  const clearFilters = () => {
    setFilters({
      data_entrada_inicio: '',
      data_entrada_fim: '',
      data_acao_inicio: '',
      data_acao_fim: '',
      cidade: '',
      status: '',
      origem: '',
      empreendimento: '',
      corretor: ''
    })
    setCurrentPage(0)
    setTimeout(fetchLeads, 100)
  }

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="h-4 w-4" />
    }
    return sortDirection === 'asc' ? 
      <ArrowUp className="h-4 w-4" /> : 
      <ArrowDown className="h-4 w-4" />
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR')
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'Novo': 'bg-blue-100 text-blue-800',
      'Em atendimento': 'bg-yellow-100 text-yellow-800',
      'Agendado': 'bg-purple-100 text-purple-800',
      'Visitou': 'bg-green-100 text-green-800',
      'Reservado': 'bg-indigo-100 text-indigo-800',
      'Vendido': 'bg-emerald-100 text-emerald-800',
      'Descartado': 'bg-red-100 text-red-800',
      'Perdido': 'bg-gray-100 text-gray-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const totalPages = Math.ceil((data?.pagination.total || 0) / pageSize)
  const hasNextPage = data?.pagination.has_more || false
  const hasPrevPage = currentPage > 0

  // Filter leads based on search term
  const filteredLeads = data?.leads.filter(lead => 
    searchTerm === '' || 
    lead.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead.telefone.includes(searchTerm) ||
    lead.cidade.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead.status.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-azo-blue mx-auto mb-4" />
          <p className="text-gray-600">Carregando leads...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="text-center py-8">
            <p className="text-red-600 mb-4">Erro ao carregar leads: {error}</p>
            <Button onClick={fetchLeads}>
              Tentar novamente
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-2xl font-bold text-azo-blue">Leads - Marketing</h1>
              <p className="text-sm text-gray-600">
                {data?.user} • {data?.pagination.total || 0} leads encontrados
                {!data?.supabase_configured && (
                  <span className="ml-2 text-yellow-600">• Supabase não configurado (dados mock)</span>
                )}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Exportar
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Quick Filters */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col lg:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Buscar por nome, email, telefone..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Select value={pageSize.toString()} onValueChange={(value) => setPageSize(Number(value))}>
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="25">25</SelectItem>
                    <SelectItem value="50">50</SelectItem>
                    <SelectItem value="100">100</SelectItem>
                  </SelectContent>
                </Select>
                <span className="text-sm text-gray-600">por página</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Advanced Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center text-lg">
              <Filter className="h-5 w-5 mr-2" />
              Filtros Avançados
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
              <div>
                <Label htmlFor="data_entrada_inicio">Data Entrada - Início</Label>
                <Input
                  id="data_entrada_inicio"
                  type="date"
                  value={filters.data_entrada_inicio}
                  onChange={(e) => handleFilterChange('data_entrada_inicio', e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="data_entrada_fim">Data Entrada - Fim</Label>
                <Input
                  id="data_entrada_fim"
                  type="date"
                  value={filters.data_entrada_fim}
                  onChange={(e) => handleFilterChange('data_entrada_fim', e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="data_acao_inicio">Data Ação - Início</Label>
                <Input
                  id="data_acao_inicio"
                  type="date"
                  value={filters.data_acao_inicio}
                  onChange={(e) => handleFilterChange('data_acao_inicio', e.target.value)}
                />
              </div>
              <div>
                <Label htmlFor="data_acao_fim">Data Ação - Fim</Label>
                <Input
                  id="data_acao_fim"
                  type="date"
                  value={filters.data_acao_fim}
                  onChange={(e) => handleFilterChange('data_acao_fim', e.target.value)}
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
                    <SelectItem value="Rio de Janeiro">Rio de Janeiro</SelectItem>
                    <SelectItem value="Campinas">Campinas</SelectItem>
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
                    <SelectItem value="Novo">Novo</SelectItem>
                    <SelectItem value="Em atendimento">Em atendimento</SelectItem>
                    <SelectItem value="Agendado">Agendado</SelectItem>
                    <SelectItem value="Visitou">Visitou</SelectItem>
                    <SelectItem value="Reservado">Reservado</SelectItem>
                    <SelectItem value="Vendido">Vendido</SelectItem>
                    <SelectItem value="Descartado">Descartado</SelectItem>
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
                    <SelectItem value="Facebook">Facebook</SelectItem>
                    <SelectItem value="Google">Google</SelectItem>
                    <SelectItem value="Instagram">Instagram</SelectItem>
                    <SelectItem value="Indicação">Indicação</SelectItem>
                    <SelectItem value="Site">Site</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="empreendimento">Empreendimento</Label>
                <Input
                  id="empreendimento"
                  placeholder="Nome do empreendimento"
                  value={filters.empreendimento}
                  onChange={(e) => handleFilterChange('empreendimento', e.target.value)}
                />
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

        {/* Leads Table */}
        <Card>
          <CardHeader>
            <CardTitle>Lista de Leads</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead 
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => handleSort('nome')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Nome</span>
                        {getSortIcon('nome')}
                      </div>
                    </TableHead>
                    <TableHead>Contato</TableHead>
                    <TableHead 
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => handleSort('cidade')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Cidade</span>
                        {getSortIcon('cidade')}
                      </div>
                    </TableHead>
                    <TableHead 
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => handleSort('data_entrada')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Data Entrada</span>
                        {getSortIcon('data_entrada')}
                      </div>
                    </TableHead>
                    <TableHead 
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => handleSort('data_acao')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Data Ação</span>
                        {getSortIcon('data_acao')}
                      </div>
                    </TableHead>
                    <TableHead 
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => handleSort('status')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Status</span>
                        {getSortIcon('status')}
                      </div>
                    </TableHead>
                    <TableHead 
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={() => handleSort('origem')}
                    >
                      <div className="flex items-center space-x-1">
                        <span>Origem</span>
                        {getSortIcon('origem')}
                      </div>
                    </TableHead>
                    <TableHead>Empreendimento</TableHead>
                    <TableHead>Corretor</TableHead>
                    <TableHead className="text-right">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredLeads.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={10} className="text-center py-8">
                        <p className="text-gray-500">
                          {searchTerm ? 'Nenhum lead encontrado para esta busca.' : 'Nenhum lead encontrado.'}
                        </p>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredLeads.map((lead) => (
                      <TableRow key={lead.id} className="hover:bg-gray-50">
                        <TableCell className="font-medium">{lead.nome}</TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <div>{lead.email}</div>
                            <div className="text-gray-500">{lead.telefone}</div>
                          </div>
                        </TableCell>
                        <TableCell>{lead.cidade}</TableCell>
                        <TableCell>{formatDate(lead.data_entrada)}</TableCell>
                        <TableCell>{formatDate(lead.data_acao)}</TableCell>
                        <TableCell>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(lead.status)}`}>
                            {lead.status}
                          </span>
                        </TableCell>
                        <TableCell>{lead.origem}</TableCell>
                        <TableCell>{lead.empreendimento}</TableCell>
                        <TableCell>{lead.corretor}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex items-center justify-end space-x-2">
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>

            {/* Pagination */}
            <div className="flex items-center justify-between mt-4">
              <div className="text-sm text-gray-600">
                Mostrando {filteredLeads.length} de {data?.pagination.total || 0} leads
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
                  disabled={!hasPrevPage}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Anterior
                </Button>
                <div className="flex items-center space-x-1">
                  {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                    const page = i
                    return (
                      <Button
                        key={page}
                        variant={currentPage === page ? "default" : "outline"}
                        size="sm"
                        onClick={() => setCurrentPage(page)}
                      >
                        {page + 1}
                      </Button>
                    )
                  })}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => prev + 1)}
                  disabled={!hasNextPage}
                >
                  Próximo
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

export default function Leads() {
  return (
    <ProtectedRoute>
      <RoleGuard allowedRoles={["marketing_rj", "marketing_sp", "admin", "mestre_do_universo"]}>
        <LeadsPage />
      </RoleGuard>
    </ProtectedRoute>
  )
}
