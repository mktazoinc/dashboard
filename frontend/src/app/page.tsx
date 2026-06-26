'use client'

import { useAuth } from '@/contexts/AuthContext'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { LogOut, Building2, TrendingUp, Users, Settings } from 'lucide-react'
import Link from 'next/link'

function HomePage() {
  const { user, logout } = useAuth()

  const handleLogout = async () => {
    try {
      await logout()
    } catch (error) {
      console.error('Error logging out:', error)
    }
  }

  const getAvailableSystems = () => {
    if (!user) return []
    
    const systems = []
    
    // Sistema 1 - Financeiro e Vendas
    if (['comercial_rj', 'comercial_sp', 'diretoria', 'admin', 'mestre_do_universo'].includes(user.role)) {
      systems.push({
        id: 'financeiro',
        title: 'Sistema 1',
        subtitle: 'Financeiro e Vendas',
        icon: Building2,
        color: 'bg-blue-500',
      })
    }
    
    // Sistema 2 - Marketing
    if (['marketing_rj', 'marketing_sp', 'admin', 'mestre_do_universo'].includes(user.role)) {
      systems.push({
        id: 'marketing',
        title: 'Sistema 2',
        subtitle: 'Marketing',
        icon: TrendingUp,
        color: 'bg-green-500',
      })
    }
    
    // Admin
    if (['admin', 'mestre_do_universo'].includes(user.role)) {
      systems.push({
        id: 'admin',
        title: 'Admin',
        subtitle: 'Administração',
        icon: Settings,
        color: 'bg-purple-500',
      })
    }
    
    return systems
  }

  const systems = getAvailableSystems()

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-2xl font-bold text-azo-blue">Dashboard AZO</h1>
              <p className="text-sm text-gray-600">
                Bem-vindo, {user?.email} • Role: {user?.role}
              </p>
            </div>
            <Button onClick={handleLogout} variant="outline" size="sm">
              <LogOut className="h-4 w-4 mr-2" />
              Sair
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Home</h2>
          <p className="text-gray-600 mt-2">
            Selecione o sistema que deseja acessar
          </p>
        </div>

        {systems.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Users className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Acesso Restrito
              </h3>
              <p className="text-gray-600 text-center">
                Você não tem permissão para acessar nenhum sistema no momento.
                Entre em contato com o administrador.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {systems.map((system) => {
              const Icon = system.icon
              return (
                <Card key={system.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                  <CardHeader className="text-center">
                    <div className={`w-16 h-16 ${system.color} rounded-full flex items-center justify-center mx-auto mb-4`}>
                      <Icon className="h-8 w-8 text-white" />
                    </div>
                    <CardTitle className="text-xl">{system.title}</CardTitle>
                    <CardDescription>{system.subtitle}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Link href={`/${system.id === 'financeiro' ? 'finance' : system.id === 'marketing' ? 'marketing' : 'admin'}`}>
                      <Button className="w-full" variant="outline">
                        Acessar Sistema
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </main>
    </div>
  )
}

export default function Home() {
  return (
    <ProtectedRoute requireAuth={true}>
      <HomePage />
    </ProtectedRoute>
  )
}
