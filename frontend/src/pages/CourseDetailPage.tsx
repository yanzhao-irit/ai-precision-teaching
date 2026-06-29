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

type Tab = 'overview' | 'diagnosis' | 'students'

const TABS: { key: Tab; label: string }[] = [
  { key: 'overview', label: '概览' },
  { key: 'diagnosis', label: '学情' },
  { key: 'students', label: '学生' },
]

export default function CourseDetailPage() {
  const { code = '' } = useParams()
  const { courseName } = useApp()
  const [sp, setSp] = useSearchParams()
  const className = sp.get('class') || ''
  const [tab, setTab] = useState<Tab>('overview')
  const [showUpload, setShowUpload] = useState(false)
  const [reloadKey, setReloadKey] = useState(0)

  const classes = useAsync(() => api.classes(code), [code, reloadKey])

  const setClassName = (c: string) => {
    const n = new URLSearchParams(sp)
    if (c) n.set('class', c)
    else n.delete('class')
    setSp(n)
  }

  return (
    <div className="space-y-5">
      {/* 面包屑 + 标题 + 班级筛选 + 导入 */}
      <div className="flex flex-wrap items-center gap-3">
        <Link to="/" className="text-sm text-blue-600 hover:underline">课程列表</Link>
        <span className="text-gray-300">/</span>
        <h2 className="text-lg font-semibold text-gray-800">{courseName(code)}</h2>
        <div className="ml-auto flex items-center gap-2">
          <select
            value={className}
            onChange={(e) => setClassName(e.target.value)}
            className="border border-gray-300 rounded-lg px-2 py-1.5 text-sm min-w-[140px]"
          >
            <option value="">全部班级</option>
            {(classes.data || []).map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <button
            onClick={() => setShowUpload((v) => !v)}
            className="px-3 py-1.5 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            导入数据
          </button>
        </div>
      </div>

      {showUpload && (
        <Card>
          <UploadPanel courseCode={code} onDone={() => setReloadKey((x) => x + 1)} />
          <p className="text-xs text-gray-400 mt-3">文件将归入当前课程「{courseName(code)}」，无需填写课程代码。导入后页面数据自动刷新。</p>
        </Card>
      )}

      {/* Tab 切换 */}
      <div className="flex gap-1 border-b border-gray-200">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm font-medium -mb-px border-b-2 transition ${
              tab === t.key
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'overview' && <OverviewTab courseCode={code} className={className} reloadKey={reloadKey} />}
      {tab === 'diagnosis' && <DiagnosisTab courseCode={code} className={className} reloadKey={reloadKey} />}
      {tab === 'students' && <StudentsTab courseCode={code} className={className} reloadKey={reloadKey} />}
    </div>
  )
}
