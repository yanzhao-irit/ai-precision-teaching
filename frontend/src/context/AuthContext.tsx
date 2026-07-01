import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

export type Role = 'teacher' | 'student'

export interface AuthUser {
  user_id: number
  login: string
  role: Role
  student_id: number | null
  must_change_password: boolean
}

interface AuthCtx {
  user: AuthUser | null
  loading: boolean
  login: (loginStr: string, password: string) => Promise<void>
  logout: () => Promise<void>
  refresh: () => Promise<void>
}

const AuthContext = createContext<AuthCtx>({
  user: null, loading: true,
  login: async () => {}, logout: async () => {}, refresh: async () => {},
})

export function useAuth() { return useContext(AuthContext) }

const BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

async function apiFetch(path: string, init?: RequestInit) {
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  return res
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = async () => {
    try {
      const res = await apiFetch('/auth/me')
      if (res.ok) setUser(await res.json())
      else setUser(null)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { refresh() }, [])

  const login = async (loginStr: string, password: string) => {
    const res = await apiFetch('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ login: loginStr, password }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail ?? 'Identifiants invalides')
    }
    setUser(await res.json())
  }

  const logout = async () => {
    await apiFetch('/auth/logout', { method: 'POST' })
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  )
}
