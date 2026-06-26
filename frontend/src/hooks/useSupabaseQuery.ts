import { useState, useEffect } from 'react'
import { supabase } from '@/lib/supabase-mock'

interface UseSupabaseQueryOptions {
  table: string
  select?: string
  filters?: Array<{ column: string; operator: string; value: any }>
  inFilters?: Array<{ column: string; values: any[] }>
  limit?: number
  order?: { column: string; ascending?: boolean }
  enabled?: boolean
}

export function useSupabaseQuery<T = any>(options: UseSupabaseQueryOptions) {
  const [data, setData] = useState<T[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const {
    table,
    select = '*',
    filters = [],
    inFilters = [],
    limit,
    order,
    enabled = true
  } = options

  const fetchData = async () => {
    if (!enabled) return

    setLoading(true)
    setError(null)

    try {
      let query = supabase.from(table).select(select)

      // Apply filters
      filters.forEach(filter => {
        const { column, operator, value } = filter
        switch (operator) {
          case 'eq':
            query = query.eq(column, value)
            break
          case 'gte':
            query = query.gte(column, value)
            break
          case 'lte':
            query = query.lte(column, value)
            break
          case 'ilike':
            query = query.ilike(column, value)
            break
          case 'in':
            query = query.in(column, value)
            break
        }
      })

      // Apply IN filters
      inFilters.forEach(inFilter => {
        const { column, values } = inFilter
        query = query.in(column, values)
      })

      // Apply ordering
      if (order) {
        query = query.order(order.column, { ascending: order.ascending ?? true })
      }

      // Apply limit
      if (limit) {
        query = query.limit(limit)
      }

      const result = await query

      if (result.error) {
        setError(result.error)
      } else {
        setData(result.data || [])
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [table, select, JSON.stringify(filters), JSON.stringify(inFilters), limit, JSON.stringify(order), enabled])

  return {
    data,
    loading,
    error,
    refetch: fetchData
  }
}

// Hook específico para leads
export function useLeads(filters?: {
  cidade?: string
  status?: string
  data_entrada_inicio?: string
  data_entrada_fim?: string
  data_acao_inicio?: string
  data_acao_fim?: string
}) {
  const queryFilters: Array<{ column: string; operator: string; value: any }> = []

  if (filters?.cidade) {
    queryFilters.push({ column: 'cidade', operator: 'eq', value: filters.cidade })
  }

  if (filters?.status) {
    queryFilters.push({ column: 'status', operator: 'eq', value: filters.status })
  }

  if (filters?.data_entrada_inicio) {
    queryFilters.push({ column: 'data_entrada', operator: 'gte', value: filters.data_entrada_inicio })
  }

  if (filters?.data_entrada_fim) {
    queryFilters.push({ column: 'data_entrada', operator: 'lte', value: filters.data_entrada_fim })
  }

  if (filters?.data_acao_inicio) {
    queryFilters.push({ column: 'data_acao', operator: 'gte', value: filters.data_acao_inicio })
  }

  if (filters?.data_acao_fim) {
    queryFilters.push({ column: 'data_acao', operator: 'lte', value: filters.data_acao_fim })
  }

  return useSupabaseQuery({
    table: 'leads',
    filters: queryFilters,
    order: { column: 'data_entrada', ascending: false }
  })
}

// Hook específico para empreendimentos
export function useEmpreendimentos() {
  return useSupabaseQuery({
    table: 'empreendimentos',
    order: { column: 'nome', ascending: true }
  })
}

// Hook específico para corretores
export function useCorretores() {
  return useSupabaseQuery({
    table: 'corretores',
    order: { column: 'nome', ascending: true }
  })
}

// Hook específico para dados de marketing
export function useMarketingData(filters?: {
  canal?: string
  cidade?: string
  data_inicio?: string
  data_fim?: string
}) {
  const queryFilters: Array<{ column: string; operator: string; value: any }> = []

  if (filters?.canal) {
    queryFilters.push({ column: 'canal', operator: 'eq', value: filters.canal })
  }

  if (filters?.cidade) {
    queryFilters.push({ column: 'cidade', operator: 'eq', value: filters.cidade })
  }

  if (filters?.data_inicio) {
    queryFilters.push({ column: 'data', operator: 'gte', value: filters.data_inicio })
  }

  if (filters?.data_fim) {
    queryFilters.push({ column: 'data', operator: 'lte', value: filters.data_fim })
  }

  return useSupabaseQuery({
    table: 'marketing_data',
    filters: queryFilters,
    order: { column: 'data', ascending: false }
  })
}
