import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AppProvider, useApp } from './context/AppContext'
import { TopBar } from './components/TopBar'
import { Loading, ErrorBox } from './components/ui'
import CoursesPage from './pages/CoursesPage'
import CourseDetailPage from './pages/CourseDetailPage'
import QuestionPage from './pages/QuestionPage'
import KnowledgePointPage from './pages/KnowledgePointPage'
import StudentPage from './pages/StudentPage'

function Shell() {
  const { loadingMeta, metaError } = useApp()
  return (
    <div className="min-h-screen bg-gray-50">
      <TopBar />
      <main className="max-w-6xl mx-auto px-4 py-6">
        {loadingMeta ? (
          <Loading text="连接后端…" />
        ) : metaError ? (
          <ErrorBox message={metaError} />
        ) : (
          <Routes>
            <Route path="/" element={<CoursesPage />} />
            <Route path="/course/:code" element={<CourseDetailPage />} />
            <Route path="/course/:code/question/:id" element={<QuestionPage />} />
            <Route path="/course/:code/kp/:kpcode" element={<KnowledgePointPage />} />
            <Route path="/course/:code/student/:no" element={<StudentPage />} />
          </Routes>
        )}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <Shell />
      </AppProvider>
    </BrowserRouter>
  )
}
