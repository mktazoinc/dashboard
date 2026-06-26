'use client'

import { useState, useEffect } from 'react'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { RoleGuard } from '@/components/RoleGuard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  Users, 
  Shield, 
  Settings, 
  Activity, 
  Plus,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Lock
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

interface SystemMetrics {
  total_users: number
  active_users: number
  logins_today: number
  logins_this_week: number
  systems_status: {
    finance: boolean
    marketing: boolean
    auth: boolean
    cache: boolean
    database: boolean
  }
  security_alerts: {
    failed_logins: number
    suspicious_activities: number
    blocked_ips: number
  }
  performance: {
    avg_response_time: number
    cpu_usage: number
    memory_usage: number
    disk_usage: number
  }
}

interface AdminData {
  user: string
  role: string
  metrics: SystemMetrics
  system_health: 'healthy' | 'warning' | 'critical'
  last_updated: string
}

function AdminPage() {
  const { user } = useAuth()
  const [data, setData] = useState<AdminData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'security' | 'system'>('overview')

  const fetchAdminData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      const token = await user?.getIdToken()
      if (!token) throw new Error('No authentication token')
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/admin/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      
      if (!response.ok) throw new Error('Failed to fetch admin data')
      const adminData = await response.json()
      setData(adminData)
      
    } catch (err) {
      console.error('Error fetching admin data:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (user) {
      fetchAdminData()
    }
  }, [user])

  const getSystemHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'text-green-600'
      case 'warning': return 'text-yellow-600'
      case 'critical': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getSystemHealthIcon = (health: string) => {
    switch (health) {
      case 'healthy': return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'warning': return <AlertTriangle className="h-5 w-5 text-yellow-600" />
      case 'critical': return <XCircle className="h-5 w-5 text-red-600" />
      default: return <Activity className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusIcon = (status: boolean) => {
    return status ? 
      <CheckCircle className="h-4 w-4 text-green-500" /> : 
      <XCircle className="h-4 w-4 text-red-500" />
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin text-azo-blue mx-auto mb-4" />
          <p className="text-gray-600">Carregando painel administrativo...</p>
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
            <Button onClick={fetchAdminData}>
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
              <h1 className="text-2xl font-bold text-azo-blue">Sistema 3 - Admin</h1>
              <p className="text-sm text-gray-600 flex items-center">
                {data?.user} • 
                <span className={`ml-2 flex items-center ${getSystemHealthColor(data?.system_health || 'unknown')}`}>
                  {getSystemHealthIcon(data?.system_health || 'unknown')}
                  <span className="ml-1">
                    {data?.system_health === 'healthy' ? 'Sistema Saudável' : 
                     data?.system_health === 'warning' ? 'Atenção' : 'Crítico'}
                  </span>
                </span>
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Novo Usuário
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Visão Geral' },
              { id: 'users', label: 'Usuários' },
              { id: 'security', label: 'Segurança' },
              { id: 'system', label: 'Sistema' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-azo-blue text-azo-blue'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div>
            {/* System Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Usuários Ativos</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics?.active_users || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    de {metrics?.total_users || 0} totais
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Logins Hoje</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics?.logins_today || 0}</div>
                  <p className="text-xs text-muted-foreground">
                    {metrics?.logins_this_week || 0} esta semana
                  </p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Alertas</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-yellow-600">
                    {(metrics?.security_alerts.failed_logins || 0) + 
                     (metrics?.security_alerts.suspicious_activities || 0)}
                  </div>
                  <p className="text-xs text-muted-foreground">Atividades suspeitas</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">CPU</CardTitle>
                  <Settings className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics?.performance.cpu_usage || 0}%</div>
                  <p className="text-xs text-muted-foreground">Uso de processador</p>
                </CardContent>
              </Card>
            </div>

            {/* System Status */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Status dos Sistemas</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Sistema Financeiro</span>
                      {getStatusIcon(metrics?.systems_status.finance || false)}
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Sistema Marketing</span>
                      {getStatusIcon(metrics?.systems_status.marketing || false)}
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Autenticação</span>
                      {getStatusIcon(metrics?.systems_status.auth || false)}
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Cache Redis</span>
                      {getStatusIcon(metrics?.systems_status.cache || false)}
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Database</span>
                      {getStatusIcon(metrics?.systems_status.database || false)}
                    </div>
                  </div>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Response Time</span>
                      <span className="text-sm">{metrics?.performance.avg_response_time || 0}ms</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Memória</span>
                      <span className="text-sm">{metrics?.performance.memory_usage || 0}%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">Disco</span>
                      <span className="text-sm">{metrics?.performance.disk_usage || 0}%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <Card>
            <CardHeader>
              <CardTitle>Gestão de Usuários</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Gestão de Usuários</h3>
                <p className="text-gray-500 mb-4">
                  Interface completa de gestão de usuários será implementada aqui
                </p>
                <Button>Gerenciar Usuários</Button>
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 'security' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="h-5 w-5 mr-2" />
                Segurança do Sistema
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <XCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
                      <div className="text-2xl font-bold">{metrics?.security_alerts.failed_logins || 0}</div>
                      <p className="text-sm text-gray-600">Logins Falhos</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
                      <div className="text-2xl font-bold">{metrics?.security_alerts.suspicious_activities || 0}</div>
                      <p className="text-sm text-gray-600">Atividades Suspeitas</p>
                    </div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center">
                      <Lock className="h-8 w-8 text-green-500 mx-auto mb-2" />
                      <div className="text-2xl font-bold">{metrics?.security_alerts.blocked_ips || 0}</div>
                      <p className="text-sm text-gray-600">IPs Bloqueados</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </CardContent>
          </Card>
        )}

        {activeTab === 'system' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="h-5 w-5 mr-2" />
                Informações do Sistema
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-medium mb-3">Recursos</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">CPU</span>
                      <span className="text-sm font-medium">{metrics?.performance.cpu_usage || 0}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Memória</span>
                      <span className="text-sm font-medium">{metrics?.performance.memory_usage || 0}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Disco</span>
                      <span className="text-sm font-medium">{metrics?.performance.disk_usage || 0}%</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-medium mb-3">Serviços</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">API Backend</span>
                      {getStatusIcon(true)}
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Frontend</span>
                      {getStatusIcon(true)}
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Database</span>
                      {getStatusIcon(metrics?.systems_status.database || false)}
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Redis Cache</span>
                      {getStatusIcon(metrics?.systems_status.cache || false)}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  )
}

export default function Admin() {
  return (
    <ProtectedRoute requireAuth={true}>
      <RoleGuard requiredSystem="admin">
        <AdminPage />
      </RoleGuard>
    </ProtectedRoute>
  )
}
