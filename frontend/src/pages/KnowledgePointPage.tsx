import { useParams, useNavigate, useSearchParams } from 'react-router-dom'
import { api } from '../services/api'
import { useAsync } from '../hooks/useAsync'
import {
  Card, Stat, Loading, ErrorBox, Empty, Badge, SectionTitle,
  TIER_CN, pct, masteryColor, tierKind,
} from '../components/ui'

export default function KnowledgePointPage() {
  const { code = '', kpcode } = useParams()
  const [sp] = useSearchParams()
  const className = sp.get('class') || ''
  const q = className ? `?class=${encodeURIComponent(className)}` : ''
  const nav = useNavigate()
  const { data, loading, error } = useAsync(
    () => api.kpDrill(code, kpcode!, className),
    [code, className, kpcode],
  )

  if (loading) return <Loading />
  if (error) return <ErrorBox message={error} />
  if (!data) return <Empty text="知识点不存在。" />

  const weak = data.students.filter((s) => (s.accuracy ?? 1) < 0.6)

  return (
    <div className="space-y-5">
      <button onClick={() => nav(-1)} className="text-sm text-blue-600 hover:underline">← 返回</button>

      <div className="flex items-center gap-2">
        <h2 className="text-lg font-semibold text-gray-800">{data.label}</h2>
        {data.tier && <Badge kind={tierKind(data.tier)}>{TIER_CN[data.tier]}</Badge>}
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <Stat label="平均掌握度" value={pct(data.avg_mastery)} />
        <Stat label="全班正确率" value={pct(data.accuracy)} />
        <Stat label="作答学生" value={data.students.length} hint={`其中薄弱 ${weak.length} 人`} />
      </div>

      <Card>
        <SectionTitle right={<span className="text-xs text-gray-400">按正确率升序</span>}>
          学生掌握情况
        </SectionTitle>
        {data.students.length === 0 ? (
          <Empty text="该范围暂无作答数据。" />
        ) : (
          <div className="divide-y divide-gray-50">
            {[...data.students]
              .sort((a, b) => (a.accuracy ?? 1) - (b.accuracy ?? 1))
              .map((s) => (
                <div
                  key={s.student_no}
                  className="py-2 flex items-center gap-3 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded-lg"
                  onClick={() => nav(`/course/${code}/student/${s.student_no}${q}`)}
                >
                  <span className="text-sm text-gray-800 w-28 truncate">{s.name || s.student_no}</span>
                  <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                    <div
                      className="h-2 rounded-full"
                      style={{ width: `${Math.round((s.accuracy ?? 0) * 100)}%`, background: masteryColor(s.accuracy) }}
                    />
                  </div>
                  <span className="text-sm font-semibold w-12 text-right" style={{ color: masteryColor(s.accuracy) }}>
                    {pct(s.accuracy)}
                  </span>
                  <span className="text-xs text-gray-400 w-12 text-right">{s.correct}/{s.total}</span>
                </div>
              ))}
          </div>
        )}
      </Card>

      <p className="text-xs text-gray-400">前置知识链路（图谱）将在 v2 知识图谱前置边就绪后展示。</p>
    </div>
  )
}
