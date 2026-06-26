'use client'

import { useState, useEffect } from 'react'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RoleGuard } from '@/components/RoleGuard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Building2, TrendingUp, DollarSign, Home, Users, Target, Activity } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

interface DashboardMetrics {
  meta_anual_vgv: number
  vgv_em_estoque: number
  realizado_vgv: number
  unidades_vendidas: number
  vso_meta: number
  vso_estoque: number
  vso_realizado: number
}

interface Enterprise {
  id: string
  name: string
  city: string
}

function FinancePage() {
  const { user } = useAuth()
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [enterprises, setEnterprises] = useState<Enterprise[]>([])
  const [selectedEnterprise, setSelectedEnterprise] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
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
      
      // Fetch enterprises first
      const enterprisesResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/finance/enterprises`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (!enterprisesResponse.ok) throw new Error('Failed to fetch enterprises')
      const enterprisesData = await enterprisesResponse.json()
      setEnterprises(enterprisesData.enterprises || [])
      
      // Fetch dashboard metrics
      const dashboardParams = new URLSearchParams()
      if (selectedEnterprise) dashboardParams.append('enterprise_id', selectedEnterprise)
      
      const dashboardResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/finance/dashboard?${dashboardParams}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (!dashboardResponse.ok) throw new Error('Failed to fetch dashboard data')
      const dashboardData = await dashboardResponse.json()
      setMetrics(dashboardData.metrics)
      
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
  }, [user, selectedEnterprise])

  const vsoCompletionPercentage = metrics ? (metrics.vso_realizado / metrics.vso_meta) * 100 : 0
  const vgvCompletionPercentage = metrics ? (metrics.realizado_vgv / metrics.meta_anual_vgv) * 100 : 0

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin text-azo-blue mx-auto mb-4" />
          <p className="text-gray-600">Carregando dados financeiros...</p>
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
            <button 
              onClick={fetchDashboardData}
              className="px-4 py-2 bg-azo-blue text-white rounded hover:bg-azo-blue/90"
            >
              Tentar novamente
            </button>
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
              <h1 className="text-2xl font-bold text-azo-blue">Sistema 1 - Financeiro e Vendas</h1>
              <p className="text-sm text-gray-600">
                {user?.email} • {metrics?.city || 'Todas as cidades'}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Select value={selectedEnterprise} onValueChange={setSelectedEnterprise}>
                <SelectTrigger className="w-64">
                  <SelectValue placeholder="Todos os empreendimentos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos os empreendimentos</SelectItem>
                  {enterprises.map((enterprise) => (
                    <SelectItem key={enterprise.id} value={enterprise.id}>
                      {enterprise.name} ({enterprise.city})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Big Numbers */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Meta Anual (VGV)</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(metrics?.meta_anual_vgv || 0)}</div>
              <p className="text-xs text-muted-foreground">Meta anual de vendas</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">VGV em Estoque</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(metrics?.vgv_em_estoque || 0)}</div>
              <p className="text-xs text-muted-foreground">Valor disponível</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Realizado (VGV)</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(metrics?.realizado_vgv || 0)}</div>
              <p className="text-xs text-muted-foreground">
                {vgvCompletionPercentage.toFixed(1)}% da meta
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Unidades Vendidas</CardTitle>
              <Home className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.unidades_vendidas || 0}</div>
              <p className="text-xs text-muted-foreground">Total no período</p>
            </CardContent>
          </Card>
        </div>

        {/* VSO Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">VSO Meta</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatPercentage(metrics?.vso_meta || 0)}</div>
              <p className="text-xs text-muted-foreground">Meta de vendas sobre estoque</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">VSO Realizado</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatPercentage(metrics?.vso_realizado || 0)}</div>
              <p className="text-xs text-muted-foreground">
                {vsoCompletionPercentage.toFixed(1)}% da meta
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">VSO Estoque</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{formatCurrency(metrics?.vso_estoque || 0)}</div>
              <p className="text-xs text-muted-foreground">Valor total em estoque</p>
            </CardContent>
          </Card>
        </div>

        {/* Progress Bars */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Progresso Meta Anual (VGV)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Realizado</span>
                  <span>{vgvCompletionPercentage.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-azo-blue h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(vgvCompletionPercentage, 100)}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-600">
                  <span>{formatCurrency(metrics?.realizado_vgv || 0)}</span>
                  <span>{formatCurrency(metrics?.meta_anual_vgv || 0)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Progresso VSO</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Realizado</span>
                  <span>{vsoCompletionPercentage.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${Math.min(vsoCompletionPercentage, 100)}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-gray-600">
                  <span>{formatPercentage(metrics?.vso_realizado || 0)}</span>
                  <span>{formatPercentage(metrics?.vso_meta || 0)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

export default function Finance() {
  return (
    <ProtectedRoute requireAuth={true}>
      <RoleGuard requiredSystem="finance">
        <FinancePage />
      </RoleGuard>
    </ProtectedRoute>
  )
}
