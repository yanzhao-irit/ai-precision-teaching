import { useEffect, useState } from 'react'
import { useAuth } from '../../context/AuthContext'
import { useLang } from '../../i18n'
import { Loading, ErrorBox } from '../../components/ui'
import type { Lang } from '../../i18n'

const BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

async function apiFetch(path: string) {
  const res = await fetch(`${BASE}${path}`, { credentials: 'include' })
  if (!res.ok) throw new Error(`API ${path} failed`)
  return res.json()
}

interface Course { course_code: string; course_name: string; term_code: string; class_name: string }
interface Dashboard {
  personal: {
    total_responses: number; correct: number; accuracy: number | null
    homework_score: number | null; final_score: number | null
    task_completed: number | null; task_total: number | null
    discussion_count: number | null; chapter_visit_count: number | null
  }
  class_avg: { accuracy: number | null; homework_score: number | null; final_score: number | null }
  weak_kps: { kp_code: string; label: string; total: number; correct: number; accuracy: number }[]
}

function pct(v: number | null | undefined) {
  return v == null ? '—' : `${Math.round(v * 100)}%`
}
function score(v: number | null | undefined) {
  return v == null ? '—' : v.toFixed(1)
}

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 flex flex-col gap-1">
      <span className="text-xs text-gray-400">{label}</span>
      <span className="text-2xl font-bold text-gray-800">{value}</span>
      {sub && <span className="text-xs text-gray-400">{sub}</span>}
    </div>
  )
}

function CompareBar({ label, me, avg }: { label: string; me: number | null; avg: number | null }) {
  const meP = (me ?? 0) * 100
  const avgP = (avg ?? 0) * 100
  return (
    <div className="mb-3">
      <div className="flex justify-between text-xs text-gray-500 mb-1">
        <span>{label}</span>
        <span>我 {pct(me)} · 均 {pct(avg)}</span>
      </div>
      <div className="relative h-3 bg-gray-100 rounded-full overflow-hidden">
        <div className="absolute inset-y-0 left-0 bg-blue-200 rounded-full" style={{ width: `${avgP}%` }} />
        <div className="absolute inset-y-0 left-0 bg-blue-500 rounded-full" style={{ width: `${meP}%` }} />
      </div>
    </div>
  )
}

export default function StudentDashboard() {
  const { logout } = useAuth()
  const { lang, setLang, t } = useLang()

  const [courses, setCourses] = useState<Course[]>([])
  const [selectedCode, setSelectedCode] = useState<string>('')
  const [dash, setDash] = useState<Dashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    apiFetch('/api/student/me/courses')
      .then((data: Course[]) => {
        setCourses(data)
        if (data.length > 0) setSelectedCode(data[0].course_code)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (!selectedCode) return
    setDash(null)
    apiFetch(`/api/student/me/dashboard?course_code=${selectedCode}`)
      .then(setDash)
      .catch(e => setError(e.message))
  }, [selectedCode])

  if (loading) return <Loading text={t.connectingBackend} />
  if (error) return <ErrorBox message={error} />

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-100 px-6 py-3 flex items-center justify-between">
        <span className="font-semibold text-gray-800">AI 精准教学 · 学生空间</span>
        <div className="flex items-center gap-3">
          {courses.length > 1 && (
            <select
              value={selectedCode}
              onChange={e => setSelectedCode(e.target.value)}
              className="text-sm border border-gray-200 rounded-lg px-2 py-1 focus:outline-none"
            >
              {courses.map(c => (
                <option key={c.course_code} value={c.course_code}>
                  {c.course_name} ({c.term_code})
                </option>
              ))}
            </select>
          )}
          <div className="flex items-center gap-1 text-sm">
            {(['zh', 'en'] as Lang[]).map(l => (
              <button key={l} onClick={() => setLang(l)}
                className={`px-2 py-0.5 rounded-md transition ${lang === l ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-gray-800'}`}>
                {l === 'zh' ? '中文' : 'EN'}
              </button>
            ))}
          </div>
          <button
            onClick={logout}
            className="text-sm text-gray-400 hover:text-red-500 transition-colors"
          >
            {t.logout ?? '退出'}
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {courses.length === 0 && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center text-yellow-700">
            暂无课程数据，请联系老师上传班级名单。
          </div>
        )}

        {dash && (
          <>
            {/* Stats grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <StatCard label={t.accuracy ?? '正确率'} value={pct(dash.personal.accuracy)} sub={`${dash.personal.correct}/${dash.personal.total_responses}`} />
              <StatCard label={t.homeworkScore ?? '作业分'} value={score(dash.personal.homework_score)} />
              <StatCard label={t.finalScore ?? '期末分'} value={score(dash.personal.final_score)} />
              <StatCard
                label={t.tasks ?? '任务进度'}
                value={dash.personal.task_total ? `${dash.personal.task_completed ?? 0}/${dash.personal.task_total}` : '—'}
              />
            </div>

            {/* Class comparison */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
              <h2 className="font-semibold text-gray-700 mb-4">{t.classComparison ?? '与班级均值对比'}</h2>
              <CompareBar label={t.accuracy ?? '正确率'} me={dash.personal.accuracy} avg={dash.class_avg.accuracy} />
              <CompareBar label={t.homeworkScore ?? '作业分（÷100）'} me={(dash.personal.homework_score ?? 0) / 100} avg={(dash.class_avg.homework_score ?? 0) / 100} />
              <CompareBar label={t.finalScore ?? '期末分（÷100）'} me={(dash.personal.final_score ?? 0) / 100} avg={(dash.class_avg.final_score ?? 0) / 100} />
            </div>

            {/* Weak KPs */}
            {dash.weak_kps.length > 0 && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
                <h2 className="font-semibold text-gray-700 mb-4">{t.weakKPs ?? '薄弱知识点'}</h2>
                <div className="space-y-3">
                  {dash.weak_kps.map(kp => (
                    <div key={kp.kp_code} className="flex items-center gap-3">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-700 truncate">{kp.label}</p>
                        <p className="text-xs text-gray-400">{kp.kp_code} · {kp.correct}/{kp.total}</p>
                      </div>
                      <div className="w-24">
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-red-400 rounded-full"
                            style={{ width: `${Math.round((kp.accuracy ?? 0) * 100)}%` }}
                          />
                        </div>
                        <p className="text-xs text-right text-red-500 mt-0.5">{pct(kp.accuracy)}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
