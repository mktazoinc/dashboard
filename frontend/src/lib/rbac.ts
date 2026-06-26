import { UserRole } from '@/types/auth'

// Role hierarchy for permission checking
export const ROLE_HIERARCHY: Record<UserRole, number> = {
  comercial_rj: 1,
  comercial_sp: 1,
  marketing_rj: 1,
  marketing_sp: 1,
  diretoria: 2,
  admin: 3,
  mestre_do_universo: 4,
}

// Role permissions
export const ROLE_PERMISSIONS: Record<UserRole, {
  canAccessFinance: boolean
  canAccessMarketing: boolean
  canAccessAdmin: boolean
  canManageUsers: boolean
  canViewAllCities: boolean
}> = {
  comercial_rj: {
    canAccessFinance: true,
    canAccessMarketing: false,
    canAccessAdmin: false,
    canManageUsers: false,
    canViewAllCities: false,
  },
  comercial_sp: {
    canAccessFinance: true,
    canAccessMarketing: false,
    canAccessAdmin: false,
    canManageUsers: false,
    canViewAllCities: false,
  },
  marketing_rj: {
    canAccessFinance: false,
    canAccessMarketing: true,
    canAccessAdmin: false,
    canManageUsers: false,
    canViewAllCities: false,
  },
  marketing_sp: {
    canAccessFinance: false,
    canAccessMarketing: true,
    canAccessAdmin: false,
    canManageUsers: false,
    canViewAllCities: false,
  },
  diretoria: {
    canAccessFinance: true,
    canAccessMarketing: false,
    canAccessAdmin: false,
    canManageUsers: false,
    canViewAllCities: true,
  },
  admin: {
    canAccessFinance: true,
    canAccessMarketing: true,
    canAccessAdmin: true,
    canManageUsers: true,
    canViewAllCities: true,
  },
  mestre_do_universo: {
    canAccessFinance: true,
    canAccessMarketing: true,
    canAccessAdmin: true,
    canManageUsers: true,
    canViewAllCities: true,
  },
}

export function hasPermission(userRole: UserRole, permission: keyof typeof ROLE_PERMISSIONS[UserRole]): boolean {
  return ROLE_PERMISSIONS[userRole][permission]
}

export function hasRoleLevel(userRole: UserRole, requiredRole: UserRole): boolean {
  return ROLE_HIERARCHY[userRole] >= ROLE_HIERARCHY[requiredRole]
}

export function canAccessSystem(userRole: UserRole, system: 'finance' | 'marketing' | 'admin'): boolean {
  switch (system) {
    case 'finance':
      return ROLE_PERMISSIONS[userRole].canAccessFinance
    case 'marketing':
      return ROLE_PERMISSIONS[userRole].canAccessMarketing
    case 'admin':
      return ROLE_PERMISSIONS[userRole].canAccessAdmin
    default:
      return false
  }
}

export function getAllowedCities(userRole: UserRole): string[] {
  if (ROLE_PERMISSIONS[userRole].canViewAllCities) {
    return ['Rio de Janeiro', 'Campinas']
  }
  
  if (userRole.includes('rj')) {
    return ['Rio de Janeiro']
  }
  
  if (userRole.includes('sp')) {
    return ['Campinas']
  }
  
  return []
}
