import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../services/api'
import { useAsync } from '../hooks/useAsync'
import { Card, Loading, ErrorBox, Empty, pct, masteryColor } from '../components/ui'
import { useLang } from '../i18n'

export default function CoursesPage() {
  const nav = useNavigate()
  const { t } = useLang()
  const [reload, setReload] = useState(0)
  const { data, loading, error } = useAsync(() => api.courseSummaries(), [reload])

  const [open, setOpen] = useState(false)
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  async function create() {
    if (!code.trim() || !name.trim()) { setErr(t.courseCodeNameRequired); return }
    setBusy(true); setErr('')
    try {
      const c = await api.createCourse(code.trim(), name.trim())
      setReload((x) => x + 1)
      nav(`/course/${c.course_code}`)
    } catch (e: unknown) {
      const x = e as { response?: { data?: { detail?: string } }; message?: string }
      setErr(x?.response?.data?.detail || x?.message || t.createError)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">{t.myCourses}</h2>
        <button
          onClick={() => setOpen((v) => !v)}
          className="px-3 py-1.5 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700"
        >
          {t.newCourse}
        </button>
      </div>

      {open && (
        <Card>
          <div className="flex flex-wrap items-center gap-3">
            <input
              value={code} onChange={(e) => setCode(e.target.value)}
              placeholder={t.courseCodePlaceholder}
              className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm w-60"
            />
            <input
              value={name} onChange={(e) => setName(e.target.value)}
              placeholder={t.courseNamePlaceholder}
              className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm w-60"
            />
            <button
              onClick={create} disabled={busy}
              className="px-4 py-1.5 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {busy ? t.creating : t.createAndEnter}
            </button>
            {err && <span className="text-sm text-red-600">{err}</span>}
          </div>
          <p className="text-xs text-gray-400 mt-2">{t.createHint}</p>
        </Card>
      )}

      {loading ? <Loading /> : error ? <ErrorBox message={error} /> :
        !data || data.length === 0 ? <Empty text={t.noCourses} /> : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.map((c) => (
              <Card key={c.course_code} className="cursor-pointer hover:shadow-md transition">
                <div onClick={() => nav(`/course/${c.course_code}`)}>
                  <div className="flex items-start justify-between">
                    <div className="text-base font-semibold text-gray-900">{c.course_name}</div>
                    <span className="text-xs text-gray-400">{c.term_code || ''}</span>
                  </div>
                  <div className="text-xs text-gray-400 mb-4">{c.course_code}</div>
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div><div className="text-xl font-bold text-gray-900">{c.student_count}</div><div className="text-xs text-gray-500">{t.students}</div></div>
                    <div><div className="text-xl font-bold text-gray-900">{c.class_count}</div><div className="text-xs text-gray-500">{t.classes}</div></div>
                    <div><div className="text-xl font-bold text-gray-900">{c.chapter_count}</div><div className="text-xs text-gray-500">{t.testedChapters}</div></div>
                  </div>
                  <div className="mt-4 flex items-center justify-between">
                    <span className="text-xs text-gray-500">{t.overallAccuracy}</span>
                    <span className="text-sm font-semibold" style={{ color: masteryColor(c.accuracy) }}>{pct(c.accuracy)}</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
    </div>
  )
}
