import { useState } from 'react'
import { useParams, useSearchParams, Link } from 'react-router-dom'
import { api } from '../services/api'
import { useApp } from '../context/AppContext'
import { useAsync } from '../hooks/useAsync'
import { Card } from '../components/ui'
import UploadPanel from '../components/UploadPanel'
import OverviewTab from './course/OverviewTab'
import DiagnosisTab from './course/DiagnosisTab'
import StudentsTab from './course/StudentsTab'
import { useLang } from '../i18n'

type Tab = 'overview' | 'diagnosis' | 'students'

export default function CourseDetailPage() {
  const { code = '' } = useParams()
  const { courseName } = useApp()
  const { t } = useLang()
  const [sp, setSp] = useSearchParams()
  const className = sp.get('class') || ''
  const [tab, setTab] = useState<Tab>('overview')
  const [showUpload, setShowUpload] = useState(false)
  const [reloadKey, setReloadKey] = useState(0)

  const classes = useAsync(() => api.classes(code), [code, reloadKey])

  const TABS: { key: Tab; label: string }[] = [
    { key: 'overview', label: t.tabOverview },
    { key: 'diagnosis', label: t.tabDiagnosis },
    { key: 'students', label: t.tabStudents },
  ]

  const setClassName = (c: string) => {
    const n = new URLSearchParams(sp)
    if (c) n.set('class', c)
    else n.delete('class')
    setSp(n)
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center gap-3">
        <Link to="/" className="text-sm text-blue-600 hover:underline">{t.courseList}</Link>
        <span className="text-gray-300">/</span>
        <h2 className="text-lg font-semibold text-gray-800">{courseName(code)}</h2>
        <div className="ml-auto flex items-center gap-2">
          <select
            value={className}
            onChange={(e) => setClassName(e.target.value)}
            className="border border-gray-300 rounded-lg px-2 py-1.5 text-sm min-w-[140px]"
          >
            <option value="">{t.allClasses}</option>
            {(classes.data || []).map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <button
            onClick={() => setShowUpload((v) => !v)}
            className="px-3 py-1.5 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            {t.importData}
          </button>
        </div>
      </div>

      {showUpload && (
        <Card>
          <UploadPanel courseCode={code} onDone={() => setReloadKey((x) => x + 1)} />
          <p className="text-xs text-gray-400 mt-3">{t.importHint(courseName(code))}</p>
        </Card>
      )}

      <div className="flex gap-1 border-b border-gray-200">
        {TABS.map((tab_) => (
          <button
            key={tab_.key}
            onClick={() => setTab(tab_.key)}
            className={`px-4 py-2 text-sm font-medium -mb-px border-b-2 transition ${
              tab === tab_.key
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {tab_.label}
          </button>
        ))}
      </div>

      {tab === 'overview' && <OverviewTab courseCode={code} className={className} reloadKey={reloadKey} />}
      {tab === 'diagnosis' && <DiagnosisTab courseCode={code} className={className} reloadKey={reloadKey} />}
      {tab === 'students' && <StudentsTab courseCode={code} className={className} reloadKey={reloadKey} />}
    </div>
  )
}
