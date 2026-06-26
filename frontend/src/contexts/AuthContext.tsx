'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { 
  User as FirebaseUser,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  sendPasswordResetEmail,
  onAuthStateChanged,
  getIdTokenResult
} from 'firebase/auth'
import { auth } from '@/lib/firebase'
import { User, AuthState, UserRole } from '@/types/auth'

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  resetPassword: (email: string) => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: true,
    error: null,
  })

  const mapFirebaseUser = async (firebaseUser: FirebaseUser): Promise<User> => {
    const tokenResult = await getIdTokenResult(firebaseUser)
    const role = tokenResult.claims.role as UserRole || 'comercial_rj'

    return {
      uid: firebaseUser.uid,
      email: firebaseUser.email!,
      displayName: firebaseUser.displayName || undefined,
      role,
      customClaims: tokenResult.claims,
    }
  }

  const login = async (email: string, password: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }))
    
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password)
      const user = await mapFirebaseUser(userCredential.user)
      setState({ user, loading: false, error: null })
    } catch (error: any) {
      const errorMessage = error.message || 'Erro ao fazer login'
      setState(prev => ({ ...prev, loading: false, error: errorMessage }))
      throw error
    }
  }

  const logout = async () => {
    setState(prev => ({ ...prev, loading: true }))
    
    try {
      await firebaseSignOut(auth)
      setState({ user: null, loading: false, error: null })
    } catch (error: any) {
      const errorMessage = error.message || 'Erro ao fazer logout'
      setState(prev => ({ ...prev, loading: false, error: errorMessage }))
      throw error
    }
  }

  const resetPassword = async (email: string) => {
    try {
      await sendPasswordResetEmail(auth, email)
    } catch (error: any) {
      const errorMessage = error.message || 'Erro ao enviar email de recuperação'
      setState(prev => ({ ...prev, error: errorMessage }))
      throw error
    }
  }

  const refreshUser = async () => {
    if (auth.currentUser) {
      const user = await mapFirebaseUser(auth.currentUser)
      setState(prev => ({ ...prev, user }))
    }
  }

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        try {
          const user = await mapFirebaseUser(firebaseUser)
          setState({ user, loading: false, error: null })
        } catch (error) {
          setState({ user: null, loading: false, error: 'Erro ao carregar usuário' })
        }
      } else {
        setState({ user: null, loading: false, error: null })
      }
    })

    return unsubscribe
  }, [])

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        logout,
        resetPassword,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
