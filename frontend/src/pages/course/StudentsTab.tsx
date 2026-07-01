import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../../services/api'
import { useAsync } from '../../hooks/useAsync'
import { Card, Loading, ErrorBox, Empty, Badge, pct, masteryColor } from '../../components/ui'
import { useLang } from '../../i18n'
import type { RosterStudent } from '../../types'

type Filter = 'all' | 'excellent' | 'on_track' | 'weak' | 'untested' | 'attitude'

const TIER_KIND: Record<RosterStudent['tier'], string> = {
  excellent: 'mastered', on_track: 'on_track', weak: 'unlearned', untested: 'low',
}

export default function StudentsTab({ courseCode, className, reloadKey }: { courseCode: string; className: string; reloadKey: number }) {
  const nav = useNavigate()
  const { t } = useLang()
  const { data, loading, error } = useAsync(() => api.roster(courseCode, className), [courseCode, className, reloadKey])
  const [filter, setFilter] = useState<Filter>('all')
  const [q, setQ] = useState('')

  const TIER_LABEL: Record<RosterStudent['tier'], string> = {
    excellent: t.filterExcellent,
    on_track: t.filterOnTrack,
    weak: t.filterWeak,
    untested: t.filterUntested,
  }

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
  if (!data) return <Empty text={t.noData} />

  const c = data.counts
  const chips: { key: Filter; label: string; n: number }[] = [
    { key: 'all', label: t.filterAll, n: data.students.length },
    { key: 'excellent', label: t.filterExcellent, n: c.excellent },
    { key: 'on_track', label: t.filterOnTrack, n: c.on_track },
    { key: 'weak', label: t.filterWeak, n: c.weak },
    { key: 'untested', label: t.filterUntested, n: c.untested },
    { key: 'attitude', label: t.filterAttitude, n: c.attitude },
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
          placeholder={t.searchPlaceholder}
          className="ml-auto border border-gray-300 rounded-lg px-3 py-1.5 text-sm w-44"
        />
      </div>

      {rows.length === 0 ? (
        <Empty text={t.noMatchStudents} />
      ) : (
        <div className="overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-100">
                <th className="py-2 font-medium">{t.colStudent}</th>
                <th className="py-2 font-medium">{t.colClass}</th>
                <th className="py-2 font-medium">{t.colTier}</th>
                <th className="py-2 font-medium text-right">{t.colMastery}</th>
                <th className="py-2 font-medium text-right">{t.colAccuracy}</th>
                <th className="py-2 font-medium text-right">{t.colHomework}</th>
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
                    <Badge kind={TIER_KIND[s.tier]}>{TIER_LABEL[s.tier]}</Badge>
                    {s.attitude && <span className="ml-1 text-xs text-amber-600">{t.attitude}</span>}
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
