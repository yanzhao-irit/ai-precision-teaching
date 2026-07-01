import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { api } from '../services/api'
import { useLang } from '../i18n'
import type { Course } from '../types'

interface AppCtxValue {
  courses: Course[]
  courseName: (code: string) => string
  loadingMeta: boolean
  metaError: string | null
}

const AppCtx = createContext<AppCtxValue | null>(null)

export function AppProvider({ children }: { children: ReactNode }) {
  const { t } = useLang()
  const [courses, setCourses] = useState<Course[]>([])
  const [loadingMeta, setLoadingMeta] = useState(true)
  const [metaError, setMetaError] = useState<string | null>(null)

  useEffect(() => {
    api
      .courses()
      .then(setCourses)
      .catch((e) => setMetaError(e?.message || t.backendError))
      .finally(() => setLoadingMeta(false))
  }, [])

  const courseName = (code: string) =>
    courses.find((c) => c.course_code === code)?.course_name || code

  return (
    <AppCtx.Provider value={{ courses, courseName, loadingMeta, metaError }}>
      {children}
    </AppCtx.Provider>
  )
}

export function useApp(): AppCtxValue {
  const ctx = useContext(AppCtx)
  if (!ctx) throw new Error('useApp must be used within AppProvider')
  return ctx
}
