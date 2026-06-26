export type UserRole = 
  | 'comercial_rj'
  | 'comercial_sp'
  | 'marketing_rj'
  | 'marketing_sp'
  | 'diretoria'
  | 'admin'
  | 'mestre_do_universo'

export interface User {
  uid: string
  email: string
  displayName?: string
  role: UserRole
  customClaims?: {
    role: UserRole
    [key: string]: any
  }
}

export interface AuthState {
  user: User | null
  loading: boolean
  error: string | null
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface ResetPasswordData {
  email: string
}
