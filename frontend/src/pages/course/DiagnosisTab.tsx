import { useNavigate } from 'react-router-dom'
import { api } from '../../services/api'
import { useAsync } from '../../hooks/useAsync'
import {
  Card, Loading, ErrorBox, Empty, RankRow, SectionTitle, COLORS, TIER_CN, pct, masteryColor,
} from '../../components/ui'

export default function DiagnosisTab({ courseCode, className, reloadKey }: { courseCode: string; className: string; reloadKey: number }) {
  const nav = useNavigate()
  const weak = useAsync(() => api.weakKPs(courseCode, className, 10), [courseCode, className, reloadKey])
  const hard = useAsync(() => api.highErrorQuestions(courseCode, className, 10), [courseCode, className, reloadKey])
  const q = className ? `?class=${encodeURIComponent(className)}` : ''

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <Card>
        <SectionTitle right={<span className="text-xs text-gray-400">点击查看详情</span>}>
          薄弱知识点 Top 10
        </SectionTitle>
        {weak.loading ? <Loading /> : weak.error ? <ErrorBox message={weak.error} /> :
          !weak.data || weak.data.length === 0 ? <Empty text="暂无数据。" /> : (
            <div className="divide-y divide-gray-50">
              {weak.data.map((k) => (
                <RankRow
                  key={k.kp_code}
                  label={k.label}
                  sub={<>掌握度 {pct(k.avg_mastery)} · 正确率 {pct(k.accuracy)} · {k.student_count} 人</>}
                  value={k.avg_mastery}
                  display={TIER_CN[k.tier] || ''}
                  color={masteryColor(k.avg_mastery)}
                  onClick={() => nav(`/course/${courseCode}/kp/${encodeURIComponent(k.kp_code)}${q}`)}
                />
              ))}
            </div>
          )}
      </Card>

      <Card>
        <SectionTitle right={<span className="text-xs text-gray-400">点击查看详情</span>}>
          高错题 Top 10
        </SectionTitle>
        {hard.loading ? <Loading /> : hard.error ? <ErrorBox message={hard.error} /> :
          !hard.data || hard.data.length === 0 ? <Empty text="暂无数据。" /> : (
            <div className="divide-y divide-gray-50">
              {hard.data.map((qq) => (
                <RankRow
                  key={qq.question_id}
                  label={<>第 {qq.seq_no} 题 · {qq.kp_label || '未标知识点'}</>}
                  sub={<span className="line-clamp-1">{qq.stem}</span>}
                  value={qq.error_rate ?? 0}
                  display={`错 ${pct(qq.error_rate)}`}
                  color={COLORS.unlearned}
                  onClick={() => nav(`/course/${courseCode}/question/${qq.question_id}${q}`)}
                />
              ))}
            </div>
          )}
      </Card>
    </div>
  )
}
