import { useContext, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppProvider, useApp } from './context/AppContext'
import { AuthProvider, useAuth } from './context/AuthContext'
import { TopBar } from './components/TopBar'
import { Loading, ErrorBox } from './components/ui'
import CoursesPage from './pages/CoursesPage'
import CourseDetailPage from './pages/CourseDetailPage'
import QuestionPage from './pages/QuestionPage'
import KnowledgePointPage from './pages/KnowledgePointPage'
import StudentPage from './pages/StudentPage'
import LoginPage from './pages/LoginPage'
import ChangePasswordPage from './pages/ChangePasswordPage'
import StudentDashboard from './pages/student/StudentDashboard'
import { LangContext, translations, type Lang } from './i18n'

function useLangCtx() { return useContext(LangContext) }

/** Teacher portal shell (existing app). */
function TeacherShell() {
  const { loadingMeta, metaError } = useApp()
  const { t } = useLangCtx()
  return (
    <div className="min-h-screen bg-gray-50">
      <TopBar />
      <main className="max-w-6xl mx-auto px-4 py-6">
        {loadingMeta ? (
          <Loading text={t.connectingBackend} />
        ) : metaError ? (
          <ErrorBox message={metaError} />
        ) : (
          <Routes>
            <Route path="/" element={<CoursesPage />} />
            <Route path="/course/:code" element={<CourseDetailPage />} />
            <Route path="/course/:code/question/:id" element={<QuestionPage />} />
            <Route path="/course/:code/kp/:kpcode" element={<KnowledgePointPage />} />
            <Route path="/course/:code/student/:no" element={<StudentPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        )}
      </main>
    </div>
  )
}

/** Root router — decides which portal to show. */
function Root() {
  const { user, loading } = useAuth()

  if (loading) return <Loading text="正在验证身份…" />

  if (!user) return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )

  if (user.must_change_password) return (
    <Routes>
      <Route path="/change-password" element={<ChangePasswordPage />} />
      <Route path="*" element={<Navigate to="/change-password" replace />} />
    </Routes>
  )

  if (user.role === 'student') return (
    <Routes>
      <Route path="/student/*" element={<StudentDashboard />} />
      <Route path="*" element={<Navigate to="/student" replace />} />
    </Routes>
  )

  // teacher
  return (
    <AppProvider>
      <TeacherShell />
    </AppProvider>
  )
}

export default function App() {
  const [lang, setLang] = useState<Lang>(() => (localStorage.getItem('lang') as Lang) || 'zh')
  const t = translations[lang]
  const setLangPersist = (l: Lang) => { setLang(l); localStorage.setItem('lang', l) }

  return (
    <LangContext.Provider value={{ lang, setLang: setLangPersist, t }}>
      <BrowserRouter>
        <AuthProvider>
          <Root />
        </AuthProvider>
      </BrowserRouter>
    </LangContext.Provider>
  )
}
