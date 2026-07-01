import type { ReactNode } from 'react'
import { api } from '../../services/api'
import { useAsync } from '../../hooks/useAsync'
import {
  Card, Stat, Loading, ErrorBox, Empty, Donut, SectionTitle, COLORS, pct, useTierLabels,
} from '../../components/ui'
import { useLang } from '../../i18n'

export default function OverviewTab({ courseCode, className, reloadKey }: { courseCode: string; className: string; reloadKey: number }) {
  const { t } = useLang()
  const tierLabels = useTierLabels()
  const { data, loading, error } = useAsync(
    () => api.dashboard(courseCode, className),
    [courseCode, className, reloadKey],
  )

  if (loading) return <Loading />
  if (error) return <ErrorBox message={error} />
  if (!data) return <Empty text={t.noData} />

  const { stats, mastery } = data
  const dist = mastery.distribution
  const hasMastery = mastery.tested_students > 0

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat label={t.studentCount} value={stats.student_count} hint={t.tested(stats.tested_students)} />
        <Stat label={t.globalAccuracy} value={pct(stats.accuracy)} hint={t.responses(stats.response_count)} />
        <Stat label={t.avgMastery} value={pct(mastery.avg_mastery)} hint={t.bktHint} />
        <Stat label={t.chaptersClasses} value={`${stats.chapter_count} / ${stats.class_count}`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card>
          <SectionTitle>{t.masteryDistribution}</SectionTitle>
          {hasMastery ? (
            <div className="flex items-center gap-6">
              <Donut
                segments={[
                  { value: dist.mastered, color: COLORS.mastered },
                  { value: dist.partial, color: COLORS.partial },
                  { value: dist.unlearned, color: COLORS.unlearned },
                ]}
                centerTop={mastery.tested_students}
                centerBottom={t.testedStudents}
              />
              <div className="space-y-2">
                {([
                  ['mastered', dist.mastered, COLORS.mastered, t.excellent],
                  ['partial', dist.partial, COLORS.partial, t.onTrack],
                  ['unlearned', dist.unlearned, COLORS.unlearned, t.weak],
                ] as const).map(([k, v, color, label]) => (
                  <div key={k} className="flex items-center gap-2 text-sm">
                    <span className="inline-block w-3 h-3 rounded-sm" style={{ background: color }} />
                    <span className="text-gray-700 w-20">{label}</span>
                    <span className="font-semibold text-gray-900">{v}{t.people && ` ${t.people}`}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <Empty text={t.noMasteryData} />
          )}
        </Card>

        <Card>
          <SectionTitle>{t.engagementGrades}</SectionTitle>
          <div className="grid grid-cols-2 gap-x-6 gap-y-4 text-sm">
            <Metric label={t.avgDiscussion} value={stats.engagement.avg_discussion_count ?? '—'} />
            <Metric label={t.avgChapterVisits} value={stats.engagement.avg_chapter_visits ?? '—'} />
            <Metric label={t.avgHomework} value={stats.grade.avg_homework ?? '—'} />
            <Metric label={t.avgFinal} value={stats.grade.avg_final ?? '—'} />
          </div>
          <p className="text-xs text-gray-400 mt-4">{t.engagementNote}</p>
        </Card>
      </div>

      <p className="text-xs text-gray-400">{t.tierNote}</p>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-gray-500">{label}</span>
      <span className="font-semibold text-gray-900">{value}</span>
    </div>
  )
}
