import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
})

// Types
export interface Account {
  id: string
  label: string
  email: string | null
  gmail_slot: string | null
  source: string
  is_active: boolean
  created_at: string
}

export interface UsageRecord {
  id: string
  account_id: string
  source: string
  timestamp: string
  model_id: string
  model_label: string
  input_tokens: number
  output_tokens: number
  cache_tokens: number
  request_count: number
  cost_usd: number | null
  request_type: string | null
}

export interface UsageSummaryItem {
  day: string
  source: string
  model_id: string
  model_label: string
  input_tokens: number
  output_tokens: number
  cache_tokens: number
  request_count: number
  cost_usd: number
}

export interface AlertRule {
  id: string
  label: string
  account_id: string | null
  source: string | null
  model_id: string | null
  threshold_pct: number
  channel: string
  webhook_url: string | null
  cooldown_minutes: number
  is_active: boolean
  last_fired_at: string | null
}

export interface GeminiLimit {
  model_id: string
  model_label: string
  rpm: number
  tpm: number
  rpd: number
}

export interface DbStats {
  usage_records: number
  quota_snapshots: number
  accounts: number
  alert_rules: number
  gemini_configs: number
}

// Queries
export function useDashboardData() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const res = await api.get('/dashboard')
      return res.data
    },
    refetchInterval: 10000, // Refetch dashboard every 10s
  })
}

export function useAccounts() {
  return useQuery<{ accounts: Account[] }>({
    queryKey: ['accounts'],
    queryFn: async () => {
      const res = await api.get('/accounts')
      return res.data
    },
  })
}

export function useUsageHistory(filters: {
  source?: string
  account_id?: string
  model_id?: string
  start_date?: string
  end_date?: string
}) {
  return useQuery<{ records: UsageRecord[]; count: number }>({
    queryKey: ['usage', filters],
    queryFn: async () => {
      const res = await api.get('/usage', { params: filters })
      return res.data
    },
  })
}

export function useUsageSummary(filters: { source?: string; account_id?: string; days?: number }) {
  return useQuery<{ summary: UsageSummaryItem[] }>({
    queryKey: ['usage-summary', filters],
    queryFn: async () => {
      const res = await api.get('/usage/summary', { params: filters })
      return res.data
    },
  })
}

export function useAlerts() {
  return useQuery<{ alerts: AlertRule[] }>({
    queryKey: ['alerts'],
    queryFn: async () => {
      const res = await api.get('/alerts')
      return res.data
    },
  })
}

export function useGeminiLimits() {
  return useQuery<{ configs: GeminiLimit[] }>({
    queryKey: ['gemini-limits'],
    queryFn: async () => {
      const res = await api.get('/gemini/limits')
      return res.data
    },
  })
}

export function useDbStats() {
  return useQuery<DbStats>({
    queryKey: ['db-stats'],
    queryFn: async () => {
      const res = await api.get('/data/stats')
      return res.data
    },
  })
}

// Mutations
export function useImportCursorCsv() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post('/cursor/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usage'] })
      queryClient.invalidateQueries({ queryKey: ['usage-summary'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })
}

export function useAccountMutations() {
  const queryClient = useQueryClient()

  const create = useMutation({
    mutationFn: async (account: Omit<Account, 'created_at' | 'is_active'>) => {
      const res = await api.post('/accounts', account)
      return res.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['accounts'] }),
  })

  const update = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Account> }) => {
      const res = await api.put(`/accounts/${id}`, data)
      return res.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['accounts'] }),
  })

  const remove = useMutation({
    mutationFn: async (id: string) => {
      const res = await api.delete(`/accounts/${id}`)
      return res.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['accounts'] }),
  })

  const testConnection = useMutation({
    mutationFn: async (id: string) => {
      const res = await api.post(`/accounts/${id}/test`)
      return res.data
    },
  })

  return { create, update, remove, testConnection }
}

export function useAlertMutations() {
  const queryClient = useQueryClient()

  const create = useMutation({
    mutationFn: async (alert: Omit<AlertRule, 'id' | 'is_active' | 'last_fired_at'>) => {
      const res = await api.post('/alerts', alert)
      return res.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })

  const update = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<AlertRule> }) => {
      const res = await api.put(`/alerts/${id}`, data)
      return res.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })

  const remove = useMutation({
    mutationFn: async (id: string) => {
      const res = await api.delete(`/alerts/${id}`)
      return res.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['alerts'] }),
  })

  return { create, update, remove }
}

export function useGeminiLimitsMutation() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ model_id, data }: { model_id: string; data: Omit<GeminiLimit, 'model_id' | 'model_label'> }) => {
      const res = await api.put(`/gemini/limits/${model_id}`, data)
      return res.data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['gemini-limits'] }),
  })
}

export function useDataMutations() {
  const queryClient = useQueryClient()

  const purge = useMutation({
    mutationFn: async (days: number) => {
      const res = await api.post(`/data/purge?days=${days}`)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['db-stats'] })
      queryClient.invalidateQueries({ queryKey: ['usage'] })
      queryClient.invalidateQueries({ queryKey: ['usage-summary'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
  })

  return { purge }
}
