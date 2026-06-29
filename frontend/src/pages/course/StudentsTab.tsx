import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../services/api'
import { useAsync } from '../../hooks/useAsync'
import { Card, Loading, ErrorBox, Empty, Badge, pct, masteryColor } from '../../components/ui'
import type { RosterStudent } from '../../types'

type Filter = 'all' | 'excellent' | 'on_track' | 'weak' | 'untested' | 'attitude'

const TIER_CN: Record<RosterStudent['tier'], string> = {
  excellent: '优秀', on_track: '达标', weak: '薄弱', untested: '未测',
}
const TIER_KIND: Record<RosterStudent['tier'], string> = {
  excellent: 'mastered', on_track: 'on_track', weak: 'unlearned', untested: 'low',
}

export default function StudentsTab({ courseCode, className, reloadKey }: { courseCode: string; className: string; reloadKey: number }) {
  const nav = useNavigate()
  const { data, loading, error } = useAsync(() => api.roster(courseCode, className), [courseCode, className, reloadKey])
  const [filter, setFilter] = useState<Filter>('all')
  const [q, setQ] = useState('')

  const rows = useMemo(() => {
    const list = data?.students || []
    const kw = q.trim().toLowerCase()
    return list.filter((s) => {
      const okFilter =
        filter === 'all' ? true : filter === 'attitude' ? s.attitude : s.tier === filter
      const okKw =
        !kw || (s.name || '').toLowerCase().includes(kw) || s.student_no.toLowerCase().includes(kw)
      return okFilter && okKw
    })
  }, [data, filter, q])

  if (loading) return <Loading />
  if (error) return <ErrorBox message={error} />
  if (!data) return <Empty text="暂无数据。" />

  const c = data.counts
  const chips: { key: Filter; label: string; n: number }[] = [
    { key: 'all', label: '全部', n: data.students.length },
    { key: 'excellent', label: '优秀', n: c.excellent },
    { key: 'on_track', label: '达标', n: c.on_track },
    { key: 'weak', label: '薄弱', n: c.weak },
    { key: 'untested', label: '未测', n: c.untested },
    { key: 'attitude', label: '态度(作业差)', n: c.attitude },
  ]

  const clsSuffix = className ? `?class=${encodeURIComponent(className)}` : ''

  return (
    <Card>
      <div className="flex flex-wrap items-center gap-2 mb-4">
        {chips.map((ch) => (
          <button
            key={ch.key}
            onClick={() => setFilter(ch.key)}
            className={`px-3 py-1 rounded-full text-sm border transition ${
              filter === ch.key
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
            }`}
          >
            {ch.label} <span className="font-semibold">{ch.n}</span>
          </button>
        ))}
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="搜索姓名 / 学号"
          className="ml-auto border border-gray-300 rounded-lg px-3 py-1.5 text-sm w-44"
        />
      </div>

      {rows.length === 0 ? (
        <Empty text="无匹配学生。" />
      ) : (
        <div className="overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-100">
                <th className="py-2 font-medium">学生</th>
                <th className="py-2 font-medium">班级</th>
                <th className="py-2 font-medium">分层</th>
                <th className="py-2 font-medium text-right">掌握度</th>
                <th className="py-2 font-medium text-right">正确率</th>
                <th className="py-2 font-medium text-right">作业</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((s) => (
                <tr
                  key={s.student_no}
                  className="border-b border-gray-50 cursor-pointer hover:bg-gray-50"
                  onClick={() => nav(`/course/${courseCode}/student/${s.student_no}${clsSuffix}`)}
                >
                  <td className="py-2">
                    <span className="text-gray-800">{s.name || s.student_no}</span>
                    <span className="text-xs text-gray-400 ml-2">{s.student_no}</span>
                  </td>
                  <td className="py-2 text-gray-500 text-xs">{s.class_name || '—'}</td>
                  <td className="py-2">
                    <Badge kind={TIER_KIND[s.tier]}>{TIER_CN[s.tier]}</Badge>
                    {s.attitude && <span className="ml-1 text-xs text-amber-600">态度</span>}
                  </td>
                  <td className="py-2 text-right font-semibold" style={{ color: masteryColor(s.avg_mastery) }}>
                    {pct(s.avg_mastery)}
                  </td>
                  <td className="py-2 text-right text-gray-600">{pct(s.accuracy)}</td>
                  <td className="py-2 text-right text-gray-600">{s.homework_score ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  )
}
