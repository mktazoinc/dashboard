'use client'

import { ReactNode } from 'react'
import { usePermissions } from '@/hooks/usePermissions'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { ShieldX } from 'lucide-react'

interface RoleGuardProps {
  children: ReactNode
  requiredRole?: string
  requiredPermission?: keyof typeof ROLE_PERMISSIONS[any]
  requiredSystem?: 'finance' | 'marketing' | 'admin'
  fallback?: ReactNode
}

export function RoleGuard({
  children,
  requiredRole,
  requiredPermission,
  requiredSystem,
  fallback,
}: RoleGuardProps) {
  const { checkRoleLevel, checkPermission, checkSystemAccess } = usePermissions()

  let hasAccess = true

  if (requiredRole) {
    hasAccess = checkRoleLevel(requiredRole as any)
  }

  if (hasAccess && requiredPermission) {
    hasAccess = checkPermission(requiredPermission)
  }

  if (hasAccess && requiredSystem) {
    hasAccess = checkSystemAccess(requiredSystem)
  }

  if (!hasAccess) {
    if (fallback) {
      return <>{fallback}</>
    }

    return (
      <div className="flex items-center justify-center min-h-96">
        <Alert variant="destructive" className="max-w-md">
          <ShieldX className="h-4 w-4" />
          <AlertDescription>
            Você não tem permissão para acessar esta página.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return <>{children}</>
}
