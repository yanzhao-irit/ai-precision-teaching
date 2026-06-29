import type { ReactNode } from 'react'
import { api } from '../../services/api'
import { useAsync } from '../../hooks/useAsync'
import {
  Card, Stat, Loading, ErrorBox, Empty, Donut, SectionTitle, COLORS, TIER_CN, pct,
} from '../../components/ui'

export default function OverviewTab({ courseCode, className, reloadKey }: { courseCode: string; className: string; reloadKey: number }) {
  const { data, loading, error } = useAsync(
    () => api.dashboard(courseCode, className),
    [courseCode, className, reloadKey],
  )

  if (loading) return <Loading />
  if (error) return <ErrorBox message={error} />
  if (!data) return <Empty text="暂无数据。" />

  const { stats, mastery } = data
  const dist = mastery.distribution
  const hasMastery = mastery.tested_students > 0

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat label="学生人数" value={stats.student_count} hint={`已测 ${stats.tested_students} 人`} />
        <Stat label="整体正确率" value={pct(stats.accuracy)} hint={`${stats.response_count} 次作答`} />
        <Stat label="平均掌握度" value={pct(mastery.avg_mastery)} hint="BKT · 三档 0.7 / 0.4" />
        <Stat label="已测章节 / 班级" value={`${stats.chapter_count} / ${stats.class_count}`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <Card>
          <SectionTitle>学生掌握分层</SectionTitle>
          {hasMastery ? (
            <div className="flex items-center gap-6">
              <Donut
                segments={[
                  { value: dist.mastered, color: COLORS.mastered },
                  { value: dist.partial, color: COLORS.partial },
                  { value: dist.unlearned, color: COLORS.unlearned },
                ]}
                centerTop={mastery.tested_students}
                centerBottom="已测学生"
              />
              <div className="space-y-2">
                {([
                  ['mastered', dist.mastered, COLORS.mastered, '优秀'],
                  ['partial', dist.partial, COLORS.partial, '达标'],
                  ['unlearned', dist.unlearned, COLORS.unlearned, '薄弱'],
                ] as const).map(([k, v, color, cn]) => (
                  <div key={k} className="flex items-center gap-2 text-sm">
                    <span className="inline-block w-3 h-3 rounded-sm" style={{ background: color }} />
                    <span className="text-gray-700 w-16">{cn}</span>
                    <span className="font-semibold text-gray-900">{v} 人</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <Empty text="该范围暂无逐题作答数据（仅客观单元测试 .doc 含逐题对错）。" />
          )}
        </Card>

        <Card>
          <SectionTitle>学习参与 · 成绩</SectionTitle>
          <div className="grid grid-cols-2 gap-x-6 gap-y-4 text-sm">
            <Metric label="人均讨论数" value={stats.engagement.avg_discussion_count ?? '—'} />
            <Metric label="人均章节访问" value={stats.engagement.avg_chapter_visits ?? '—'} />
            <Metric label="平均作业分" value={stats.grade.avg_homework ?? '—'} />
            <Metric label="平均综合分" value={stats.grade.avg_final ?? '—'} />
          </div>
          <p className="text-xs text-gray-400 mt-4">参与/成绩来自班级一键导出（聚合信号），覆盖全部学生。</p>
        </Card>
      </div>

      <p className="text-xs text-gray-400">
        分层说明：优秀（掌握度 ≥70%）/ 达标（40–70%）/ 薄弱（&lt;40%）。{TIER_CN.mastered}口径与个体诊断一致。
      </p>
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
