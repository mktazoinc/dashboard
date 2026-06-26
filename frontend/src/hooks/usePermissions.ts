import { useAuth } from '@/contexts/AuthContext'
import { hasPermission, hasRoleLevel, canAccessSystem, getAllowedCities } from '@/lib/rbac'

export function usePermissions() {
  const { user } = useAuth()

  const checkPermission = (permission: keyof typeof ROLE_PERMISSIONS[typeof user.role]) => {
    if (!user) return false
    return hasPermission(user.role, permission)
  }

  const checkRoleLevel = (requiredRole: typeof user.role) => {
    if (!user) return false
    return hasRoleLevel(user.role, requiredRole)
  }

  const checkSystemAccess = (system: 'finance' | 'marketing' | 'admin') => {
    if (!user) return false
    return canAccessSystem(user.role, system)
  }

  const getUserCities = () => {
    if (!user) return []
    return getAllowedCities(user.role)
  }

  const isMestreDoUniverso = () => {
    return user?.role === 'mestre_do_universo'
  }

  const isAdmin = () => {
    return user?.role === 'admin' || isMestreDoUniverso()
  }

  const isCommercial = () => {
    return user?.role.includes('comercial')
  }

  const isMarketing = () => {
    return user?.role.includes('marketing')
  }

  const isDirector = () => {
    return user?.role === 'diretoria'
  }

  const isRJ = () => {
    return user?.role.includes('rj')
  }

  const isSP = () => {
    return user?.role.includes('sp')
  }

  return {
    user,
    checkPermission,
    checkRoleLevel,
    checkSystemAccess,
    getUserCities,
    isMestreDoUniverso,
    isAdmin,
    isCommercial,
    isMarketing,
    isDirector,
    isRJ,
    isSP,
  }
}
